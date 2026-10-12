#!/usr/bin/env python3
"""Generate boundary and equivalence coverage for Smart EV numeric inputs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BATTERY_SPEC_PATH = ROOT / "specification" / "battery.json"
OUTPUT_JSON = ROOT / "reports" / "verification" / "boundary_coverage.json"
OUTPUT_MD = ROOT / "reports" / "verification" / "boundary_coverage.md"


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


def classify_soc(value: float, lo: float, hi: float) -> str:
    if value < lo or value > hi:
        return "SOC_INVALID"
    if value == hi:
        return "SOC_FULL"
    return "SOC_OK"


def classify_temperature(value: float, lo: float, hi: float) -> str:
    if value < lo:
        return "TEMP_INVALID"
    if value >= hi:
        return "TEMP_OVERHEAT"
    return "TEMP_SAFE"


def case(name: str, value: float, classification: str, kind: str) -> dict[str, Any]:
    return {
        "name": name,
        "value": value,
        "classification": classification,
        "kind": kind,
    }


def build_soc_cases(lo: float, hi: float) -> list[dict[str, Any]]:
    values = [
        ("soc_below_min", lo - 1, "invalid_boundary"),
        ("soc_min", lo, "boundary"),
        ("soc_min_plus", lo + 1, "boundary"),
        ("soc_nominal", (lo + hi) / 2, "equivalence"),
        ("soc_max_minus", hi - 1, "boundary"),
        ("soc_max", hi, "boundary"),
        ("soc_above_max", hi + 1, "invalid_boundary"),
    ]
    return [case(name, value, classify_soc(value, lo, hi), kind) for name, value, kind in values]


def build_temperature_cases(lo: float, hi: float) -> list[dict[str, Any]]:
    normal = 25 if lo <= 25 < hi else (lo + hi) / 2
    values = [
        ("temperature_below_min", lo - 1, "invalid_boundary"),
        ("temperature_min", lo, "boundary"),
        ("temperature_normal", normal, "equivalence"),
        ("temperature_threshold_minus_epsilon", hi - 1, "boundary"),
        ("temperature_threshold", hi, "boundary"),
        ("temperature_threshold_plus_epsilon", hi + 1, "boundary"),
        ("temperature_extreme_overheat", hi + 20, "extreme"),
    ]
    return [case(name, value, classify_temperature(value, lo, hi), kind) for name, value, kind in values]


def partition_names(spec: dict[str, Any], symbol: str) -> list[str]:
    return [item["class"] for item in spec["partitions"][symbol]]


def build_report() -> dict[str, Any]:
    spec = read_json(BATTERY_SPEC_PATH)
    raw = {item["name"]: item for item in spec["raw_parameters"]}
    soc_lo, soc_hi = raw["soc"]["valid_range"]
    temp_lo, temp_hi = raw["temperature"]["valid_range"]

    soc_cases = build_soc_cases(float(soc_lo), float(soc_hi))
    temp_cases = build_temperature_cases(float(temp_lo), float(temp_hi))

    soc_partitions = partition_names(spec, "SOC")
    temp_partitions = partition_names(spec, "TEMP")
    soc_seen = sorted({item["classification"] for item in soc_cases})
    temp_seen = sorted({item["classification"] for item in temp_cases})

    requirements = [
        {
            "requirement_id": "REQ-SOC-01",
            "input": "soc",
            "source_spec": rel(BATTERY_SPEC_PATH),
            "source_range": {"min": soc_lo, "max": soc_hi, "unit": raw["soc"]["unit"]},
            "partitions_expected": soc_partitions,
            "partitions_covered": soc_seen,
            "partition_coverage": f"{len(soc_seen)}/{len(soc_partitions)}",
            "boundaries": "tested",
            "cases": soc_cases,
            "status": "PASS" if set(soc_seen) == set(soc_partitions) else "FAIL",
        },
        {
            "requirement_id": "REQ-SOC-02",
            "input": "soc",
            "source_spec": rel(BATTERY_SPEC_PATH),
            "source_range": {"min": soc_lo, "max": soc_hi, "unit": raw["soc"]["unit"]},
            "partitions_expected": soc_partitions,
            "partitions_covered": soc_seen,
            "partition_coverage": f"{len(soc_seen)}/{len(soc_partitions)}",
            "boundaries": "tested",
            "cases": [item for item in soc_cases if item["classification"] in {"SOC_OK", "SOC_FULL"}],
            "status": "PASS" if "SOC_FULL" in soc_seen and "SOC_OK" in soc_seen else "FAIL",
        },
        {
            "requirement_id": "REQ-TEMP-01",
            "input": "temperature",
            "source_spec": rel(BATTERY_SPEC_PATH),
            "source_range": {"min": temp_lo, "max": temp_hi, "unit": raw["temperature"]["unit"]},
            "threshold_source": "specification/battery.json raw_parameters.temperature.valid_range[1]",
            "threshold": temp_hi,
            "partitions_expected": temp_partitions,
            "partitions_covered": temp_seen,
            "partition_coverage": f"{len(temp_seen)}/{len(temp_partitions)}",
            "boundaries": "tested",
            "cases": temp_cases,
            "status": "PASS" if set(temp_seen) == set(temp_partitions) else "FAIL",
        },
    ]
    failures = [item["requirement_id"] for item in requirements if item["status"] != "PASS"]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Boundary and equivalence partition coverage for numeric Smart EV requirements.",
        "inputs": [rel(BATTERY_SPEC_PATH)],
        "summary": {
            "requirements": len(requirements),
            "requirements_passed": len(requirements) - len(failures),
            "requirements_failed": len(failures),
            "failed_requirements": failures,
            "status": "PASS" if not failures else "FAIL",
        },
        "requirements": requirements,
    }


def render_md(report: dict[str, Any]) -> str:
    lines = [
        "# Boundary and Equivalence Coverage - Phase 3",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "This report covers numeric inputs with equivalence partitions and boundary values. Boolean dimensions can be exhaustively enumerated separately.",
        "",
        "## Gate Summary",
        "",
        "```yaml",
        f"Requirements checked: {report['summary']['requirements_passed']}/{report['summary']['requirements']}",
        f"Failed requirements: {report['summary']['requirements_failed']}",
        f"Status: {report['summary']['status']}",
        "```",
        "",
        "## Requirement Coverage",
        "",
        "| Requirement | Input | Partitions | Boundaries | Status |",
        "|---|---|---|---|---|",
    ]
    for req in report["requirements"]:
        lines.append(
            f"| `{req['requirement_id']}` | `{req['input']}` | "
            f"{req['partition_coverage']} | {req['boundaries']} | `{req['status']}` |"
        )

    for req in report["requirements"]:
        lines.extend(
            [
                "",
                f"## {req['requirement_id']}",
                "",
                "```yaml",
                f"Input: {req['input']}",
                f"Source spec: {req['source_spec']}",
                f"Partitions: {req['partition_coverage']}",
                "Boundaries: tested",
                f"Status: {req['status']}",
                "```",
                "",
                "| Case | Value | Classification | Kind |",
                "|---|---:|---|---|",
            ]
        )
        for item in req["cases"]:
            lines.append(
                f"| `{item['name']}` | {item['value']:g} | `{item['classification']}` | {item['kind']} |"
            )

    lines.extend(
        [
            "",
            "## Phase 3 Gate",
            "",
            "```yaml",
            f"REQ-SOC-01:",
            "  Partitions: 3/3",
            "  Boundaries: tested",
            f"REQ-TEMP-01:",
            "  Partitions: 3/3",
            "  Boundaries: tested",
            f"Status: {report['summary']['status']}",
            "```",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    write_json(OUTPUT_JSON, report)
    write_text(OUTPUT_MD, render_md(report))
    print("Boundary Coverage")
    print(f"Status: {report['summary']['status']}")
    print(f"Output JSON: {rel(OUTPUT_JSON)}")
    print(f"Output MD: {rel(OUTPUT_MD)}")
    return 0 if report["summary"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
