# GĐ10 Final Requirement Matrix

Negative controls are confidence evidence and are not counted as ordinary
requirement pass tests.

## Status Matrix

| Requirement | Formal CTL | Boundary | SMT | Prod Harness | Static | Dynamic | Sanitizer | Neg Ctrl | Trace | Final |
|---|---|---|---|---|---|---|---|---|---|---|
| REQ-AUTH-01 | PASS | NOT_APPLICABLE | NOT_APPLICABLE | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| REQ-AUTH-02 | PASS | NOT_APPLICABLE | NOT_APPLICABLE | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| REQ-SOC-01 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| REQ-SOC-02 | PASS | PASS | NOT_APPLICABLE | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| REQ-TEMP-01 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| REQ-PORT-01 | PASS | NOT_APPLICABLE | NOT_APPLICABLE | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| REQ-PORT-02 | PASS | NOT_APPLICABLE | NOT_APPLICABLE | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| REQ-PORT-03 | PASS | NOT_APPLICABLE | NOT_APPLICABLE | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| REQ-CHG-01 | PASS | NOT_APPLICABLE | NOT_APPLICABLE | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| REQ-CHG-02 | PASS | NOT_APPLICABLE | NOT_APPLICABLE | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| REQ-EMG-01 | PASS | NOT_APPLICABLE | NOT_APPLICABLE | PASS | PASS | PASS | PASS | PASS | PASS | PASS |

## Human-Readable Evidence Map

| Requirement | Constraint | CTL property | Production function(s) | Dynamic/production test | Primary evidence |
|---|---|---|---|---|---|
| REQ-AUTH-01 | AUTH-01, AUTH-02 | `AG(!req_auth_01_violation)` | `xac_thuc_xe`, `ket_noi_xe_vao_tram`, `kiem_tra_sr02_xac_thuc` | `verification/harness/req_auth_01.c` | `evidence/production_verification/req_auth_01.json`, `reports/verification/formal_adapter_mapping.json`, `evidence/formal_verification/teacher_app_result.json` |
| REQ-AUTH-02 | AUTH-03, AUTH-04 | `AG(!req_auth_02_violation)` | `ngat_ket_noi_xe_khoi_tram`, `ngat_ket_noi_cong` | `verification/harness/req_auth_02.c` | `evidence/production_verification/req_auth_02.json`, `reports/verification/formal_adapter_mapping.json`, `evidence/formal_verification/teacher_app_result.json` |
| REQ-SOC-01 | BAT-01 | `AG(!req_soc_01_violation)` | `soc_hop_le`, `cap_nhat_pin`, `kiem_tra_sr06_soc_hop_le` | `verification/harness/req_soc_01.c` | `evidence/production_verification/req_soc_01.json`, `reports/verification/smt_traceability.json`, `reports/verification/boundary_coverage.json` |
| REQ-SOC-02 | BAT-02 | `AG(!req_soc_02_violation)` | `co_the_bat_dau_sac`, `giam_sat_xe_va_cong`, `kiem_tra_sr04_pin_day` | `verification/harness/req_soc_02.c` | `evidence/production_verification/req_soc_02.json`, `reports/verification/boundary_coverage.json`, `reports/verification/production_dynamic_verification.json` |
| REQ-TEMP-01 | BAT-03 | `AG(!req_temp_01_violation)` | `co_the_bat_dau_sac`, `giam_sat_xe_va_cong`, `kiem_tra_sr03_nhiet_do`, `pin_qua_nhiet` | `verification/harness/req_temp_01.c` | `evidence/production_verification/req_temp_01.json`, `reports/verification/smt_traceability.json`, `reports/verification/boundary_coverage.json` |
| REQ-PORT-01 | PORT-01 | `AG(!req_port_01_violation)` | `ket_noi_xe_vao_cong`, `ket_noi_xe_vao_tram`, `co_the_bat_dau_sac` | `verification/harness/req_port_01.c` | `evidence/production_verification/req_port_01.json`, `reports/verification/formal_adapter_mapping.json`, `reports/verification/production_dynamic_verification.json` |
| REQ-PORT-02 | PORT-04, PORT-05 | `AG(!req_port_02_violation)` | `ket_noi_xe_vao_cong`, `ket_noi_xe_vao_tram`, `kiem_tra_sr07_doc_quyen_cong` | `verification/harness/req_port_02.c` | `evidence/production_verification/req_port_02.json`, `reports/verification/negative_control_selectivity.json`, `reports/verification/production_dynamic_verification.json` |
| REQ-PORT-03 | PORT-03 | `AG(!req_port_03_violation)` | `kich_hoat_dung_khan_cap_cong`, `giam_sat_xe_va_cong`, `kiem_tra_sr08_ma_loi` | `verification/harness/req_port_03.c` | `evidence/production_verification/req_port_03.json`, `reports/verification/formal_adapter_mapping.json`, `reports/verification/gd96_security_sanitizer.json` |
| REQ-CHG-01 | CHG-01..CHG-05, CHG-08 | `AG(!req_chg_01_violation)` | `co_the_bat_dau_sac`, `bat_dau_sac`, `giam_sat_xe_va_cong` | `verification/harness/req_chg_01.c`; 128 boolean combinations | `evidence/production_verification/req_chg_01.json`, `reports/verification/production_dynamic_verification.json`, `reports/verification/full_state_model_v2.json` |
| REQ-CHG-02 | CHG-08 | `AG(!req_chg_02_violation)` | `co_the_bat_dau_sac`, `kiem_tra_toan_bo_tram` | `verification/harness/req_chg_02.c`; station monitor path | `evidence/production_verification/req_chg_02.json`, `reports/verification/transition_sequence_coverage.json`, `reports/verification/production_dynamic_verification.json` |
| REQ-EMG-01 | CHG-06, CHG-07 | `AG(!req_emg_01_violation)` | `kich_hoat_dung_khan_cap_cong`, `kich_hoat_dung_khan_cap_tram`, `kiem_tra_sr05_khan_cap` | `verification/harness/req_emg_01.c` | `evidence/production_verification/req_emg_01.json`, `reports/verification/negative_control_selectivity.json`, `reports/verification/gd96_security_sanitizer.json` |

Shared evidence used across all requirements:

- `reports/traceability/spec_traceability.json`
- `reports/verification/final_requirement_matrix.json`
- `reports/verification/final_evidence_manifest.json`
- `evidence/production_verification/production_verification_summary.json`
- `reports/verification/gd96_security_sanitizer.json`
