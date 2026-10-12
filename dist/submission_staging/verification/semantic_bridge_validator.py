#!/usr/bin/env python3
"""GD12.2 semantic bridge validator.

Validates the bridge without treating teacher-generated code as production code.
"""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from semantic_contracts import (
    CONTRACTS_JSON,
    ROOT,
    V2_SPEC,
    V3_SPEC,
    build_arithmetic_checks,
    build_contract_report,
    build_v3_spec,
    fmt_number,
    rel,
    write_json,
)


BRIDGE_JSON = ROOT / "reports" / "verification" / "gd122_semantic_bridge.json"
BRIDGE_MD = ROOT / "reports" / "verification" / "gd122_semantic_bridge.md"
EVIDENCE_DIR = ROOT / "evidence" / "semantic_bridge"
HARNESS_C = EVIDENCE_DIR / "gd122_oracle_harness.c"
HARNESS_EXE = EVIDENCE_DIR / "gd122_oracle_harness.exe"
HARNESS_CSV = EVIDENCE_DIR / "gd122_oracle_results.csv"


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def run_command(cmd: list[str]) -> dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=30)
        return {
            "cmd": cmd,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "timeout": False,
        }
    except FileNotFoundError as exc:
        return {"cmd": cmd, "exit_code": None, "stdout": "", "stderr": str(exc), "timeout": False}
    except subprocess.TimeoutExpired as exc:
        return {"cmd": cmd, "exit_code": None, "stdout": exc.stdout or "", "stderr": exc.stderr or "", "timeout": True}


def ensure_contracts_and_spec() -> tuple[dict[str, Any], dict[str, Any]]:
    report = build_contract_report()
    write_json(CONTRACTS_JSON, report)
    v3 = build_v3_spec(report["contracts"], report["production_constants"])
    write_json(V3_SPEC, v3)
    return report, v3


def validate_v2_unchanged(v3: dict[str, Any]) -> dict[str, Any]:
    v2 = read_json(V2_SPEC)
    state_same = v2["state_machine"] == v3["state_machine"]
    properties_same = v2["safety_properties"] == v3["safety_properties"]
    return {
        "state_machine_unchanged": state_same,
        "safety_properties_unchanged": properties_same,
        "properties_count": len(v3["safety_properties"]),
        "pass": state_same and properties_same and len(v3["safety_properties"]) == 16,
    }


def validate_teacher_checks(contract_report: dict[str, Any], v3: dict[str, Any]) -> dict[str, Any]:
    expected = build_arithmetic_checks(contract_report["production_constants"])
    actual = v3.get("arithmetic_checks", [])
    drift = expected != actual
    return {
        "expected_checks": expected,
        "actual_checks": actual,
        "spec_drift": "DETECTED" if drift else "NONE",
        "pass": not drift,
    }


def validate_artifact_roles(v3: dict[str, Any]) -> dict[str, Any]:
    contract_report = read_json(CONTRACTS_JSON)
    roles = contract_report.get("teacher_artifact_roles", [])
    unsupported_kinds = []
    fake_mappings = []
    exact_relations = []
    supported = {"c/buffer_copy", "c/alloc_release", "c/arithmetic", "python/divide", "python/magic_value"}
    for role in roles:
        if role.get("kind") not in supported:
            unsupported_kinds.append(role)
        if role.get("counts_as_production_evidence") is True:
            fake_mappings.append(role)
        if role.get("semantic_relation") == "EXACT":
            exact_relations.append(role)
        if role.get("production_equivalent") not in {"NONE", None}:
            fake_mappings.append(role)
    return {
        "roles": roles,
        "unsupported_function_kinds": unsupported_kinds,
        "fake_mappings": fake_mappings,
        "exact_relations_without_proof": exact_relations,
        "pass": not unsupported_kinds and not fake_mappings and not exact_relations,
    }


def write_harness(contract_report: dict[str, Any]) -> None:
    constants = contract_report["production_constants"]
    soc_values = next(c["boundary_values"] for c in contract_report["contracts"] if c["requirement_id"] == "REQ-SOC-01")
    temp_values = next(c["boundary_values"] for c in contract_report["contracts"] if c["requirement_id"] == "REQ-TEMP-01")
    soc_init = ", ".join(f"{fmt_number(v)}.0f" if float(v).is_integer() else f"{v}f" for v in soc_values)
    temp_init = ", ".join(f"{fmt_number(v)}.0f" if float(v).is_integer() else f"{v}f" for v in temp_values)
    source = f"""#include <stdio.h>
#include "pin.h"
#include "hang_so.h"

int main(void) {{
    float soc_values[] = {{{soc_init}}};
    float temp_values[] = {{{temp_init}}};
    int soc_count = (int)(sizeof(soc_values) / sizeof(soc_values[0]));
    int temp_count = (int)(sizeof(temp_values) / sizeof(temp_values[0]));

    printf("requirement,input,expected,production_actual,match\\n");
    for (int i = 0; i < soc_count; i++) {{
        Pin pin;
        khoi_tao_pin(&pin, 60.0f, soc_values[i], 25.0f);
        int expected = (soc_values[i] >= SOC_MIN && soc_values[i] <= SOC_MAX) ? 1 : 0;
        int actual = soc_hop_le(&pin);
        printf("REQ-SOC-01,%.6g,%d,%d,%d\\n", soc_values[i], expected, actual, expected == actual);
    }}
    for (int i = 0; i < temp_count; i++) {{
        Pin pin;
        khoi_tao_pin(&pin, 60.0f, 50.0f, temp_values[i]);
        int expected = (temp_values[i] >= NHIET_DO_TOI_DA) ? 1 : 0;
        int actual = pin_qua_nhiet(&pin);
        printf("REQ-TEMP-01,%.6g,%d,%d,%d\\n", temp_values[i], expected, actual, expected == actual);
    }}
    (void){constants["SOC_MIN"]};
    return 0;
}}
"""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_text(HARNESS_C, source)


def run_production_oracle(contract_report: dict[str, Any]) -> dict[str, Any]:
    write_harness(contract_report)
    compile_cmd = [
        "gcc",
        "-std=c17",
        "-Wall",
        "-Wextra",
        "-Isrc",
        "-Isrc/core",
        "-Isrc/vehicle",
        "src/vehicle/pin.c",
        str(HARNESS_C),
        "-o",
        str(HARNESS_EXE),
    ]
    compile_result = run_command(compile_cmd)
    rows: list[dict[str, Any]] = []
    run_result: dict[str, Any] | None = None
    if compile_result["exit_code"] == 0:
        run_result = run_command([str(HARNESS_EXE)])
        if run_result["exit_code"] == 0:
            write_text(HARNESS_CSV, run_result["stdout"])
            reader = csv.DictReader(run_result["stdout"].splitlines())
            for row in reader:
                rows.append(
                    {
                        "requirement": row["requirement"],
                        "input": float(row["input"]),
                        "expected": int(row["expected"]),
                        "production_actual": int(row["production_actual"]),
                        "match": row["match"] == "1",
                    }
                )
    mismatches = [row for row in rows if not row["match"]]
    by_requirement: dict[str, str] = {}
    for rid in ["REQ-SOC-01", "REQ-TEMP-01"]:
        req_rows = [row for row in rows if row["requirement"] == rid]
        by_requirement[rid] = "PASS" if req_rows and all(row["match"] for row in req_rows) else "FAIL"
    return {
        "harness": rel(HARNESS_C),
        "compile": compile_result,
        "run": run_result,
        "cases": rows,
        "case_count": len(rows),
        "mismatches": mismatches,
        "mismatch_count": len(mismatches),
        "status_by_requirement": by_requirement,
        "pass": compile_result["exit_code"] == 0 and run_result is not None and run_result["exit_code"] == 0 and not mismatches and len(rows) == 14,
    }


def build_bridge_rows(contract_report: dict[str, Any], oracle: dict[str, Any], v3: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    role_by_kind = {role["semantic_role"]: role for role in contract_report.get("teacher_artifact_roles", [])}
    for contract in contract_report["contracts"]:
        rid = contract["requirement_id"]
        rows.append(
            {
                "Requirement": rid,
                "Formal CTL": contract["formal_property"],
                "Semantic Contract": contract["expected_semantics"],
                "Teacher Ch2": "TOOL_CAPABILITY_ARTIFACT" if rid == "REQ-SOC-01" else "NONE",
                "Teacher Ch3": ", ".join(contract["teacher_path"]["checks"]),
                "Teacher Ch4": "DISABLED_BY_GD12_2" if role_by_kind.get("PROBE_ONLY_DISABLED") else ("PROBE_ONLY" if role_by_kind.get("PROBE_ONLY") else "NONE"),
                "Production Function": ", ".join(contract["production_functions"]),
                "Production Dynamic": oracle["status_by_requirement"].get(rid, "FAIL"),
                "Relation": contract["semantic_relation"],
                "Evidence": [rel(CONTRACTS_JSON), rel(V3_SPEC), rel(HARNESS_CSV)],
            }
        )
    return rows


def render_md(report: dict[str, Any]) -> str:
    lines = [
        "# GD12.2 Smart EV Semantic Bridge",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "This bridge does not claim teacher-generated code is production code. Ch2/Ch4 artifacts are capability/probe artifacts only.",
        "",
        "## Summary",
        "",
        "```yaml",
    ]
    for key, value in report["summary"].items():
        lines.append(f"{key}: {value}")
    lines.extend(["```", "", "## Traceability", ""])
    lines.append("| Requirement | Formal CTL | Semantic Contract | Teacher Ch2 | Teacher Ch3 | Teacher Ch4 | Production Function | Production Dynamic | Relation | Evidence |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for row in report["bridge_rows"]:
        contract_text = json.dumps(row["Semantic Contract"], ensure_ascii=False)
        lines.append(
            f"| `{row['Requirement']}` | `{row['Formal CTL']}` | `{contract_text}` | {row['Teacher Ch2']} | {row['Teacher Ch3']} | {row['Teacher Ch4']} | `{row['Production Function']}` | {row['Production Dynamic']} | {row['Relation']} | {'<br>'.join(row['Evidence'])} |"
        )
    lines.extend(["", "## Production Oracle Cases", ""])
    lines.append("| Requirement | Input | Expected | Production actual | Match |")
    lines.append("|---|---:|---:|---:|---|")
    for case in report["production_oracle"]["cases"]:
        lines.append(f"| `{case['requirement']}` | {case['input']} | {case['expected']} | {case['production_actual']} | {case['match']} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    contract_report, v3 = ensure_contracts_and_spec()
    v2_gate = validate_v2_unchanged(v3)
    checks_gate = validate_teacher_checks(contract_report, v3)
    role_gate = validate_artifact_roles(v3)
    oracle = run_production_oracle(contract_report)
    bridge_rows = build_bridge_rows(contract_report, oracle, v3)

    semantic_contracts = len(contract_report["contracts"])
    teacher_ch2 = len([role for role in contract_report.get("teacher_artifact_roles", []) if role["semantic_role"] == "TOOL_CAPABILITY_ARTIFACT"])
    teacher_ch4 = len([role for role in contract_report.get("teacher_artifact_roles", []) if role["semantic_role"] == "PROBE_ONLY"])
    teacher_ch4_disabled = len([role for role in contract_report.get("teacher_artifact_roles", []) if role["semantic_role"] == "PROBE_ONLY_DISABLED"])
    fake_mappings = len(role_gate["fake_mappings"])
    gates_pass = v2_gate["pass"] and checks_gate["pass"] and role_gate["pass"] and oracle["pass"]
    ready = "YES" if gates_pass else "NO"

    summary = {
        "Requirements": 11,
        "Semantic contracts": semantic_contracts,
        "Production constants extracted": len(contract_report["production_constants"]),
        "Teacher Ch1 properties": v2_gate["properties_count"],
        "Teacher Ch2 artifacts": teacher_ch2,
        "Teacher Ch3 semantic checks": len(v3["arithmetic_checks"]),
        "Teacher Ch4 probes": teacher_ch4,
        "Teacher Ch4 disabled probes": teacher_ch4_disabled,
        "Exact mappings": 0,
        "Semantic subsets": semantic_contracts,
        "Probe-only artifacts": teacher_ch4 + teacher_ch4_disabled,
        "SOC contract": oracle["status_by_requirement"].get("REQ-SOC-01", "FAIL"),
        "TEMP contract": oracle["status_by_requirement"].get("REQ-TEMP-01", "FAIL"),
        "Spec drift": checks_gate["spec_drift"],
        "Production oracle cases": oracle["case_count"],
        "Production oracle mismatches": oracle["mismatch_count"],
        "Fake mappings": fake_mappings,
        "READY_FOR_TEACHER_RUNTIME": ready,
    }

    report = {
        "phase": "GD12.2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validation_gates": {
            "v2_model_unchanged": v2_gate,
            "teacher_z3_conditions_match_contract": checks_gate,
            "artifact_roles": role_gate,
            "production_oracle": {"pass": oracle["pass"], "case_count": oracle["case_count"], "mismatch_count": oracle["mismatch_count"]},
        },
        "semantic_contracts": contract_report["contracts"],
        "teacher_spec": rel(V3_SPEC),
        "production_oracle": oracle,
        "bridge_rows": bridge_rows,
        "summary": summary,
    }
    write_json(BRIDGE_JSON, report)
    write_text(BRIDGE_MD, render_md(report))

    print("============================================================")
    print(" GD12.2 - SMART EV SEMANTIC BRIDGE")
    print("============================================================")
    print(f"Requirements                    : {summary['Requirements']}")
    print(f"Semantic contracts              : {summary['Semantic contracts']}")
    print(f"Production constants extracted  : {summary['Production constants extracted']}")
    print("")
    print(f"Teacher Ch1 properties          : {summary['Teacher Ch1 properties']}")
    print(f"Teacher Ch2 artifacts           : {summary['Teacher Ch2 artifacts']}")
    print(f"Teacher Ch3 semantic checks     : {summary['Teacher Ch3 semantic checks']}")
    print(f"Teacher Ch4 probes              : {summary['Teacher Ch4 probes']}")
    print(f"Teacher Ch4 disabled probes     : {summary['Teacher Ch4 disabled probes']}")
    print("")
    print(f"Exact mappings                  : {summary['Exact mappings']}")
    print(f"Semantic subsets                : {summary['Semantic subsets']}")
    print(f"Probe-only artifacts            : {summary['Probe-only artifacts']}")
    print("")
    print(f"SOC contract                    : {summary['SOC contract']}")
    print(f"TEMP contract                   : {summary['TEMP contract']}")
    print(f"Spec drift                      : {summary['Spec drift']}")
    print("")
    print(f"Production oracle cases         : {summary['Production oracle cases']}")
    print(f"Production oracle mismatches    : {summary['Production oracle mismatches']}")
    print("")
    print(f"Fake mappings                   : {summary['Fake mappings']}")
    print("")
    print(f"READY_FOR_TEACHER_RUNTIME       : {summary['READY_FOR_TEACHER_RUNTIME']}")
    print("============================================================")
    return 0 if gates_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
