from __future__ import annotations

import json
import os
import time
import threading
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from spec_generator.pipeline import run_pipeline

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPEC_UPLOAD_ROOT = PROJECT_ROOT / ".tmp_spec_uploads"
ALLOWED_SPEC_EXTENSIONS = {".xlsx", ".csv", ".txt"}
MAX_SPEC_BYTES = 10 * 1024 * 1024
SNAPSHOT_PATH = Path(
    os.getenv(
        "SMART_EV_SNAPSHOT_PATH",
        PROJECT_ROOT / "logs" / "telemetry" / "latest_state.json",
    )
)

app = FastAPI(title="Smart EV Charging Safety Bridge", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class FaultRequest(BaseModel):
    vehicleId: str
    faultType: Literal["OVERHEAT", "AUTH_FAILURE", "UNEXPECTED_DISCONNECT"]


class VehicleArrivedRequest(BaseModel):
    vehicleId: str
    portId: int


class ScenarioRequest(BaseModel):
    scenario: Literal["NORMAL", "OVERHEAT", "CRITICAL_TEMPERATURE", "THERMAL_RUNAWAY", "FIRE_RISK", "AUTH_FAILURE", "UNEXPECTED_DISCONNECT", "POWER_OVERLOAD", "EMERGENCY_STOP", "MIXED"]
    vehicleId: str = ""


def read_snapshot() -> dict[str, Any]:
    # Windows can briefly deny access while the C writer replaces its snapshot.
    for attempt in range(10):
        try:
            with SNAPSHOT_PATH.open("r", encoding="utf-8") as snapshot_file:
                snapshot = json.load(snapshot_file)
                generated_at_ms = os.fstat(snapshot_file.fileno()).st_mtime_ns // 1_000_000
            break
        except (OSError, json.JSONDecodeError) as error:
            if attempt == 9:
                raise HTTPException(
                    status_code=503,
                    detail="C simulator snapshot is unavailable or invalid",
                ) from error
            time.sleep(0.01)

    if not isinstance(snapshot, dict) or "tick" not in snapshot:
        raise HTTPException(status_code=503, detail="C simulator snapshot has an invalid shape")

    snapshot["generatedAtMs"] = generated_at_ms
    snapshot["telemetryAgeMs"] = max(0, int(time.time() * 1000) - generated_at_ms)
    return snapshot


COMMAND_PATH = Path(
    os.getenv(
        "SMART_EV_COMMAND_PATH",
        PROJECT_ROOT / "logs" / "control" / "command.json",
    )
)


command_lock = threading.Lock()


def write_command(command: dict[str, Any]) -> None:
    with command_lock:
        snapshot = read_snapshot()
        command_name = command.get("command")
        stale_allowed_commands = {
            "RESET",
            "START",
            "NEXT_TICK",
            "PAUSE",
            "SET_SPEED",
            "EMERGENCY_RELEASE",
        }
        if snapshot["telemetryAgeMs"] > 3000 and command_name not in stale_allowed_commands:
            raise HTTPException(status_code=503, detail="C simulator is offline. Start smart_ev and select option 2.")
        deadline = time.monotonic() + 3
        while COMMAND_PATH.exists():
            try:
                pending = json.loads(COMMAND_PATH.read_text(encoding="utf-8"))
                if pending.get("command") == "NONE":
                    break
            except (OSError, json.JSONDecodeError):
                pass
            if time.monotonic() >= deadline:
                raise HTTPException(status_code=409, detail="Previous command has not been consumed by C simulator.")
            time.sleep(0.02)
        _write_command(command)
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            try:
                if json.loads(COMMAND_PATH.read_text(encoding="utf-8")).get("command") == "NONE":
                    return
            except (OSError, json.JSONDecodeError):
                pass
            time.sleep(0.02)
        raise HTTPException(status_code=504, detail="C simulator did not acknowledge the command.")


def _write_command(command: dict[str, Any]) -> None:
    COMMAND_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = COMMAND_PATH.with_suffix(".tmp")
    payload = json.dumps(command, separators=(",", ":")) + "\n"

    # On Windows, replacing an existing command.json can fail when the C simulator
    # is still reading it. Writing directly to the destination avoids the rename
    # race while keeping the file in the format the simulator expects.
    for attempt in range(20):
        try:
            with temp_path.open("w", encoding="utf-8") as command_file:
                command_file.write(payload)
                command_file.flush()
                os.fsync(command_file.fileno())

            try:
                os.replace(temp_path, COMMAND_PATH)
            except PermissionError:
                with COMMAND_PATH.open("w", encoding="utf-8") as command_file:
                    command_file.write(payload)
                    command_file.flush()
                    os.fsync(command_file.fileno())
            return
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.05)

    # Safety fallback for the rare case an OS file lock is still held.
    with COMMAND_PATH.open("w", encoding="utf-8") as command_file:
        command_file.write(payload)
        command_file.flush()
        os.fsync(command_file.fileno())


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "source": "c-simulator-snapshot"}


@app.get("/api/state")
def state() -> dict[str, Any]:
    return read_snapshot()


@app.get("/api/verification")
def verification() -> dict[str, Any]:
    report_path = PROJECT_ROOT / "reports" / "dashboard" / "summary.json"
    if not report_path.exists():
        return {
            "overallStatus": "UNKNOWN",
            "message": "Verification report not generated",
        }

    try:
        with report_path.open("r", encoding="utf-8") as report_file:
            return json.load(report_file)
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=503, detail="Verification report is invalid") from error


def _traceability_records() -> list[dict[str, Any]]:
    path = PROJECT_ROOT / "evidence" / "traceability.json"
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=503, detail="Traceability report is invalid") from error
    return payload if isinstance(payload, list) else []


@app.post("/api/specification/verify")
async def verify_specification(file: UploadFile = File(...)) -> dict[str, Any]:
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_SPEC_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Only .xlsx, .csv, and .txt files are supported")
    SPEC_UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    destination = SPEC_UPLOAD_ROOT / f"upload{extension}"
    total = 0
    try:
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_SPEC_BYTES:
                    destination.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail="Specification file exceeds 10 MB")
                output.write(chunk)
        run_pipeline(destination, PROJECT_ROOT / "spec_generator" / "input" / "code_mapping.json")
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Specification verification failed: {error}") from error
    summary_path = PROJECT_ROOT / "evidence" / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    return {"status": "completed", "filename": filename, "summary": summary}


@app.get("/api/verification/summary")
def verification_summary() -> dict[str, Any]:
    path = PROJECT_ROOT / "evidence" / "summary.json"
    if not path.exists():
        return {"total": 0, "pass": 0, "fail": 0, "inconclusive": 0, "not_mapped": 0, "not_verifiable": 0}
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/verification/requirements")
def verification_requirements() -> list[dict[str, Any]]:
    return _traceability_records()


@app.get("/api/verification/requirements/{requirement_id}")
def verification_requirement(requirement_id: str) -> dict[str, Any]:
    record = next((item for item in _traceability_records() if item.get("requirement_id") == requirement_id), None)
    if record is None:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return record


@app.get("/api/verification/requirements/{requirement_id}/evidence")
def verification_requirement_evidence(requirement_id: str) -> dict[str, Any]:
    record = verification_requirement(requirement_id)
    evidence = []
    for relative_path in record.get("evidence", []):
        path = (PROJECT_ROOT / relative_path).resolve()
        if PROJECT_ROOT.resolve() not in path.parents:
            continue
        if path.is_file():
            evidence.append({"path": relative_path, "content": path.read_text(encoding="utf-8", errors="replace")})
    return {"requirement_id": requirement_id, "evidence": evidence}


@app.get("/api/verification/evidence/{tool}")
def verification_evidence(tool: str) -> dict[str, Any]:
    allowed_tools = {"staticAnalysis", "memorySafety", "cbmc", "smtZ3", "fuzzing", "e2e", "goldenBrowser", "postgresql"}
    if tool not in allowed_tools:
        raise HTTPException(status_code=404, detail="Unknown verification tool")

    summary_path = PROJECT_ROOT / "reports" / "dashboard" / "summary.json"
    if not summary_path.exists():
        raise HTTPException(status_code=404, detail="Verification report not generated")

    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        report_name = summary.get("tools", {}).get(tool, {}).get("report")
        if not report_name:
            raise HTTPException(status_code=404, detail="Evidence not generated")
        report_path = (PROJECT_ROOT / report_name).resolve()
        reports_root = (PROJECT_ROOT / "reports").resolve()
        evidence_root = (PROJECT_ROOT / 'evidence').resolve()
        if reports_root not in report_path.parents and evidence_root not in report_path.parents:
            raise HTTPException(status_code=400, detail="Invalid evidence path")
        return {
            "tool": tool,
            "report": report_name,
            "content": report_path.read_text(encoding="utf-8", errors="replace"),
        }
    except HTTPException:
        raise
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=503, detail="Evidence report is invalid") from error


@app.post("/api/emergency-stop")
def emergency_stop() -> dict[str, Any]:
    write_command({"command": "EMERGENCY_STOP"})
    return {"accepted": True, "command": "EMERGENCY_STOP"}


@app.post("/api/start")
def start_simulation() -> dict[str, Any]:
    write_command({"command": "START"})
    return {"accepted": True, "command": "START"}


@app.post("/api/pause")
def pause_simulation() -> dict[str, Any]:
    write_command({"command": "PAUSE"})
    return {"accepted": True, "command": "PAUSE"}


@app.post("/api/tick")
def next_tick() -> dict[str, Any]:
    write_command({"command": "NEXT_TICK"})
    return {"accepted": True, "command": "NEXT_TICK"}


@app.post("/api/emergency-release")
def emergency_release() -> dict[str, Any]:
    write_command({"command": "EMERGENCY_RELEASE"})
    return {"accepted": True, "command": "EMERGENCY_RELEASE"}


@app.post("/api/fault")
def inject_fault(request: FaultRequest) -> dict[str, Any]:
    write_command({
        "command": "INJECT_FAULT",
        "vehicleId": request.vehicleId,
        "faultType": request.faultType,
    })
    return {
        "accepted": True,
        "vehicleId": request.vehicleId,
        "faultType": request.faultType,
    }


@app.post("/api/vehicle-arrived")
def vehicle_arrived(request: VehicleArrivedRequest) -> dict[str, Any]:
    write_command({
        "command": "VEHICLE_ARRIVED",
        "vehicleId": request.vehicleId,
        "portId": request.portId,
    })
    return {
        "accepted": True,
        "command": "VEHICLE_ARRIVED",
        "vehicleId": request.vehicleId,
        "portId": request.portId,
    }


@app.post("/api/scenario")
def load_scenario(request: ScenarioRequest) -> dict[str, Any]:
    write_command({
        "command": "LOAD_SCENARIO",
        "scenario": request.scenario,
        "vehicleId": request.vehicleId,
    })
    return {
        "accepted": True,
        "command": "LOAD_SCENARIO",
        "scenario": request.scenario,
        "vehicleId": request.vehicleId,
    }


@app.post("/api/reset")
def reset() -> dict[str, Any]:
    write_command({"command": "RESET"})
    return {"accepted": True, "command": "RESET"}


class SpeedRequest(BaseModel):
    speed: float


@app.post("/api/speed")
def set_speed(request: SpeedRequest) -> dict[str, Any]:
    if request.speed not in (0.5, 1, 2, 5):
        raise HTTPException(status_code=422, detail="Speed must be 0.5, 1, 2 or 5")
    write_command({"command": "SET_SPEED", "intervalMs": int(1000 / request.speed)})
    return {"accepted": True, "speed": request.speed}
