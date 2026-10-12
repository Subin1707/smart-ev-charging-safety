#!/usr/bin/env python3
"""Generate the Phase 6 Smart EV formal property suite V2."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "reports" / "verification" / "formal_adapter_mapping.json"
CAPABILITY_PATH = ROOT / "reports" / "verification" / "formal_mapping_draft.json"
TRANSITION_COVERAGE_PATH = ROOT / "reports" / "verification" / "transition_sequence_coverage.json"
OUTPUT_JSON = ROOT / "reports" / "verification" / "formal_property_suite_v2.json"
OUTPUT_MD = ROOT / "reports" / "verification" / "formal_property_suite_v2.md"


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


PROPERTY_RE = re.compile(r"^(AG|EF|AF|EG|AX|EX)\((!?[A-Za-z0-9_:-]+)\)$")


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


def supported_operators(capability: dict[str, Any]) -> set[str]:
    supported = set()
    for item in capability["operator_capability"]:
        if item["status"].startswith("SUPPORTED"):
            supported.add(item["operator"])
    return supported


def states_with_label(transition_coverage: dict[str, Any], label: str) -> list[str]:
    return [
        state["id"]
        for state in transition_coverage["states"]
        if label in state["labels"]
    ]


def transitions_for_requirements(
    transition_coverage: dict[str, Any],
    requirements: list[str],
) -> list[str]:
    by_req = transition_coverage["coverage"]["transitions_by_requirement"]
    transitions = []
    for requirement in requirements:
        transitions.extend(by_req.get(requirement, []))
    return sorted(set(transitions))


def build_safety_properties(
    mapping: dict[str, Any],
    transition_coverage: dict[str, Any],
) -> list[dict[str, Any]]:
    by_req = {item["requirement_id"]: item for item in mapping["requirements"]}
    properties = []
    for rid in REQUIREMENT_ORDER:
        item = by_req[rid]
        suffix = rid.replace("REQ-", "").replace("-", "_")
        properties.append(
            {
                "property_id": f"FP-{suffix}-SAFETY",
                "requirement_id": rid,
                "group": "SAFETY",
                "formula": item["ctl_property"],
                "operator": "AG",
                "meaning": f"No reachable execution may enter a state labeled {item['violation_label']}.",
                "expected_semantics": item["semantic_condition"],
                "states_involved": item["states_with_label"],
                "transitions_involved": transitions_for_requirements(transition_coverage, [rid]),
                "source": rel(MAPPING_PATH),
            }
        )
    return properties


def build_extra_properties(
    operators: set[str],
    transition_coverage: dict[str, Any],
) -> list[dict[str, Any]]:
    candidates = [
        {
            "property_id": "FP-CHG-01-REACH-CHARGING",
            "requirement_id": "REQ-CHG-01",
            "group": "REACHABILITY",
            "formula": "EF(charging)",
            "operator": "EF",
            "meaning": "There exists a valid connect/auth/start execution that reaches CHARGING.",
            "expected_semantics": "The normal start sequence is feasible when all safety-gate inputs are valid.",
            "label": "charging",
            "requirements": ["REQ-AUTH-01", "REQ-PORT-01", "REQ-CHG-01", "REQ-CHG-02"],
        },
        {
            "property_id": "FP-CHG-01-REACH-START-BLOCKED",
            "requirement_id": "REQ-CHG-01",
            "group": "REACHABILITY",
            "formula": "EF(start_blocked)",
            "operator": "EF",
            "meaning": "There exists an invalid start execution that reaches START_BLOCKED instead of CHARGING.",
            "expected_semantics": "The model includes the auth-failure/start-blocked branch required by the safety gate.",
            "label": "start_blocked",
            "requirements": ["REQ-AUTH-01", "REQ-CHG-01"],
        },
        {
            "property_id": "FP-STOP-REACH-STOPPED",
            "requirement_id": "REQ-CHG-02",
            "group": "REACHABILITY",
            "formula": "EF(stopped)",
            "operator": "EF",
            "meaning": "There exists at least one fault, emergency, SOC-full, overheat, or disconnect path that reaches a stopped safe state.",
            "expected_semantics": "Unsafe charging conditions have modeled stop outcomes.",
            "label": "stopped",
            "requirements": ["REQ-SOC-02", "REQ-TEMP-01", "REQ-PORT-03", "REQ-EMG-01", "REQ-AUTH-02", "REQ-CHG-02"],
        },
        {
            "property_id": "FP-RECOVERY-REACH-RECOVERED",
            "requirement_id": "REQ-CHG-02",
            "group": "RECOVERY",
            "formula": "EF(recovered)",
            "operator": "EF",
            "meaning": "There exists a recovery execution from stopped fault/emergency/overheat into a recovered safe state.",
            "expected_semantics": "Recovery sequences modeled in Phase 5 are reachable.",
            "label": "recovered",
            "requirements": ["REQ-PORT-03", "REQ-EMG-01", "REQ-TEMP-01", "REQ-CHG-02"],
        },
        {
            "property_id": "FP-SAFE-LIVENESS-AF-SAFE",
            "requirement_id": "REQ-CHG-02",
            "group": "RECOVERY_LIVENESS",
            "formula": "AF(safe)",
            "operator": "AF",
            "meaning": "Along modeled executions from the initial lifecycle state, a safe state is eventually encountered.",
            "expected_semantics": "The lifecycle starts safe and all modeled stop/recovery branches return to safe labeled states.",
            "label": "safe",
            "requirements": ["REQ-AUTH-02", "REQ-SOC-02", "REQ-TEMP-01", "REQ-PORT-03", "REQ-CHG-02", "REQ-EMG-01"],
        },
    ]
    properties = []
    for candidate in candidates:
        if candidate["operator"] not in operators:
            continue
        states = states_with_label(transition_coverage, candidate["label"])
        if not states:
            continue
        properties.append(
            {
                "property_id": candidate["property_id"],
                "requirement_id": candidate["requirement_id"],
                "group": candidate["group"],
                "formula": candidate["formula"],
                "operator": candidate["operator"],
                "meaning": candidate["meaning"],
                "expected_semantics": candidate["expected_semantics"],
                "states_involved": states,
                "transitions_involved": transitions_for_requirements(transition_coverage, candidate["requirements"]),
                "source": rel(TRANSITION_COVERAGE_PATH),
            }
        )
    return properties


def validate_properties(properties: list[dict[str, Any]], operators: set[str]) -> dict[str, Any]:
    formulas = [item["formula"] for item in properties]
    errors = []
    if len(formulas) != len(set(formulas)):
        errors.append("duplicate property formula")
    for item in properties:
        formula = item["formula"]
        match = PROPERTY_RE.match(formula)
        if not match:
            errors.append(f"unsupported property syntax: {formula}")
            continue
        if item["operator"] not in operators:
            errors.append(f"unsupported operator: {item['operator']}")
        if any(token in formula for token in ("&&", "||", "->")):
            errors.append(f"unsupported boolean operator in property: {formula}")
        if not item["states_involved"]:
            errors.append(f"property has no states involved: {item['property_id']}")
        if item["group"] != "SAFETY" and not item["transitions_involved"]:
            errors.append(f"non-safety property has no transitions involved: {item['property_id']}")
    safety_count = sum(1 for item in properties if item["group"] == "SAFETY")
    if safety_count != len(REQUIREMENT_ORDER):
        errors.append(f"expected {len(REQUIREMENT_ORDER)} safety baseline properties, found {safety_count}")
    return {
        "errors": errors,
        "safety_baseline": safety_count,
        "total_properties": len(properties),
        "status": "PASS" if not errors else "FAIL",
    }


def build_report() -> dict[str, Any]:
    mapping = read_json(MAPPING_PATH)
    capability = read_json(CAPABILITY_PATH)
    transition_coverage = read_json(TRANSITION_COVERAGE_PATH)
    operators = supported_operators(capability)
    properties = build_safety_properties(mapping, transition_coverage)
    properties.extend(build_extra_properties(operators, transition_coverage))
    validation = validate_properties(properties, operators)
    groups: dict[str, int] = {}
    for item in properties:
        groups[item["group"]] = groups.get(item["group"], 0) + 1
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Phase 6 Formal Property Suite V2. Keeps 11 safety baseline properties and adds only semantics-backed supported properties.",
        "inputs": [rel(MAPPING_PATH), rel(CAPABILITY_PATH), rel(TRANSITION_COVERAGE_PATH)],
        "supported_operators_used": sorted({item["operator"] for item in properties}),
        "properties": properties,
        "summary": {
            "properties_total": len(properties),
            "safety_properties": groups.get("SAFETY", 0),
            "reachability_properties": groups.get("REACHABILITY", 0),
            "recovery_properties": groups.get("RECOVERY", 0),
            "recovery_liveness_properties": groups.get("RECOVERY_LIVENESS", 0),
            "status": validation["status"],
        },
        "validation": validation,
    }


def render_md(report: dict[str, Any]) -> str:
    lines = [
        "# Formal Property Suite V2 - Phase 6",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "This suite keeps the 11 existing `AG(!req_x_violation)` safety properties and adds only properties with explicit semantics, involved states, involved transitions, and supported parser operators.",
        "",
        "## Summary",
        "",
        "```yaml",
        f"Properties total: {report['summary']['properties_total']}",
        f"Safety baseline: {report['summary']['safety_properties']}/11",
        f"Reachability: {report['summary']['reachability_properties']}",
        f"Recovery: {report['summary']['recovery_properties']}",
        f"Recovery/Liveness: {report['summary']['recovery_liveness_properties']}",
        f"Supported operators used: {', '.join(report['supported_operators_used'])}",
        f"Status: {report['summary']['status']}",
        "```",
        "",
        "## Property Index",
        "",
        "| Property ID | Requirement | Group | Formula | States | Transitions |",
        "|---|---|---|---|---:|---:|",
    ]
    for item in report["properties"]:
        lines.append(
            f"| `{item['property_id']}` | `{item['requirement_id']}` | {item['group']} | "
            f"`{item['formula']}` | {len(item['states_involved'])} | {len(item['transitions_involved'])} |"
        )

    for item in report["properties"]:
        lines.extend(
            [
                "",
                f"## {item['property_id']}",
                "",
                "```yaml",
                f"Requirement ID: {item['requirement_id']}",
                f"Group: {item['group']}",
                f"Formula: {item['formula']}",
                "Meaning: >",
                f"  {item['meaning']}",
                "Expected semantics: >",
                f"  {item['expected_semantics']}",
                "States involved:",
            ]
        )
        for state in item["states_involved"]:
            lines.append(f"  - {state}")
        lines.append("Transitions involved:")
        for transition in item["transitions_involved"]:
            lines.append(f"  - {transition}")
        lines.append("```")

    lines.extend(
        [
            "",
            "## Phase 6 Gate",
            "",
            "```yaml",
            f"Safety baseline preserved: {report['summary']['safety_properties']}/11",
            f"Unsupported syntax errors: {sum(1 for error in report['validation']['errors'] if 'unsupported' in error)}",
            f"Missing states/transitions errors: {sum(1 for error in report['validation']['errors'] if 'no states' in error or 'no transitions' in error)}",
            f"Status: {report['validation']['status']}",
            "```",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    write_json(OUTPUT_JSON, report)
    write_text(OUTPUT_MD, render_md(report))
    print("Formal Property Suite V2")
    print(f"Status: {report['summary']['status']}")
    print(f"Properties total: {report['summary']['properties_total']}")
    print(f"Safety baseline: {report['summary']['safety_properties']}/11")
    print(f"Output JSON: {rel(OUTPUT_JSON)}")
    print(f"Output MD: {rel(OUTPUT_MD)}")
    return 0 if report["summary"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
