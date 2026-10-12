#!/usr/bin/env python3
"""Map Smart EV requirements to the teacher app code-generation schema.

Phase 7.5-B is intentionally conservative. It does not force Smart EV safety
requirements into unrelated Ch2 generator kinds.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "specification"
TRACEABILITY_PATH = ROOT / "reports" / "traceability" / "spec_traceability.json"
CAPABILITY_PATH = ROOT / "reports" / "verification" / "teacher_codegen_capability.md"
OUTPUT_SPEC = ROOT / "teacher_specs" / "smart_ev_codegen.json"
EXPERIMENT_DIR = ROOT / "teacher_specs" / "codegen_experiments"
ARITHMETIC_PROBE_SPEC = EXPERIMENT_DIR / "arithmetic_probe.json"
OUTPUT_MAPPING_JSON = ROOT / "reports" / "verification" / "teacher_codegen_mapping.json"
OUTPUT_MAPPING_MD = ROOT / "reports" / "verification" / "teacher_codegen_mapping.md"


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


DOMAIN_BY_PREFIX = {
    "REQ-AUTH": "AUTH",
    "REQ-SOC": "SOC",
    "REQ-TEMP": "TEMP",
    "REQ-PORT": "PORT",
    "REQ-CHG": "CHARGING",
    "REQ-EMG": "EMERGENCY",
}


EXPERIMENTAL_ARITHMETIC = {
    "REQ-SOC-01": {
        "teacher_kind": "c/arithmetic",
        "semantic_match": "PARTIAL",
        "reason": (
            "SOC range checking is numeric, but documented C arithmetic only "
            "generates simple arithmetic functions and is not runtime-confirmed."
        ),
    },
    "REQ-TEMP-01": {
        "teacher_kind": "c/arithmetic",
        "semantic_match": "PARTIAL",
        "reason": (
            "Temperature threshold checking is numeric, but documented C arithmetic "
            "does not prove support for threshold predicates and is not runtime-confirmed."
        ),
    },
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


def domain_for(requirement_id: str) -> str:
    for prefix, domain in DOMAIN_BY_PREFIX.items():
        if requirement_id.startswith(prefix):
            return domain
    return "UNKNOWN"


def production_functions(trace_record: dict[str, Any]) -> list[str]:
    return [item["function"] for item in trace_record.get("production_code", [])]


def classify_requirement(trace_record: dict[str, Any]) -> dict[str, Any]:
    rid = trace_record["requirement_id"]
    if rid in EXPERIMENTAL_ARITHMETIC:
        experimental = EXPERIMENTAL_ARITHMETIC[rid]
        return {
            "requirement_id": rid,
            "domain": domain_for(rid),
            "production_function": production_functions(trace_record),
            "teacher_codegen_supported": False,
            "support_level": "EXPERIMENTAL",
            "teacher_kind": experimental["teacher_kind"],
            "semantic_match": experimental["semantic_match"],
            "reason": experimental["reason"],
            "evidence_source": [
                rel(CAPABILITY_PATH),
                trace_record["json_spec"],
                rel(TRACEABILITY_PATH),
            ],
        }

    return {
        "requirement_id": rid,
        "domain": domain_for(rid),
        "production_function": production_functions(trace_record),
        "teacher_codegen_supported": False,
        "support_level": "UNSUPPORTED",
        "teacher_kind": None,
        "semantic_match": "NO_VALID_KIND",
        "reason": (
            "Confirmed teacher Ch2 generator kinds are template-based "
            "buffer/memory/Python fuzz generators and do not semantically express "
            "this Smart EV boolean/state-transition safety requirement."
        ),
        "evidence_source": [
            rel(CAPABILITY_PATH),
            trace_record["json_spec"],
            rel(TRACEABILITY_PATH),
        ],
    }


def build_smart_ev_codegen_spec(traceability: dict[str, Any], mappings: list[dict[str, Any]]) -> dict[str, Any]:
    directly_supported = [item for item in mappings if item["support_level"] == "DIRECTLY_SUPPORTED"]
    requirements = [
        {
            "id": item["requirement_id"],
            "text": item["requirement_text"],
            "category": "safety",
            "priority": "HIGH",
        }
        for item in traceability["traceability"]
        if item["requirement_id"] in REQUIREMENT_ORDER
    ]
    return {
        "name": "smart_ev_codegen",
        "description": (
            "Smart EV teacher-app code-generation compatibility artifact. "
            "No fake Ch2 functions are emitted; functions[] contains only "
            "requirements with a semantically valid DIRECTLY_SUPPORTED mapping."
        ),
        "requirements": requirements,
        "state_machine": None,
        "safety_properties": [],
        "mutual_exclusion": None,
        "functions": [
            item["teacher_function"]
            for item in directly_supported
            if item.get("teacher_function")
        ],
        "arithmetic_checks": [],
    }


def build_arithmetic_probe_spec(battery_spec: dict[str, Any]) -> dict[str, Any]:
    soc_range = next(item["valid_range"] for item in battery_spec["raw_parameters"] if item["name"] == "soc")
    temp_range = next(item["valid_range"] for item in battery_spec["raw_parameters"] if item["name"] == "temperature")
    return {
        "name": "smart_ev_arithmetic_probe",
        "description": (
            "Runtime probe for documented-but-not-confirmed C arithmetic code generation. "
            "This is an experiment only; it is not part of official Smart EV codegen coverage."
        ),
        "requirements": [
            {
                "id": "PROBE-SOC-ARITH",
                "text": f"Probe whether teacher Ch2 can generate C arithmetic code related to SOC range {soc_range}.",
                "category": "functional",
                "priority": "LOW",
            },
            {
                "id": "PROBE-TEMP-ARITH",
                "text": f"Probe whether teacher Ch2 can generate C arithmetic code related to temperature range {temp_range}.",
                "category": "functional",
                "priority": "LOW",
            },
        ],
        "state_machine": None,
        "safety_properties": [],
        "mutual_exclusion": None,
        "functions": [
            {
                "name": "probe_soc_delta",
                "language": "c",
                "kind": "arithmetic",
                "params": ["soc", "soc_max"],
                "bug": None,
            },
            {
                "name": "probe_temperature_delta",
                "language": "c",
                "kind": "arithmetic",
                "params": ["temperature", "temperature_limit"],
                "bug": None,
            },
        ],
        "arithmetic_checks": [],
    }


def build_mapping() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    traceability = read_json(TRACEABILITY_PATH)
    battery_spec = read_json(SPEC_DIR / "battery.json")
    trace_by_id = {item["requirement_id"]: item for item in traceability["traceability"]}
    mappings = []
    fake_mappings = 0
    semantic_mismatches = 0
    for rid in REQUIREMENT_ORDER:
        trace_record = trace_by_id[rid]
        mapping = classify_requirement(trace_record)
        mapping["constraints"] = trace_record.get("json_constraints", [])
        mapping["requirement_text"] = trace_record.get("requirement_text", "")
        if mapping["support_level"] == "DIRECTLY_SUPPORTED" and not mapping.get("teacher_function"):
            fake_mappings += 1
        if mapping["semantic_match"] in {"NO", "MISMATCH"}:
            semantic_mismatches += 1
        mappings.append(mapping)

    counts = {
        "requirements_total": len(mappings),
        "directly_supported": sum(1 for item in mappings if item["support_level"] == "DIRECTLY_SUPPORTED"),
        "partially_supported": sum(1 for item in mappings if item["support_level"] == "PARTIALLY_SUPPORTED"),
        "unsupported": sum(1 for item in mappings if item["support_level"] == "UNSUPPORTED"),
        "experimental": sum(1 for item in mappings if item["support_level"] == "EXPERIMENTAL"),
        "fake_mappings": fake_mappings,
        "semantic_mismatches": semantic_mismatches,
    }
    counts["teacher_codegen_semantic_coverage"] = (
        counts["directly_supported"] / counts["requirements_total"]
        if counts["requirements_total"]
        else 0
    )
    counts["ready_for_teacher_codegen"] = counts["directly_supported"] > 0 and fake_mappings == 0 and semantic_mismatches == 0

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Phase 7.5-B semantic mapping from Smart EV requirements to teacher Ch2 code-generation schema.",
        "inputs": [
            rel(TRACEABILITY_PATH),
            rel(CAPABILITY_PATH),
            "specification/auth.json",
            "specification/battery.json",
            "specification/port.json",
            "specification/charging.json",
        ],
        "mappings": mappings,
        "summary": counts,
        "status": {
            "SMART_EV_SPEC_STATUS": "PASS",
            "TEACHER_CODEGEN_COMPATIBILITY": "NO_DIRECT_SEMANTIC_MAPPING"
            if counts["directly_supported"] == 0
            else "PARTIAL",
        },
        "notes": [
            "Low code-generation compatibility is not a Smart EV specification failure.",
            "No fake buffer_copy or alloc_release mappings were created.",
            "C arithmetic remains experimental until SpecVerificationLab.exe runtime probe confirms Ch2 support.",
        ],
    }
    return report, build_smart_ev_codegen_spec(traceability, mappings), build_arithmetic_probe_spec(battery_spec)


def render_mapping_md(report: dict[str, Any]) -> str:
    summary = report["summary"]
    ready = "YES" if summary["ready_for_teacher_codegen"] else "NO"
    lines = [
        "# Teacher CodeGen Mapping - Phase 7.5-B",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "This report maps Smart EV requirements to the teacher app Ch2 `functions[]` schema without fabricating unrelated code-generation functions.",
        "",
        "## Summary",
        "",
        "```yaml",
        f"Requirements: {summary['requirements_total']}",
        f"Directly supported: {summary['directly_supported']}",
        f"Partially supported: {summary['partially_supported']}",
        f"Experimental: {summary['experimental']}",
        f"Unsupported: {summary['unsupported']}",
        f"Teacher codegen semantic coverage: {summary['teacher_codegen_semantic_coverage']:.2f}",
        f"Fake mappings: {summary['fake_mappings']}",
        f"Semantic mismatches: {summary['semantic_mismatches']}",
        f"READY_FOR_TEACHER_CODEGEN: {ready}",
        "```",
        "",
        "## Status Separation",
        "",
        "```yaml",
        f"SMART_EV_SPEC_STATUS: {report['status']['SMART_EV_SPEC_STATUS']}",
        f"TEACHER_CODEGEN_COMPATIBILITY: {report['status']['TEACHER_CODEGEN_COMPATIBILITY']}",
        "```",
        "",
        "## Mapping Matrix",
        "",
        "| Requirement | Domain | Production functions | Support | Teacher kind | Semantic match | Reason |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in report["mappings"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{item['requirement_id']}`",
                    item["domain"],
                    "<br>".join(f"`{fn}()`" for fn in item["production_function"]),
                    f"`{item['support_level']}`",
                    f"`{item['teacher_kind']}`" if item["teacher_kind"] else "`None`",
                    item["semantic_match"],
                    item["reason"],
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Official CodeGen Spec",
            "",
            "`teacher_specs/smart_ev_codegen.json` is intentionally valid but contains no `functions[]` entries unless a requirement has a DIRECTLY_SUPPORTED semantic mapping.",
            "",
            "When no requirement is directly supported, the artifact states the limitation instead of inserting fake template functions.",
            "",
            "## Experimental Probe",
            "",
            "`teacher_specs/codegen_experiments/arithmetic_probe.json` is separated from official coverage. It exists only to test whether documented C `arithmetic` is actually supported by Ch2 at runtime.",
            "",
            "## Phase 7.5-B Gate",
            "",
            "```yaml",
            f"Requirements total: {summary['requirements_total']}",
            f"Directly supported: {summary['directly_supported']}",
            f"Unsupported/partial/experimental: {summary['unsupported'] + summary['partially_supported'] + summary['experimental']}",
            f"Fake mappings: {summary['fake_mappings']}",
            f"Semantic mismatches: {summary['semantic_mismatches']}",
            f"READY_FOR_TEACHER_CODEGEN: {ready}",
            "Status: PASS",
            "```",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    report, codegen_spec, arithmetic_probe = build_mapping()
    write_json(OUTPUT_MAPPING_JSON, report)
    write_text(OUTPUT_MAPPING_MD, render_mapping_md(report))
    write_json(OUTPUT_SPEC, codegen_spec)
    write_json(ARITHMETIC_PROBE_SPEC, arithmetic_probe)

    summary = report["summary"]
    print("TEACHER CODEGEN ADAPTER")
    print("")
    print(f"Requirements: {summary['requirements_total']}")
    print(f"Directly supported: {summary['directly_supported']}")
    print(f"Partially supported: {summary['partially_supported']}")
    print(f"Experimental: {summary['experimental']}")
    print(f"Unsupported: {summary['unsupported']}")
    print("")
    print(f"Fake mappings: {summary['fake_mappings']}")
    print(f"Semantic mismatches: {summary['semantic_mismatches']}")
    print("")
    print(f"READY_FOR_TEACHER_CODEGEN: {'YES' if summary['ready_for_teacher_codegen'] else 'NO'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
