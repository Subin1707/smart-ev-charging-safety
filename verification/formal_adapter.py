#!/usr/bin/env python3
"""Generate a Smart EV formal-verification spec for SpecVerificationLab.

The teacher app supports simple CTL forms such as AG(!p). This adapter moves
Smart EV requirement logic into state labels, then emits one property per
requirement: AG(!<requirement_violation_label>).
"""

from __future__ import annotations

import itertools
import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
TRACEABILITY_PATH = ROOT / "reports" / "traceability" / "spec_traceability.json"
MAPPING_DRAFT_PATH = ROOT / "reports" / "verification" / "formal_mapping_draft.json"
OUTPUT_SPEC_PATH = ROOT / "teacher_specs" / "smart_ev_formal_verification.json"
OUTPUT_MAPPING_PATH = ROOT / "reports" / "verification" / "formal_adapter_mapping.json"


State = dict[str, bool]
Predicate = Callable[[State], bool]


BASE_VARIABLES = [
    "connected",
    "token_valid",
    "authenticated",
    "disconnected",
    "soc_out_of_range",
    "soc_full",
    "overheat",
    "port_multi_vehicle",
    "fault",
    "emergency",
    "charging",
    "power_positive",
    "safety_gate_valid",
]


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


VIOLATION_RULES: dict[str, tuple[str, Predicate, str]] = {
    "REQ-AUTH-01": (
        "req_auth_01_violation",
        lambda s: s["authenticated"] and (not s["connected"] or not s["token_valid"]),
        "authenticated && (!connected || !token_valid)",
    ),
    "REQ-AUTH-02": (
        "req_auth_02_violation",
        lambda s: s["disconnected"] and s["authenticated"],
        "disconnected && authenticated",
    ),
    "REQ-SOC-01": (
        "req_soc_01_violation",
        lambda s: s["soc_out_of_range"],
        "soc_out_of_range",
    ),
    "REQ-SOC-02": (
        "req_soc_02_violation",
        lambda s: s["soc_full"] and (s["charging"] or s["power_positive"]),
        "soc_full && (charging || power_positive)",
    ),
    "REQ-TEMP-01": (
        "req_temp_01_violation",
        lambda s: s["overheat"] and s["charging"],
        "overheat && charging",
    ),
    "REQ-PORT-01": (
        "req_port_01_violation",
        lambda s: s["charging"] and not s["connected"],
        "charging && !connected",
    ),
    "REQ-PORT-02": (
        "req_port_02_violation",
        lambda s: s["port_multi_vehicle"],
        "port_multi_vehicle",
    ),
    "REQ-PORT-03": (
        "req_port_03_violation",
        lambda s: s["fault"] and (s["charging"] or s["power_positive"]),
        "fault && (charging || power_positive)",
    ),
    "REQ-CHG-01": (
        "req_chg_01_violation",
        lambda s: s["charging"] and not s["safety_gate_valid"],
        "charging && !safety_gate_valid",
    ),
    "REQ-CHG-02": (
        "req_chg_02_violation",
        lambda s: s["charging"] and not s["safety_gate_valid"],
        "charging && !safety_gate_valid",
    ),
    "REQ-EMG-01": (
        "req_emg_01_violation",
        lambda s: (s["emergency"] or s["fault"]) and (s["charging"] or s["power_positive"]),
        "(emergency || fault) && (charging || power_positive)",
    ),
}


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


def state_id(prefix: str, index: int) -> str:
    return f"{prefix}_{index:04d}"


def all_boolean_states() -> list[State]:
    states = []
    for values in itertools.product([False, True], repeat=len(BASE_VARIABLES)):
        states.append(dict(zip(BASE_VARIABLES, values)))
    return states


def active_violations(state: State) -> list[str]:
    labels = []
    for rid in REQUIREMENT_ORDER:
        label, predicate, _ = VIOLATION_RULES[rid]
        if predicate(state):
            labels.append(label)
    return labels


def is_semantically_consistent(state: State) -> bool:
    if state["connected"] and state["disconnected"]:
        return False
    if state["charging"] and not state["power_positive"]:
        return False
    if state["power_positive"] and not state["charging"]:
        return False
    return True


def labels_for_state(state: State, extra_labels: list[str] | None = None) -> list[str]:
    labels = ["smart_ev", "safe"]
    labels.extend(name for name in BASE_VARIABLES if state[name])
    labels.extend(active_violations(state))
    if extra_labels:
        labels.extend(extra_labels)
    return sorted(set(labels))


def build_reachable_safe_states(raw_states: list[State]) -> list[tuple[str, State]]:
    safe_states = [
        state
        for state in raw_states
        if is_semantically_consistent(state) and not active_violations(state)
    ]
    return [(state_id("ok", idx), state) for idx, state in enumerate(safe_states)]


def build_witness_states(raw_states: list[State]) -> list[tuple[str, State]]:
    witnesses = []
    for idx, rid in enumerate(REQUIREMENT_ORDER):
        label, predicate, _ = VIOLATION_RULES[rid]
        witness = next(
            state
            for state in raw_states
            if is_semantically_consistent(state) and predicate(state) and label in active_violations(state)
        )
        witnesses.append((state_id("witness", idx), witness))
    return witnesses


def reachable_states(initial: list[str], transitions: list[list[str]]) -> set[str]:
    outgoing: dict[str, list[str]] = {}
    for src, dst in transitions:
        outgoing.setdefault(src, []).append(dst)

    seen = set(initial)
    queue = deque(initial)
    while queue:
        current = queue.popleft()
        for dst in outgoing.get(current, []):
            if dst not in seen:
                seen.add(dst)
                queue.append(dst)
    return seen


def build_spec_and_mapping() -> tuple[dict[str, Any], dict[str, Any]]:
    traceability = read_json(TRACEABILITY_PATH)
    mapping_draft = read_json(MAPPING_DRAFT_PATH)
    req_text = {
        item["requirement_id"]: item.get("requirement_text", "")
        for item in traceability.get("traceability", [])
    }
    constraints = {
        item["requirement_id"]: item.get("json_constraints", [])
        for item in traceability.get("traceability", [])
    }

    raw_states = all_boolean_states()
    safe_states = build_reachable_safe_states(raw_states)
    witness_states = build_witness_states(raw_states)
    all_states = safe_states + witness_states

    initial = [safe_states[0][0]]
    transitions: list[list[str]] = []
    safe_ids = [sid for sid, _ in safe_states]
    for sid in safe_ids:
        transitions.append([sid, sid])
    for src, dst in zip(safe_ids, safe_ids[1:]):
        transitions.append([src, dst])
    for sid, _ in witness_states:
        transitions.append([sid, sid])

    labeling = {sid: labels_for_state(state) for sid, state in all_states}
    properties = [
        f"AG(!{VIOLATION_RULES[rid][0]})"
        for rid in REQUIREMENT_ORDER
    ]

    requirements = [
        {
            "id": rid,
            "text": req_text.get(rid, ""),
            "category": "safety",
            "priority": "HIGH",
        }
        for rid in REQUIREMENT_ORDER
    ]

    spec = {
        "name": "smart_ev_formal_verification",
        "description": (
            "Smart EV requirement formal adapter. Requirement semantics are "
            "encoded as atomic violation labels so SpecVerificationLab can "
            "check AG(!label) properties without unsupported boolean operators."
        ),
        "requirements": requirements,
        "state_machine": {
            "states": [sid for sid, _ in all_states],
            "initial": initial,
            "labeling": labeling,
            "transitions": transitions,
        },
        "additional_flows": {},
        "safety_properties": properties,
        "mutual_exclusion": None,
        "functions": [],
        "arithmetic_checks": [],
    }

    reachable = reachable_states(initial, transitions)
    mapping_records = []
    draft_by_id = {item["requirement_id"]: item for item in mapping_draft.get("mappings", [])}
    for rid in REQUIREMENT_ORDER:
        label, _, semantic_condition = VIOLATION_RULES[rid]
        ctl_property = f"AG(!{label})"
        states_with_label = sorted(sid for sid, labels in labeling.items() if label in labels)
        reachable_states_with_label = [sid for sid in states_with_label if sid in reachable]
        mapping_records.append(
            {
                "requirement_id": rid,
                "constraints": constraints.get(rid, []),
                "requirement_text": req_text.get(rid, ""),
                "violation_label": label,
                "semantic_condition": semantic_condition,
                "ctl_property": ctl_property,
                "source_mapping": draft_by_id.get(rid, {}),
                "states_with_label": states_with_label,
                "reachable_states_with_label": reachable_states_with_label,
            }
        )

    mapping_report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs": [rel(TRACEABILITY_PATH), rel(MAPPING_DRAFT_PATH)],
        "output_spec": rel(OUTPUT_SPEC_PATH),
        "requirements": mapping_records,
        "summary": {
            "requirements": len(REQUIREMENT_ORDER),
            "violation_labels": len({VIOLATION_RULES[rid][0] for rid in REQUIREMENT_ORDER}),
            "ctl_properties": len(properties),
            "total_states": len(all_states),
            "reachable_states": len(reachable),
            "witness_states": len(witness_states),
            "violation_capable_predicates": sum(1 for item in mapping_records if item["states_with_label"]),
            "reachable_violation_states": sum(1 for item in mapping_records if item["reachable_states_with_label"]),
        },
        "validation": {},
    }
    return spec, mapping_report


def validate(spec: dict[str, Any], mapping_report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    records = mapping_report["requirements"]
    labels = [record["violation_label"] for record in records]
    properties = spec["safety_properties"]
    vocabulary = {
        label
        for state_labels in spec["state_machine"]["labeling"].values()
        for label in state_labels
    }

    if len(records) != len(REQUIREMENT_ORDER):
        errors.append(f"Expected {len(REQUIREMENT_ORDER)} requirements, found {len(records)}.")
    if len(labels) != len(set(labels)):
        errors.append("Violation labels are not unique.")
    for record in records:
        expected_property = f"AG(!{record['violation_label']})"
        if properties.count(expected_property) != 1:
            errors.append(f"{record['requirement_id']} does not have exactly one {expected_property}.")
        if record["violation_label"] not in vocabulary:
            errors.append(f"{record['violation_label']} is not in state labeling vocabulary.")
        if not record["states_with_label"]:
            errors.append(f"{record['violation_label']} has no witness state.")
        if record["reachable_states_with_label"]:
            errors.append(f"{record['violation_label']} appears in reachable states.")

    for prop in properties:
        if any(token in prop for token in ("&&", "||", "->")):
            errors.append(f"Unsupported boolean operator found in safety property: {prop}")
        if not prop.startswith("AG(!") or not prop.endswith(")"):
            errors.append(f"Safety property is not AG(!label): {prop}")

    mapping_report["validation"] = {
        "errors": errors,
        "rules": [
            "Each requirement has exactly one violation label.",
            "Each violation label has exactly one AG(!label) property.",
            "Property labels are present in state_machine labeling vocabulary.",
            "No &&, ||, or -> appears in safety_properties.",
            "Traceability includes requirement_id -> violation_label -> CTL property.",
            "Each violation label has at least one witness state.",
            "No violation label is reachable from the initial state.",
        ],
    }
    return errors


def main() -> int:
    spec, mapping_report = build_spec_and_mapping()
    errors = validate(spec, mapping_report)
    write_json(OUTPUT_SPEC_PATH, spec)
    write_json(OUTPUT_MAPPING_PATH, mapping_report)

    summary = mapping_report["summary"]
    print("Formal Adapter Summary")
    print(f"Requirements: {summary['requirements']}")
    print(f"Violation labels: {summary['violation_labels']}")
    print(f"CTL properties: {summary['ctl_properties']}")
    print(f"Reachable states: {summary['reachable_states']}")
    print(f"Violation-capable predicates: {summary['violation_capable_predicates']}")
    print(f"Properties: {summary['ctl_properties']}")
    print(f"Validation errors: {len(errors)}")
    print(f"Output: {rel(OUTPUT_SPEC_PATH)}")
    print(f"Mapping: {rel(OUTPUT_MAPPING_PATH)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
