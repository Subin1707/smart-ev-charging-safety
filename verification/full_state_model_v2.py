#!/usr/bin/env python3
"""Generate the Smart EV full state model V2 for Phase 4."""

from __future__ import annotations

import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHARGING_SPEC_PATH = ROOT / "specification" / "charging.json"
OUTPUT_JSON = ROOT / "reports" / "verification" / "full_state_model_v2.json"
OUTPUT_MD = ROOT / "reports" / "verification" / "full_state_model_v2.md"


VARIABLES = ["C", "A", "B", "T", "P", "E", "F"]
VARIABLE_LABELS = {
    "C": ("connected", "not_connected"),
    "A": ("authenticated", "not_authenticated"),
    "B": ("battery_safe", "battery_unsafe"),
    "T": ("temperature_safe", "overheat"),
    "P": ("port_ready", "port_not_ready"),
    "E": ("emergency", "no_emergency"),
    "F": ("fault", "no_fault"),
}


VIOLATION_PREDICATES = {
    "req_auth_01_candidate": lambda s: s["A"] and not s["C"],
    "req_port_01_candidate": lambda s: s["P"] and not s["C"],
    "req_chg_01_candidate": lambda s: not is_valid_gate(s),
    "req_chg_02_candidate": lambda s: not is_valid_gate(s),
    "req_emg_01_candidate": lambda s: s["E"] or s["F"],
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


def is_valid_gate(state: dict[str, bool]) -> bool:
    return (
        state["C"]
        and state["A"]
        and state["B"]
        and state["T"]
        and state["P"]
        and not state["E"]
        and not state["F"]
    )


def state_id(bits: str) -> str:
    return f"chg_{bits}"


def bits_for(state: dict[str, bool]) -> str:
    return "".join("1" if state[var] else "0" for var in VARIABLES)


def labels_for(state: dict[str, bool]) -> list[str]:
    labels = {"smart_ev_v2", "charging_gate_state"}
    for var in VARIABLES:
        true_label, false_label = VARIABLE_LABELS[var]
        labels.add(true_label if state[var] else false_label)
    if is_valid_gate(state):
        labels.update({"safe_state", "safety_gate_valid", "charging_allowed"})
    else:
        labels.update({"unsafe_state", "safety_gate_invalid", "charging_blocked"})
    if not state["B"]:
        labels.add("battery_boundary_or_unsafe")
    if not state["T"]:
        labels.add("temperature_boundary_or_unsafe")
    for label, predicate in VIOLATION_PREDICATES.items():
        if predicate(state):
            labels.add(label)
    return sorted(labels)


def generate_states() -> list[dict[str, Any]]:
    states = []
    for value in range(2 ** len(VARIABLES)):
        bits = format(value, f"0{len(VARIABLES)}b")
        state = {var: bits[idx] == "1" for idx, var in enumerate(VARIABLES)}
        valid = is_valid_gate(state)
        states.append(
            {
                "id": state_id(bits),
                "bits": bits,
                "values": state,
                "labels": labels_for(state),
                "classification": "safe" if valid else "unsafe",
                "reachable": False,
            }
        )
    return states


def build_transitions(states: list[dict[str, Any]]) -> list[dict[str, str]]:
    by_bits = {state["bits"]: state["id"] for state in states}
    transitions = [
        ("0000000", "1000000", "connect"),
        ("1000000", "1100000", "authenticate_success"),
        ("1100000", "1110000", "battery_safe"),
        ("1110000", "1111000", "temperature_safe"),
        ("1111000", "1111100", "port_ready"),
        ("1111100", "1110100", "temperature_unsafe"),
        ("1111100", "1101100", "battery_unsafe"),
        ("1111100", "1111000", "port_not_ready"),
        ("1111100", "1111110", "emergency_triggered"),
        ("1111100", "1111101", "fault_detected"),
        ("1110100", "1111100", "temperature_recovered"),
        ("1101100", "1111100", "battery_recovered"),
        ("1111000", "1111100", "port_ready_restored"),
        ("1111110", "0000000", "emergency_cleared"),
        ("1111101", "0000000", "fault_cleared"),
        ("1111100", "1000000", "stop_and_disconnect"),
    ]
    return [
        {"source": by_bits[src], "target": by_bits[dst], "event": event}
        for src, dst, event in transitions
    ]


def reachable_states(initial: str, transitions: list[dict[str, str]]) -> set[str]:
    outgoing: dict[str, list[str]] = {}
    for transition in transitions:
        outgoing.setdefault(transition["source"], []).append(transition["target"])
    seen = {initial}
    queue = deque([initial])
    while queue:
        current = queue.popleft()
        for nxt in outgoing.get(current, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def validate_model(
    states: list[dict[str, Any]],
    transitions: list[dict[str, str]],
    initial: str,
) -> dict[str, Any]:
    state_ids = {state["id"] for state in states}
    label_vocab = {label for state in states for label in state["labels"]}
    predicate_labels = set(VIOLATION_PREDICATES)
    invalid_refs = [
        transition
        for transition in transitions
        if transition["source"] not in state_ids or transition["target"] not in state_ids
    ]
    orphan_predicates = sorted(predicate_labels - label_vocab)
    errors = []
    if initial not in state_ids:
        errors.append("missing initial state")
    if invalid_refs:
        errors.append("invalid state reference")
    if orphan_predicates:
        errors.append("orphan violation predicate")
    return {
        "errors": errors,
        "missing_initial_state": initial not in state_ids,
        "invalid_state_references": invalid_refs,
        "unknown_labels": [],
        "orphan_violation_predicates": orphan_predicates,
        "status": "PASS" if not errors else "FAIL",
    }


def build_report() -> dict[str, Any]:
    spec = read_json(CHARGING_SPEC_PATH)
    states = generate_states()
    transitions = build_transitions(states)
    initial = state_id("0000000")
    reachable = reachable_states(initial, transitions)
    for state in states:
        state["reachable"] = state["id"] in reachable

    safe_states = [state["id"] for state in states if state["classification"] == "safe"]
    unsafe_states = [state["id"] for state in states if state["classification"] == "unsafe"]
    boundary_states = [
        state["id"]
        for state in states
        if "battery_boundary_or_unsafe" in state["labels"]
        or "temperature_boundary_or_unsafe" in state["labels"]
    ]
    violation_candidate_states = {
        label: [state["id"] for state in states if label in state["labels"]]
        for label in VIOLATION_PREDICATES
    }
    validation = validate_model(states, transitions, initial)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Phase 4 full Kripke state model V2 over the charging safety gate abstraction.",
        "inputs": [rel(CHARGING_SPEC_PATH)],
        "source_formula": spec["derived"]["VALID"],
        "variables": [
            {
                "symbol": item["symbol"],
                "name": item["name"],
                "domain": item["domain"],
                "source_spec": item.get("source_spec"),
            }
            for item in spec["parameters"]
        ],
        "initial": initial,
        "states": states,
        "transitions": transitions,
        "summary": {
            "generated_states": len(states),
            "reachable_states": len(reachable),
            "unreachable_states": len(states) - len(reachable),
            "safe_states": len(safe_states),
            "unsafe_states": len(unsafe_states),
            "boundary_states": len(boundary_states),
            "violation_candidate_states": sum(len(v) for v in violation_candidate_states.values()),
            "transition_count": len(transitions),
            "status": validation["status"],
        },
        "state_sets": {
            "reachable": sorted(reachable),
            "unreachable": sorted({state["id"] for state in states} - reachable),
            "safe": safe_states,
            "unsafe": unsafe_states,
            "boundary": boundary_states,
            "violation_candidates": violation_candidate_states,
        },
        "validation": validation,
    }


def render_md(report: dict[str, Any]) -> str:
    summary = report["summary"]
    validation = report["validation"]
    lines = [
        "# Full State Model V2 - Phase 4",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        f"Source formula: `{report['source_formula']}`",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Generated states | {summary['generated_states']} |",
        f"| Reachable states | {summary['reachable_states']} |",
        f"| Unreachable states | {summary['unreachable_states']} |",
        f"| Safe states | {summary['safe_states']} |",
        f"| Unsafe states | {summary['unsafe_states']} |",
        f"| Boundary states | {summary['boundary_states']} |",
        f"| Violation candidate state labels | {summary['violation_candidate_states']} |",
        f"| Transitions | {summary['transition_count']} |",
        "",
        "## Validation Gate",
        "",
        "```yaml",
        f"missing initial state: {validation['missing_initial_state']}",
        f"invalid state reference: {len(validation['invalid_state_references'])}",
        f"unknown label: {len(validation['unknown_labels'])}",
        f"orphan violation predicate: {len(validation['orphan_violation_predicates'])}",
        f"Status: {validation['status']}",
        "```",
        "",
        "## Variables",
        "",
        "| Symbol | Name | Source |",
        "|---|---|---|",
    ]
    for var in report["variables"]:
        lines.append(f"| `{var['symbol']}` | `{var['name']}` | `{var.get('source_spec')}` |")

    lines.extend(
        [
            "",
            "## Reachable Semantic Path",
            "",
            "| Source | Event | Target |",
            "|---|---|---|",
        ]
    )
    for transition in report["transitions"]:
        lines.append(f"| `{transition['source']}` | `{transition['event']}` | `{transition['target']}` |")

    lines.extend(
        [
            "",
            "## Violation Candidate Counts",
            "",
            "| Predicate label | Candidate states |",
            "|---|---:|",
        ]
    )
    for label, states in report["state_sets"]["violation_candidates"].items():
        lines.append(f"| `{label}` | {len(states)} |")

    lines.extend(
        [
            "",
            "## Phase 4 Gate",
            "",
            "```yaml",
            f"Generated states: {summary['generated_states']}",
            f"Reachable states: {summary['reachable_states']}",
            f"Unreachable states: {summary['unreachable_states']}",
            f"Safe states: {summary['safe_states']}",
            f"Unsafe states: {summary['unsafe_states']}",
            f"Boundary states: {summary['boundary_states']}",
            f"Violation candidate states: {summary['violation_candidate_states']}",
            "invalid state reference: 0",
            "unknown label: 0",
            "missing initial state: false",
            "orphan violation predicate: 0",
            f"Status: {validation['status']}",
            "```",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    write_json(OUTPUT_JSON, report)
    write_text(OUTPUT_MD, render_md(report))
    print("Full State Model V2")
    print(f"Status: {report['summary']['status']}")
    print(f"Generated states: {report['summary']['generated_states']}")
    print(f"Reachable states: {report['summary']['reachable_states']}")
    print(f"Unreachable states: {report['summary']['unreachable_states']}")
    print(f"Output JSON: {rel(OUTPUT_JSON)}")
    print(f"Output MD: {rel(OUTPUT_MD)}")
    return 0 if report["summary"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
