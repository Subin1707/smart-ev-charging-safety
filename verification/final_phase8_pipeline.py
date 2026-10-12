#!/usr/bin/env python3
"""Build the final V2 spec and Phase 8 verification report."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import formal_result_explainer


ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "reports" / "verification" / "formal_adapter_mapping.json"
TRANSITION_COVERAGE_PATH = ROOT / "reports" / "verification" / "transition_sequence_coverage.json"
PROPERTY_SUITE_PATH = ROOT / "reports" / "verification" / "formal_property_suite_v2.json"
NEGATIVE_SELECTIVITY_PATH = ROOT / "reports" / "verification" / "negative_control_selectivity.json"
OUTPUT_SPEC = ROOT / "teacher_specs" / "smart_ev_formal_verification_v2.json"
RAW_RESULT = ROOT / "evidence" / "formal_verification" / "teacher_app_result_v2.json"
EXPLAINED_RESULT = ROOT / "reports" / "verification" / "formal_explained_result_v2.md"
COUNTEREXAMPLE_DIR = ROOT / "reports" / "verification" / "counterexamples_v2"
FINAL_JSON = ROOT / "reports" / "verification" / "final_phase8_verification.json"
FINAL_MD = ROOT / "reports" / "verification" / "final_phase8_verification.md"


PHASE_REPORTS = [
    ROOT / "reports" / "verification" / "requirement_audit.md",
    ROOT / "reports" / "verification" / "coverage_matrix.md",
    ROOT / "reports" / "verification" / "boundary_coverage.json",
    ROOT / "reports" / "verification" / "full_state_model_v2.json",
    ROOT / "reports" / "verification" / "transition_sequence_coverage.json",
    ROOT / "reports" / "verification" / "formal_property_suite_v2.json",
    ROOT / "reports" / "verification" / "negative_control_selectivity.json",
]


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


def phase_gates() -> list[dict[str, Any]]:
    gates = []
    for index, path in enumerate(PHASE_REPORTS, start=1):
        status = "PASS" if path.exists() else "MISSING"
        if path.suffix == ".json" and path.exists():
            data = read_json(path)
            status = data.get("summary", {}).get("status") or data.get("validation", {}).get("status") or status
        elif path.suffix == ".md" and path.exists():
            text = path.read_text(encoding="utf-8")
            if "Status: PASS" not in text:
                status = "UNKNOWN"
        gates.append({"phase": index, "path": rel(path), "status": status})
    return gates


def build_v2_spec() -> dict[str, Any]:
    mapping = read_json(MAPPING_PATH)
    transition_coverage = read_json(TRANSITION_COVERAGE_PATH)
    property_suite = read_json(PROPERTY_SUITE_PATH)
    states = [item["id"] for item in transition_coverage["states"]]
    labeling = {item["id"]: item["labels"] for item in transition_coverage["states"]}
    transitions = [
        [item["source"], item["target"]]
        for item in transition_coverage["transitions"]
    ]

    for record in mapping["requirements"]:
        witness_id = f"unreachable_{record['violation_label']}"
        states.append(witness_id)
        labeling[witness_id] = [
            "smart_ev_v2",
            "unreachable_violation_witness",
            record["violation_label"],
            record["requirement_id"].lower().replace("-", "_"),
        ]

    for state in states:
        transitions.append([state, state])

    requirements_seen = []
    for prop in property_suite["properties"]:
        rid = prop["requirement_id"]
        if rid not in requirements_seen:
            requirements_seen.append(rid)

    requirements = [
        {
            "id": rid,
            "text": f"See Phase 1 audit and Phase 6 property suite for {rid}.",
            "category": "safety",
            "priority": "HIGH",
        }
        for rid in requirements_seen
    ]
    spec = {
        "name": "smart_ev_formal_verification_v2",
        "description": "Final Smart EV V2 formal model built after Phase 1-7 gates: lifecycle transitions, safety/reachability/recovery properties, and explainer-ready labels.",
        "requirements": requirements,
        "state_machine": {
            "states": states,
            "initial": [transition_coverage["initial"]],
            "labeling": labeling,
            "transitions": transitions,
        },
        "additional_flows": {},
        "safety_properties": [item["formula"] for item in property_suite["properties"]],
        "mutual_exclusion": None,
        "functions": [],
        "arithmetic_checks": [],
    }
    write_json(OUTPUT_SPEC, spec)
    return spec


def raw_result_summary() -> dict[str, Any]:
    if not RAW_RESULT.exists():
        return {
            "status": "WAITING_FOR_TEACHER_APP_RESULT",
            "path": rel(RAW_RESULT),
            "pass": 0,
            "fail": 0,
            "unknown": 0,
            "total": 0,
        }
    result = read_json(RAW_RESULT)
    pass_count = 0
    fail_count = 0
    unknown_count = 0
    for item in result.get("properties", []):
        status = formal_result_explainer.normalize_result_status(item.get("status") or item.get("reported_result"))
        if status == "PASS":
            pass_count += 1
        elif status == "FAIL":
            fail_count += 1
        else:
            unknown_count += 1
    return {
        "status": "PASS" if fail_count == 0 and unknown_count == 0 else "FAIL" if fail_count else "UNKNOWN",
        "path": rel(RAW_RESULT),
        "pass": pass_count,
        "fail": fail_count,
        "unknown": unknown_count,
        "total": pass_count + fail_count + unknown_count,
    }


def run_explainer_if_possible() -> bool:
    if not RAW_RESULT.exists():
        return False
    formal_result_explainer.explain(
        OUTPUT_SPEC.resolve(),
        RAW_RESULT.resolve(),
        EXPLAINED_RESULT.resolve(),
        COUNTEREXAMPLE_DIR.resolve(),
    )
    return True


def build_report() -> dict[str, Any]:
    gates = phase_gates()
    gates_pass = all(item["status"] == "PASS" for item in gates)
    spec = build_v2_spec()
    explainer_ran = run_explainer_if_possible()
    result = raw_result_summary()
    final_status = "PASS" if gates_pass and result["status"] == "PASS" else "WAITING_FOR_APP" if gates_pass and not RAW_RESULT.exists() else "BLOCKED"
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase_gates": gates,
        "phase_gates_pass": gates_pass,
        "final_spec": rel(OUTPUT_SPEC),
        "teacher_app": {
            "tool": "teacher_app/SpecVerificationLab.exe",
            "raw_result_expected_path": rel(RAW_RESULT),
            "raw_result_status": result,
        },
        "explainer": {
            "ran": explainer_ran,
            "output": rel(EXPLAINED_RESULT),
            "counterexample_dir": rel(COUNTEREXAMPLE_DIR),
        },
        "spec_summary": {
            "states": len(spec["state_machine"]["states"]),
            "transitions": len(spec["state_machine"]["transitions"]),
            "properties": len(spec["safety_properties"]),
        },
        "status": final_status,
    }


def render_md(report: dict[str, Any]) -> str:
    lines = [
        "# Final App Run + Explainer + Report - Phase 8",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Pipeline",
        "",
        "```text",
        "teacher_specs/smart_ev_formal_verification_v2.json",
        "  -> SpecVerificationLab.exe",
        "  -> evidence/formal_verification/teacher_app_result_v2.json",
        "  -> verification/formal_result_explainer.py",
        "  -> reports/verification/formal_explained_result_v2.md",
        "```",
        "",
        "## Phase Gates",
        "",
        "| Phase | Artifact | Status |",
        "|---:|---|---|",
    ]
    for gate in report["phase_gates"]:
        lines.append(f"| {gate['phase']} | `{gate['path']}` | `{gate['status']}` |")

    lines.extend(
        [
            "",
            "## Final Spec",
            "",
            "```yaml",
            f"Spec: {report['final_spec']}",
            f"States: {report['spec_summary']['states']}",
            f"Transitions: {report['spec_summary']['transitions']}",
            f"Properties: {report['spec_summary']['properties']}",
            "```",
            "",
            "## Teacher App Result",
            "",
            "```yaml",
            f"Raw result path: {report['teacher_app']['raw_result_expected_path']}",
            f"Raw result status: {report['teacher_app']['raw_result_status']['status']}",
            f"PASS: {report['teacher_app']['raw_result_status']['pass']}",
            f"FAIL: {report['teacher_app']['raw_result_status']['fail']}",
            f"UNKNOWN: {report['teacher_app']['raw_result_status']['unknown']}",
            "```",
            "",
        ]
    )
    if report["explainer"]["ran"]:
        lines.extend(
            [
                "## Explained Result",
                "",
                f"Explainer output: `{report['explainer']['output']}`",
                f"Counterexamples: `{report['explainer']['counterexample_dir']}`",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Explained Result",
                "",
                "Explainer has not run because the V2 raw teacher-app result is not present yet.",
                "",
                "Run the teacher app on `teacher_specs/smart_ev_formal_verification_v2.json`, save/export the result as `evidence/formal_verification/teacher_app_result_v2.json`, then rerun:",
                "",
                "```powershell",
                "python verification\\final_phase8_pipeline.py",
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Phase 8 Gate",
            "",
            "```yaml",
            f"Phase 1-7 gates pass: {str(report['phase_gates_pass']).lower()}",
            f"Teacher app raw result present: {str(RAW_RESULT.exists()).lower()}",
            f"Explainer ran: {str(report['explainer']['ran']).lower()}",
            f"Status: {report['status']}",
            "```",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    write_json(FINAL_JSON, report)
    write_text(FINAL_MD, render_md(report))
    print("Final Phase 8 Pipeline")
    print(f"Status: {report['status']}")
    print(f"Final spec: {rel(OUTPUT_SPEC)}")
    print(f"Final report: {rel(FINAL_MD)}")
    return 0 if report["status"] in {"PASS", "WAITING_FOR_APP"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
