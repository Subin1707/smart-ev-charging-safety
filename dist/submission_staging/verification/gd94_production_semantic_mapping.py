#!/usr/bin/env python3
"""Generate GD9.4 production-semantic static/fuzz mapping reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "reports" / "verification" / "gd94_production_semantic_mapping.json"
OUT_MD = ROOT / "reports" / "verification" / "gd94_production_semantic_mapping.md"


TEACHER_KINDS = {
    "buffer_copy": "C fixed local buffer copy template; Ch2 checks strcpy/strncpy-style memory patterns.",
    "alloc_release": "C malloc/free lifecycle template; Ch2 checks leak/double-free/use-after-free patterns.",
    "arithmetic": "C int addition template; Ch3 can extract simple addition expressions.",
    "divide": "Python integer floor-division template; Ch4 fuzzes for divide-by-zero crashes.",
    "magic_value": "Python nested magic-value branch template; Ch4 concolic fuzz target.",
}


FUNCTIONS = [
    {
        "name": "xac_thuc_xe",
        "signature": "int xac_thuc_xe(XeDien *xe, const char *token)",
        "parameters": ["XeDien *xe", "const char *token"],
        "return_type": "int",
        "source_file": "src/auth/xac_thuc.c",
        "conditions": [
            "!xe || !xe->da_ket_noi -> return 0",
            "token && kiem_tra_token_hop_le(xe->ma_xe, token) -> authenticate",
            "else clear da_xac_thuc",
        ],
        "loops": [],
        "memory_operations": ["Reads token pointer; delegates token comparison to token.c; no local copy."],
        "arithmetic_operations": [],
        "requirement_ids": ["REQ-AUTH-01"],
        "teacher_classification": "UNSUPPORTED",
        "classification_reason": "Authentication is a boolean/state predicate. It accepts a string but does not implement equivalent bounded buffer-copy behavior for the requirement.",
    },
    {
        "name": "soc_hop_le",
        "signature": "int soc_hop_le(const Pin *pin)",
        "parameters": ["const Pin *pin"],
        "return_type": "int",
        "source_file": "src/vehicle/pin.c",
        "conditions": ["!pin -> return 0", "pin->soc >= SOC_MIN && pin->soc <= SOC_MAX"],
        "loops": [],
        "memory_operations": ["Pointer null check only."],
        "arithmetic_operations": ["Float comparisons against SOC_MIN=0.0f and SOC_MAX=100.0f."],
        "requirement_ids": ["REQ-SOC-01"],
        "teacher_classification": "SEMANTIC_SUBSET",
        "classification_reason": "Ch3 arithmetic_checks can represent the numeric range predicate, but no functions[].kind exactly preserves the production float predicate.",
    },
    {
        "name": "pin_qua_nhiet",
        "signature": "int pin_qua_nhiet(const Pin *pin)",
        "parameters": ["const Pin *pin"],
        "return_type": "int",
        "source_file": "src/vehicle/pin.c",
        "conditions": ["!pin -> return 1", "pin->nhiet_do >= NHIET_DO_TOI_DA"],
        "loops": [],
        "memory_operations": ["Pointer null check only."],
        "arithmetic_operations": ["Float comparison against NHIET_DO_TOI_DA=60.0f."],
        "requirement_ids": ["REQ-TEMP-01"],
        "teacher_classification": "SEMANTIC_SUBSET",
        "classification_reason": "Ch3 arithmetic_checks can represent the threshold predicate, but no functions[].kind exactly preserves null-as-overheat semantics.",
    },
    {
        "name": "co_the_bat_dau_sac",
        "signature": "int co_the_bat_dau_sac(const XeDien *xe, const CongSac *cong)",
        "parameters": ["const XeDien *xe", "const CongSac *cong"],
        "return_type": "int",
        "source_file": "src/charging/dieu_khien_sac.c",
        "conditions": [
            "Rejects null pointers",
            "Requires vehicle connected and port vehicle_id match",
            "Requires authenticated vehicle",
            "Rejects XE_LOI, non-finite SOC/temp, negative SOC",
            "Rejects SOC >= SOC_MAX",
            "Rejects temperature >= NHIET_DO_TOI_DA",
            "Rejects emergency, fault state, and nonzero port error code",
        ],
        "loops": [],
        "memory_operations": ["Pointer null checks only."],
        "arithmetic_operations": ["Float comparisons; isfinite checks."],
        "requirement_ids": ["REQ-SOC-02", "REQ-TEMP-01", "REQ-PORT-01", "REQ-CHG-01", "REQ-CHG-02"],
        "teacher_classification": "UNSUPPORTED",
        "classification_reason": "Composite production safety gate is not represented by any confirmed functions[].kind. Ch1 labels can model it; Ch2/Ch4 cannot.",
    },
    {
        "name": "bat_dau_sac",
        "signature": "int bat_dau_sac(XeDien *xe, CongSac *cong, PhienSac *phien, float cong_suat_kw)",
        "parameters": ["XeDien *xe", "CongSac *cong", "PhienSac *phien", "float cong_suat_kw"],
        "return_type": "int",
        "source_file": "src/charging/dieu_khien_sac.c",
        "conditions": ["Rejects non-finite or <=0 power", "Calls co_the_bat_dau_sac before state mutation", "Initializes session when phien is non-null"],
        "loops": [],
        "memory_operations": ["Pointer guarded writes to xe/cong/phien."],
        "arithmetic_operations": ["g_session_counter++", "float power comparisons."],
        "requirement_ids": ["REQ-CHG-01"],
        "teacher_classification": "UNSUPPORTED",
        "classification_reason": "Stateful production start operation has no equivalent teacher static/fuzz function kind.",
    },
    {
        "name": "ket_noi_xe_vao_cong",
        "signature": "int ket_noi_xe_vao_cong(CongSac *cong, int vehicle_id)",
        "parameters": ["CongSac *cong", "int vehicle_id"],
        "return_type": "int",
        "source_file": "src/station/cong_sac.c",
        "conditions": ["!cong -> return 0", "Rejects different vehicle when port occupied", "Sets vehicle_id and connected state"],
        "loops": [],
        "memory_operations": ["Pointer guarded struct writes."],
        "arithmetic_operations": ["Comparison with sentinel -1."],
        "requirement_ids": ["REQ-PORT-01", "REQ-PORT-02"],
        "teacher_classification": "UNSUPPORTED",
        "classification_reason": "Exclusive port binding is a state invariant, not buffer/memory/Python fuzz behavior.",
    },
    {
        "name": "ket_noi_xe_vao_tram",
        "signature": "int ket_noi_xe_vao_tram(TramSac *tram, int port_idx, XeDien *xe)",
        "parameters": ["TramSac *tram", "int port_idx", "XeDien *xe"],
        "return_type": "int",
        "source_file": "src/station/tram_sac.c",
        "conditions": ["Rejects nulls/out-of-range port", "Rejects emergency and negative vehicle id", "Rejects duplicate vehicle assignment except idempotent same-port connection"],
        "loops": ["for i in SO_CONG_SAC checks duplicate vehicle assignment"],
        "memory_operations": ["Pointer guarded writes; calls ket_noi_xe_vao_cong."],
        "arithmetic_operations": ["port_idx bounds; i + 1 assigned_port."],
        "requirement_ids": ["REQ-AUTH-01", "REQ-PORT-01", "REQ-PORT-02"],
        "teacher_classification": "UNSUPPORTED",
        "classification_reason": "Station connection semantics require looped state checks; no confirmed teacher Ch2/Ch4 kind preserves them.",
    },
    {
        "name": "ngat_ket_noi_xe_khoi_tram",
        "signature": "int ngat_ket_noi_xe_khoi_tram(TramSac *tram, int port_idx, XeDien *xe)",
        "parameters": ["TramSac *tram", "int port_idx", "XeDien *xe"],
        "return_type": "int",
        "source_file": "src/station/tram_sac.c",
        "conditions": ["Rejects null tram/out-of-range port", "Rejects mismatched vehicle id", "Clears port and vehicle connection/authentication state"],
        "loops": [],
        "memory_operations": ["Pointer guarded writes; calls ngat_ket_noi_cong."],
        "arithmetic_operations": ["port_idx bounds; cap_nhat_tong_cong_suat_tram aggregation after disconnect."],
        "requirement_ids": ["REQ-AUTH-02"],
        "teacher_classification": "UNSUPPORTED",
        "classification_reason": "Disconnect clears authentication state; no static/fuzz function kind captures this production transition.",
    },
    {
        "name": "giam_sat_xe_va_cong",
        "signature": "KetQuaGiamSat giam_sat_xe_va_cong(XeDien *xe, CongSac *cong, TramSac *tram)",
        "parameters": ["XeDien *xe", "CongSac *cong", "TramSac *tram"],
        "return_type": "KetQuaGiamSat",
        "source_file": "src/safety/giam_sat_an_toan.c",
        "conditions": ["Rejects null port", "Cuts power on emergency, overheat, full battery, invalid connection, or unauthenticated charging"],
        "loops": [],
        "memory_operations": ["Pointer guarded writes to CongSac and XeDien."],
        "arithmetic_operations": ["Sets power/current to 0.0f; delegates predicate checks."],
        "requirement_ids": ["REQ-SOC-02", "REQ-TEMP-01", "REQ-PORT-01", "REQ-PORT-03", "REQ-CHG-01", "REQ-EMG-01"],
        "teacher_classification": "UNSUPPORTED",
        "classification_reason": "Runtime monitor mutates state based on multiple predicates; not a generated Ch2/Ch4 template.",
    },
    {
        "name": "kiem_tra_toan_bo_tram",
        "signature": "int kiem_tra_toan_bo_tram(TramSac *tram, XeDien ds_xe[], int so_xe)",
        "parameters": ["TramSac *tram", "XeDien ds_xe[]", "int so_xe"],
        "return_type": "int",
        "source_file": "src/safety/giam_sat_an_toan.c",
        "conditions": ["!tram -> return 0", "Monitors occupied ports only", "Increments incident count when monitor result is unsafe"],
        "loops": ["Nested for over SO_CONG_SAC ports and so_xe vehicles."],
        "memory_operations": ["Array indexing into tram->cong and ds_xe; guarded by bounds/inputs."],
        "arithmetic_operations": ["so_su_co++", "cap_nhat_tong_cong_suat_tram sums float power."],
        "requirement_ids": ["REQ-CHG-02"],
        "teacher_classification": "UNSUPPORTED",
        "classification_reason": "Nested production monitoring loop has no equivalent teacher function kind.",
    },
]


def build_report() -> dict:
    exact = [f for f in FUNCTIONS if f["teacher_classification"] == "EXACT_SEMANTIC_MATCH"]
    subsets = [f for f in FUNCTIONS if f["teacher_classification"] == "SEMANTIC_SUBSET"]
    probe_only = [
        {
            "name": "handle_auth_token",
            "classification": "PROBE_ONLY",
            "reason": "Generated/probe token buffer-copy shape is not a production Smart EV requirement operation.",
        },
        {
            "name": "compute_charging_rate",
            "classification": "PROBE_ONLY",
            "reason": "Teacher Python divide target uses integer floor division and has no equivalent named production function.",
        },
    ]
    unsupported = [f for f in FUNCTIONS if f["teacher_classification"] == "UNSUPPORTED"]
    return {
        "phase": "GD9.4",
        "title": "Production-Semantic Static/Fuzz Mapping",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "constraints": {
            "modified_teacher_exe": False,
            "modified_production_source": False,
            "modified_official_v2_spec": False,
            "fake_requirement_mappings": 0,
        },
        "teacher_kinds_confirmed": TEACHER_KINDS,
        "production_functions": FUNCTIONS,
        "classification_summary": {
            "production_functions_analyzed": len(FUNCTIONS),
            "teacher_kinds_confirmed": len(TEACHER_KINDS),
            "exact_semantic_matches": len(exact),
            "semantic_subsets": len(subsets),
            "probe_only": len(probe_only),
            "unsupported": len(unsupported),
        },
        "ch2_mapping": {
            "production_semantic_path": False,
            "classification": "NO_VALID_PRODUCTION_STATIC_PATH",
            "reason": "No analyzed production requirement operation legitimately maps to Ch2 generated memory templates. Token authentication must not be mapped to buffer_copy merely because it accepts a string.",
            "note": "Other production code has bounded string operations such as snprintf/strncpy, but no official requirement mapping is created here unless it preserves the relevant production requirement semantics.",
        },
        "ch4_mapping": {
            "production_semantic_path": False,
            "compute_charging_rate": {
                "classification": "PROBE_ONLY",
                "crash_trigger": "time_hours == 0, causing Python ZeroDivisionError in return energy_kwh // time_hours",
                "observed_crashes": "11/300 black-box fuzz iterations",
                "production_equivalent_exists": False,
            },
        },
        "overflow_analyzer_limitation": {
            "bounded_condition_output": "req_soc_01_overflow_v2_bounded: sat model={'soc_current': 0, 'soc_delta': 0}",
            "heuristic_overflow_output": "req_soc_01_overflow_v2_bounded (int32 overflow?): sat model={'soc_current': -1, 'soc_delta': -2147483648}",
            "bounded_condition_respected_by_z3": True,
            "bounded_condition_respected_by_heuristic": False,
            "classification": "TOOL_MODEL_LIMITATION",
            "reason": "The condition query preserves bounded values, but the overflow heuristic builds a separate int32-overflow query over the raw overflow_expr and loses the condition preconditions. Production SOC is float-bounded by SOC_MIN/SOC_MAX, so this is not a production CWE-190 finding.",
        },
        "readiness": {
            "ready_for_production_e2e_adapter": False,
            "next_action": "Keep teacher Ch2/Ch4 probes separate from production evidence; build production-native static/dynamic verification for real C, or only create GD9.5 if a future exact semantic match is found.",
        },
        "probe_only_functions": probe_only,
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(path: Path, data: dict) -> None:
    summary = data["classification_summary"]
    lines = [
        "# GD9.4 — Production-Semantic Static/Fuzz Mapping",
        "",
        f"Generated: {data['generated_at']}",
        "",
        "## Summary",
        "",
        f"- Production functions analyzed: {summary['production_functions_analyzed']}",
        f"- Teacher kinds confirmed: {summary['teacher_kinds_confirmed']}",
        f"- Exact semantic matches: {summary['exact_semantic_matches']}",
        f"- Semantic subsets: {summary['semantic_subsets']}",
        f"- Probe only: {summary['probe_only']}",
        f"- Unsupported: {summary['unsupported']}",
        f"- Ch2 production-semantic path: {'YES' if data['ch2_mapping']['production_semantic_path'] else 'NO'}",
        f"- Ch4 production-semantic path: {'YES' if data['ch4_mapping']['production_semantic_path'] else 'NO'}",
        f"- READY_FOR_PRODUCTION_E2E_ADAPTER: {'YES' if data['readiness']['ready_for_production_e2e_adapter'] else 'NO'}",
        "",
        "## Production Function Inventory",
        "",
        "| Function | Signature | Source | Req IDs | Conditions | Loops | Memory ops | Arithmetic ops | Classification |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for f in data["production_functions"]:
        lines.append(
            "| `{name}` | `{signature}` | `{source}` | {reqs} | {conditions} | {loops} | {memory} | {arith} | `{cls}` |".format(
                name=f["name"],
                signature=f["signature"],
                source=f["source_file"],
                reqs=", ".join(f["requirement_ids"]),
                conditions="<br>".join(f["conditions"]),
                loops="<br>".join(f["loops"]) if f["loops"] else "None",
                memory="<br>".join(f["memory_operations"]) if f["memory_operations"] else "None",
                arith="<br>".join(f["arithmetic_operations"]) if f["arithmetic_operations"] else "None",
                cls=f["teacher_classification"],
            )
        )
    lines.extend([
        "",
        "## Teacher Kind Comparison",
        "",
        "| Kind | Production-semantic result |",
        "|---|---|",
    ])
    for kind, desc in data["teacher_kinds_confirmed"].items():
        lines.append(f"| `{kind}` | {desc} No exact Smart EV production requirement match found in the analyzed function set. |")
    lines.extend([
        "",
        "## Ch2 Mapping",
        "",
        data["ch2_mapping"]["reason"],
        "",
        "## Ch4 Mapping",
        "",
        f"`compute_charging_rate` classification: `{data['ch4_mapping']['compute_charging_rate']['classification']}`.",
        f"Crash trigger: {data['ch4_mapping']['compute_charging_rate']['crash_trigger']}.",
        "",
        "## SOC Overflow",
        "",
        f"- Bounded condition output: `{data['overflow_analyzer_limitation']['bounded_condition_output']}`",
        f"- Heuristic overflow output: `{data['overflow_analyzer_limitation']['heuristic_overflow_output']}`",
        f"- Classification: `{data['overflow_analyzer_limitation']['classification']}`",
        f"- Reason: {data['overflow_analyzer_limitation']['reason']}",
        "",
        "## Conclusion",
        "",
        f"Fake requirement mappings: `{data['constraints']['fake_requirement_mappings']}`.",
        f"Next action: {data['readiness']['next_action']}",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_banner(data: dict) -> None:
    summary = data["classification_summary"]
    overflow = data["overflow_analyzer_limitation"]
    compute = data["ch4_mapping"]["compute_charging_rate"]
    print("============================================================")
    print(" GD9.4 — PRODUCTION SEMANTIC STATIC/FUZZ MAPPING")
    print("============================================================")
    print(f"Production functions analyzed : {summary['production_functions_analyzed']}")
    print(f"Teacher kinds confirmed       : {summary['teacher_kinds_confirmed']}")
    print()
    print(f"Exact semantic matches        : {summary['exact_semantic_matches']}")
    print(f"Semantic subsets              : {summary['semantic_subsets']}")
    print(f"Probe only                    : {summary['probe_only']}")
    print(f"Unsupported                   : {summary['unsupported']}")
    print()
    print(f"Ch2 production-semantic path  : {'YES' if data['ch2_mapping']['production_semantic_path'] else 'NO'}")
    print(f"Ch4 production-semantic path  : {'YES' if data['ch4_mapping']['production_semantic_path'] else 'NO'}")
    print()
    print("compute_charging_rate:")
    print(f"classification                : {compute['classification']}")
    print(f"crash trigger                 : {compute['crash_trigger']}")
    print()
    print("SOC overflow:")
    print(f"bounded condition respected by Z3      : {'YES' if overflow['bounded_condition_respected_by_z3'] else 'NO'}")
    print(f"bounded condition respected by heuristic: {'YES' if overflow['bounded_condition_respected_by_heuristic'] else 'NO'}")
    print(f"classification                         : {overflow['classification']}")
    print()
    print(f"Fake requirement mappings     : {data['constraints']['fake_requirement_mappings']}")
    print()
    print(f"READY_FOR_PRODUCTION_E2E_ADAPTER: {'YES' if data['readiness']['ready_for_production_e2e_adapter'] else 'NO'}")
    print(f"NEXT_ACTION: {data['readiness']['next_action']}")
    print("============================================================")


def main() -> int:
    report = build_report()
    write_json(OUT_JSON, report)
    write_md(OUT_MD, report)
    print_banner(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
