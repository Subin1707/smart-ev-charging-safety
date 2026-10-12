"""Build JSON, CSV, summary, and Markdown traceability reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable


STATUSES = ("pass", "fail", "inconclusive", "not_mapped", "not_verifiable")


def build_traceability(requirement_results: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for result in requirement_results:
        mapping = result.get("mapping", {}) or {}
        records.append({
            "requirement_id": result.get("requirement_id"),
            "specification": result.get("specification", result.get("content")),
            "property_type": result.get("property_type", result.get("ir", {}).get("property_type")),
            "ir": result.get("ir", {}),
            "production_mapping": mapping,
            "production_code": result.get("production_sources", []),
            "generated_code": result.get("generated_artifacts", result.get("artifacts", [])),
            "verification_tools": result.get("verification_tools", result.get("strategy", [])),
            "verification_level": result.get("verification_level"),
            "execution": result.get("execution", {}),
            "result": result.get("overall_result", result.get("result", "INCONCLUSIVE")),
            "failure_class": result.get("failure_class"),
            "evidence": result.get("evidence", []),
            "counterexample": result.get("counterexample"),
            "reason": result.get("reason"),
        })
    return records


def save_traceability_json(records: list[dict[str, Any]], output: str | Path) -> None:
    Path(output).write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_traceability_csv(records: list[dict[str, Any]], output: str | Path) -> None:
    fields = ["requirement_id", "specification", "property_type", "mapping", "production_code", "generated_code", "tools", "result", "failure_class", "evidence", "counterexample", "reason"]
    with Path(output).open("w", newline="", encoding="utf-8-sig") as report_file:
        writer = csv.DictWriter(report_file, fieldnames=fields)
        writer.writeheader()
        for record in records:
            row = dict(record)
            row["mapping"] = (record.get("production_mapping") or {}).get("status", "NOT_MAPPED")
            for field in ("production_code", "generated_code", "verification_tools", "evidence"):
                key = "tools" if field == "verification_tools" else field
                value = record.get(field, [])
                row[key] = "; ".join(f"{item.get('level', '')}:{item.get('name', '')}={item.get('status', 'UNKNOWN')}" if isinstance(item, dict) else str(item) for item in value) if isinstance(value, list) else str(value)
            row["counterexample"] = str(record.get("counterexample") or "")
            writer.writerow({field: row.get(field, "") for field in fields})


def build_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {"total": len(records), **{status: 0 for status in STATUSES}}
    for record in records:
        status = str(record.get("result", "INCONCLUSIVE")).lower()
        if status not in summary:
            status = "inconclusive"
        summary[status] += 1
    verifiable = [record for record in records if record.get("result") != "NOT_VERIFIABLE"]
    generated = [record for record in verifiable if record.get("generated_code")]
    mapped = [record for record in verifiable if (record.get("production_mapping") or {}).get("status") == "MAPPED"]
    executed = [record for record in mapped if record.get("result") in {"PASS", "FAIL", "INCONCLUSIVE"}]
    summary["coverage"] = {
        "specification": len(verifiable) / len(records) if records else 0,
        "generation": len(generated) / len(verifiable) if verifiable else 0,
        "production_mapping": len(mapped) / len(verifiable) if verifiable else 0,
        "verification": len(executed) / len(mapped) if mapped else 0,
    }
    summary["verifiable"] = len(verifiable)
    summary["generated"] = len(generated)
    summary["mapped"] = len(mapped)
    summary["executed"] = len(executed)
    return summary


def save_summary(summary: dict[str, Any], output: str | Path) -> None:
    Path(output).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def generate_markdown_report(records: list[dict[str, Any]], summary: dict[str, Any], output: str | Path) -> None:
    lines = ["# Specification Verification Report", "", "## Summary", "", f"Total Requirements: {summary['total']}", ""]
    for status in STATUSES:
        lines.append(f"- {status.upper()}: {summary[status]}")
    lines.extend(["", "## Coverage", ""])
    for name, value in summary.get("coverage", {}).items():
        lines.append(f"- {name}: {value * 100:.1f}%")
    for record in records:
        lines.extend(["", f"## {record['requirement_id']}", "", f"**Result:** {record['result']}", "", f"**Specification:** {record.get('specification') or ''}", ""])
        lines.append(f"**Property:** `{record.get('property_type')}`")
        mapping = record.get("production_mapping") or {}
        lines.append(f"**Production mapping:** `{mapping.get('status', 'NOT_MAPPED')}`")
        if record.get("reason"):
            lines.extend(["", f"**Reason:** {record['reason']}"])
        if record.get("counterexample"):
            lines.extend(["", "### Counterexample", "", "```text", str(record["counterexample"]), "```"])
        if record.get("evidence"):
            lines.extend(["", "### Evidence", "", *[f"- `{item}`" for item in record["evidence"]]])
    Path(output).write_text("\n".join(lines) + "\n", encoding="utf-8")
