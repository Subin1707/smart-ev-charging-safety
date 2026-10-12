#!/usr/bin/env python3
"""Generate transition and sequence coverage for Smart EV Phase 5."""

from __future__ import annotations

import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "reports" / "verification" / "transition_sequence_coverage.json"
OUTPUT_MD = ROOT / "reports" / "verification" / "transition_sequence_coverage.md"


STATES = [
    {
        "id": "DISCONNECTED",
        "labels": ["disconnected", "auth_clear", "power_zero", "safe"],
        "meaning": "Vehicle is not connected and no session is active.",
    },
    {
        "id": "CONNECTED",
        "labels": ["connected", "not_authenticated", "port_occupied", "power_zero", "safe"],
        "meaning": "Vehicle is connected to a port but not authenticated.",
    },
    {
        "id": "AUTHENTICATED",
        "labels": ["connected", "authenticated", "port_ready", "power_zero", "safe"],
        "meaning": "Vehicle has passed authentication and can request charging.",
    },
    {
        "id": "AUTH_FAILED",
        "labels": ["connected", "auth_failed", "start_not_allowed", "power_zero", "safe"],
        "meaning": "Authentication failed and charging must not start.",
    },
    {
        "id": "START_BLOCKED",
        "labels": ["connected", "start_blocked", "power_zero", "safe"],
        "meaning": "A start request was rejected by the safety gate.",
    },
    {
        "id": "CHARGING",
        "labels": ["connected", "authenticated", "charging", "power_positive", "safety_gate_valid", "safe"],
        "meaning": "Charging is active with the safety gate valid.",
    },
    {
        "id": "SOC_FULL",
        "labels": ["connected", "authenticated", "soc_full", "stop_required", "unsafe_until_stopped"],
        "meaning": "SOC reached full threshold while charging.",
    },
    {
        "id": "OVERHEAT",
        "labels": ["connected", "authenticated", "overheat", "stop_required", "unsafe_until_stopped"],
        "meaning": "Temperature reached or exceeded the safety threshold.",
    },
    {
        "id": "PORT_FAULT",
        "labels": ["connected", "authenticated", "fault", "port_fault", "stop_required", "unsafe_until_stopped"],
        "meaning": "The charging port entered a fault state.",
    },
    {
        "id": "EMERGENCY",
        "labels": ["emergency", "stop_required", "unsafe_until_stopped"],
        "meaning": "Emergency stop is active.",
    },
    {
        "id": "DISCONNECTING",
        "labels": ["disconnecting", "stop_required", "auth_clear_required"],
        "meaning": "Vehicle disconnect was requested during an active flow.",
    },
    {
        "id": "STOPPED_SOC_FULL",
        "labels": ["connected", "authenticated", "soc_full", "stopped", "power_zero", "safe"],
        "meaning": "Charging stopped because SOC is full.",
    },
    {
        "id": "STOPPED_OVERHEAT",
        "labels": ["connected", "authenticated", "overheat", "stopped", "power_zero", "safe"],
        "meaning": "Charging stopped because of overheat.",
    },
    {
        "id": "STOPPED_PORT_FAULT",
        "labels": ["connected", "authenticated", "fault", "stopped", "power_zero", "safe"],
        "meaning": "Charging stopped because of a port fault.",
    },
    {
        "id": "STOPPED_EMERGENCY",
        "labels": ["emergency", "stopped", "power_zero", "safe"],
        "meaning": "Charging stopped because of emergency.",
    },
    {
        "id": "STOPPED_DISCONNECT",
        "labels": ["disconnected", "auth_clear", "stopped", "power_zero", "safe"],
        "meaning": "Charging stopped because the vehicle disconnected.",
    },
    {
        "id": "RECOVERED_SAFE",
        "labels": ["connected", "authenticated", "recovered", "power_zero", "safe"],
        "meaning": "Fault or emergency has cleared and the system is safe but not charging.",
    },
]


TRANSITIONS = [
    ("DISCONNECTED", "CONNECTED", "connect", ["REQ-AUTH-01", "REQ-PORT-01"], "normal_start"),
    ("CONNECTED", "AUTHENTICATED", "auth_success", ["REQ-AUTH-01"], "normal_start"),
    ("AUTHENTICATED", "CHARGING", "start", ["REQ-CHG-01", "REQ-CHG-02"], "normal_start"),
    ("CONNECTED", "AUTH_FAILED", "auth_fail", ["REQ-AUTH-01"], "auth_failure"),
    ("AUTH_FAILED", "START_BLOCKED", "start", ["REQ-AUTH-01", "REQ-CHG-01"], "auth_failure"),
    ("CHARGING", "SOC_FULL", "soc_full", ["REQ-SOC-02"], "soc_full_stop"),
    ("SOC_FULL", "STOPPED_SOC_FULL", "stop", ["REQ-SOC-02"], "soc_full_stop"),
    ("CHARGING", "OVERHEAT", "overheat", ["REQ-TEMP-01"], "overheat_stop"),
    ("OVERHEAT", "STOPPED_OVERHEAT", "stop", ["REQ-TEMP-01"], "overheat_stop"),
    ("CHARGING", "PORT_FAULT", "port_fault", ["REQ-PORT-03", "REQ-EMG-01"], "port_fault_stop"),
    ("PORT_FAULT", "STOPPED_PORT_FAULT", "stop", ["REQ-PORT-03", "REQ-EMG-01"], "port_fault_stop"),
    ("CHARGING", "EMERGENCY", "emergency", ["REQ-EMG-01"], "emergency_stop"),
    ("EMERGENCY", "STOPPED_EMERGENCY", "stop", ["REQ-EMG-01"], "emergency_stop"),
    ("CHARGING", "DISCONNECTING", "disconnect", ["REQ-AUTH-02", "REQ-PORT-01", "REQ-CHG-02"], "disconnect_stop"),
    ("DISCONNECTING", "STOPPED_DISCONNECT", "stop", ["REQ-AUTH-02"], "disconnect_stop"),
    ("STOPPED_PORT_FAULT", "RECOVERED_SAFE", "clear_fault", ["REQ-PORT-03", "REQ-EMG-01", "REQ-CHG-02"], "fault_recovery"),
    ("STOPPED_EMERGENCY", "RECOVERED_SAFE", "clear_emergency", ["REQ-EMG-01", "REQ-CHG-02"], "emergency_recovery"),
    ("STOPPED_OVERHEAT", "RECOVERED_SAFE", "temperature_recovered", ["REQ-TEMP-01", "REQ-CHG-02"], "overheat_recovery"),
    ("RECOVERED_SAFE", "CHARGING", "restart", ["REQ-CHG-01", "REQ-CHG-02"], "restart_after_recovery"),
]


REQUIRED_SEQUENCES = [
    {
        "id": "connect_auth_start_charging",
        "type": "safety",
        "path": ["DISCONNECTED", "CONNECTED", "AUTHENTICATED", "CHARGING"],
        "requirements": ["REQ-AUTH-01", "REQ-PORT-01", "REQ-CHG-01", "REQ-CHG-02"],
    },
    {
        "id": "connect_authfail_startblocked",
        "type": "safety",
        "path": ["DISCONNECTED", "CONNECTED", "AUTH_FAILED", "START_BLOCKED"],
        "requirements": ["REQ-AUTH-01", "REQ-CHG-01"],
    },
    {
        "id": "charging_socfull_stop",
        "type": "safety",
        "path": ["CHARGING", "SOC_FULL", "STOPPED_SOC_FULL"],
        "requirements": ["REQ-SOC-02"],
    },
    {
        "id": "charging_overheat_stop",
        "type": "safety",
        "path": ["CHARGING", "OVERHEAT", "STOPPED_OVERHEAT"],
        "requirements": ["REQ-TEMP-01"],
    },
    {
        "id": "charging_portfault_stop",
        "type": "safety",
        "path": ["CHARGING", "PORT_FAULT", "STOPPED_PORT_FAULT"],
        "requirements": ["REQ-PORT-03", "REQ-EMG-01"],
    },
    {
        "id": "charging_emergency_stop",
        "type": "safety",
        "path": ["CHARGING", "EMERGENCY", "STOPPED_EMERGENCY"],
        "requirements": ["REQ-EMG-01"],
    },
    {
        "id": "charging_disconnect_stop",
        "type": "safety",
        "path": ["CHARGING", "DISCONNECTING", "STOPPED_DISCONNECT"],
        "requirements": ["REQ-AUTH-02", "REQ-PORT-01", "REQ-CHG-02"],
    },
    {
        "id": "fault_clear_safe",
        "type": "recovery",
        "path": ["PORT_FAULT", "STOPPED_PORT_FAULT", "RECOVERED_SAFE"],
        "requirements": ["REQ-PORT-03", "REQ-EMG-01", "REQ-CHG-02"],
    },
    {
        "id": "emergency_recovery_safe",
        "type": "recovery",
        "path": ["EMERGENCY", "STOPPED_EMERGENCY", "RECOVERED_SAFE"],
        "requirements": ["REQ-EMG-01", "REQ-CHG-02"],
    },
]


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


def transition_id(src: str, dst: str, event: str) -> str:
    return f"{src}->{dst}:{event}"


def transition_records() -> list[dict[str, Any]]:
    return [
        {
            "id": transition_id(src, dst, event),
            "source": src,
            "target": dst,
            "event": event,
            "requirements": requirements,
            "scenario": scenario,
        }
        for src, dst, event, requirements, scenario in TRANSITIONS
    ]


def reachable_nodes(initial: str, transitions: list[dict[str, Any]]) -> set[str]:
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


def sequence_edges(path: list[str]) -> set[tuple[str, str]]:
    return set(zip(path, path[1:]))


def validate_sequences(transitions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    edge_events = {(item["source"], item["target"]): item for item in transitions}
    validated = []
    for seq in REQUIRED_SEQUENCES:
        missing_edges = [
            {"source": src, "target": dst}
            for src, dst in sequence_edges(seq["path"])
            if (src, dst) not in edge_events
        ]
        events = [
            edge_events[(src, dst)]["event"]
            for src, dst in zip(seq["path"], seq["path"][1:])
            if (src, dst) in edge_events
        ]
        validated.append({**seq, "events": events, "missing_edges": missing_edges, "status": "PASS" if not missing_edges else "FAIL"})
    return validated


def build_report() -> dict[str, Any]:
    states = STATES
    state_ids = {state["id"] for state in states}
    transitions = transition_records()
    initial = "DISCONNECTED"
    reachable = reachable_nodes(initial, transitions)
    reachable_transition_ids = [
        item["id"]
        for item in transitions
        if item["source"] in reachable and item["target"] in reachable
    ]
    transitions_without_requirement = [item["id"] for item in transitions if not item["requirements"]]
    transitions_by_requirement: dict[str, list[str]] = {}
    for item in transitions:
        for requirement in item["requirements"]:
            transitions_by_requirement.setdefault(requirement, []).append(item["id"])

    sequences = validate_sequences(transitions)
    safety_sequences = [item for item in sequences if item["type"] == "safety"]
    recovery_sequences = [item for item in sequences if item["type"] == "recovery"]
    invalid_refs = [
        item["id"]
        for item in transitions
        if item["source"] not in state_ids or item["target"] not in state_ids
    ]
    failed_sequences = [item["id"] for item in sequences if item["status"] != "PASS"]
    errors = []
    if initial not in state_ids:
        errors.append("missing initial state")
    if invalid_refs:
        errors.append("invalid state reference")
    if failed_sequences:
        errors.append("missing required sequence edge")
    if transitions_without_requirement:
        errors.append("transition without requirement")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Phase 5 full transition and sequence coverage for Smart EV V2.",
        "initial": initial,
        "states": states,
        "transitions": transitions,
        "sequences": sequences,
        "summary": {
            "transitions_total": len(transitions),
            "transitions_reachable": len(reachable_transition_ids),
            "transitions_covered_by_requirement": len(transitions) - len(transitions_without_requirement),
            "transitions_without_requirement": len(transitions_without_requirement),
            "sequences_generated": len(sequences),
            "safety_sequences": len(safety_sequences),
            "recovery_sequences": len(recovery_sequences),
            "reachable_states": len(reachable),
            "unreachable_states": len(state_ids - reachable),
            "status": "PASS" if not errors else "FAIL",
        },
        "coverage": {
            "reachable_states": sorted(reachable),
            "unreachable_states": sorted(state_ids - reachable),
            "reachable_transitions": reachable_transition_ids,
            "transitions_without_requirement": transitions_without_requirement,
            "transitions_by_requirement": transitions_by_requirement,
            "failed_sequences": failed_sequences,
        },
        "validation": {
            "errors": errors,
            "missing_initial_state": initial not in state_ids,
            "invalid_state_references": invalid_refs,
            "failed_sequences": failed_sequences,
            "status": "PASS" if not errors else "FAIL",
        },
    }


def render_md(report: dict[str, Any]) -> str:
    summary = report["summary"]
    validation = report["validation"]
    lines = [
        "# Transition and Sequence Coverage - Phase 5",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Transitions total | {summary['transitions_total']} |",
        f"| Transitions reachable | {summary['transitions_reachable']} |",
        f"| Transitions covered by requirement | {summary['transitions_covered_by_requirement']} |",
        f"| Transitions without requirement | {summary['transitions_without_requirement']} |",
        f"| Sequences generated | {summary['sequences_generated']} |",
        f"| Safety sequences | {summary['safety_sequences']} |",
        f"| Recovery sequences | {summary['recovery_sequences']} |",
        f"| Reachable states | {summary['reachable_states']} |",
        f"| Unreachable states | {summary['unreachable_states']} |",
        "",
        "## Required Sequences",
        "",
        "| Sequence | Type | Path | Requirements | Status |",
        "|---|---|---|---|---|",
    ]
    for seq in report["sequences"]:
        lines.append(
            f"| `{seq['id']}` | {seq['type']} | "
            f"{' -> '.join(f'`{state}`' for state in seq['path'])} | "
            f"{'<br>'.join(f'`{req}`' for req in seq['requirements'])} | `{seq['status']}` |"
        )

    lines.extend(
        [
            "",
            "## Transition Coverage",
            "",
            "| Source | Event | Target | Requirements | Scenario |",
            "|---|---|---|---|---|",
        ]
    )
    for item in report["transitions"]:
        lines.append(
            f"| `{item['source']}` | `{item['event']}` | `{item['target']}` | "
            f"{'<br>'.join(f'`{req}`' for req in item['requirements'])} | `{item['scenario']}` |"
        )

    lines.extend(
        [
            "",
            "## Validation Gate",
            "",
            "```yaml",
            f"missing initial state: {validation['missing_initial_state']}",
            f"invalid state reference: {len(validation['invalid_state_references'])}",
            f"failed required sequences: {len(validation['failed_sequences'])}",
            f"transitions without requirement: {summary['transitions_without_requirement']}",
            f"Status: {validation['status']}",
            "```",
            "",
            "## Phase 5 Gate",
            "",
            "```yaml",
            f"Transitions total: {summary['transitions_total']}",
            f"Transitions reachable: {summary['transitions_reachable']}",
            f"Transitions covered by requirement: {summary['transitions_covered_by_requirement']}",
            f"Transitions without requirement: {summary['transitions_without_requirement']}",
            f"Sequences generated: {summary['sequences_generated']}",
            f"Safety sequences: {summary['safety_sequences']}",
            f"Recovery sequences: {summary['recovery_sequences']}",
            f"Status: {summary['status']}",
            "```",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    write_json(OUTPUT_JSON, report)
    write_text(OUTPUT_MD, render_md(report))
    print("Transition and Sequence Coverage")
    print(f"Status: {report['summary']['status']}")
    print(f"Transitions total: {report['summary']['transitions_total']}")
    print(f"Transitions reachable: {report['summary']['transitions_reachable']}")
    print(f"Sequences generated: {report['summary']['sequences_generated']}")
    print(f"Output JSON: {rel(OUTPUT_JSON)}")
    print(f"Output MD: {rel(OUTPUT_MD)}")
    return 0 if report["summary"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
