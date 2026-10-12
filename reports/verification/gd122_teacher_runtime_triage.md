# GD12.2 Teacher Runtime Triage

This report explains the raw `smart_ev_teacher_e2e_v3` teacher-pipeline output. It separates teacher tool capability from Smart EV production evidence.

## Chapter Triage

| Chapter | Raw Observation | Analysis | Production relevance | Status | Evidence |
|---|---|---|---|---|---|
| Ch1 | No deadlock; 16 CTL properties evaluate true. | This is direct Smart EV formal evidence because the V3 state_machine and safety_properties are preserved from V2. | HIGH | PASS | teacher_specs/smart_ev_teacher_e2e_v3.json<br>reports/verification/formal_property_suite_v2.json |
| Ch2 | Static checker reports no heuristic memory finding on gd122_teacher_token_copy_probe. | This only proves the teacher pipeline can generate and statically scan a safe C artifact. It is not xac_thuc_xe and is not production evidence. | TOOL_CAPABILITY_ONLY | EXPECTED_NO_FINDING | reports/verification/gd122_semantic_contracts.json |
| Ch3-AST | AST/complexity is extracted for gd122_teacher_token_copy_probe. | The AST result is structural evidence for generated C only; it does not validate Smart EV production semantics. | TOOL_CAPABILITY_ONLY | INFORMATIONAL | teacher_specs/smart_ev_teacher_e2e_v3.json |
| Ch3-Z3 | SOC/TEMP arithmetic_checks produce SAT/UNSAT results. | This is the meaningful teacher-production bridge: checks are generated from production constants and mapped to REQ-SOC-01 and REQ-TEMP-01 semantic contracts. | SEMANTIC_SUBSET | PASS | reports/verification/gd122_semantic_contracts.json<br>reports/verification/gd122_semantic_bridge.json<br>evidence/semantic_bridge/gd122_oracle_results.csv |
| Ch4 | No dynamic fuzz target is present in the runtime spec. | This is intentional. GD12.1 found no semantic oracle or cross-implementation oracle in teacher Ch4; including python/divide creates non-production crash findings. | DISABLED_BY_DESIGN | NOT_APPLICABLE | reports/verification/gd121_teacher_codegen_capabilities.json<br>reports/verification/gd122_semantic_contracts.json |
| CWE/CVE | No finding to classify. | Expected after disabling Ch4 crash probes and using safe Ch2 artifact. CWE/CVE absence here does not replace production security/sanitizer evidence. | EXPECTED_EMPTY | EXPECTED_NO_FINDING | reports/verification/gd96_security_sanitizer.json<br>reports/verification/gd122_semantic_bridge.json |
| Test cases | 5 documentation test cases are declared in the V3 spec. | Test cases document how Ch1, Ch2, Ch3, Ch4-disabled and production-oracle evidence should be interpreted. | TRACEABILITY_DOCUMENTATION | DOCUMENTED | teacher_specs/smart_ev_teacher_e2e_v3.json |

## Ch3 Expected SAT/UNSAT

| Check | Contract | Expected |
|---|---|---|
| `gd122_req_soc_01_valid_domain` | `REQ-SOC-01` | `SAT` |
| `gd122_req_soc_01_contradictory_violation` | `REQ-SOC-01` | `UNSAT` |
| `gd122_req_temp_01_overheat_threshold` | `REQ-TEMP-01` | `SAT` |
| `gd122_req_temp_01_contradictory_condition` | `REQ-TEMP-01` | `UNSAT` |
| `gd122_req_temp_01_safe_range` | `REQ-TEMP-01` | `SAT` |

## Production Oracle

- Cases: 14
- Mismatches: 0

The oracle calls real production functions `soc_hop_le` and `pin_qua_nhiet`; it does not compare unsupported teacher-generated arithmetic code as production.
