#!/usr/bin/env python3
"""GD12.1 deep capability analysis for the teacher CodeGen/AST/SMT/Fuzz path.

This script is intentionally observational. It does not execute or modify
SpecVerificationLab.exe, production C, or the final V2 formal model.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEACHER_SPECS = ROOT / "teacher_specs"
EXTRACTED_SPECS = ROOT / "teacher_app" / "extracted_static" / "dataset" / "specs"
REPORT_DIR = ROOT / "reports" / "verification"
TRACEABILITY = ROOT / "reports" / "traceability" / "spec_traceability.json"
PIPELINE_CAPABILITY = REPORT_DIR / "teacher_pipeline_capability.json"
SEMANTIC_VALIDATION = ROOT / "evidence" / "codegen_semantic_validation" / "gd75d_summary.json"
HANG_SO = ROOT / "src" / "core" / "hang_so.h"

CAP_JSON = REPORT_DIR / "gd121_teacher_codegen_capabilities.json"
CAP_MD = REPORT_DIR / "gd121_teacher_codegen_capabilities.md"
CAND_JSON = REPORT_DIR / "gd121_smart_ev_codegen_candidates.json"
CAND_MD = REPORT_DIR / "gd121_smart_ev_codegen_candidates.md"


PRODUCTION_FUNCTIONS = [
    "xac_thuc_xe",
    "soc_hop_le",
    "pin_qua_nhiet",
    "co_the_bat_dau_sac",
    "bat_dau_sac",
    "ket_noi_xe_vao_cong",
    "ket_noi_xe_vao_tram",
    "ngat_ket_noi_xe_khoi_tram",
    "giam_sat_xe_va_cong",
    "kiem_tra_toan_bo_tram",
]


KIND_DEFINITIONS: dict[tuple[str, str], dict[str, Any]] = {
    ("c", "buffer_copy"): {
        "required_fields": ["name", "language", "kind", "params", "buffer_size"],
        "generated_signature": "void name(char *param)",
        "generated_behavior": "Copies a string into a fixed local buffer using strcpy for the bug variant or strncpy for the safe variant.",
        "generated_code_pattern": "char buf[N]; strcpy/strncpy(buf, input);",
        "supports_ch2": True,
        "supports_ch3_ast": True,
        "supports_ch3_smt": False,
        "supports_ch4": False,
        "semantic_expressiveness": "String-copy memory safety template; not a Smart EV safety predicate.",
        "smart_ev_candidate_requirement": "REQ-AUTH-01 as PROBE_ONLY token-buffer handling, not authentication semantics.",
        "runtime_evidence": "OBSERVED_IN_SAMPLES",
    },
    ("c", "alloc_release"): {
        "required_fields": ["name", "language", "kind", "buffer_size"],
        "generated_signature": "void name(void)",
        "generated_behavior": "Allocates memory and releases it, with optional leak, double-free, or use-after-free bug variants.",
        "generated_code_pattern": "char *p = malloc(N); ... free(p);",
        "supports_ch2": True,
        "supports_ch3_ast": True,
        "supports_ch3_smt": False,
        "supports_ch4": False,
        "semantic_expressiveness": "Memory lifetime template; no Smart EV domain state semantics.",
        "smart_ev_candidate_requirement": "None; memory-probe only.",
        "runtime_evidence": "OBSERVED_IN_SAMPLES",
    },
    ("c", "arithmetic"): {
        "required_fields": ["name", "language", "kind", "params"],
        "generated_signature": "int name(int a, int b)",
        "generated_behavior": "Returns addition of the first two integer parameters.",
        "generated_code_pattern": "return a + b;",
        "supports_ch2": True,
        "supports_ch3_ast": True,
        "supports_ch3_smt": True,
        "supports_ch4": False,
        "semantic_expressiveness": "Addition expression only; not range, threshold, implication, or boolean predicate.",
        "smart_ev_candidate_requirement": "REQ-SOC-01 / REQ-TEMP-01 as PROBE_ONLY; semantic mismatch already confirmed.",
        "runtime_evidence": "CONFIRMED_BY_GD75D",
    },
    ("python", "divide"): {
        "required_fields": ["name", "language", "kind", "params"],
        "generated_signature": "def name(a, b)",
        "generated_behavior": "Returns integer division a // b; fuzzing can find divide-by-zero crashes.",
        "generated_code_pattern": "return a // b",
        "supports_ch2": False,
        "supports_ch3_ast": False,
        "supports_ch3_smt": False,
        "supports_ch4": True,
        "semantic_expressiveness": "Crash-oriented division target; no Smart EV production oracle.",
        "smart_ev_candidate_requirement": "compute_charging_rate probe only; not a production function.",
        "runtime_evidence": "OBSERVED_IN_SAMPLES",
    },
    ("python", "magic_value"): {
        "required_fields": ["name", "language", "kind", "params", "magic_values"],
        "generated_signature": "def name(a, b)",
        "generated_behavior": "Nested branch checks against two magic constants and raises/fails when found.",
        "generated_code_pattern": "if a == m1 and b == m2: raise ...",
        "supports_ch2": False,
        "supports_ch3_ast": False,
        "supports_ch3_smt": False,
        "supports_ch4": True,
        "semantic_expressiveness": "Concolic target for branch discovery; not arbitrary predicate fuzzing.",
        "smart_ev_candidate_requirement": "Auth token PROBE_ONLY if modeled as magic constants, not real xac_thuc_xe.",
        "runtime_evidence": "OBSERVED_IN_SAMPLES",
    },
}


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
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
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def discover_json_specs() -> list[Path]:
    roots = [EXTRACTED_SPECS, TEACHER_SPECS]
    paths: list[Path] = []
    for root in roots:
        if root.exists():
            paths.extend(sorted(root.rglob("*.json")))
    return paths


def collect_functions(spec_paths: list[Path]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    observed: list[dict[str, Any]] = []
    arithmetic_checks: list[dict[str, Any]] = []
    malformed_specs: list[str] = []
    for path in spec_paths:
        try:
            data = read_json(path, {})
        except json.JSONDecodeError:
            malformed_specs.append(rel(path))
            continue
        for fn in data.get("functions", []) or []:
            item = dict(fn)
            item["_source"] = rel(path)
            observed.append(item)
        for check in data.get("arithmetic_checks", []) or []:
            item = dict(check)
            item["_source"] = rel(path)
            arithmetic_checks.append(item)
    summary = {
        "spec_files_scanned": len(spec_paths),
        "malformed_specs": malformed_specs,
        "functions_observed": len(observed),
        "arithmetic_checks_observed": len(arithmetic_checks),
    }
    return observed, {"summary": summary, "arithmetic_checks": arithmetic_checks}


def minimal_probe(language: str, kind: str) -> dict[str, Any]:
    base = {
        "name": f"gd121_probe_{language}_{kind}",
        "requirements": [
            {
                "id": f"GD121-{language.upper()}-{kind.upper()}",
                "text": f"Minimal probe for {language}/{kind}.",
                "category": "functional",
                "priority": "LOW",
            }
        ],
        "state_machine": None,
        "safety_properties": [],
        "mutual_exclusion": None,
        "functions": [],
        "arithmetic_checks": [],
    }
    if (language, kind) == ("c", "buffer_copy"):
        base["functions"] = [{"name": "probe_copy", "language": "c", "kind": "buffer_copy", "params": ["input"], "buffer_size": 16, "bug": None}]
    elif (language, kind) == ("c", "alloc_release"):
        base["functions"] = [{"name": "probe_alloc", "language": "c", "kind": "alloc_release", "params": [], "buffer_size": 16, "bug": None}]
    elif (language, kind) == ("c", "arithmetic"):
        base["functions"] = [{"name": "probe_add", "language": "c", "kind": "arithmetic", "params": ["a", "b"], "bug": None}]
    elif (language, kind) == ("python", "divide"):
        base["functions"] = [{"name": "probe_divide", "language": "python", "kind": "divide", "params": ["a", "b"]}]
    elif (language, kind) == ("python", "magic_value"):
        base["functions"] = [{"name": "probe_magic", "language": "python", "kind": "magic_value", "params": ["a", "b"], "magic_values": [1234, 5678]}]
    return base


def parse_constants() -> dict[str, float]:
    constants: dict[str, float] = {}
    if not HANG_SO.exists():
        return constants
    pattern = re.compile(r"^\s*#define\s+([A-Z0-9_]+)\s+([-+]?\d+(?:\.\d+)?)(?:f)?\b")
    for line in HANG_SO.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = pattern.match(line)
        if match:
            constants[match.group(1)] = float(match.group(2))
    return constants


def build_capability_matrix(observed_functions: list[dict[str, Any]], arithmetic_data: dict[str, Any]) -> list[dict[str, Any]]:
    observed_sources: dict[tuple[str, str], list[str]] = defaultdict(list)
    observed_field_sets: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for fn in observed_functions:
        key = (fn.get("language", "UNKNOWN"), fn.get("kind", "UNKNOWN"))
        observed_sources[key].append(fn["_source"])
        for field in fn:
            if not field.startswith("_"):
                observed_field_sets[key][field] += 1

    matrix: list[dict[str, Any]] = []
    for (language, kind), definition in sorted(KIND_DEFINITIONS.items()):
        sources = sorted(set(observed_sources.get((language, kind), [])))
        status = "DOCUMENTED_AND_OBSERVED" if sources else "DOCUMENTED_NEEDS_RUNTIME_TEST"
        if definition["runtime_evidence"] == "CONFIRMED_BY_GD75D":
            status = "RUNTIME_CONFIRMED_BY_EXISTING_EVIDENCE"
        fields_seen = sorted(observed_field_sets.get((language, kind), {}).keys())
        matrix.append(
            {
                "language": language,
                "kind": kind,
                "schema": {
                    "required_fields": definition["required_fields"],
                    "observed_fields": fields_seen,
                },
                "generated_signature": definition["generated_signature"],
                "generated_behavior": definition["generated_behavior"],
                "generated_code_pattern": definition["generated_code_pattern"],
                "supports_ch2": definition["supports_ch2"],
                "supports_ch3_ast": definition["supports_ch3_ast"],
                "supports_ch3_smt": definition["supports_ch3_smt"],
                "supports_ch4": definition["supports_ch4"],
                "semantic_expressiveness": definition["semantic_expressiveness"],
                "smart_ev_candidate_requirement": definition["smart_ev_candidate_requirement"],
                "sample_sources": sources,
                "probe_spec": minimal_probe(language, kind),
                "runtime_status": status,
            }
        )

    checks = arithmetic_data["arithmetic_checks"]
    matrix.append(
        {
            "language": "spec",
            "kind": "arithmetic_checks",
            "schema": {
                "required_fields": ["name", "int_vars"],
                "optional_fields": ["condition", "overflow_expr"],
                "observed_fields": sorted({key for check in checks for key in check if not key.startswith("_")}),
            },
            "generated_signature": "No generated function; direct Ch3/Z3 specification item.",
            "generated_behavior": "Checks SAT/UNSAT for condition and int32 overflow for overflow_expr.",
            "generated_code_pattern": "condition: x >= 0 and x <= N; overflow_expr: x + y",
            "supports_ch2": False,
            "supports_ch3_ast": False,
            "supports_ch3_smt": True,
            "supports_ch4": False,
            "semantic_expressiveness": "Comparisons, ranges, and simple boolean connectives over integer variables.",
            "smart_ev_candidate_requirement": "REQ-SOC-01 and REQ-TEMP-01 directly; limited adapter support for simple power/fault implications.",
            "sample_sources": sorted({check["_source"] for check in checks}),
            "probe_spec": {
                "name": "gd121_probe_arithmetic_checks",
                "functions": [],
                "arithmetic_checks": [{"name": "probe_range", "int_vars": ["x"], "condition": "x >= 0 and x <= 100"}],
            },
            "runtime_status": "DOCUMENTED_AND_OBSERVED",
        }
    )
    return matrix


def build_expression_feature_analysis() -> dict[str, Any]:
    return {
        "comparisons": {
            "functions_schema": "NO for functions[] generated behavior except equality inside python magic_value templates.",
            "arithmetic_checks": "YES for integer condition expressions.",
        },
        "ranges": {
            "functions_schema": "NO; c/arithmetic returns addition and does not implement range predicates.",
            "arithmetic_checks": "YES; e.g. soc >= 0 and soc <= 100.",
        },
        "boolean_conjunction": {
            "functions_schema": "NO arbitrary conjunction generation.",
            "arithmetic_checks": "YES for simple integer conditions with and/or.",
        },
        "boolean_negation": {
            "functions_schema": "NO arbitrary negated predicate generation.",
            "arithmetic_checks": "PARTIAL via != and inverted comparisons; no evidence for general not().",
        },
        "state_guards": {
            "functions_schema": "NO for functions[]; YES in Ch1 state_machine labels/transitions.",
            "arithmetic_checks": "NO state machine semantics.",
        },
        "return_values": {
            "functions_schema": "FIXED by template: void C memory functions, int addition, Python division/magic exception.",
            "custom_expected_return_values": "NO evidence.",
        },
        "branch_behavior": {
            "functions_schema": "Only magic_value has fixed nested equality branches.",
            "custom_branch_behavior": "NO evidence.",
        },
        "parameter_preconditions": {
            "functions_schema": "NO custom preconditions.",
            "arithmetic_checks": "YES as constraints inside condition.",
        },
    }


def build_fuzz_oracle_analysis() -> dict[str, str]:
    return {
        "crash_only_detection": "YES",
        "expected_return_values": "NO",
        "assertions": "NO evidence",
        "property_predicates": "NO evidence",
        "custom_input_domains": "UNKNOWN",
        "boundary_seeds": "UNKNOWN",
        "cross_implementation_comparison": "NO",
        "summary": "Ch4 targets generated Python divide/magic_value functions and reports crashes/path discovery. Existing evidence does not show semantic oracle support.",
    }


def classify_function(name: str) -> dict[str, Any]:
    exact: list[str] = []
    subset: list[str] = []
    probe: list[str] = []
    unsupported_reasons: list[str] = []

    if name == "soc_hop_le":
        subset.append("arithmetic_checks[] can represent SOC range constraints, but not the production C return function itself.")
        probe.append("c/arithmetic was runtime-confirmed but mismatches the predicate; use only as negative/probe evidence.")
    elif name == "pin_qua_nhiet":
        subset.append("arithmetic_checks[] can represent temperature threshold comparisons, but not the production C helper function itself.")
        probe.append("c/arithmetic addition can be probed but is not a threshold predicate.")
    elif name == "xac_thuc_xe":
        probe.append("python/magic_value can model fixed secret constants as a fuzz target only.")
        unsupported_reasons.append("No function kind validates connected-state plus token-valid authentication semantics.")
    elif name in {"co_the_bat_dau_sac", "bat_dau_sac"}:
        unsupported_reasons.append("Safety gate requires multi-field boolean conjunction, state guards, and side-effect-aware semantics.")
    elif name in {"ket_noi_xe_vao_cong", "ket_noi_xe_vao_tram", "ngat_ket_noi_xe_khoi_tram"}:
        unsupported_reasons.append("Connection/disconnection functions mutate structs and state; functions[] has no struct/state-transition generator.")
    elif name in {"giam_sat_xe_va_cong", "kiem_tra_toan_bo_tram"}:
        unsupported_reasons.append("Runtime monitor over vehicle/port/station structs is outside template CodeGen and Ch4 fuzz schema.")
    else:
        unsupported_reasons.append("No known teacher kind maps this production function.")

    if exact:
        classification = "EXACT_SEMANTIC_CANDIDATE"
    elif subset:
        classification = "SEMANTIC_SUBSET_CANDIDATE"
    elif probe and not unsupported_reasons:
        classification = "PROBE_ONLY"
    elif probe:
        classification = "PROBE_ONLY"
    else:
        classification = "UNSUPPORTED"

    return {
        "production_function": name,
        "classification": classification,
        "exact_candidate_paths": exact,
        "subset_candidate_paths": subset,
        "probe_paths": probe,
        "unsupported_reasons": unsupported_reasons,
        "validated": False,
        "note": "GD12.1 does not promote candidates to validated.",
    }


def render_capability_md(report: dict[str, Any]) -> str:
    lines = [
        "# GD12.1 Teacher CodeGen Deep Capability",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "This report distinguishes teacher-document instructions from the user request. It inspects schema/resources and preserves limitations; it does not modify `SpecVerificationLab.exe` or production C.",
        "",
        "## Summary",
        "",
        "```yaml",
    ]
    for key, value in report["summary"].items():
        lines.append(f"{key}: {value}")
    lines.extend(["```", "", "## Capability Matrix", ""])
    lines.append("| Language | Kind | Ch2 | Ch3 AST | Ch3 SMT | Ch4 | Runtime status | Smart EV candidate |")
    lines.append("|---|---|---:|---:|---:|---:|---|---|")
    for item in report["capability_matrix"]:
        lines.append(
            f"| `{item['language']}` | `{item['kind']}` | {item['supports_ch2']} | {item['supports_ch3_ast']} | {item['supports_ch3_smt']} | {item['supports_ch4']} | {item['runtime_status']} | {item['smart_ev_candidate_requirement']} |"
        )
    lines.extend(
        [
            "",
            "## Expression Feature Analysis",
            "",
            "| Feature | functions[] | arithmetic_checks[] / other path |",
            "|---|---|---|",
        ]
    )
    for feature, data in report["expression_feature_analysis"].items():
        other = data.get("arithmetic_checks") or data.get("custom_expected_return_values") or data.get("custom_branch_behavior") or ""
        lines.append(f"| {feature} | {data.get('functions_schema', '')} | {other} |")
    lines.extend(["", "## Ch4 Oracle Capability", "", "| Capability | Status |", "|---|---|"])
    for key, value in report["fuzz_oracle_analysis"].items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Production Constants",
            "",
            "Constants are extracted from `src/core/hang_so.h` so V3 can avoid hard-coding verification thresholds in multiple places.",
            "",
            "```json",
            json.dumps(report["production_constants"], indent=2),
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def render_candidates_md(report: dict[str, Any]) -> str:
    lines = [
        "# GD12.1 Smart EV CodeGen Candidates",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "No candidate is marked validated in GD12.1. This is an analysis gate for GD12.2.",
        "",
        "| Production function | Classification | Candidate path / reason |",
        "|---|---|---|",
    ]
    for item in report["production_function_candidates"]:
        details = item["subset_candidate_paths"] + item["probe_paths"] + item["unsupported_reasons"]
        lines.append(f"| `{item['production_function']}` | `{item['classification']}` | {'<br>'.join(details)} |")
    lines.extend(
        [
            "",
            "## Requirement Candidate Summary",
            "",
            "| Requirement | Candidate status | Notes |",
            "|---|---|---|",
        ]
    )
    for item in report["requirement_candidates"]:
        lines.append(f"| `{item['requirement_id']}` | `{item['candidate_status']}` | {item['notes']} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat()
    spec_paths = discover_json_specs()
    observed_functions, arithmetic_data = collect_functions(spec_paths)
    matrix = build_capability_matrix(observed_functions, arithmetic_data)
    constants = parse_constants()
    pipeline = read_json(PIPELINE_CAPABILITY, {})
    semantic_validation = read_json(SEMANTIC_VALIDATION, {})

    languages = sorted({fn.get("language", "UNKNOWN") for fn in observed_functions})
    kinds_by_language: dict[str, list[str]] = defaultdict(list)
    for item in matrix:
        if item["language"] != "spec":
            kinds_by_language[item["language"]].append(item["kind"])

    c_kinds = sorted(set(kinds_by_language.get("c", [])))
    py_kinds = sorted(set(kinds_by_language.get("python", [])))
    ch2_kinds = [f"{item['language']}/{item['kind']}" for item in matrix if item["supports_ch2"]]
    ch3_ast_kinds = [f"{item['language']}/{item['kind']}" for item in matrix if item["supports_ch3_ast"]]
    ch4_kinds = [f"{item['language']}/{item['kind']}" for item in matrix if item["supports_ch4"]]

    fuzz = build_fuzz_oracle_analysis()
    summary = {
        "spec_files_scanned": len(spec_paths),
        "functions_observed": len(observed_functions),
        "languages_observed": ", ".join(languages),
        "C function kinds confirmed": len(c_kinds),
        "Python function kinds confirmed": len(py_kinds),
        "Ch2-capable kinds": len(ch2_kinds),
        "Ch3-AST-capable kinds": len(ch3_ast_kinds),
        "Ch3-SMT pathway": "functions[c/arithmetic] AST plus arithmetic_checks[] direct Z3",
        "Ch4-fuzz-capable kinds": len(ch4_kinds),
        "Fuzz custom domain": "UNKNOWN",
        "Fuzz semantic oracle": "NO",
        "Cross-implementation oracle": "NO",
    }

    capability_report = {
        "phase": "GD12.1",
        "generated_at": generated_at,
        "scope": "Complete usable semantic surface of unchanged SpecVerificationLab.exe CodeGen/AST/SMT/Fuzz pipeline based on extracted resources and existing runtime evidence.",
        "do_not": [
            "modify SpecVerificationLab.exe",
            "modify production C",
            "modify final V2 model",
            "invent unsupported function kinds",
            "rename probe functions as production functions",
            "count generated code as production evidence without semantic validation",
        ],
        "input_sources": [rel(path) for path in spec_paths]
        + [rel(PIPELINE_CAPABILITY), rel(SEMANTIC_VALIDATION), rel(HANG_SO)],
        "observed_functions": observed_functions,
        "capability_matrix": matrix,
        "arithmetic_checks_observed": arithmetic_data["arithmetic_checks"],
        "expression_feature_analysis": build_expression_feature_analysis(),
        "fuzz_oracle_analysis": fuzz,
        "production_constants": constants,
        "existing_runtime_evidence": {
            "pipeline_capability": pipeline.get("title"),
            "c_arithmetic_runtime_support": semantic_validation.get("teacher_codegen_capability", {}).get("c_arithmetic_runtime_support", "UNKNOWN"),
            "generated_C_compiles": semantic_validation.get("teacher_codegen_capability", {}).get("generated_C_compiles", "UNKNOWN"),
            "semantic_match_to_requirements": semantic_validation.get("teacher_codegen_capability", {}).get("semantic_match_to_requirements", "UNKNOWN"),
        },
        "summary": summary,
    }

    production_candidates = [classify_function(name) for name in PRODUCTION_FUNCTIONS]
    candidate_counts = Counter(item["classification"] for item in production_candidates)
    requirement_candidates = [
        {"requirement_id": "REQ-AUTH-01", "candidate_status": "PROBE_ONLY", "notes": "magic_value/buffer_copy can probe token-like artifacts only; no xac_thuc_xe semantic validation."},
        {"requirement_id": "REQ-AUTH-02", "candidate_status": "UNSUPPORTED", "notes": "disconnect clears auth is state mutation, not a CodeGen function kind."},
        {"requirement_id": "REQ-SOC-01", "candidate_status": "SEMANTIC_SUBSET_CANDIDATE", "notes": "arithmetic_checks[] can express 0 <= soc <= SOC_MAX from production constants."},
        {"requirement_id": "REQ-SOC-02", "candidate_status": "SEMANTIC_SUBSET_CANDIDATE", "notes": "threshold part expressible; power-zero implication remains state/production harness work."},
        {"requirement_id": "REQ-TEMP-01", "candidate_status": "SEMANTIC_SUBSET_CANDIDATE", "notes": "arithmetic_checks[] can express temperature >= NHIET_DO_TOI_DA from production constants."},
        {"requirement_id": "REQ-PORT-01", "candidate_status": "UNSUPPORTED", "notes": "port/vehicle state relation needs Kripke or production harness."},
        {"requirement_id": "REQ-PORT-02", "candidate_status": "UNSUPPORTED", "notes": "exclusive ownership needs state/mutual exclusion, not functions[] CodeGen."},
        {"requirement_id": "REQ-PORT-03", "candidate_status": "SEMANTIC_SUBSET_CANDIDATE", "notes": "simple fault/power condition may fit arithmetic_checks[] if encoded numerically; not Ch2/Ch4."},
        {"requirement_id": "REQ-CHG-01", "candidate_status": "UNSUPPORTED", "notes": "complete safety gate requires arbitrary boolean conjunction and state guards."},
        {"requirement_id": "REQ-CHG-02", "candidate_status": "UNSUPPORTED", "notes": "runtime validity gate cannot be generated by available function templates."},
        {"requirement_id": "REQ-EMG-01", "candidate_status": "SEMANTIC_SUBSET_CANDIDATE", "notes": "emergency/power-zero can be numerically encoded in arithmetic_checks[], but production behavior remains external."},
    ]
    ready_for_v3 = "YES" if summary["Fuzz semantic oracle"] == "YES" and candidate_counts["EXACT_SEMANTIC_CANDIDATE"] > 0 else "NO"
    candidates_report = {
        "phase": "GD12.1",
        "generated_at": generated_at,
        "production_functions_analyzed": len(production_candidates),
        "production_function_candidates": production_candidates,
        "requirement_candidates": requirement_candidates,
        "summary": {
            "exact_candidates": candidate_counts["EXACT_SEMANTIC_CANDIDATE"],
            "subset_candidates": candidate_counts["SEMANTIC_SUBSET_CANDIDATE"],
            "probe_only": candidate_counts["PROBE_ONLY"],
            "unsupported": candidate_counts["UNSUPPORTED"],
            "ready_for_v3_design": ready_for_v3,
        },
    }

    write_json(CAP_JSON, capability_report)
    write_json(CAND_JSON, candidates_report)
    write_text(CAP_MD, render_capability_md(capability_report))
    write_text(CAND_MD, render_candidates_md(candidates_report))

    print("============================================================")
    print(" GD12.1 - TEACHER CODEGEN DEEP CAPABILITY")
    print("============================================================")
    print(f"C function kinds confirmed       : {len(c_kinds)}")
    print(f"Python function kinds confirmed  : {len(py_kinds)}")
    print(f"Ch2-capable kinds                : {len(ch2_kinds)}")
    print(f"Ch3-AST-capable kinds            : {len(ch3_ast_kinds)}")
    print(f"Ch3-SMT pathway                  : {summary['Ch3-SMT pathway']}")
    print(f"Ch4-fuzz-capable kinds           : {len(ch4_kinds)}")
    print("")
    print(f"Production functions analyzed    : {len(production_candidates)}")
    print(f"Exact candidates                 : {candidate_counts['EXACT_SEMANTIC_CANDIDATE']}")
    print(f"Subset candidates                : {candidate_counts['SEMANTIC_SUBSET_CANDIDATE']}")
    print(f"Unsupported                      : {candidate_counts['UNSUPPORTED']}")
    print("")
    print(f"Fuzz custom domain               : {summary['Fuzz custom domain']}")
    print(f"Fuzz semantic oracle             : {summary['Fuzz semantic oracle']}")
    print(f"Cross-implementation oracle      : {summary['Cross-implementation oracle']}")
    print("")
    print(f"READY_FOR_V3_DESIGN              : {ready_for_v3}")
    print("============================================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
