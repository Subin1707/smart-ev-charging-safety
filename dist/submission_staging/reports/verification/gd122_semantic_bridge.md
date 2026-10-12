# GD12.2 Smart EV Semantic Bridge

Generated: `2026-09-30T09:48:04.949559+00:00`

This bridge does not claim teacher-generated code is production code. Ch2/Ch4 artifacts are capability/probe artifacts only.

## Summary

```yaml
Requirements: 11
Semantic contracts: 2
Production constants extracted: 11
Teacher Ch1 properties: 16
Teacher Ch2 artifacts: 1
Teacher Ch3 semantic checks: 5
Teacher Ch4 probes: 0
Teacher Ch4 disabled probes: 1
Exact mappings: 0
Semantic subsets: 2
Probe-only artifacts: 1
SOC contract: PASS
TEMP contract: PASS
Spec drift: NONE
Production oracle cases: 14
Production oracle mismatches: 0
Fake mappings: 0
READY_FOR_TEACHER_RUNTIME: YES
```

## Traceability

| Requirement | Formal CTL | Semantic Contract | Teacher Ch2 | Teacher Ch3 | Teacher Ch4 | Production Function | Production Dynamic | Relation | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| `REQ-SOC-01` | `AG(!req_soc_01_violation)` | `{"valid": "0 <= soc <= 100", "invalid": "soc < 0 or soc > 100"}` | TOOL_CAPABILITY_ARTIFACT | gd122_req_soc_01_valid_domain, gd122_req_soc_01_contradictory_violation | DISABLED_BY_GD12_2 | `soc_hop_le` | PASS | SEMANTIC_SUBSET | reports/verification/gd122_semantic_contracts.json<br>teacher_specs/smart_ev_teacher_e2e_v3.json<br>evidence/semantic_bridge/gd122_oracle_results.csv |
| `REQ-TEMP-01` | `AG(!req_temp_01_violation)` | `{"safe": "-20 <= temperature < 60", "overheat": "temperature >= 60"}` | NONE | gd122_req_temp_01_overheat_threshold, gd122_req_temp_01_contradictory_condition, gd122_req_temp_01_safe_range | DISABLED_BY_GD12_2 | `pin_qua_nhiet` | PASS | SEMANTIC_SUBSET | reports/verification/gd122_semantic_contracts.json<br>teacher_specs/smart_ev_teacher_e2e_v3.json<br>evidence/semantic_bridge/gd122_oracle_results.csv |

## Production Oracle Cases

| Requirement | Input | Expected | Production actual | Match |
|---|---:|---:|---:|---|
| `REQ-SOC-01` | -1.0 | 0 | 0 | True |
| `REQ-SOC-01` | 0.0 | 1 | 1 | True |
| `REQ-SOC-01` | 1.0 | 1 | 1 | True |
| `REQ-SOC-01` | 50.0 | 1 | 1 | True |
| `REQ-SOC-01` | 99.0 | 1 | 1 | True |
| `REQ-SOC-01` | 100.0 | 1 | 1 | True |
| `REQ-SOC-01` | 101.0 | 0 | 0 | True |
| `REQ-TEMP-01` | -21.0 | 0 | 0 | True |
| `REQ-TEMP-01` | -20.0 | 0 | 0 | True |
| `REQ-TEMP-01` | -19.0 | 0 | 0 | True |
| `REQ-TEMP-01` | 59.0 | 0 | 0 | True |
| `REQ-TEMP-01` | 60.0 | 1 | 1 | True |
| `REQ-TEMP-01` | 61.0 | 1 | 1 | True |
| `REQ-TEMP-01` | 80.0 | 1 | 1 | True |
