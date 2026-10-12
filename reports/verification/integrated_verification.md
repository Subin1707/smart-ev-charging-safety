# Integrated Verification Report

Generated at: `2026-09-28T07:30:11.287967+00:00`

## Summary

- Total requirements: 11
- PASS: 11
- FAIL: 0
- INCONCLUSIVE: 0
- Formal verification: 11/11 PASS
- Production verification: 11/11 PASS
- Deadlock: NONE
- Negative control: MUTATION_DETECTED

## Formal Verification

- Source: `SpecVerificationLab.exe`
- Specification: `teacher_specs/smart_ev_formal_verification.json`
- Properties: 11/11 PASS
- Deadlock: NONE

Requirement-level formal status is PASS only when requirement id, violation label, CTL property, and teacher result match.

## Requirement Traceability

| Requirement | Constraints | Violation label | CTL property | Production files | Production functions | Harness | Formal | Production | Evidence | Final |
|---|---|---|---|---|---|---|---|---|---|---|
| `REQ-AUTH-01`<br>Vehicle authentication may succeed only when the vehicle is connected and the token is valid. | `AUTH-01`<br>`AUTH-02` | `req_auth_01_violation` | `AG(!req_auth_01_violation)` | `src/auth/xac_thuc.c`<br>`src/safety/quy_tac_an_toan.c`<br>`src/station/tram_sac.c` | `xac_thuc_xe`<br>`ket_noi_xe_vao_tram`<br>`kiem_tra_sr02_xac_thuc` | `verification/harness/req_auth_01.c` | PASS | PASS | `evidence/production_verification/req_auth_01.json`<br>`evidence/production_verification/production_verification_summary.json`<br>`reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json` | PASS |
| `REQ-AUTH-02`<br>When a vehicle disconnects from the station, authentication must be cleared. | `AUTH-03`<br>`AUTH-04` | `req_auth_02_violation` | `AG(!req_auth_02_violation)` | `src/station/cong_sac.c`<br>`src/station/tram_sac.c` | `ngat_ket_noi_xe_khoi_tram`<br>`ngat_ket_noi_cong` | `verification/harness/req_auth_02.c` | PASS | PASS | `evidence/production_verification/req_auth_02.json`<br>`evidence/production_verification/production_verification_summary.json`<br>`reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json` | PASS |
| `REQ-SOC-01`<br>Vehicle SOC must remain between 0% and 100%. | `BAT-01` | `req_soc_01_violation` | `AG(!req_soc_01_violation)` | `src/safety/quy_tac_an_toan.c`<br>`src/vehicle/pin.c` | `soc_hop_le`<br>`cap_nhat_pin`<br>`kiem_tra_sr06_soc_hop_le` | `verification/harness/req_soc_01.c` | PASS | PASS | `evidence/production_verification/req_soc_01.json`<br>`evidence/production_verification/production_verification_summary.json`<br>`reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json` | PASS |
| `REQ-SOC-02`<br>A vehicle with SOC at 100% must not continue receiving charging power. | `BAT-02` | `req_soc_02_violation` | `AG(!req_soc_02_violation)` | `src/charging/dieu_khien_sac.c`<br>`src/safety/giam_sat_an_toan.c`<br>`src/safety/quy_tac_an_toan.c` | `co_the_bat_dau_sac`<br>`giam_sat_xe_va_cong`<br>`kiem_tra_sr04_pin_day` | `verification/harness/req_soc_02.c` | PASS | PASS | `evidence/production_verification/req_soc_02.json`<br>`evidence/production_verification/production_verification_summary.json`<br>`reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json` | PASS |
| `REQ-TEMP-01`<br>When battery temperature reaches or exceeds 60 C, charging must stop. | `BAT-03` | `req_temp_01_violation` | `AG(!req_temp_01_violation)` | `src/charging/dieu_khien_sac.c`<br>`src/safety/giam_sat_an_toan.c`<br>`src/safety/quy_tac_an_toan.c`<br>`src/vehicle/pin.c` | `co_the_bat_dau_sac`<br>`giam_sat_xe_va_cong`<br>`kiem_tra_sr03_nhiet_do`<br>`pin_qua_nhiet` | `verification/harness/req_temp_01.c` | PASS | PASS | `evidence/production_verification/req_temp_01.json`<br>`evidence/production_verification/production_verification_summary.json`<br>`reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json` | PASS |
| `REQ-PORT-01`<br>A port may enter CHARGING only when a valid vehicle is connected. | `PORT-01` | `req_port_01_violation` | `AG(!req_port_01_violation)` | `src/charging/dieu_khien_sac.c`<br>`src/station/cong_sac.c`<br>`src/station/tram_sac.c` | `ket_noi_xe_vao_cong`<br>`ket_noi_xe_vao_tram`<br>`co_the_bat_dau_sac` | `verification/harness/req_port_01.c` | PASS | PASS | `evidence/production_verification/req_port_01.json`<br>`evidence/production_verification/production_verification_summary.json`<br>`reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json` | PASS |
| `REQ-PORT-02`<br>At any time, one charging port may be linked to at most one vehicle. | `PORT-04`<br>`PORT-05` | `req_port_02_violation` | `AG(!req_port_02_violation)` | `src/safety/quy_tac_an_toan.c`<br>`src/station/cong_sac.c`<br>`src/station/tram_sac.c` | `ket_noi_xe_vao_cong`<br>`ket_noi_xe_vao_tram`<br>`kiem_tra_sr07_doc_quyen_cong` | `verification/harness/req_port_02.c` | PASS | PASS | `evidence/production_verification/req_port_02.json`<br>`evidence/production_verification/production_verification_summary.json`<br>`reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json` | PASS |
| `REQ-PORT-03`<br>A faulted port must not deliver charging power. | `PORT-03` | `req_port_03_violation` | `AG(!req_port_03_violation)` | `src/safety/dung_khan_cap.c`<br>`src/safety/giam_sat_an_toan.c`<br>`src/safety/quy_tac_an_toan.c` | `kich_hoat_dung_khan_cap_cong`<br>`giam_sat_xe_va_cong`<br>`kiem_tra_sr08_ma_loi` | `verification/harness/req_port_03.c` | PASS | PASS | `evidence/production_verification/req_port_03.json`<br>`evidence/production_verification/production_verification_summary.json`<br>`reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json` | PASS |
| `REQ-CHG-01`<br>Charging may start only when the vehicle is connected, authenticated, battery and temperature are safe, the port is ready, and no emergency or fault is active. | `CHG-01`<br>`CHG-02`<br>`CHG-03`<br>`CHG-04`<br>`CHG-05`<br>`CHG-08` | `req_chg_01_violation` | `AG(!req_chg_01_violation)` | `src/charging/dieu_khien_sac.c`<br>`src/safety/giam_sat_an_toan.c` | `co_the_bat_dau_sac`<br>`bat_dau_sac`<br>`giam_sat_xe_va_cong` | `verification/harness/req_chg_01.c` | PASS | PASS | `evidence/production_verification/req_chg_01.json`<br>`evidence/production_verification/production_verification_summary.json`<br>`reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json` | PASS |
| `REQ-CHG-02`<br>Charging requires the complete safety gate to remain valid. | `CHG-08` | `req_chg_02_violation` | `AG(!req_chg_02_violation)` | `src/charging/dieu_khien_sac.c`<br>`src/safety/giam_sat_an_toan.c` | `co_the_bat_dau_sac`<br>`kiem_tra_toan_bo_tram` | `verification/harness/req_chg_02.c` | PASS | PASS | `evidence/production_verification/req_chg_02.json`<br>`evidence/production_verification/production_verification_summary.json`<br>`reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json` | PASS |
| `REQ-EMG-01`<br>Emergency or fault conditions must stop charging and force charging power to zero. | `CHG-06`<br>`CHG-07` | `req_emg_01_violation` | `AG(!req_emg_01_violation)` | `src/safety/dung_khan_cap.c`<br>`src/safety/quy_tac_an_toan.c` | `kich_hoat_dung_khan_cap_cong`<br>`kich_hoat_dung_khan_cap_tram`<br>`kiem_tra_sr05_khan_cap` | `verification/harness/req_emg_01.c` | PASS | PASS | `evidence/production_verification/req_emg_01.json`<br>`evidence/production_verification/production_verification_summary.json`<br>`reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json` | PASS |

## Notes

- `PASS` final status requires formal verification PASS, production verification PASS, and complete evidence.
- `FAIL` is reported if either formal or production verification fails.
- `INCONCLUSIVE` is preserved when mapping or evidence is missing.
- Formal PASS is derived from `formal_adapter_mapping.json` plus `teacher_app_result.json`; it is not copied globally.
