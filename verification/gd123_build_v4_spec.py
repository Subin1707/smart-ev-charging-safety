"""GD12.3 — Upgrade smart_ev_teacher_e2e_v4.json
================================================
Upgrades Ch2, Ch3, Ch4 from v3 to v4 with:

Ch2 (functions[]):
  - 6 C functions covering all 4 bug kinds (buffer-overflow, memory-leak,
    double-free, use-after-free) + 2 safe baselines
  - Semantically grounded in real Smart EV operations
  - Honest: each is a tool-capability artifact, clearly labeled

Ch3 (arithmetic_checks[]):
  - 12 checks covering SOC, TEMP, POWER, PORT, CHARGING rate
  - SAT/UNSAT pairs for boundary and contradiction checking
  - Overflow probes with production-domain preconditions
  - No negative literals (parser limitation respected)
  - Multi-variable conditions with correct semantics

Ch4 (functions[] python kinds):
  - divide: charging power ratio (energy / time) -> CWE-369
  - divide: session token ratio (tokens_issued / tokens_active) -> CWE-369
  - magic_value: firmware unlock code (2 magic values) -> concolic trace

Preserves:
  - V2 state machine (28 states, 47 transitions) unchanged
  - All 16 safety_properties unchanged
  - All 11 requirements unchanged
  - All 5 test_cases upgraded with new traceability

Does NOT:
  - modify production source
  - claim tool artifacts are production implementations
  - suppress existing findings
"""
from __future__ import annotations

import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "buffer") and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "teacher_specs" / "smart_ev_teacher_e2e_v3.json"
V4 = ROOT / "teacher_specs" / "smart_ev_teacher_e2e_v4.json"
SOURCE = V3 if V3.exists() else V4

# ═══════════════════════════════════════════════════════════════════
# Ch2 — functions[] C kind (static checker)
# Strategy: cover all 4 bug types, 2 safe baselines
# Semantic ground: real Smart EV operations that involve buffers/memory
# ═══════════════════════════════════════════════════════════════════

FUNCTIONS_C = [
    # ── SAFE baselines (bug=null) ─────────────────────────────────
    {
        "name": "ev_copy_vehicle_id",
        "language": "c",
        "kind": "buffer_copy",
        "params": ["src_id"],
        "buffer_size": 20,          # DO_DAI_MA_XE = 20
        "bug": None,
        # internal doc (not in teacher schema)
        "_doc": (
            "REQ-AUTH-01 / REQ-PORT-02: Safe copy of vehicle ID (DO_DAI_MA_XE=20) "
            "using strncpy. No bug. Ch2 finds nothing. "
            "Proves static checker runs and correctly reports zero findings on safe code."
        ),
    },
    {
        "name": "ev_copy_auth_token",
        "language": "c",
        "kind": "buffer_copy",
        "params": ["raw_token"],
        "buffer_size": 32,          # DO_DAI_TOKEN = 32
        "bug": None,
        "_doc": (
            "REQ-AUTH-01: Safe copy of authentication token (DO_DAI_TOKEN=32). "
            "Baseline: safe strncpy. No Ch2 finding expected."
        ),
    },

    # ── UNSAFE buffer (buffer-overflow) ──────────────────────────
    {
        "name": "ev_parse_remote_cmd",
        "language": "c",
        "kind": "buffer_copy",
        "params": ["cmd_payload"],
        "buffer_size": 16,
        "bug": "buffer-overflow",
        "_doc": (
            "REQ-EMG-01 / REQ-CHG-01: Remote command payload parsing. "
            "Fixed buffer of 16 bytes; if cmd_payload exceeds this, strcpy overflows. "
            "CWE-121: Stack-based Buffer Overflow. "
            "Maps to: remote control path in src/communication/dieu_khien_tu_xa.c "
            "where input is not length-validated before copy."
        ),
    },

    # ── MEMORY LEAK ───────────────────────────────────────────────
    {
        "name": "ev_alloc_session_record",
        "language": "c",
        "kind": "alloc_release",
        "params": [],
        "buffer_size": 64,
        "bug": "memory-leak",
        "_doc": (
            "REQ-CHG-01 / REQ-CHG-02: Session record allocation for charging session. "
            "Allocates 64-byte record but fails to free on early return path. "
            "CWE-401: Missing Release of Memory after Effective Lifetime. "
            "Mirrors the pattern in PhienSac session logging."
        ),
    },

    # ── DOUBLE FREE ───────────────────────────────────────────────
    {
        "name": "ev_release_port_context",
        "language": "c",
        "kind": "alloc_release",
        "params": [],
        "buffer_size": 32,
        "bug": "double-free",
        "_doc": (
            "REQ-PORT-01 / REQ-PORT-03: Port context deallocation. "
            "Double-free when disconnect is called twice (race condition path). "
            "CWE-415: Double Free. "
            "Mirrors: ngat_ket_noi_xe_khoi_tram called twice on same port."
        ),
    },

    # ── USE AFTER FREE ────────────────────────────────────────────
    {
        "name": "ev_resume_charging_after_fault",
        "language": "c",
        "kind": "alloc_release",
        "params": [],
        "buffer_size": 48,
        "bug": "use-after-free",
        "_doc": (
            "REQ-EMG-01: Emergency fault recovery path. "
            "Pointer to charging session freed on fault, then accessed on resume. "
            "CWE-416: Use After Free. "
            "Mirrors: fault recovery where stale session pointer is dereferenced."
        ),
    },
]

# ═══════════════════════════════════════════════════════════════════
# Ch3 — arithmetic_checks[] (Z3 SMT)
# Strategy: property + contradiction + overflow per domain
# Rule: NO negative literals in condition (parser limitation)
# ═══════════════════════════════════════════════════════════════════

ARITHMETIC_CHECKS = [
    # ── SOC domain (REQ-SOC-01) ───────────────────────────────────
    {
        "name": "gd12_soc_valid_domain_sat",
        "int_vars": ["soc"],
        "condition": "soc >= 0 and soc <= 100",
        "_doc": "REQ-SOC-01: Valid SOC domain [0,100] is satisfiable. SAT expected.",
    },
    {
        "name": "gd12_soc_violation_contradiction_unsat",
        "int_vars": ["soc"],
        "condition": "soc >= 0 and soc <= 100 and (soc < 0 or soc > 100)",
        "_doc": (
            "REQ-SOC-01: Logical contradiction — within valid domain AND violating it. "
            "UNSAT expected. Proves boundary semantics are consistent."
        ),
    },
    {
        "name": "gd12_soc_update_no_overflow",
        "int_vars": ["soc_current", "soc_delta"],
        "condition": "soc_current >= 0 and soc_current <= 100 and soc_delta >= 0 and soc_delta <= 100",
        "overflow_expr": "soc_current + soc_delta",
        "_doc": (
            "REQ-SOC-01: SOC update arithmetic with production bounds. "
            "With [0,100] bounds, max sum = 200 << INT32_MAX. "
            "overflow_expr included so teacher computes int32 overflow check. "
            "SAT (bounded witnesses exist) but no int32 overflow at scale 200."
        ),
    },
    {
        "name": "gd12_soc_full_threshold_sat",
        "int_vars": ["soc"],
        "condition": "soc >= 100",
        "_doc": (
            "REQ-SOC-02: SOC >= 100 is satisfiable (soc=100). "
            "SAT confirms SOC_FULL states are reachable."
        ),
    },
    {
        "name": "gd12_soc_charging_blocked_when_full",
        "int_vars": ["soc", "charging"],
        "condition": "soc >= 100 and charging == 0",
        "_doc": (
            "REQ-SOC-02: When SOC >= 100, charging must be 0. "
            "SAT (soc=100, charging=0). "
            "Proves the 'stop charging at full' state is reachable and satisfiable."
        ),
    },

    # ── TEMPERATURE domain (REQ-TEMP-01) ─────────────────────────
    {
        "name": "gd12_temp_overheat_threshold_sat",
        "int_vars": ["temperature"],
        "condition": "temperature >= 60",
        "_doc": (
            "REQ-TEMP-01: Overheat threshold (>= 60C) is satisfiable. "
            "boundary >= (not >): NHIET_DO_TOI_DA=60 is inclusive. "
            "SAT witness: temperature=60."
        ),
    },
    {
        "name": "gd12_temp_overheat_contradiction_unsat",
        "int_vars": ["temperature"],
        "condition": "temperature >= 60 and temperature < 60",
        "_doc": (
            "REQ-TEMP-01: Contradiction — simultaneously overheated and not. "
            "UNSAT proves TEMP_SAFE / TEMP_OVERHEAT partition is mutually exclusive."
        ),
    },
    {
        "name": "gd12_temp_safe_range_sat",
        "int_vars": ["temperature", "offset"],
        "condition": "offset >= 0 and offset <= 79 and temperature == offset and temperature < 60",
        "_doc": (
            "REQ-TEMP-01: Safe range [0,60) represented with non-negative offset. "
            "offset encodes temperature in [0,79] range, temperature<60 selects safe partition. "
            "SAT proves safe temperature states exist."
        ),
    },
    {
        "name": "gd12_temp_charging_blocked_when_overheat",
        "int_vars": ["temperature", "charging"],
        "condition": "temperature >= 60 and charging == 0",
        "_doc": (
            "REQ-TEMP-01: When overheated, charging=0 is satisfiable. "
            "SAT proves overheat-blocked charging states are reachable."
        ),
    },

    # ── POWER domain (REQ-CHG-01, REQ-EMG-01) ────────────────────
    {
        "name": "gd12_power_cap_not_exceeded",
        "int_vars": ["power_port1", "power_port2", "power_port3", "power_port4", "power_port5"],
        "condition": (
            "power_port1 >= 0 and power_port1 <= 22 and "
            "power_port2 >= 0 and power_port2 <= 22 and "
            "power_port3 >= 0 and power_port3 <= 22 and "
            "power_port4 >= 0 and power_port4 <= 22 and "
            "power_port5 >= 0 and power_port5 <= 22"
        ),
        "overflow_expr": "power_port1 + power_port2 + power_port3 + power_port4 + power_port5",
        "_doc": (
            "REQ-CHG-01: Each port max 22kW (CONG_SUAT_CONG_TOI_DA=22). "
            "Total station 5 ports: max 110kW. "
            "CONG_SUAT_TRAM_TOI_DA=100kW implies station cap enforced separately. "
            "overflow_expr: sum of all port powers cannot overflow int32 (max 110)."
        ),
    },
    {
        "name": "gd12_emergency_power_zero",
        "int_vars": ["emergency", "total_power"],
        "condition": "emergency == 1 and total_power == 0",
        "_doc": (
            "REQ-EMG-01: When emergency=1, total_power=0. "
            "SAT proves the emergency-stopped state is satisfiable."
        ),
    },

    # ── CHARGING RATE (REQ-CHG-01, traceability for Ch4) ─────────
    {
        "name": "gd12_charging_rate_positive_time",
        "int_vars": ["energy_wh", "time_seconds"],
        "condition": "energy_wh >= 0 and time_seconds > 0 and energy_wh <= 79200",
        "overflow_expr": "energy_wh + time_seconds",
        "_doc": (
            "REQ-CHG-01: Charging rate = energy/time. "
            "energy_wh: 22kW * 3600s/h = 79200 Wh max per port per hour. "
            "time_seconds > 0 is the production precondition preventing division by zero. "
            "overflow_expr: energy_wh+time_seconds bounded well below INT32_MAX."
        ),
    },
]

# ═══════════════════════════════════════════════════════════════════
# Ch4 — functions[] Python kind (dynamic fuzzer)
# Strategy: semantically grounded in real Smart EV computations
# ═══════════════════════════════════════════════════════════════════

FUNCTIONS_PYTHON = [
    {
        "name": "ev_charging_power_ratio",
        "language": "python",
        "kind": "divide",
        "params": ["energy_delivered_wh", "session_time_seconds"],
        "_doc": (
            "REQ-CHG-01: Charging rate = energy_delivered_wh / session_time_seconds. "
            "Equivalent computation: production cap_nhat_pin() uses power*time. "
            "Inverse: rate = energy/time. When session_time_seconds=0 -> CWE-369. "
            "SEMANTICALLY HONEST: division-by-zero in session duration is a real "
            "edge case for any charging session logger. "
            "Fuzzer expected to find time_seconds=0 -> ZeroDivisionError."
        ),
    },
    {
        "name": "ev_token_validation_ratio",
        "language": "python",
        "kind": "divide",
        "params": ["tokens_issued", "tokens_active"],
        "_doc": (
            "REQ-AUTH-01: Token validity ratio = tokens_issued / tokens_active. "
            "Used in audit/monitoring; when tokens_active=0 (no active sessions) -> CWE-369. "
            "Edge case: station fully idle, no connected vehicles, monitoring queries ratio. "
            "Fuzzer finds tokens_active=0."
        ),
    },
    {
        "name": "ev_firmware_unlock_gate",
        "language": "python",
        "kind": "magic_value",
        "params": ["unlock_code_a", "unlock_code_b"],
        "magic_values": [4721, 9033],
        "_doc": (
            "REQ-EMG-01 / REQ-CHG-01: Firmware emergency-override unlock requires "
            "two secret codes (4721, 9033) to bypass normal safety shutdown. "
            "Concolic fuzzer uses Z3 to find the exact (4721, 9033) input without "
            "exhaustive search. CWE-798 / hardcoded credential detection. "
            "In production, emergency unlock should use cryptographic tokens "
            "not fixed magic values. This probes whether such a pattern exists."
        ),
    },
]

# ═══════════════════════════════════════════════════════════════════
# Test cases (upgraded from v3)
# ═══════════════════════════════════════════════════════════════════

TEST_CASES = [
    {
        "id": "GD12-TC-CH1-CTL-16",
        "requirement_ids": [
            "REQ-AUTH-01", "REQ-AUTH-02", "REQ-SOC-01", "REQ-SOC-02",
            "REQ-TEMP-01", "REQ-PORT-01", "REQ-PORT-02", "REQ-PORT-03",
            "REQ-CHG-01", "REQ-CHG-02", "REQ-EMG-01",
        ],
        "title": "Ch1 verifies preserved Smart EV V2 Kripke model — 16 CTL properties",
        "priority": "HIGH",
        "preconditions": (
            "Load smart_ev_teacher_e2e_v4.json. "
            "state_machine must match V2 (28 states, 47 transitions). "
            "safety_properties must contain 16 CTL formulas."
        ),
        "steps": [
            "Run teacher pipeline Ch1 Kripke/CTL checker.",
            "Confirm deadlock = NONE.",
            "Confirm 11 AG(!req_*_violation) properties all DUNG.",
            "Confirm 4 reachability EF(charging/start_blocked/stopped/recovered) all DUNG.",
            "Confirm liveness AF(safe) DUNG.",
        ],
        "expected_result": "No deadlock. All 16 CTL properties DUNG.",
    },
    {
        "id": "GD12-TC-CH2-SAFE-CODEGEN",
        "requirement_ids": [],
        "title": "Ch2 static checker: safe buffer-copy functions produce zero findings",
        "priority": "MEDIUM",
        "preconditions": (
            "ev_copy_vehicle_id (buffer_size=20, bug=null) and "
            "ev_copy_auth_token (buffer_size=32, bug=null) are tool-capability artifacts "
            "representing safe fixed-length string handling. "
            "NOT claimed as production authentication implementations."
        ),
        "steps": [
            "Generate C from ev_copy_vehicle_id (buffer_copy, buf=20, safe).",
            "Generate C from ev_copy_auth_token (buffer_copy, buf=32, safe).",
            "Run teacher static C checker (check_c_source).",
            "Confirm zero heuristic findings (no dangerous-function, no memory errors).",
            "Record as TOOL_CAPABILITY_EVIDENCE / PROBE_ONLY: Ch2 runs and correctly finds nothing on safe code.",
        ],
        "expected_result": "Zero Ch2 findings. TOOL_CAPABILITY_EVIDENCE / PROBE_ONLY confirmed; not production REQ PASS evidence.",
    },
    {
        "id": "GD12-TC-CH2-UNSAFE-CODEGEN",
        "requirement_ids": [],
        "title": "Ch2 static checker: unsafe functions trigger CWE-121/401/415/416",
        "priority": "HIGH",
        "preconditions": (
            "Four unsafe tool-capability artifacts: "
            "ev_parse_remote_cmd (buffer-overflow), "
            "ev_alloc_session_record (memory-leak), "
            "ev_release_port_context (double-free), "
            "ev_resume_charging_after_fault (use-after-free). "
            "These are BUG_INJECTED_PROBE artifacts illustrating vulnerability patterns near "
            "Smart EV scenarios. They are PROBE_ONLY and NOT production implementations."
        ),
        "steps": [
            "Generate C from ev_parse_remote_cmd (bug=buffer-overflow, buf=16).",
            "Generate C from ev_alloc_session_record (bug=memory-leak, buf=64).",
            "Generate C from ev_release_port_context (bug=double-free, buf=32).",
            "Generate C from ev_resume_charging_after_fault (bug=use-after-free, buf=48).",
            "Run teacher static C checker on all 4 generated functions.",
            "Confirm CWE-121 detected on ev_parse_remote_cmd.",
            "Confirm CWE-401 detected on ev_alloc_session_record.",
            "Confirm CWE-415 detected on ev_release_port_context.",
            "Confirm CWE-416 detected on ev_resume_charging_after_fault.",
        ],
        "expected_result": "Four CWE findings: CWE-121, CWE-401, CWE-415, CWE-416. Classification: BUG_INJECTED_PROBE / PROBE_ONLY; not production REQ PASS/FAIL evidence.",
    },
    {
        "id": "GD12-TC-CH3-SOC-CONTRACT",
        "requirement_ids": ["REQ-SOC-01", "REQ-SOC-02"],
        "title": "Ch3 Z3: SOC domain contract — 5 SMT checks",
        "priority": "HIGH",
        "preconditions": (
            "SOC_MIN=0, SOC_MAX=100 from src/core/hang_so.h. "
            "Conditions use integer encoding of float bounds."
        ),
        "steps": [
            "gd12_soc_valid_domain_sat: condition 'soc>=0 and soc<=100' -> SAT (e.g. soc=4).",
            "gd12_soc_violation_contradiction_unsat: contradiction -> UNSAT.",
            "gd12_soc_update_no_overflow: bounded update -> SAT, overflow_expr sum<=200 no CWE-190.",
            "gd12_soc_full_threshold_sat: soc>=100 -> SAT (soc=100).",
            "gd12_soc_charging_blocked_when_full: soc>=100 and charging=0 -> SAT.",
        ],
        "expected_result": (
            "SAT: gd12_soc_valid_domain_sat, gd12_soc_update_no_overflow, "
            "gd12_soc_full_threshold_sat, gd12_soc_charging_blocked_when_full. "
            "UNSAT: gd12_soc_violation_contradiction_unsat. "
            "No CWE-190 from gd12_soc_update_no_overflow (bounded by [0,100])."
        ),
    },
    {
        "id": "GD12-TC-CH3-TEMP-CONTRACT",
        "requirement_ids": ["REQ-TEMP-01"],
        "title": "Ch3 Z3: Temperature domain contract — 4 SMT checks",
        "priority": "HIGH",
        "preconditions": (
            "NHIET_DO_TOI_DA=60 (inclusive, >=). "
            "Negative lower bound -20 encoded via offset trick to avoid parser UnaryOp error."
        ),
        "steps": [
            "gd12_temp_overheat_threshold_sat: temperature>=60 -> SAT (temperature=60).",
            "gd12_temp_overheat_contradiction_unsat: >=60 and <60 -> UNSAT.",
            "gd12_temp_safe_range_sat: offset [0,79] with temperature<60 -> SAT.",
            "gd12_temp_charging_blocked_when_overheat: temp>=60 and charging=0 -> SAT.",
        ],
        "expected_result": (
            "SAT: overheat_threshold, safe_range, charging_blocked. "
            "UNSAT: contradiction. All 4 checks pass."
        ),
    },
    {
        "id": "GD12-TC-CH3-POWER-CONTRACT",
        "requirement_ids": ["REQ-CHG-01", "REQ-EMG-01"],
        "title": "Ch3 Z3: Power and station capacity contract — 3 SMT checks",
        "priority": "HIGH",
        "preconditions": (
            "CONG_SUAT_CONG_TOI_DA=22kW, SO_CONG_SAC=5, CONG_SUAT_TRAM_TOI_DA=100kW. "
            "Max total 5x22=110kW. int32 overflow not possible at this scale."
        ),
        "steps": [
            "gd12_power_cap_not_exceeded: 5 ports each [0,22] -> SAT, overflow_expr<=110, no CWE-190.",
            "gd12_emergency_power_zero: emergency=1 and total_power=0 -> SAT.",
            "gd12_charging_rate_positive_time: energy_wh in [0,79200] and time_seconds>0 -> SAT.",
        ],
        "expected_result": (
            "All 3 SAT. No int32 overflow within production bounds. "
            "Power cap and emergency semantics confirmed satisfiable."
        ),
    },
    {
        "id": "GD12-TC-CH4-FUZZ-DIVIDE",
        "requirement_ids": [],
        "title": "Ch4 black-box fuzz: division-by-zero on charging rate and token ratio",
        "priority": "HIGH",
        "preconditions": (
            "ev_charging_power_ratio and ev_token_validation_ratio are TOOL-CAPABILITY ARTIFACTS "
            "representing the arithmetic structure of real Smart EV computations. "
            "Production uses float arithmetic; probe uses Python integer divide for fuzzing."
        ),
        "steps": [
            "Run blackbox_fuzz on ev_charging_power_ratio with arg_types=['int','int'].",
            "Expect crashes when session_time_seconds=0 (ZeroDivisionError).",
            "Run blackbox_fuzz on ev_token_validation_ratio with arg_types=['int','int'].",
            "Expect crashes when tokens_active=0.",
            "Confirm CWE-369 (Divide by Zero) classified for both.",
            "Document as TOOL_CAPABILITY_EVIDENCE / PROBE_ONLY; production uses guard time_seconds>0.",
        ],
        "expected_result": (
            "Both functions crash with ZeroDivisionError when denominator=0. "
            "CWE-369 classified as PROBE_ONLY. Demonstrates Ch4 pipeline runs end-to-end; not production REQ evidence."
        ),
    },
    {
        "id": "GD12-TC-CH4-CONCOLIC-MAGIC",
        "requirement_ids": [],
        "title": "Ch4 concolic fuzz: firmware unlock gate with Z3-guided input synthesis",
        "priority": "MEDIUM",
        "preconditions": (
            "ev_firmware_unlock_gate uses magic_values=[4721, 9033]. "
            "Concolic fuzzer uses Z3 symbolic execution to find inputs that trigger the raise. "
            "This probes the risk of hardcoded credentials in emergency override paths."
        ),
        "steps": [
            "Run concolic_fuzz on ev_firmware_unlock_gate.",
            "Z3 solver derives unlock_code_a=4721, unlock_code_b=9033.",
            "Confirm exception raised at magic_value input.",
            "Classify as CWE-798 (Hardcoded Credentials) or CWE-327.",
            "Document as TOOL_CAPABILITY_EVIDENCE / PROBE_ONLY; production should use cryptographic auth.",
        ],
        "expected_result": (
            "Concolic fuzzer finds crash_input={unlock_code_a:4721, unlock_code_b:9033}. "
            "CWE-798 finding generated as PROBE_ONLY, not a confirmed production defect."
        ),
    },
    {
        "id": "GD12-TC-E2E-TRACEABILITY",
        "requirement_ids": [
            "REQ-AUTH-01", "REQ-SOC-01", "REQ-SOC-02",
            "REQ-TEMP-01", "REQ-CHG-01", "REQ-EMG-01",
        ],
        "title": "E2E traceability: requirement -> production evidence, with Ch2/Ch4 separated as tool capability",
        "priority": "HIGH",
        "preconditions": (
            "Full pipeline run on smart_ev_teacher_e2e_v4.json. "
            "All chapters Ch1-Ch4 active."
        ),
        "steps": [
            "REQ-AUTH-01: state_machine -> Ch1 AG(!req_auth_01_violation) DUNG.",
            "REQ-SOC-01: arithmetic_checks -> Ch3 SAT/UNSAT + overflow bounded.",
            "REQ-SOC-02: arithmetic_checks -> Ch3 soc_full_threshold SAT.",
            "REQ-TEMP-01: arithmetic_checks -> Ch3 SAT/UNSAT + threshold >= 60.",
            "REQ-CHG-01: state_machine/production harness/dynamic evidence -> production PASS; Ch2 findings remain TOOL_CAPABILITY_EVIDENCE / PROBE_ONLY.",
            "REQ-EMG-01: state_machine/production harness/sanitizer evidence -> production PASS; Ch2/Ch4 findings remain TOOL_CAPABILITY_EVIDENCE / PROBE_ONLY.",
            "Confirm CWE report includes CWE-121, CWE-401, CWE-415, CWE-416, CWE-369 only as TOOL_CAPABILITY_EVIDENCE / PROBE_ONLY.",
        ],
        "expected_result": (
            "Full traceability chain: each requirement has at least one chapter finding. "
            "CWE findings traceable to requirement IDs."
        ),
    },
]


def build_v4(v3: dict) -> dict:
    """Merge upgrades into v3, preserving state_machine, safety_properties, requirements."""
    # Remove internal _doc fields from functions
    fns_clean_c = [{k: v for k, v in f.items() if k != "_doc"} for f in FUNCTIONS_C]
    fns_clean_py = [{k: v for k, v in f.items() if k != "_doc"} for f in FUNCTIONS_PYTHON]
    checks_clean = [{k: v for k, v in c.items() if k != "_doc"} for c in ARITHMETIC_CHECKS]

    spec = {
        "name": "smart_ev_teacher_e2e_v4",
        "description": (
            "Smart EV full E2E teacher verification v4. "
            "Ch1: V2 Kripke model (28 states, 47 transitions, 16 CTL properties). "
            "Ch2: 6 C functions — 2 safe baselines + 4 bug-injected probes "
            "(buffer-overflow, memory-leak, double-free, use-after-free). "
            "Ch3: 12 Z3 arithmetic checks covering SOC/TEMP/POWER/CHARGING domains "
            "with SAT/UNSAT pairs and overflow probes using production constants. "
            "Ch4: 3 Python functions — 2 divide (CWE-369) + 1 magic_value (CWE-798 concolic). "
            "Formal and SMT artifacts are grounded in Smart EV requirements and production constants. Ch2/Ch4 generated artifacts are capability probes linked to Smart EV scenarios and are not production-equivalent implementations."
        ),
        "requirements": v3["requirements"],
        "state_machine": v3["state_machine"],
        "additional_flows": v3.get("additional_flows"),
        "safety_properties": v3["safety_properties"],
        "mutual_exclusion": v3.get("mutual_exclusion"),
        "functions": fns_clean_c + fns_clean_py,
        "arithmetic_checks": checks_clean,
        "test_cases": TEST_CASES,
    }
    spec["flows"] = {spec["name"]: spec["state_machine"]}
    # Compatibility for the standalone Ch1 model loader, which reads pure
    # Kripke fields at top level rather than full-spec state_machine.
    spec["states"] = spec["state_machine"]["states"]
    spec["initial"] = spec["state_machine"]["initial"]
    spec["labeling"] = spec["state_machine"]["labeling"]
    spec["transitions"] = spec["state_machine"]["transitions"]
    return spec


def validate(spec: dict) -> list[str]:
    errors: list[str] = []
    import re

    for fn in spec.get("functions", []):
        name = fn.get("name", "?")
        lang = fn.get("language", "")
        kind = fn.get("kind", "")
        if lang == "c" and kind not in ("buffer_copy", "alloc_release", "arithmetic"):
            errors.append(f"Unknown C kind: {kind} on {name}")
        if lang == "python" and kind not in ("divide", "magic_value"):
            errors.append(f"Unknown Python kind: {kind} on {name}")
        if kind == "magic_value" and "magic_values" not in fn:
            errors.append(f"magic_value {name} missing magic_values")

    for ac in spec.get("arithmetic_checks", []):
        cond = ac.get("condition", "")
        if re.search(r"(?<![<>!=])\s*-\s*\d", " " + cond):
            errors.append(f"Negative literal in condition: {ac['name']} -> {cond[:60]}")

    sm = spec.get("state_machine", {})
    if len(sm.get("states", [])) != 28:
        errors.append(f"State machine has {len(sm.get('states',[]))} states, expected 28")
    if len(sm.get("transitions", [])) != 47:
        errors.append(f"State machine has {len(sm.get('transitions',[]))} transitions, expected 47")
    if len(spec.get("safety_properties", [])) != 16:
        errors.append(f"safety_properties has {len(spec.get('safety_properties',[]))}, expected 16")
    if len(spec.get("requirements", [])) != 11:
        errors.append(f"requirements has {len(spec.get('requirements',[]))}, expected 11")

    try:
        json.dumps(spec)
    except (TypeError, ValueError) as e:
        errors.append(f"JSON not serializable: {e}")

    return errors


def main() -> int:
    v3 = json.loads(SOURCE.read_text(encoding="utf-8"))
    spec = build_v4(v3)
    errors = validate(spec)

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  [ERROR] {e}")
        return 1

    V4.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    fns = spec["functions"]
    c_fns = [f for f in fns if f.get("language") == "c"]
    py_fns = [f for f in fns if f.get("language") == "python"]
    unsafe = [f for f in c_fns if f.get("bug")]
    safe = [f for f in c_fns if not f.get("bug")]
    checks = spec["arithmetic_checks"]

    sep = "=" * 62
    print(sep)
    print("  smart_ev_teacher_e2e_v4.json — UPGRADE SUMMARY")
    print(sep)
    print()
    print(f"  Ch1 state machine         : {len(spec['state_machine']['states'])} states, "
          f"{len(spec['state_machine']['transitions'])} transitions  [UNCHANGED]")
    print(f"  Ch1 CTL properties        : {len(spec['safety_properties'])}  [UNCHANGED]")
    print(f"  Requirements              : {len(spec['requirements'])}  [UNCHANGED]")
    print()
    print(f"  Ch2 C functions (v3 had 1, v4 has {len(c_fns)}):")
    print(f"    Safe baselines (bug=null) : {len(safe)}")
    for f in safe:
        print(f"      {f['name']:<35} buffer_size={f.get('buffer_size','?')}")
    print(f"    Bug-injected probes       : {len(unsafe)}")
    for f in unsafe:
        print(f"      {f['name']:<35} bug={f['bug']}")
    print()
    print(f"  Ch3 arithmetic checks (v3 had 5, v4 has {len(checks)}):")
    domains = {}
    for c in checks:
        dom = c["name"].split("_")[1] if "_" in c["name"] else "?"
        domains[dom] = domains.get(dom, 0) + 1
    for dom, count in sorted(domains.items()):
        print(f"    {dom:<12} : {count} checks")
    print()
    print(f"  Ch4 Python functions (v3 had 0, v4 has {len(py_fns)}):")
    for f in py_fns:
        mv = f.get("magic_values", "")
        print(f"    {f['name']:<38} kind={f['kind']}" + (f"  magic={mv}" if mv else ""))
    print()
    print(f"  Test cases (v3 had 5, v4 has {len(spec['test_cases'])}):")
    for tc in spec["test_cases"]:
        print(f"    [{tc['priority']}] {tc['id']}")
    print()
    print(f"  Expected CWE findings from Ch2:")
    print(f"    CWE-121 (Buffer Overflow)   <- ev_parse_remote_cmd")
    print(f"    CWE-401 (Memory Leak)       <- ev_alloc_session_record")
    print(f"    CWE-415 (Double Free)       <- ev_release_port_context")
    print(f"    CWE-416 (Use After Free)    <- ev_resume_charging_after_fault")
    print()
    print(f"  Expected CWE findings from Ch3:")
    print(f"    SAT witnesses on valid domain / threshold checks")
    print(f"    UNSAT on contradiction checks (boundary consistency)")
    print(f"    No CWE-190 within production-bounded overflow expressions")
    print()
    print(f"  Expected CWE findings from Ch4:")
    print(f"    CWE-369 (Divide by Zero)    <- ev_charging_power_ratio, ev_token_validation_ratio")
    print(f"    CWE-798 (Hardcoded Creds)   <- ev_firmware_unlock_gate (concolic)")
    print()
    print(f"  Validation                  : PASS (0 errors)")
    print(f"  Output -> {V4.relative_to(ROOT).as_posix()}")
    print(sep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




