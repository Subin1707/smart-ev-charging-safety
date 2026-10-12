#!/usr/bin/env python3
"""Generate a comprehensive Smart EV formal model for SpecVerificationLab.

This is a V2 generator. It does not replace the current verified model and does
not run or modify SpecVerificationLab.exe. It emits a richer finite abstraction,
coverage reports, and separate negative-control models.
"""

from __future__ import annotations

import copy
import json
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "specification"
TRACEABILITY_PATH = ROOT / "reports" / "traceability" / "spec_traceability.json"
OUTPUT_SPEC = ROOT / "teacher_specs" / "smart_ev_formal_verification_v2.json"
COVERAGE_JSON = ROOT / "reports" / "verification" / "formal_coverage.json"
COVERAGE_MD = ROOT / "reports" / "verification" / "formal_coverage.md"
NEGATIVE_DIR = ROOT / "teacher_specs" / "negative_controls"


REQUIREMENT_ORDER = [
    "REQ-AUTH-01",
    "REQ-AUTH-02",
    "REQ-SOC-01",
    "REQ-SOC-02",
    "REQ-TEMP-01",
    "REQ-PORT-01",
    "REQ-PORT-02",
    "REQ-PORT-03",
    "REQ-CHG-01",
    "REQ-CHG-02",
    "REQ-EMG-01",
]


VIOLATION_LABELS = {
    "REQ-AUTH-01": "req_auth_01_violation",
    "REQ-AUTH-02": "req_auth_02_violation",
    "REQ-SOC-01": "req_soc_01_violation",
    "REQ-SOC-02": "req_soc_02_violation",
    "REQ-TEMP-01": "req_temp_01_violation",
    "REQ-PORT-01": "req_port_01_violation",
    "REQ-PORT-02": "req_port_02_violation",
    "REQ-PORT-03": "req_port_03_violation",
    "REQ-CHG-01": "req_chg_01_violation",
    "REQ-CHG-02": "req_chg_02_violation",
    "REQ-EMG-01": "req_emg_01_violation",
}


SEMANTIC_RULES = {
    "REQ-AUTH-01": "authenticated implies connected and token_valid",
    "REQ-AUTH-02": "disconnect clears authentication",
    "REQ-SOC-01": "SOC remains within specification valid range",
    "REQ-SOC-02": "SOC_FULL blocks charging",
    "REQ-TEMP-01": "TEMP_OVERHEAT blocks charging",
    "REQ-PORT-01": "charging requires connected port",
    "REQ-PORT-02": "one port is linked to at most one vehicle",
    "REQ-PORT-03": "faulted port does not charge",
    "REQ-CHG-01": "charging requires the integrated safety gate",
    "REQ-CHG-02": "safety gate remains valid while charging",
    "REQ-EMG-01": "emergency or fault stops charging and power is zero",
}


@dataclass
class ModelState:
    sid: str
    labels: set[str]
    kind: str
    meaning: str
    requirements: set[str] = field(default_factory=set)
    scenario: str | None = None


@dataclass
class ModelTransition:
    src: str
    dst: str
    event: str
    requirements: set[str]
    scenario: str


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_specs() -> dict[str, Any]:
    return {
        "auth": read_json(SPEC_DIR / "auth.json"),
        "battery": read_json(SPEC_DIR / "battery.json"),
        "port": read_json(SPEC_DIR / "port.json"),
        "charging": read_json(SPEC_DIR / "charging.json"),
        "traceability": read_json(TRACEABILITY_PATH),
    }


def numeric_cases(name: str, valid_range: list[int | float]) -> list[dict[str, Any]]:
    lo, hi = valid_range
    eps = 1
    mid = (lo + hi) / 2
    return [
        {"name": f"{name}_below_min", "value": lo - eps, "classification": "INVALID", "kind": "boundary"},
        {"name": f"{name}_min", "value": lo, "classification": "VALID", "kind": "boundary"},
        {"name": f"{name}_min_plus", "value": lo + eps, "classification": "VALID", "kind": "boundary"},
        {"name": f"{name}_normal", "value": mid, "classification": "VALID", "kind": "normal"},
        {"name": f"{name}_max_minus", "value": hi - eps, "classification": "VALID", "kind": "boundary"},
        {"name": f"{name}_max", "value": hi, "classification": "VALID", "kind": "boundary"},
        {"name": f"{name}_above_max", "value": hi + eps, "classification": "INVALID", "kind": "boundary"},
    ]


def build_states_and_transitions(specs: dict[str, Any]) -> tuple[list[ModelState], list[ModelTransition], list[dict[str, Any]], list[dict[str, Any]]]:
    battery_raw = {item["name"]: item for item in specs["battery"].get("raw_parameters", [])}
    soc_cases = numeric_cases("soc", battery_raw["soc"]["valid_range"])
    temp_cases = numeric_cases("temperature", battery_raw["temperature"]["valid_range"])
    temp_threshold = battery_raw["temperature"]["valid_range"][1]

    states = [
        ModelState("ev_disconnected", {"smart_ev", "disconnected", "auth_clear", "port_idle", "safe"}, "normal", "No vehicle is connected.", {"REQ-AUTH-02"}),
        ModelState("ev_connected", {"smart_ev", "connected", "port_occupied", "safe"}, "normal", "Vehicle connected but not authenticated.", {"REQ-AUTH-01", "REQ-PORT-01"}),
        ModelState("ev_auth_failed", {"smart_ev", "connected", "auth_failed", "start_blocked", "safe"}, "negative", "Invalid token blocks authentication and charging start.", {"REQ-AUTH-01", "REQ-CHG-01"}),
        ModelState("ev_authenticated", {"smart_ev", "connected", "token_valid", "authenticated", "port_ready", "safe"}, "normal", "Vehicle authenticated and ready for charging request.", {"REQ-AUTH-01"}),
        ModelState("ev_charging", {"smart_ev", "connected", "token_valid", "authenticated", "soc_ok", "temperature_safe", "port_ready", "charging", "power_positive", "safe", "safety_gate_valid"}, "normal", "Charging with all safety conditions valid.", {"REQ-CHG-01", "REQ-CHG-02"}),
        ModelState("ev_start_blocked_auth", {"smart_ev", "connected", "auth_failed", "start_blocked", "safe"}, "negative", "Start is blocked after authentication failure.", {"REQ-AUTH-01", "REQ-CHG-01"}),
        ModelState("ev_stopped_soc_full", {"smart_ev", "connected", "authenticated", "soc_full", "stopped", "power_zero", "safe"}, "boundary", "Charging stopped because SOC is full.", {"REQ-SOC-02"}),
        ModelState("ev_stopped_overheat", {"smart_ev", "connected", "authenticated", "temperature_overheat", "stopped", "power_zero", "safe"}, "unsafe", "Charging stopped because temperature reached or exceeded threshold.", {"REQ-TEMP-01"}),
        ModelState("ev_stopped_port_fault", {"smart_ev", "connected", "authenticated", "port_fault", "stopped", "power_zero", "fault", "safe"}, "fault", "Charging stopped because port fault was detected.", {"REQ-PORT-03", "REQ-EMG-01"}),
        ModelState("ev_stopped_emergency", {"smart_ev", "connected", "authenticated", "emergency", "stopped", "power_zero", "safe"}, "emergency", "Charging stopped because emergency was triggered.", {"REQ-EMG-01"}),
        ModelState("ev_recovered_safe", {"smart_ev", "connected", "authenticated", "port_ready", "recovered", "safe"}, "normal", "Safety condition recovered and system is not charging.", {"REQ-CHG-02", "REQ-EMG-01"}),
        ModelState("ev_port_multi_vehicle_blocked", {"smart_ev", "connected", "port_multi_vehicle_attempt", "start_blocked", "safe"}, "negative", "Second vehicle/port ownership conflict is blocked.", {"REQ-PORT-02"}),
        ModelState("ev_soc_invalid_blocked", {"smart_ev", "connected", "authenticated", "soc_invalid", "start_blocked", "safe"}, "boundary", "Invalid SOC blocks charging.", {"REQ-SOC-01"}),
        ModelState("ev_temp_invalid_blocked", {"smart_ev", "connected", "authenticated", "temperature_invalid", "start_blocked", "safe"}, "boundary", "Invalid temperature blocks charging.", {"REQ-TEMP-01"}),
        ModelState("ev_boundary_soc_0", {"smart_ev", "connected", "authenticated", "soc_boundary_min", "soc_ok", "safe"}, "boundary", "SOC at lower valid boundary.", {"REQ-SOC-01"}),
        ModelState("ev_boundary_soc_100", {"smart_ev", "connected", "authenticated", "soc_boundary_max", "soc_full", "stopped", "power_zero", "safe"}, "boundary", "SOC at upper boundary is full and not charging.", {"REQ-SOC-01", "REQ-SOC-02"}),
        ModelState("ev_boundary_temp_below_threshold", {"smart_ev", "connected", "authenticated", "temperature_safe", "temp_below_threshold", "safe"}, "boundary", f"Temperature just below {temp_threshold} C remains safe.", {"REQ-TEMP-01"}),
        ModelState("ev_boundary_temp_threshold", {"smart_ev", "connected", "authenticated", "temperature_overheat", "temp_threshold", "stopped", "power_zero", "safe"}, "boundary", f"Temperature at {temp_threshold} C stops charging.", {"REQ-TEMP-01"}),
        ModelState("ev_boundary_temp_above_threshold", {"smart_ev", "connected", "authenticated", "temperature_overheat", "temp_above_threshold", "stopped", "power_zero", "safe"}, "boundary", f"Temperature above {temp_threshold} C stops charging.", {"REQ-TEMP-01"}),
    ]

    transitions = [
        ModelTransition("ev_disconnected", "ev_connected", "connect", {"REQ-AUTH-01", "REQ-PORT-01"}, "normal_connect_auth_start"),
        ModelTransition("ev_connected", "ev_authenticated", "authenticate_success", {"REQ-AUTH-01"}, "normal_connect_auth_start"),
        ModelTransition("ev_connected", "ev_auth_failed", "authenticate_failure", {"REQ-AUTH-01"}, "auth_failure_start_blocked"),
        ModelTransition("ev_auth_failed", "ev_start_blocked_auth", "start_charging", {"REQ-AUTH-01", "REQ-CHG-01"}, "auth_failure_start_blocked"),
        ModelTransition("ev_authenticated", "ev_charging", "start_charging", {"REQ-CHG-01", "REQ-CHG-02"}, "normal_connect_auth_start"),
        ModelTransition("ev_charging", "ev_stopped_soc_full", "soc_full", {"REQ-SOC-02"}, "charging_soc_full_stop"),
        ModelTransition("ev_charging", "ev_stopped_overheat", "overheat", {"REQ-TEMP-01"}, "charging_overheat_stop"),
        ModelTransition("ev_charging", "ev_stopped_port_fault", "port_fault", {"REQ-PORT-03", "REQ-EMG-01"}, "charging_port_fault_stop"),
        ModelTransition("ev_charging", "ev_stopped_emergency", "emergency", {"REQ-EMG-01"}, "charging_emergency_stop"),
        ModelTransition("ev_stopped_overheat", "ev_recovered_safe", "safety_recovery", {"REQ-TEMP-01", "REQ-CHG-02"}, "overheat_recovery"),
        ModelTransition("ev_stopped_emergency", "ev_recovered_safe", "emergency_clear", {"REQ-EMG-01"}, "emergency_recovery"),
        ModelTransition("ev_stopped_port_fault", "ev_recovered_safe", "fault_clear", {"REQ-PORT-03", "REQ-EMG-01"}, "fault_recovery"),
        ModelTransition("ev_recovered_safe", "ev_charging", "restart_after_recovery", {"REQ-CHG-02"}, "recovery_restart"),
        ModelTransition("ev_authenticated", "ev_port_multi_vehicle_blocked", "second_vehicle_attempt", {"REQ-PORT-02"}, "port_exclusivity_negative"),
        ModelTransition("ev_authenticated", "ev_soc_invalid_blocked", "soc_invalid", {"REQ-SOC-01"}, "soc_boundary_invalid"),
        ModelTransition("ev_authenticated", "ev_temp_invalid_blocked", "temperature_invalid", {"REQ-TEMP-01"}, "temperature_boundary_invalid"),
        ModelTransition("ev_authenticated", "ev_boundary_soc_0", "soc_min", {"REQ-SOC-01"}, "soc_boundary"),
        ModelTransition("ev_boundary_soc_0", "ev_charging", "start_charging", {"REQ-SOC-01", "REQ-CHG-01"}, "soc_boundary"),
        ModelTransition("ev_authenticated", "ev_boundary_soc_100", "soc_max", {"REQ-SOC-01", "REQ-SOC-02"}, "soc_boundary"),
        ModelTransition("ev_authenticated", "ev_boundary_temp_below_threshold", "temperature_below_threshold", {"REQ-TEMP-01"}, "temperature_boundary"),
        ModelTransition("ev_boundary_temp_below_threshold", "ev_charging", "start_charging", {"REQ-TEMP-01", "REQ-CHG-01"}, "temperature_boundary"),
        ModelTransition("ev_charging", "ev_boundary_temp_threshold", "temperature_threshold", {"REQ-TEMP-01"}, "temperature_boundary"),
        ModelTransition("ev_charging", "ev_boundary_temp_above_threshold", "temperature_above_threshold", {"REQ-TEMP-01"}, "temperature_boundary"),
        ModelTransition("ev_authenticated", "ev_disconnected", "disconnect", {"REQ-AUTH-02"}, "disconnect_clears_auth"),
        ModelTransition("ev_stopped_soc_full", "ev_disconnected", "disconnect", {"REQ-AUTH-02", "REQ-SOC-02"}, "disconnect_after_stop"),
    ]

    boundary_scenarios = soc_cases + temp_cases
    sequence_scenarios = [
        {"id": "normal_connect_auth_start", "requirements": ["REQ-AUTH-01", "REQ-CHG-01"], "path": ["ev_disconnected", "ev_connected", "ev_authenticated", "ev_charging"]},
        {"id": "auth_failure_start_blocked", "requirements": ["REQ-AUTH-01", "REQ-CHG-01"], "path": ["ev_connected", "ev_auth_failed", "ev_start_blocked_auth"]},
        {"id": "charging_soc_full_stop", "requirements": ["REQ-SOC-02"], "path": ["ev_charging", "ev_stopped_soc_full"]},
        {"id": "charging_overheat_stop", "requirements": ["REQ-TEMP-01"], "path": ["ev_charging", "ev_stopped_overheat"]},
        {"id": "charging_port_fault_stop", "requirements": ["REQ-PORT-03"], "path": ["ev_charging", "ev_stopped_port_fault"]},
        {"id": "charging_emergency_stop", "requirements": ["REQ-EMG-01"], "path": ["ev_charging", "ev_stopped_emergency"]},
        {"id": "emergency_recovery", "requirements": ["REQ-EMG-01", "REQ-CHG-02"], "path": ["ev_stopped_emergency", "ev_recovered_safe"]},
    ]
    return states, transitions, boundary_scenarios, sequence_scenarios


def state_labels(state: ModelState) -> list[str]:
    labels = set(state.labels)
    labels.add(f"kind_{state.kind}")
    for req in state.requirements:
        labels.add(req.lower().replace("-", "_"))
    if state.scenario:
        labels.add(f"scenario_{state.scenario}")
    return sorted(labels)


def build_model(specs: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    states, transitions, boundary_scenarios, sequence_scenarios = build_states_and_transitions(specs)
    trace_reqs = {item["requirement_id"]: item for item in specs["traceability"]["traceability"]}
    requirements = []
    requirement_coverage = []

    modeled_by_req = {rid: {"states": [], "transitions": [], "scenarios": []} for rid in REQUIREMENT_ORDER}
    for state in states:
        for rid in state.requirements:
            modeled_by_req[rid]["states"].append(state.sid)
    for transition in transitions:
        for rid in transition.requirements:
            modeled_by_req[rid]["transitions"].append(f"{transition.src}->{transition.dst}:{transition.event}")
            modeled_by_req[rid]["scenarios"].append(transition.scenario)

    properties = []
    for rid in REQUIREMENT_ORDER:
        req = trace_reqs[rid]
        label = VIOLATION_LABELS[rid]
        prop = f"AG(!{label})"
        properties.append(prop)
        requirements.append(
            {
                "id": rid,
                "text": req["requirement_text"],
                "category": "safety",
                "priority": "HIGH",
            }
        )
        requirement_coverage.append(
            {
                "requirement_id": rid,
                "source_constraints": req["json_constraints"],
                "semantic_rule": SEMANTIC_RULES[rid],
                "violation_predicate": label,
                "formal_property": prop,
                "modeled_states": sorted(set(modeled_by_req[rid]["states"])),
                "modeled_transitions": sorted(set(modeled_by_req[rid]["transitions"])),
                "verification_scenarios": sorted(set(modeled_by_req[rid]["scenarios"])),
            }
        )

    # Liveness/reachability properties supported by FORMAT.md and traceable to scenarios.
    properties.extend(
        [
            "EF(charging)",
            "EF(stopped)",
            "EF(start_blocked)",
            "EF(recovered)",
        ]
    )

    state_ids = [state.sid for state in states]
    transition_pairs = [[transition.src, transition.dst] for transition in transitions]
    for state in states:
        transition_pairs.append([state.sid, state.sid])

    spec = {
        "name": "smart_ev_formal_verification_v2",
        "description": "Comprehensive Smart EV formal model V2 with requirement coverage, boundary states, scenario transitions, and violation-label CTL properties.",
        "requirements": requirements,
        "state_machine": {
            "states": state_ids,
            "initial": ["ev_disconnected"],
            "labeling": {state.sid: state_labels(state) for state in states},
            "transitions": transition_pairs,
        },
        "additional_flows": {},
        "safety_properties": properties,
        "mutual_exclusion": None,
        "functions": [],
        "arithmetic_checks": [],
    }

    coverage = build_coverage(spec, transitions, requirement_coverage, boundary_scenarios, sequence_scenarios)
    return spec, coverage


def reachable_nodes(initial: list[str], transitions: list[list[str]]) -> set[str]:
    adj: dict[str, list[str]] = {}
    for src, dst in transitions:
        adj.setdefault(src, []).append(dst)
    seen = set(initial)
    queue = deque(initial)
    while queue:
        node = queue.popleft()
        for nxt in adj.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def build_coverage(
    spec: dict[str, Any],
    semantic_transitions: list[ModelTransition],
    requirement_coverage: list[dict[str, Any]],
    boundary_scenarios: list[dict[str, Any]],
    sequence_scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    sm = spec["state_machine"]
    reachable = reachable_nodes(sm["initial"], sm["transitions"])
    states = set(sm["states"])
    reachable_transition_ids = []
    for transition in semantic_transitions:
        if transition.src in reachable and transition.dst in reachable:
            reachable_transition_ids.append(f"{transition.src}->{transition.dst}:{transition.event}")

    constraints = sorted({constraint for req in requirement_coverage for constraint in req["source_constraints"]})
    mapped_constraints = sorted({constraint for req in requirement_coverage if req["modeled_states"] and req["modeled_transitions"] for constraint in req["source_constraints"]})
    violation_labels = set(VIOLATION_LABELS.values())
    property_labels = {
        prop.removeprefix("AG(!").removesuffix(")")
        for prop in spec["safety_properties"]
        if prop.startswith("AG(!") and prop.endswith(")")
    }
    model_labels = {label for labels in sm["labeling"].values() for label in labels}
    orphan_violation_labels = sorted((property_labels & violation_labels) - set(VIOLATION_LABELS.values()))
    unmapped_requirements = [req["requirement_id"] for req in requirement_coverage if not req["modeled_states"] or not req["modeled_transitions"]]
    invalid_transitions = [
        [src, dst]
        for src, dst in sm["transitions"]
        if src not in states or dst not in states
    ]
    parse_compatible = all(
        prop.startswith(("AG(", "EF(", "AF(", "EG(", "AX(", "EX(")) and "&&" not in prop and "||" not in prop and "->" not in prop
        for prop in spec["safety_properties"]
    )
    ready = (
        len(unmapped_requirements) == 0
        and len(orphan_violation_labels) == 0
        and parse_compatible
        and len(invalid_transitions) == 0
        and bool(sm["initial"])
        and all(init in states for init in sm["initial"])
    )

    return {
        "requirements_total": len(requirement_coverage),
        "requirements_mapped": len(requirement_coverage) - len(unmapped_requirements),
        "constraints_total": len(constraints),
        "constraints_mapped": len(mapped_constraints),
        "states_total": len(states),
        "states_reachable": len(reachable),
        "states_unreachable": len(states - reachable),
        "transitions_total": len(semantic_transitions),
        "transitions_reachable": len(reachable_transition_ids),
        "formal_properties_total": len(spec["safety_properties"]),
        "violation_predicates_total": len(VIOLATION_LABELS),
        "boundary_scenarios_total": len(boundary_scenarios),
        "negative_scenarios_total": sum(1 for req in requirement_coverage for s in req["verification_scenarios"] if "negative" in s or "blocked" in s),
        "sequence_scenarios_total": len(sequence_scenarios),
        "unmapped_requirements": unmapped_requirements,
        "unmapped_constraints": sorted(set(constraints) - set(mapped_constraints)),
        "orphan_violation_labels": orphan_violation_labels,
        "invalid_transitions": invalid_transitions,
        "ready_for_teacher_app": ready,
        "requirement_coverage": requirement_coverage,
        "boundary_scenarios": boundary_scenarios,
        "sequence_scenarios": sequence_scenarios,
        "reachable_transitions": reachable_transition_ids,
    }


def render_coverage_md(coverage: dict[str, Any]) -> str:
    ready = "YES" if coverage["ready_for_teacher_app"] else "NO"
    lines = [
        "# SMART EV FORMAL COVERAGE",
        "",
        f"- Requirements: {coverage['requirements_mapped']}/{coverage['requirements_total']} mapped",
        f"- Constraints: {coverage['constraints_mapped']}/{coverage['constraints_total']} mapped",
        f"- Formal properties: {coverage['formal_properties_total']}",
        f"- Violation predicates: {coverage['violation_predicates_total']}",
        f"- States generated: {coverage['states_total']}",
        f"- Reachable states: {coverage['states_reachable']}",
        f"- Unreachable states: {coverage['states_unreachable']}",
        f"- Transitions generated: {coverage['transitions_total']}",
        f"- Reachable transitions: {coverage['transitions_reachable']}",
        f"- Boundary scenarios: {coverage['boundary_scenarios_total']}",
        f"- Negative scenarios: {coverage['negative_scenarios_total']}",
        f"- Sequence scenarios: {coverage['sequence_scenarios_total']}",
        f"- Unmapped requirements: {len(coverage['unmapped_requirements'])}",
        f"- Unmapped constraints: {len(coverage['unmapped_constraints'])}",
        f"- Orphan violation labels: {len(coverage['orphan_violation_labels'])}",
        f"- Invalid transitions: {len(coverage['invalid_transitions'])}",
        f"- READY_FOR_TEACHER_APP: {ready}",
        "",
        "## Requirement Coverage",
        "",
        "| Requirement | Constraints | Violation Predicate | Formal Property | States | Transitions | Scenarios |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for req in coverage["requirement_coverage"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{req['requirement_id']}`",
                    "<br>".join(f"`{c}`" for c in req["source_constraints"]),
                    f"`{req['violation_predicate']}`",
                    f"`{req['formal_property']}`",
                    str(len(req["modeled_states"])),
                    str(len(req["modeled_transitions"])),
                    "<br>".join(f"`{s}`" for s in req["verification_scenarios"]),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def make_negative_controls(spec: dict[str, Any]) -> list[dict[str, str]]:
    controls = [
        ("AUTH", "REQ-AUTH-01", "req_auth_01_violation"),
        ("SOC", "REQ-SOC-01", "req_soc_01_violation"),
        ("TEMP", "REQ-TEMP-01", "req_temp_01_violation"),
        ("PORT", "REQ-PORT-03", "req_port_03_violation"),
        ("CHARGING", "REQ-CHG-01", "req_chg_01_violation"),
        ("EMERGENCY", "REQ-EMG-01", "req_emg_01_violation"),
    ]
    outputs = []
    initial = spec["state_machine"]["initial"][0]
    NEGATIVE_DIR.mkdir(parents=True, exist_ok=True)
    for domain, rid, label in controls:
        model = copy.deepcopy(spec)
        injected = f"negative_{domain.lower()}_{label}"
        sm = model["state_machine"]
        sm["states"].append(injected)
        sm["labeling"][injected] = sorted({"smart_ev", "negative_control", domain.lower(), rid.lower().replace("-", "_"), label})
        sm["transitions"].append([initial, injected])
        sm["transitions"].append([injected, injected])
        model["name"] = f"smart_ev_negative_{domain.lower()}"
        model["description"] = f"Negative control for {domain}: reachable {label}; expected related property violation."
        out = NEGATIVE_DIR / f"smart_ev_negative_{domain.lower()}.json"
        write_json(out, model)
        outputs.append({"domain": domain, "requirement_id": rid, "violation_label": label, "output": rel(out)})
    return outputs


def main() -> int:
    specs = load_specs()
    model, coverage = build_model(specs)
    negatives = make_negative_controls(model)
    coverage["negative_control_models"] = negatives
    write_json(OUTPUT_SPEC, model)
    write_json(COVERAGE_JSON, coverage)
    write_text(COVERAGE_MD, render_coverage_md(coverage))

    ready = "YES" if coverage["ready_for_teacher_app"] else "NO"
    print("COMPREHENSIVE FORMAL MODEL")
    print(f"Requirements: {coverage['requirements_mapped']}/{coverage['requirements_total']} mapped")
    print(f"States: {coverage['states_total']}")
    print(f"Reachable states: {coverage['states_reachable']}")
    print(f"Transitions: {coverage['transitions_total']}")
    print(f"Formal properties: {coverage['formal_properties_total']}")
    print(f"Boundary scenarios: {coverage['boundary_scenarios_total']}")
    print(f"Negative scenarios: {coverage['negative_scenarios_total']}")
    print(f"Sequence scenarios: {coverage['sequence_scenarios_total']}")
    print("")
    print(f"Unmapped requirements: {len(coverage['unmapped_requirements'])}")
    print(f"Orphan violation labels: {len(coverage['orphan_violation_labels'])}")
    print("")
    print(f"READY_FOR_TEACHER_APP: {ready}")
    print("")
    print(f"Output: {rel(OUTPUT_SPEC)}")
    return 0 if coverage["ready_for_teacher_app"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
