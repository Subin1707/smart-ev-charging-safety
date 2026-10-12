from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "logs" / "telemetry" / "latest_state.json"
CONSTANTS_PATH = ROOT / "src" / "core" / "hang_so.h"


def load_reference_constants() -> dict[str, str]:
    constants: dict[str, str] = {}
    pattern = re.compile(r"^\s*#define\s+([A-Z0-9_]+)\s+(.+?)\s*$")
    for line in CONSTANTS_PATH.read_text(encoding="utf-8-sig").splitlines():
        match = pattern.match(line)
        if match:
            constants[match.group(1)] = match.group(2)
    return constants


def read_snapshot() -> tuple[dict[str, Any] | None, str | None]:
    for _ in range(10):
        try:
            return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8")), None
        except FileNotFoundError:
            return None, f"Snapshot not found: {SNAPSHOT_PATH.relative_to(ROOT).as_posix()}"
        except json.JSONDecodeError:
            time.sleep(0.02)
        except OSError as error:
            time.sleep(0.02)
            last_error = str(error)
    return None, f"Snapshot temporarily unavailable: {locals().get('last_error', 'invalid JSON')}"


def fmt_bool(value: Any) -> str:
    return "YES" if value else "NO"


def render(snapshot: dict[str, Any] | None, constants: dict[str, str], error: str | None) -> str:
    lines: list[str] = []
    lines.append("SMART EV LIVE MONITOR")
    lines.append("=" * 72)
    lines.append(f"Snapshot        : {SNAPSHOT_PATH.relative_to(ROOT).as_posix()}")
    lines.append(f"Reference source: {CONSTANTS_PATH.relative_to(ROOT).as_posix()}")
    lines.append(
        "Reference data  : "
        f"SOC_MAX={constants.get('SOC_MAX', '?')}, "
        f"TEMP_MAX={constants.get('NHIET_DO_TOI_DA', '?')}, "
        f"STATION_MAX={constants.get('CONG_SUAT_TRAM_TOI_DA', '?')}, "
        f"PORT_MAX={constants.get('CONG_SUAT_CONG_TOI_DA', '?')}"
    )

    if error:
        lines.append("")
        lines.append(f"WAITING         : {error}")
        lines.append("Start the simulator, then keep this monitor running.")
        return "\n".join(lines)

    if snapshot is None:
        return "\n".join(lines)

    station = snapshot.get("station", {})
    simulation = snapshot.get("simulation", {})
    vehicles = snapshot.get("vehicles", [])
    ports = snapshot.get("ports", [])
    queue = snapshot.get("queue", {})
    checks = snapshot.get("safetyChecks", [])
    events = snapshot.get("events", [])

    charging = [v for v in vehicles if v.get("state") == "CHARGING"]
    connected = [v for v in vehicles if v.get("connected")]
    authenticated = [v for v in vehicles if v.get("authenticated")]
    faults = [v for v in vehicles if v.get("fault")]

    lines.append("-" * 72)
    lines.append(
        f"Tick={snapshot.get('tick')} | Status={simulation.get('status')} | "
        f"Emergency={fmt_bool(station.get('emergency'))}"
    )
    lines.append(
        f"Power={station.get('totalPower', 0):.2f}/{station.get('maxPower', 0):.2f} kW | "
        f"Connected={len(connected)} | Authenticated={len(authenticated)} | "
        f"Charging={len(charging)} | Faults={len(faults)} | Queue={queue.get('count', 0)}"
    )

    lines.append("")
    lines.append("VEHICLES")
    lines.append("ID    STATE       SOC     TEMP    POWER   PORT AUTH CONN FAULT")
    for vehicle in vehicles:
        is_connected = bool(vehicle.get("connected"))
        port = vehicle.get("port") if is_connected else None
        fault = vehicle.get("fault") or "-"
        soc = f"{vehicle.get('soc', 0):>6.2f}" if is_connected else f"{'--':>6}"
        temperature = f"{vehicle.get('temperature', 0):>7.2f}" if is_connected else f"{'--':>7}"
        power = f"{vehicle.get('allocatedPower', 0):>7.2f}" if is_connected else f"{'--':>7}"
        auth = fmt_bool(vehicle.get("authenticated")) if is_connected else "--"
        lines.append(
            f"{vehicle.get('id', '-'):<5} "
            f"{vehicle.get('state', '-'):<10} "
            f"{soc} "
            f"{temperature} "
            f"{power} "
            f"{str(port if port is not None else '-'):<4} "
            f"{auth:<4} "
            f"{fmt_bool(is_connected):<4} "
            f"{fault}"
        )

    lines.append("")
    lines.append("PORTS")
    lines.append("ID  STATE       VEHICLE POWER")
    for port in ports:
        lines.append(
            f"{port.get('id', '-'):<3} "
            f"{port.get('state', '-'):<10} "
            f"{str(port.get('vehicleId') or '-'):<7} "
            f"{port.get('power', 0):>6.2f}"
        )

    lines.append("")
    lines.append("SAFETY CHECKS")
    if checks:
        lines.append(", ".join(f"{check.get('id')}={check.get('status')}" for check in checks))
    else:
        lines.append("No safety checks in snapshot.")

    lines.append("")
    lines.append("LATEST EVENTS")
    for event in events[-5:]:
        lines.append(
            f"t={event.get('tick')} {event.get('type')} {event.get('severity')} "
            f"{event.get('vehicleId')}: {event.get('code')}"
        )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Watch live simulator telemetry in the terminal.")
    parser.add_argument("--interval", type=float, default=1.0, help="Refresh interval in seconds.")
    parser.add_argument("--once", action="store_true", help="Print one snapshot and exit.")
    args = parser.parse_args()

    constants = load_reference_constants()
    while True:
        snapshot, error = read_snapshot()
        if not args.once:
            os.system("cls" if os.name == "nt" else "clear")
        print(render(snapshot, constants, error))
        if args.once:
            return
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
