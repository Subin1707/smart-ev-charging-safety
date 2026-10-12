#!/usr/bin/env python3
"""GD12.2 canonical semantic contracts for the Smart EV teacher bridge."""

from __future__ import annotations

import copy
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HANG_SO = ROOT / "src" / "core" / "hang_so.h"
TRACEABILITY = ROOT / "reports" / "traceability" / "spec_traceability.json"
FORMAL_SUITE = ROOT / "reports" / "verification" / "formal_property_suite_v2.json"
V2_SPEC = ROOT / "teacher_specs" / "smart_ev_formal_verification_v2.json"
CONTRACTS_JSON = ROOT / "reports" / "verification" / "gd122_semantic_contracts.json"
V3_SPEC = ROOT / "teacher_specs" / "smart_ev_teacher_e2e_v3.json"


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def extract_production_constants() -> dict[str, float]:
    pattern = re.compile(r"^\s*#define\s+([A-Z0-9_]+)\s+([-+]?\d+(?:\.\d+)?)(?:f)?\b")
    constants: dict[str, float] = {}
    for line in HANG_SO.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = pattern.match(line)
        if match:
            constants[match.group(1)] = float(match.group(2))
    required = ["SOC_MIN", "SOC_MAX", "NHIET_DO_TOI_THIEU", "NHIET_DO_TOI_DA"]
    missing = [name for name in required if name not in constants]
    if missing:
        raise RuntimeError(f"Missing production constants: {', '.join(missing)}")
    return constants


def fmt_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def trace_by_requirement() -> dict[str, Any]:
    data = read_json(TRACEABILITY)
    return {item["requirement_id"]: item for item in data["traceability"]}


def formal_property_by_requirement() -> dict[str, str]:
    data = read_json(FORMAL_SUITE)
    out: dict[str, str] = {}
    for prop in data["properties"]:
        rid = prop.get("requirement_id")
        if rid and prop.get("group") == "SAFETY" and rid not in out:
            out[rid] = prop["formula"]
    return out


def build_arithmetic_checks(constants: dict[str, float]) -> list[dict[str, Any]]:
    soc_min = fmt_number(constants["SOC_MIN"])
    soc_max = fmt_number(constants["SOC_MAX"])
    temp_min_raw = constants["NHIET_DO_TOI_THIEU"]
    temp_min = fmt_number(temp_min_raw)
    temp_max = fmt_number(constants["NHIET_DO_TOI_DA"])
    return [
        {
            "name": "gd122_req_soc_01_valid_domain",
            "int_vars": ["soc"],
            "condition": f"soc >= {soc_min} and soc <= {soc_max}",
        },
        {
            "name": "gd122_req_soc_01_contradictory_violation",
            "int_vars": ["soc"],
            "condition": f"soc >= {soc_min} and soc <= {soc_max} and (soc < {soc_min} or soc > {soc_max})",
        },
        {
            "name": "gd122_req_temp_01_overheat_threshold",
            "int_vars": ["temperature"],
            "condition": f"temperature >= {temp_max}",
        },
        {
            "name": "gd122_req_temp_01_contradictory_condition",
            "int_vars": ["temperature"],
            "condition": f"temperature >= {temp_max} and temperature < {temp_max}",
        },
        {
            "name": "gd122_req_temp_01_safe_range",
            "int_vars": ["temperature"],
            "condition": f"temperature + {fmt_number(abs(temp_min_raw))} >= 0 and temperature < {temp_max}",
        },
    ]


def build_arithmetic_check_metadata() -> list[dict[str, str]]:
    return [
        {
            "name": "gd122_req_soc_01_valid_domain",
            "expected": "SAT",
            "contract": "REQ-SOC-01",
        },
        {
            "name": "gd122_req_soc_01_contradictory_violation",
            "expected": "UNSAT",
            "contract": "REQ-SOC-01",
        },
        {
            "name": "gd122_req_temp_01_overheat_threshold",
            "expected": "SAT",
            "contract": "REQ-TEMP-01",
        },
        {
            "name": "gd122_req_temp_01_contradictory_condition",
            "expected": "UNSAT",
            "contract": "REQ-TEMP-01",
        },
        {
            "name": "gd122_req_temp_01_safe_range",
            "expected": "SAT",
            "contract": "REQ-TEMP-01",
        },
    ]


def build_contracts(constants: dict[str, float]) -> list[dict[str, Any]]:
    traces = trace_by_requirement()
    formal = formal_property_by_requirement()
    soc_min = constants["SOC_MIN"]
    soc_max = constants["SOC_MAX"]
    temp_min = constants["NHIET_DO_TOI_THIEU"]
    temp_max = constants["NHIET_DO_TOI_DA"]
    return [
        {
            "requirement_id": "REQ-SOC-01",
            "requirement_text": traces["REQ-SOC-01"]["requirement_text"],
            "production_constants": {
                "SOC_MIN": soc_min,
                "SOC_MAX": soc_max,
            },
            "production_functions": ["soc_hop_le"],
            "formal_property": formal["REQ-SOC-01"],
            "teacher_path": {
                "chapter": "Ch3",
                "mechanism": "arithmetic_checks[]",
                "checks": ["gd122_req_soc_01_valid_domain", "gd122_req_soc_01_contradictory_violation"],
            },
            "production_path": {
                "source": "src/vehicle/pin.c",
                "function": "soc_hop_le",
                "behavior": "return pin->soc >= SOC_MIN && pin->soc <= SOC_MAX",
            },
            "input_domain": "soc in real numbers",
            "boundary_values": [soc_min - 1, soc_min, soc_min + 1, 50, soc_max - 1, soc_max, soc_max + 1],
            "expected_semantics": {
                "valid": f"{fmt_number(soc_min)} <= soc <= {fmt_number(soc_max)}",
                "invalid": f"soc < {fmt_number(soc_min)} or soc > {fmt_number(soc_max)}",
            },
            "semantic_relation": "SEMANTIC_SUBSET",
        },
        {
            "requirement_id": "REQ-TEMP-01",
            "requirement_text": traces["REQ-TEMP-01"]["requirement_text"],
            "production_constants": {
                "NHIET_DO_TOI_THIEU": temp_min,
                "NHIET_DO_TOI_DA": temp_max,
            },
            "production_functions": ["pin_qua_nhiet"],
            "formal_property": formal["REQ-TEMP-01"],
            "teacher_path": {
                "chapter": "Ch3",
                "mechanism": "arithmetic_checks[]",
                "checks": [
                    "gd122_req_temp_01_overheat_threshold",
                    "gd122_req_temp_01_contradictory_condition",
                    "gd122_req_temp_01_safe_range",
                ],
            },
            "production_path": {
                "source": "src/vehicle/pin.c",
                "function": "pin_qua_nhiet",
                "behavior": "return pin->nhiet_do >= NHIET_DO_TOI_DA",
            },
            "input_domain": "temperature in real numbers",
            "boundary_values": [temp_min - 1, temp_min, temp_min + 1, temp_max - 1, temp_max, temp_max + 1, 80],
            "expected_semantics": {
                "safe": f"{fmt_number(temp_min)} <= temperature < {fmt_number(temp_max)}",
                "overheat": f"temperature >= {fmt_number(temp_max)}",
            },
            "semantic_relation": "SEMANTIC_SUBSET",
        },
    ]


def build_v3_spec(contracts: list[dict[str, Any]], constants: dict[str, float]) -> dict[str, Any]:
    v2 = read_json(V2_SPEC)
    traces = trace_by_requirement()
    v3 = copy.deepcopy(v2)
    v3["name"] = "smart_ev_teacher_e2e_v3"
    v3["description"] = (
        "GD12.2 teacher integration spec. V2 state_machine and 16 CTL properties are preserved; "
        "SOC/TEMP Ch3 checks are generated from production constants through semantic contracts. "
        "Generated functions are tool capability artifacts, not production implementations."
    )
    v3["requirements"] = [
        {
            "id": item["requirement_id"],
            "text": item["requirement_text"],
            "category": "safety",
            "priority": "HIGH",
        }
        for item in traces.values()
    ]
    v3["functions"] = [
        {
            "name": "gd122_teacher_token_copy_probe",
            "language": "c",
            "kind": "buffer_copy",
            "params": ["token_input"],
            "buffer_size": int(constants.get("DO_DAI_TOKEN", 32)),
            "bug": None,
        },
    ]
    v3["arithmetic_checks"] = build_arithmetic_checks(constants)
    return v3


def build_teacher_artifact_roles(constants: dict[str, float]) -> list[dict[str, Any]]:
    return [
        {
            "teacher_function": "gd122_teacher_token_copy_probe",
            "kind": "c/buffer_copy",
            "linked_requirement": "REQ-AUTH-01",
            "semantic_role": "TOOL_CAPABILITY_ARTIFACT",
            "production_equivalent": "NONE",
            "counts_as_production_evidence": False,
            "schema_location": "teacher_specs/smart_ev_teacher_e2e_v3.json:functions[]",
            "buffer_size_source": "DO_DAI_TOKEN",
            "buffer_size": int(constants.get("DO_DAI_TOKEN", 32)),
        },
        {
            "teacher_function": "NONE_IN_RUNTIME_SPEC",
            "kind": "python/divide",
            "linked_requirement": "NONE",
            "semantic_role": "PROBE_ONLY_DISABLED",
            "purpose": "TEACHER_DYNAMIC_ENGINE_VALIDATION",
            "reason_disabled": (
                "Teacher Ch4 has no semantic oracle and python/divide creates "
                "uncontrolled-crash findings that are unrelated to Smart EV production."
            ),
            "production_equivalent": "NONE",
            "counts_as_production_evidence": False,
            "schema_location": "reports/verification/gd122_semantic_contracts.json only",
        },
    ]


def build_contract_report() -> dict[str, Any]:
    constants = extract_production_constants()
    contracts = build_contracts(constants)
    return {
        "phase": "GD12.2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "production_constant_source": rel(HANG_SO),
        "production_constants": constants,
        "contracts": contracts,
        "teacher_arithmetic_checks": build_arithmetic_checks(constants),
        "teacher_arithmetic_check_metadata": build_arithmetic_check_metadata(),
        "teacher_artifact_roles": build_teacher_artifact_roles(constants),
        "summary": {
            "semantic_contracts": len(contracts),
            "semantic_relation": "SEMANTIC_SUBSET",
            "exact_mappings": 0,
        },
    }


def main() -> int:
    report = build_contract_report()
    write_json(CONTRACTS_JSON, report)
    v3 = build_v3_spec(report["contracts"], report["production_constants"])
    write_json(V3_SPEC, v3)
    print(f"Semantic contracts: {len(report['contracts'])}")
    print(f"Production constants extracted: {len(report['production_constants'])}")
    print(f"Wrote: {rel(CONTRACTS_JSON)}")
    print(f"Wrote: {rel(V3_SPEC)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
