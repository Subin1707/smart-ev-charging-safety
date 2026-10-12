from __future__ import annotations

import argparse
import ast
import json
import os
import re
import time
from itertools import product
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "specification"
SPEC_FILES = ["auth.json", "battery.json", "port.json", "charging.json"]
CONSTANTS_PATH = ROOT / "src" / "core" / "hang_so.h"
REFERENCE_CONSTANTS = [
    "SOC_MIN",
    "SOC_MAX",
    "NHIET_DO_TOI_DA",
    "NHIET_DO_TOI_THIEU",
    "CONG_SUAT_TRAM_TOI_DA",
    "CONG_SUAT_CONG_TOI_DA",
    "SO_CONG_SAC",
    "SO_XE_TOI_DA",
]


def load_spec(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_reference_constants() -> dict[str, str]:
    constants: dict[str, str] = {}
    pattern = re.compile(r"^\s*#define\s+([A-Z0-9_]+)\s+(.+?)\s*$")
    for line in CONSTANTS_PATH.read_text(encoding="utf-8-sig").splitlines():
        match = pattern.match(line)
        if match:
            constants[match.group(1)] = match.group(2)
    return constants


def print_reference_data(constants: dict[str, str]) -> None:
    print("[REFERENCE DATA]")
    print(f"Source          : {CONSTANTS_PATH.relative_to(ROOT).as_posix()}")
    for name in REFERENCE_CONSTANTS:
        if name in constants:
            print(f"{name:<16}: {constants[name]}")
    print()


def referenced_constants_for(spec_id: str) -> list[str]:
    if spec_id == "BATTERY":
        return ["SOC_MIN", "SOC_MAX", "NHIET_DO_TOI_DA", "NHIET_DO_TOI_THIEU"]
    if spec_id == "PORT":
        return ["SO_CONG_SAC", "SO_XE_TOI_DA", "CONG_SUAT_CONG_TOI_DA"]
    if spec_id == "CHARGING":
        return ["SOC_MAX", "NHIET_DO_TOI_DA", "CONG_SUAT_TRAM_TOI_DA", "CONG_SUAT_CONG_TOI_DA"]
    if spec_id == "AUTH":
        return ["DO_DAI_TOKEN"]
    return []


def bit_value(value: Any) -> str:
    if value in (0, 1):
        return str(value)
    return str(value)


def state_id(values: tuple[Any, ...]) -> str:
    if all(value in (0, 1) for value in values):
        return "".join(str(value) for value in values)
    return " | ".join(str(value) for value in values)


def evaluate(expression: str, env: dict[str, Any]) -> bool:
    safe_globals = {"__builtins__": {}}
    return bool(eval(expression, safe_globals, env))


def expression_names(expression: str) -> set[str]:
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        return set()
    return {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}


def add_derived_values(spec: dict[str, Any], env: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(env)
    for name, expression in spec.get("derived", {}).items():
        try:
            enriched[name] = evaluate(expression, enriched)
        except NameError:
            continue
    return enriched


def valid_state(spec: dict[str, Any], env: dict[str, Any]) -> bool:
    enriched = add_derived_values(spec, env)
    if spec.get("id") == "CHARGING" and "VALID" in enriched:
        return bool(enriched["VALID"])

    for constraint in spec["constraints"]:
        if constraint.get("scope", "state") != "state":
            continue
        expression = constraint.get("expression")
        if not expression:
            continue
        if not expression_names(expression).issubset(enriched):
            continue
        if not evaluate(expression, enriched):
            return False
    return True


def derived_value(spec: dict[str, Any], env: dict[str, Any], name: str) -> Any:
    return add_derived_values(spec, env).get(name)


def enumerate_states(spec: dict[str, Any]) -> tuple[list[tuple[Any, ...]], list[tuple[Any, ...]]]:
    parameters = spec["parameters"]
    domains = [parameter["domain"] for parameter in parameters]
    valid: list[tuple[Any, ...]] = []
    rejected: list[tuple[Any, ...]] = []

    for values in product(*domains):
        env = {parameter["symbol"]: value for parameter, value in zip(parameters, values)}
        if valid_state(spec, env):
            valid.append(values)
        else:
            rejected.append(values)

    return valid, rejected


def print_report(spec: dict[str, Any], constants: dict[str, str]) -> None:
    parameters = spec["parameters"]
    raw_states = 1
    for parameter in parameters:
        raw_states *= len(parameter["domain"])

    valid, rejected = enumerate_states(spec)

    print(f"[{spec['id']}]")
    print(f"Name            : {spec['name']}")
    print(f"Parameters      : {len(parameters)}")
    print("Symbols         : " + " ".join(parameter["symbol"] for parameter in parameters))
    print(f"Raw states      : {raw_states}")
    if spec["id"] == "CHARGING":
        print(f"Charging-allowed states : {len(valid)}")
        print(f"Charging-blocked states : {len(rejected)}")
    else:
        print(f"Valid states    : {len(valid)}")
        print(f"Rejected states : {len(rejected)}")
    print("Requirements    : " + ", ".join(req["id"] for req in spec["requirements"]))
    if spec.get("source_references"):
        print("Source refs     : " + ", ".join(spec["source_references"]))
    referenced = referenced_constants_for(spec["id"])
    if referenced:
        rendered = [
            f"{name}={constants[name]}"
            for name in referenced
            if name in constants
        ]
        if rendered:
            print("Reference data  : " + ", ".join(rendered))
    print("Constraints:")
    for constraint in spec["constraints"]:
        scope = constraint.get("scope", "state")
        print(f"  - {constraint['id']} [{scope}]: {constraint['formula']}")
    print("Allowed state IDs:" if spec["id"] == "CHARGING" else "Valid state IDs:")
    for values in valid:
        print(f"  {state_id(values)}")
    if spec["id"] == "CHARGING":
        print("Classification rule : VALID == true => charging_allowed; VALID == false => charging_blocked")
    if rejected:
        print("Blocked state IDs:" if spec["id"] == "CHARGING" else "Rejected state IDs:")
        for values in rejected:
            print(f"  {state_id(values)}")
    print()


def run_once() -> None:
    constants = load_reference_constants()
    print_reference_data(constants)
    for filename in SPEC_FILES:
        print_report(load_spec(SPEC_DIR / filename), constants)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and print formal state-space summaries.")
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Continuously print the reference data and state-space summary.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Refresh interval in seconds when --watch is enabled.",
    )
    args = parser.parse_args()

    if not args.watch:
        run_once()
        return

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print(f"State-space monitor | refresh interval: {args.interval:.1f}s")
        print("Press Ctrl+C to stop.\n")
        run_once()
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
