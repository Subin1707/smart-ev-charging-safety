# GD12.1 Teacher CodeGen Deep Capability

Generated: `2026-09-30T09:27:52.272467+00:00`

This report distinguishes teacher-document instructions from the user request. It inspects schema/resources and preserves limitations; it does not modify `SpecVerificationLab.exe` or production C.

## Summary

```yaml
spec_files_scanned: 30
functions_observed: 39
languages_observed: c, python
C function kinds confirmed: 3
Python function kinds confirmed: 2
Ch2-capable kinds: 3
Ch3-AST-capable kinds: 3
Ch3-SMT pathway: functions[c/arithmetic] AST plus arithmetic_checks[] direct Z3
Ch4-fuzz-capable kinds: 2
Fuzz custom domain: UNKNOWN
Fuzz semantic oracle: NO
Cross-implementation oracle: NO
```

## Capability Matrix

| Language | Kind | Ch2 | Ch3 AST | Ch3 SMT | Ch4 | Runtime status | Smart EV candidate |
|---|---|---:|---:|---:|---:|---|---|
| `c` | `alloc_release` | True | True | False | False | DOCUMENTED_AND_OBSERVED | None; memory-probe only. |
| `c` | `arithmetic` | True | True | True | False | RUNTIME_CONFIRMED_BY_EXISTING_EVIDENCE | REQ-SOC-01 / REQ-TEMP-01 as PROBE_ONLY; semantic mismatch already confirmed. |
| `c` | `buffer_copy` | True | True | False | False | DOCUMENTED_AND_OBSERVED | REQ-AUTH-01 as PROBE_ONLY token-buffer handling, not authentication semantics. |
| `python` | `divide` | False | False | False | True | DOCUMENTED_AND_OBSERVED | compute_charging_rate probe only; not a production function. |
| `python` | `magic_value` | False | False | False | True | DOCUMENTED_AND_OBSERVED | Auth token PROBE_ONLY if modeled as magic constants, not real xac_thuc_xe. |
| `spec` | `arithmetic_checks` | False | False | True | False | DOCUMENTED_AND_OBSERVED | REQ-SOC-01 and REQ-TEMP-01 directly; limited adapter support for simple power/fault implications. |

## Expression Feature Analysis

| Feature | functions[] | arithmetic_checks[] / other path |
|---|---|---|
| comparisons | NO for functions[] generated behavior except equality inside python magic_value templates. | YES for integer condition expressions. |
| ranges | NO; c/arithmetic returns addition and does not implement range predicates. | YES; e.g. soc >= 0 and soc <= 100. |
| boolean_conjunction | NO arbitrary conjunction generation. | YES for simple integer conditions with and/or. |
| boolean_negation | NO arbitrary negated predicate generation. | PARTIAL via != and inverted comparisons; no evidence for general not(). |
| state_guards | NO for functions[]; YES in Ch1 state_machine labels/transitions. | NO state machine semantics. |
| return_values | FIXED by template: void C memory functions, int addition, Python division/magic exception. | NO evidence. |
| branch_behavior | Only magic_value has fixed nested equality branches. | NO evidence. |
| parameter_preconditions | NO custom preconditions. | YES as constraints inside condition. |

## Ch4 Oracle Capability

| Capability | Status |
|---|---|
| crash_only_detection | YES |
| expected_return_values | NO |
| assertions | NO evidence |
| property_predicates | NO evidence |
| custom_input_domains | UNKNOWN |
| boundary_seeds | UNKNOWN |
| cross_implementation_comparison | NO |
| summary | Ch4 targets generated Python divide/magic_value functions and reports crashes/path discovery. Existing evidence does not show semantic oracle support. |

## Production Constants

Constants are extracted from `src/core/hang_so.h` so V3 can avoid hard-coding verification thresholds in multiple places.

```json
{
  "SO_XE_TOI_DA": 7.0,
  "SO_CONG_SAC": 5.0,
  "SOC_MIN": 0.0,
  "SOC_MAX": 100.0,
  "NHIET_DO_TOI_DA": 60.0,
  "NHIET_DO_TOI_THIEU": -20.0,
  "CONG_SUAT_TRAM_TOI_DA": 100.0,
  "CONG_SUAT_CONG_TOI_DA": 22.0,
  "DO_DAI_MA_XE": 20.0,
  "DO_DAI_TOKEN": 32.0,
  "SO_TICK_TOI_DA": 100.0
}
```
