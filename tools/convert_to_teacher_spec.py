from __future__ import annotations

import json
from itertools import product
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "specification"
OUT_DIR = ROOT / "teacher_specs"

SPEC_FILES = [
    "auth.json",
    "battery.json",
    "port.json",
    "charging.json",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def requirement_category(requirement: dict[str, Any]) -> str:
    category = requirement.get("category") or requirement.get("type") or "functional"
    allowed = {"safety", "liveness", "memory", "functional"}
    return category if category in allowed else "functional"


def convert_requirements(spec: dict[str, Any]) -> list[dict[str, Any]]:
    converted = []
    for requirement in spec.get("requirements", []):
        converted.append(
            {
                "id": requirement["id"],
                "text": requirement.get("text", requirement.get("description", requirement["id"])),
                "category": requirement_category(requirement),
                "priority": requirement.get("priority", "MEDIUM"),
            }
        )
    converted.extend(codegen_requirements(spec))
    return converted


def codegen_requirements(spec: dict[str, Any]) -> list[dict[str, str]]:
    spec_id = spec["id"]
    if spec_id == "AUTH":
        return [
            {
                "id": "REQ-AUTH-CODE-01",
                "text": "Generated token parsing code must handle fixed-size token buffers safely.",
                "category": "memory",
                "priority": "HIGH",
            },
            {
                "id": "REQ-AUTH-CODE-02",
                "text": "Generated authentication-ratio code must tolerate zero total attempts during fuzzing.",
                "category": "functional",
                "priority": "MEDIUM",
            },
        ]
    if spec_id == "BATTERY":
        return [
            {
                "id": "REQ-BAT-CODE-01",
                "text": "Generated battery telemetry code must handle bounded SOC and temperature calculations.",
                "category": "safety",
                "priority": "HIGH",
            },
            {
                "id": "REQ-BAT-CODE-02",
                "text": "Generated SOC ratio code must tolerate zero capacity values during fuzzing.",
                "category": "functional",
                "priority": "MEDIUM",
            },
        ]
    if spec_id == "PORT":
        return [
            {
                "id": "REQ-PORT-CODE-01",
                "text": "Generated port identifier parsing code must not overflow its fixed-size buffer.",
                "category": "memory",
                "priority": "HIGH",
            },
            {
                "id": "REQ-PORT-CODE-02",
                "text": "Generated port allocation cleanup code must release allocated memory exactly once.",
                "category": "memory",
                "priority": "HIGH",
            },
        ]
    if spec_id == "CHARGING":
        return [
            {
                "id": "REQ-CHG-CODE-01",
                "text": "Generated charging session code must safely copy vehicle identifiers into fixed-size buffers.",
                "category": "memory",
                "priority": "HIGH",
            },
            {
                "id": "REQ-CHG-CODE-02",
                "text": "Generated power aggregation checks must expose possible int32 overflow in total charging power.",
                "category": "safety",
                "priority": "HIGH",
            },
            {
                "id": "REQ-CHG-CODE-03",
                "text": "Generated charging efficiency code must tolerate zero delivered energy during fuzzing.",
                "category": "functional",
                "priority": "MEDIUM",
            },
        ]
    return []


def labels_for_state(spec: dict[str, Any], state: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    state_id = state["id"]

    if state.get("valid") is False:
        labels.extend(["rejected", "violation"])
    elif state.get("classification") == "charging_allowed" or state.get("charging_allowed") is True:
        labels.extend(["safe", "charging_allowed"])
    elif state.get("classification") == "charging_blocked" or state.get("charging_allowed") is False:
        labels.extend(["safe", "charging_blocked"])
    else:
        labels.append("safe")

    if "reason" in state:
        labels.append(state["reason"])

    if "violates" in state:
        labels.extend(state["violates"])

    labels.append(state_id.lower())
    labels.append(spec["id"].lower())
    return sorted(set(labels))


def state_machine_from_examples(spec: dict[str, Any]) -> dict[str, Any] | None:
    examples = spec.get("example_states") or []
    if not examples:
        return None

    states = [state["id"] for state in examples]
    known = set(states)
    initial = spec.get("initial_state")
    initial_id = examples[0]["id"]
    if isinstance(initial, dict):
        encoding = spec.get("state_encoding", [parameter["symbol"] for parameter in spec.get("parameters", [])])
        bits = "".join(str(initial.get(symbol, 0)) for symbol in encoding)
        initial_id = next((state["id"] for state in examples if state.get("bits") == bits), initial_id)

    labeling = {state["id"]: labels_for_state(spec, state) for state in examples}

    transitions = []
    for transition in spec.get("transitions", []):
        source = transition["from"]
        target = transition["to"]
        if source in known and target in known:
            transitions.append([source, target])

    if not transitions:
        transitions = [[state, state] for state in states]

    outgoing = {source for source, _ in transitions}
    for state in states:
        if state not in outgoing:
            transitions.append([state, state])

    return {
        "states": states,
        "initial": [initial_id],
        "labeling": labeling,
        "transitions": transitions,
    }


def bool_state_id(values: tuple[Any, ...]) -> str:
    return "".join(str(value) for value in values)


def charging_state_machine(spec: dict[str, Any]) -> dict[str, Any]:
    parameters = spec["parameters"]
    domains = [parameter["domain"] for parameter in parameters]
    states = []
    labeling: dict[str, list[str]] = {}

    for values in product(*domains):
        state = bool_state_id(values)
        env = {parameter["symbol"]: value for parameter, value in zip(parameters, values)}
        valid = bool(env["C"] and env["A"] and env["B"] and env["T"] and env["P"] and not env["E"] and not env["F"])
        states.append(state)
        labels = ["charging_allowed" if valid else "charging_blocked", "charging", "safe"]
        if not env["C"]:
            labels.append("connection_required")
        if not env["A"]:
            labels.append("authentication_required")
        if not env["B"]:
            labels.append("battery_unsafe")
        if not env["T"]:
            labels.append("temperature_unsafe")
        if not env["P"]:
            labels.append("port_not_ready")
        if env["E"]:
            labels.append("emergency_active")
        if env["F"]:
            labels.append("fault_active")
        labeling[state] = sorted(set(labels))

    transitions = [[state, state] for state in states]
    allowed = "1111100"
    for state in states:
        if state != allowed:
            transitions.append([state, allowed])
            transitions.append([allowed, state])

    return {
        "states": states,
        "initial": ["0000000"],
        "labeling": labeling,
        "transitions": transitions,
    }


def convert_state_machine(spec: dict[str, Any]) -> dict[str, Any] | None:
    if spec["id"] == "CHARGING":
        return charging_state_machine(spec)
    return state_machine_from_examples(spec)


def codegen_functions(spec: dict[str, Any]) -> list[dict[str, Any]]:
    spec_id = spec["id"]
    if spec_id == "AUTH":
        return [
            {
                "name": "parse_vehicle_token",
                "language": "c",
                "kind": "buffer_copy",
                "params": ["raw_token"],
                "buffer_size": 32,
                "bug": None,
            },
            {
                "name": "cleanup_auth_session",
                "language": "c",
                "kind": "alloc_release",
                "params": [],
                "buffer_size": 8,
                "bug": None,
            },
            {
                "name": "auth_success_ratio",
                "language": "python",
                "kind": "divide",
                "params": ["success_count", "attempt_count"],
            },
        ]
    if spec_id == "BATTERY":
        return [
            {
                "name": "copy_battery_sensor_frame",
                "language": "c",
                "kind": "buffer_copy",
                "params": ["raw_frame"],
                "buffer_size": 24,
                "bug": None,
            },
            {
                "name": "sum_soc_temperature",
                "language": "c",
                "kind": "arithmetic",
                "params": ["soc", "temperature"],
            },
            {
                "name": "soc_capacity_ratio",
                "language": "python",
                "kind": "divide",
                "params": ["soc_percent", "capacity_percent"],
            },
        ]
    if spec_id == "PORT":
        return [
            {
                "name": "parse_port_identifier",
                "language": "c",
                "kind": "buffer_copy",
                "params": ["raw_port_id"],
                "buffer_size": 16,
                "bug": None,
            },
            {
                "name": "release_port_assignment",
                "language": "c",
                "kind": "alloc_release",
                "params": [],
                "buffer_size": 12,
                "bug": None,
            },
            {
                "name": "port_load_ratio",
                "language": "python",
                "kind": "divide",
                "params": ["occupied_ports", "total_ports"],
            },
        ]
    if spec_id == "CHARGING":
        return [
            {
                "name": "copy_charging_vehicle_id",
                "language": "c",
                "kind": "buffer_copy",
                "params": ["vehicle_id"],
                "buffer_size": 20,
                "bug": None,
            },
            {
                "name": "release_charging_session",
                "language": "c",
                "kind": "alloc_release",
                "params": [],
                "buffer_size": 16,
                "bug": None,
            },
            {
                "name": "sum_station_power",
                "language": "c",
                "kind": "arithmetic",
                "params": ["port_power", "queued_power"],
            },
            {
                "name": "charging_efficiency_ratio",
                "language": "python",
                "kind": "divide",
                "params": ["delivered_energy", "requested_energy"],
            },
            {
                "name": "emergency_override_code",
                "language": "python",
                "kind": "magic_value",
                "params": ["code_a", "code_b"],
                "magic_values": [2718, 3141],
            },
        ]
    return []


def arithmetic_checks(spec: dict[str, Any]) -> list[dict[str, Any]]:
    spec_id = spec["id"]
    if spec_id == "AUTH":
        return [
            {
                "name": "auth_attempt_counter",
                "int_vars": ["failed_attempts", "successful_attempts"],
                "condition": "failed_attempts >= 0 and successful_attempts >= 0",
                "overflow_expr": "failed_attempts + successful_attempts",
            }
        ]
    if spec_id == "BATTERY":
        return [
            {
                "name": "battery_sensor_sum",
                "int_vars": ["soc_scaled", "temperature_scaled"],
                "condition": "soc_scaled >= 0 and temperature_scaled >= -2000",
                "overflow_expr": "soc_scaled + temperature_scaled",
            }
        ]
    if spec_id == "PORT":
        return [
            {
                "name": "port_vehicle_assignment_counter",
                "int_vars": ["ports", "vehicles"],
                "condition": "ports >= 0 and vehicles >= 0",
                "overflow_expr": "ports + vehicles",
            }
        ]
    if spec_id == "CHARGING":
        return [
            {
                "name": "station_power_aggregation",
                "int_vars": ["active_power_kw", "queued_power_kw"],
                "condition": "active_power_kw >= 0 and queued_power_kw >= 0",
                "overflow_expr": "active_power_kw + queued_power_kw",
            }
        ]
    return []


def convert_spec(spec: dict[str, Any]) -> dict[str, Any]:
    state_machine = convert_state_machine(spec)
    return {
        "name": spec["id"].lower(),
        "description": spec.get("description", spec.get("name", spec["id"])),
        "requirements": convert_requirements(spec),
        "state_machine": state_machine,
        "additional_flows": {},
        "safety_properties": ["AG(!violation)"] if state_machine else [],
        "mutual_exclusion": None,
        "functions": codegen_functions(spec),
        "arithmetic_checks": arithmetic_checks(spec),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename in SPEC_FILES:
        spec = load_json(SPEC_DIR / filename)
        converted = convert_spec(spec)
        output = OUT_DIR / filename.replace(".json", "_teacher.json")
        write_json(output, converted)
        print(output.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
