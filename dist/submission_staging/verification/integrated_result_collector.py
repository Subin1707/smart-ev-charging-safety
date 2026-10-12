#!/usr/bin/env python3
"""Build the integrated verification report.

The report joins:
- requirement traceability,
- formal adapter mapping,
- actual SpecVerificationLab.exe results,
- production harness evidence.

Requirement-level formal PASS is reported only when requirement id,
violation label, CTL property, and teacher result all match.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRACEABILITY_PATH = ROOT / "reports" / "traceability" / "spec_traceability.json"
PRODUCTION_EVIDENCE_DIR = ROOT / "evidence" / "production_verification"
FORMAL_ADAPTER_MAPPING_PATH = ROOT / "reports" / "verification" / "formal_adapter_mapping.json"
TEACHER_APP_RESULT_PATH = ROOT / "evidence" / "formal_verification" / "teacher_app_result.json"
OUTPUT_DIR = ROOT / "reports" / "verification"
OUTPUT_JSON = OUTPUT_DIR / "integrated_verification.json"
OUTPUT_MD = OUTPUT_DIR / "integrated_verification.md"


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


def normalize_rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def split_csv(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if not value:
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def load_production_records() -> tuple[dict[str, dict[str, Any]], dict[str, Any] | None]:
    summary_path = PRODUCTION_EVIDENCE_DIR / "production_verification_summary.json"
    summary = read_json(summary_path)
    records = {}
    for record in summary.get("records", []):
        rid = record.get("requirement_id")
        if rid:
            records[rid] = record

    mutation_path = PRODUCTION_EVIDENCE_DIR / "negative_control_mutation.json"
    mutation = read_json(mutation_path) if mutation_path.exists() else summary.get("negative_control_mutation")
    return records, mutation


def load_formal_evidence() -> tuple[dict[str, dict[str, Any]], dict[str, Any], dict[str, Any]]:
    adapter_mapping = read_json(FORMAL_ADAPTER_MAPPING_PATH)
    teacher_result = read_json(TEACHER_APP_RESULT_PATH)

    result_by_requirement = {
        item.get("requirement_id"): item
        for item in teacher_result.get("properties", [])
        if item.get("requirement_id")
    }
    mapping_by_requirement = {
        item.get("requirement_id"): item
        for item in adapter_mapping.get("requirements", [])
        if item.get("requirement_id")
    }

    formal_records = {}
    for requirement_id, mapping in mapping_by_requirement.items():
        formal_records[requirement_id] = {
            "mapping": mapping,
            "teacher_result": result_by_requirement.get(requirement_id),
        }

    return formal_records, adapter_mapping, teacher_result


def build_formal_verification(requirement_id: str, formal_record: dict[str, Any] | None) -> dict[str, Any]:
    if not formal_record:
        return {
            "status": "INCONCLUSIVE",
            "reason": "Missing formal adapter mapping.",
        }

    mapping = formal_record.get("mapping") or {}
    teacher = formal_record.get("teacher_result")
    if not teacher:
        return {
            "status": "INCONCLUSIVE",
            "reason": "Missing teacher app result for mapped CTL property.",
            "mapping": mapping,
        }

    expected_label = mapping.get("violation_label")
    expected_property = mapping.get("ctl_property")
    mismatches = []
    if teacher.get("requirement_id") != requirement_id:
        mismatches.append("requirement_id")
    if teacher.get("violation_label") != expected_label:
        mismatches.append("violation_label")
    if teacher.get("property") != expected_property:
        mismatches.append("ctl_property")

    teacher_status = teacher.get("status")
    if mismatches:
        status = "INCONCLUSIVE"
        reason = "Teacher result does not match formal adapter mapping: " + ", ".join(mismatches)
    elif teacher_status == "PASS":
        status = "PASS"
        reason = "SpecVerificationLab result matches formal adapter mapping."
    elif teacher_status == "FAIL":
        status = "FAIL"
        reason = "SpecVerificationLab reported formal property failure."
    else:
        status = "INCONCLUSIVE"
        reason = "Teacher result status is missing or inconclusive."

    return {
        "status": status,
        "violation_label": expected_label,
        "ctl_property": expected_property,
        "semantic_condition": mapping.get("semantic_condition"),
        "teacher_result": teacher,
        "reason": reason,
    }


def build_production_verification(record: dict[str, Any] | None) -> dict[str, Any]:
    if not record:
        return {
            "status": "INCONCLUSIVE",
            "reason": "Missing production verification evidence record.",
        }

    compile_status = record.get("compile", {}).get("status")
    run_status = record.get("run", {}).get("status")
    status = record.get("status")
    if status == "PASS" and compile_status == "PASS" and run_status == "PASS":
        result = "PASS"
    elif "FAIL" in {status, compile_status, run_status}:
        result = "FAIL"
    else:
        result = "INCONCLUSIVE"

    return {
        "status": result,
        "compile_status": compile_status,
        "run_status": run_status,
        "timestamp": record.get("timestamp"),
    }


def final_status(formal: dict[str, Any], production: dict[str, Any], evidence: list[str]) -> str:
    if production.get("status") == "FAIL" or formal.get("status") == "FAIL":
        return "FAIL"
    if not evidence or production.get("status") == "INCONCLUSIVE" or formal.get("status") == "INCONCLUSIVE":
        return "INCONCLUSIVE"
    if production.get("status") == "PASS" and formal.get("status") == "PASS":
        return "PASS"
    return "INCONCLUSIVE"


def build_report() -> dict[str, Any]:
    traceability = read_json(TRACEABILITY_PATH)
    production_records, mutation = load_production_records()
    formal_records, adapter_mapping, teacher_result = load_formal_evidence()

    requirements = []
    for req in traceability.get("traceability", []):
        rid = req["requirement_id"]
        prod_record = production_records.get(rid)
        prod_code = req.get("production_code", [])
        prod_files = sorted({item.get("file") for item in prod_code if item.get("file")})
        prod_functions = [item.get("function") for item in prod_code if item.get("function")]
        harness = prod_record.get("harness") if prod_record else f"verification/harness/{rid.lower().replace('-', '_')}.c"

        evidence_file = PRODUCTION_EVIDENCE_DIR / f"{rid.lower().replace('-', '_')}.json"
        evidence = []
        if evidence_file.exists():
            evidence.append(normalize_rel(evidence_file))
        if prod_record:
            evidence.append(normalize_rel(PRODUCTION_EVIDENCE_DIR / "production_verification_summary.json"))
        if FORMAL_ADAPTER_MAPPING_PATH.exists():
            evidence.append(normalize_rel(FORMAL_ADAPTER_MAPPING_PATH))
        if TEACHER_APP_RESULT_PATH.exists():
            evidence.append(normalize_rel(TEACHER_APP_RESULT_PATH))

        formal = build_formal_verification(rid, formal_records.get(rid))
        production = build_production_verification(prod_record)

        requirements.append(
            {
                "requirement_id": rid,
                "requirement_text": req.get("requirement_text", ""),
                "constraints": req.get("json_constraints", []),
                "constraint_expression": prod_record.get("constraint") if prod_record else None,
                "production_files": prod_files or split_csv(prod_record.get("production_sources") if prod_record else None),
                "production_functions": prod_functions or split_csv(prod_record.get("production_functions") if prod_record else None),
                "harness": harness.replace("\\", "/") if harness else None,
                "formal_verification": formal,
                "production_verification": production,
                "evidence": evidence,
                "final_status": final_status(formal, production, evidence),
            }
        )

    formal_passes = sum(1 for item in requirements if item["formal_verification"]["status"] == "PASS")
    production_passes = sum(1 for r in production_records.values() if r.get("status") == "PASS")
    counts = {
        "total_requirements": len(requirements),
        "PASS": sum(1 for item in requirements if item["final_status"] == "PASS"),
        "FAIL": sum(1 for item in requirements if item["final_status"] == "FAIL"),
        "INCONCLUSIVE": sum(1 for item in requirements if item["final_status"] == "INCONCLUSIVE"),
        "formal_verification": "11/11 PASS"
        if formal_passes == 11 and len(formal_records) == 11
        else f"{formal_passes}/{len(formal_records)} PASS",
        "production_verification": "11/11 PASS"
        if len(production_records) == 11 and production_passes == 11
        else f"{production_passes}/{len(production_records)} PASS",
        "deadlock": (teacher_result.get("deadlock") or {}).get("result", "INCONCLUSIVE"),
        "negative_control": (mutation or {}).get("conclusion", "INCONCLUSIVE"),
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "title": "Integrated Verification Report",
        "inputs": [
            normalize_rel(TRACEABILITY_PATH),
            normalize_rel(PRODUCTION_EVIDENCE_DIR),
            normalize_rel(FORMAL_ADAPTER_MAPPING_PATH),
            normalize_rel(TEACHER_APP_RESULT_PATH),
        ],
        "formal_verification": {
            "source": teacher_result.get("source", "SpecVerificationLab.exe"),
            "specification": teacher_result.get("specification"),
            "deadlock": teacher_result.get("deadlock"),
            "adapter_mapping_summary": adapter_mapping.get("summary"),
            "teacher_summary": teacher_result.get("summary"),
        },
        "requirements": requirements,
        "summary": counts,
    }


def md_status(status: str) -> str:
    return status if status in {"PASS", "FAIL", "INCONCLUSIVE"} else "INCONCLUSIVE"


def render_markdown(report: dict[str, Any]) -> str:
    formal_summary = report["formal_verification"].get("teacher_summary") or {}
    deadlock = report["formal_verification"].get("deadlock") or {}
    lines = [
        "# Integrated Verification Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Total requirements: {report['summary']['total_requirements']}",
        f"- PASS: {report['summary']['PASS']}",
        f"- FAIL: {report['summary']['FAIL']}",
        f"- INCONCLUSIVE: {report['summary']['INCONCLUSIVE']}",
        f"- Formal verification: {report['summary']['formal_verification']}",
        f"- Production verification: {report['summary']['production_verification']}",
        f"- Deadlock: {report['summary']['deadlock']}",
        f"- Negative control: {report['summary']['negative_control']}",
        "",
        "## Formal Verification",
        "",
        f"- Source: `{report['formal_verification'].get('source')}`",
        f"- Specification: `{report['formal_verification'].get('specification')}`",
        f"- Properties: {formal_summary.get('formal_verification', 'INCONCLUSIVE')}",
        f"- Deadlock: {deadlock.get('result', 'INCONCLUSIVE')}",
        "",
        "Requirement-level formal status is PASS only when requirement id, violation label, CTL property, and teacher result match.",
        "",
        "## Requirement Traceability",
        "",
        "| Requirement | Constraints | Violation label | CTL property | Production files | Production functions | Harness | Formal | Production | Evidence | Final |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]

    for item in report["requirements"]:
        files = "<br>".join(f"`{x}`" for x in item["production_files"])
        functions = "<br>".join(f"`{x}`" for x in item["production_functions"])
        evidence = "<br>".join(f"`{x}`" for x in item["evidence"])
        formal = item["formal_verification"]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{item['requirement_id']}`<br>{item['requirement_text']}",
                    "<br>".join(f"`{x}`" for x in item["constraints"]),
                    f"`{formal.get('violation_label', '')}`",
                    f"`{formal.get('ctl_property', '')}`",
                    files,
                    functions,
                    f"`{item['harness']}`",
                    md_status(formal["status"]),
                    md_status(item["production_verification"]["status"]),
                    evidence,
                    md_status(item["final_status"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `PASS` final status requires formal verification PASS, production verification PASS, and complete evidence.",
            "- `FAIL` is reported if either formal or production verification fails.",
            "- `INCONCLUSIVE` is preserved when mapping or evidence is missing.",
            "- Formal PASS is derived from `formal_adapter_mapping.json` plus `teacher_app_result.json`; it is not copied globally.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    report = build_report()
    write_json(OUTPUT_JSON, report)
    write_text(OUTPUT_MD, render_markdown(report))
    print(f"Wrote {normalize_rel(OUTPUT_JSON)}")
    print(f"Wrote {normalize_rel(OUTPUT_MD)}")


if __name__ == "__main__":
    main()
