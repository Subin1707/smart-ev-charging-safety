import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).resolve().parents[2]
E2E_PORT = os.getenv("SMART_EV_E2E_PORT", "8010")
BASE_URL = os.getenv("SMART_EV_E2E_BASE_URL", f"http://127.0.0.1:{E2E_PORT}")


def pytest_sessionfinish(session, exitstatus):
    report_path = ROOT / "reports" / "e2e" / "report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    total = session.testscollected
    failed = session.testsfailed
    report_path.write_text(
        json.dumps({
            "status": "PASS" if exitstatus == 0 and total > 0 else "FAIL",
            "total": total,
            "passed": max(0, total - failed),
            "failed": failed,
        }, indent=2) + "\n",
        encoding="utf-8",
    )


def get_state():
    response = requests.get(f"{BASE_URL}/api/state", timeout=2)
    response.raise_for_status()
    return response.json()


def wait_until(predicate, timeout=8, interval=0.1):
    deadline = time.monotonic() + timeout
    last_state = None

    while time.monotonic() < deadline:
        try:
            last_state = get_state()
        except requests.RequestException:
            time.sleep(interval)
            continue
        if predicate(last_state):
            return last_state
        time.sleep(interval)

    raise AssertionError(f"Timed out waiting for simulator state; last state: {last_state}")


def post(path, **kwargs):
    response = requests.post(f"{BASE_URL}{path}", timeout=2, **kwargs)
    response.raise_for_status()
    return response.json()


@pytest.fixture(scope="session")
def runtime_directory():
    runtime_root = ROOT / "evidence" / "06_e2e" / ".runtime"
    runtime_root.mkdir(parents=True, exist_ok=True)
    runtime = Path(tempfile.mkdtemp(prefix="e2e-runtime-", dir=str(runtime_root)))
    for directory in ("telemetry", "control", "simulation", "database"):
        (runtime / "logs" / directory).mkdir(parents=True)
    return runtime


@pytest.fixture(scope="session", autouse=True)
def bridge_process(runtime_directory):
    if os.getenv("SMART_EV_E2E_EXTERNAL_SERVICES") == "1":
        wait_until(lambda state: "tick" in state)
        yield
        return

    command = [sys.executable, "-m", "uvicorn", "bridge.main:app", "--host", "127.0.0.1", "--port", E2E_PORT]
    env = dict(os.environ,
               SMART_EV_SNAPSHOT_PATH=str(runtime_directory / "logs/telemetry/latest_state.json"),
               SMART_EV_COMMAND_PATH=str(runtime_directory / "logs/control/command.json"))
    bridge_log_path = ROOT / "evidence/06_e2e/bridge.log"
    bridge_log_path.parent.mkdir(parents=True, exist_ok=True)
    bridge_log = bridge_log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        env=env,
        stdout=bridge_log,
        stderr=bridge_log,
    )

    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("E2E bridge exited before readiness; check whether its port is occupied")
            try:
                response = requests.get(f"{BASE_URL}/api/health", timeout=1)
                if response.ok:
                    break
            except requests.RequestException:
                time.sleep(0.1)
        else:
            raise RuntimeError("FastAPI bridge did not become ready")
        yield
    finally:
        process.terminate()
        process.wait(timeout=5)
        bridge_log.close()


@pytest.fixture(scope='session')
def simulator_executable(runtime_directory):
    executable = runtime_directory / ("smart_ev.exe" if os.name == "nt" else "smart_ev")
    includes = [arg for directory in sorted((ROOT / "src").iterdir())
                if directory.is_dir() for arg in ("-I", str(directory))]
    sources = sorted(str(path) for path in (ROOT / "src").rglob("*.c"))
    subprocess.run(["gcc", "-Wall", "-Wextra", "-std=c17", *includes,
                    *sources, "-o", str(executable)], cwd=ROOT, check=True)
    return executable


@pytest.fixture
def simulator(bridge_process, simulator_executable, runtime_directory, request):
    if os.getenv("SMART_EV_E2E_EXTERNAL_SERVICES") == "1":
        yield None
        return
    executable = simulator_executable
    snapshot_path = runtime_directory / "logs" / "telemetry" / "latest_state.json"
    snapshot_path.unlink(missing_ok=True)

    env = os.environ.copy()
    env['SMART_EV_POSTGRES'] = '0'
    env.pop('SMART_EV_SCENARIO', None)
    if request.node.name == 'test_golden_ev03_overheat':
        env['SMART_EV_SCENARIO'] = 'GOLDEN_OVERHEAT'
    process = subprocess.Popen(
        [str(executable)],
        env=env,
        cwd=runtime_directory,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    process.stdin.write("2\n")
    process.stdin.flush()

    try:
        wait_until(lambda state: state.get("tick") == 0 and state.get("simulation", {}).get("status") == "PAUSED")
        yield process
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)


@pytest.fixture
def connected_vehicles(simulator):
    """Reserve all five ports, then explicitly deliver vehicle arrivals."""
    for tick in range(1, 6):
        post("/api/tick")
        wait_until(lambda state: state["tick"] == tick)
    state = get_state()
    for vehicle in state["vehicles"]:
        if vehicle["assignedPort"] is not None:
            post("/api/vehicle-arrived", json={
                "vehicleId": vehicle["id"], "portId": vehicle["assignedPort"]})
    wait_until(lambda state: sum(v["connected"] for v in state["vehicles"]) == 5)
