# Coverage Matrix - Phase 2

Purpose: show exactly how each audited requirement is checked from specification constraint to formal property, production code, harness, and evidence.

## Gate Summary

```yaml
Requirements mapped: 11/11
Constraints mapped: 19/19
Formal mapping: 11/11
Production mapping: 11/11
Harness mapping: 11/11
Evidence mapping: 11/11
Unmapped requirements: 0
Orphan violation labels: 0
Reachable violation labels in safe model: 0
Status: PASS
```

## Matrix

| Requirement | Constraints | State variables | Violation predicate | Relevant transitions | Formal property | Production function | Harness | Evidence |
|---|---|---|---|---|---|---|---|---|
| `REQ-AUTH-01` | `AUTH-01`, `AUTH-02` | `connected`, `token_valid`, `authenticated`, `charging` | `authenticated && (!connected || !token_valid)` | `connect -> valid_token -> authenticate_success`; invalid token/auth failure blocks start | `AG(!req_auth_01_violation)` | `xac_thuc_xe()`<br>`ket_noi_xe_vao_tram()`<br>`kiem_tra_sr02_xac_thuc()` | `verification/harness/req_auth_01.c` | `reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json`<br>`evidence/production_verification/req_auth_01.json` |
| `REQ-AUTH-02` | `AUTH-03`, `AUTH-04` | `connected`, `disconnected`, `authenticated`, `disconnect_request` | `disconnected && authenticated` | `disconnect_request -> disconnect_complete`; `vehicle_disconnect -> auth_clear` | `AG(!req_auth_02_violation)` | `ngat_ket_noi_xe_khoi_tram()`<br>`ngat_ket_noi_cong()` | `verification/harness/req_auth_02.c` | `reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json`<br>`evidence/production_verification/req_auth_02.json` |
| `REQ-SOC-01` | `BAT-01` | `soc`, `soc_out_of_range`, `SOC_INVALID`, `SOC_OK`, `SOC_FULL` | `soc_out_of_range` | `sensor_read -> soc_classification`; `soc_update -> clamp_or_reject_invalid` | `AG(!req_soc_01_violation)` | `soc_hop_le()`<br>`cap_nhat_pin()`<br>`kiem_tra_sr06_soc_hop_le()` | `verification/harness/req_soc_01.c` | `reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json`<br>`evidence/production_verification/req_soc_01.json` |
| `REQ-SOC-02` | `BAT-02` | `soc_full`, `charging`, `power_positive`, `stopped` | `soc_full && (charging || power_positive)` | `charging -> soc_full -> stopped`; `monitor_tick -> power_zero` | `AG(!req_soc_02_violation)` | `co_the_bat_dau_sac()`<br>`giam_sat_xe_va_cong()`<br>`kiem_tra_sr04_pin_day()` | `verification/harness/req_soc_02.c` | `reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json`<br>`evidence/production_verification/req_soc_02.json` |
| `REQ-TEMP-01` | `BAT-03` | `temperature`, `temperature_safe`, `overheat`, `charging`, `power_positive` | `overheat && charging` | `charging -> temperature_rise -> overheat -> stopped`; `monitor_tick -> safety_cutoff` | `AG(!req_temp_01_violation)` | `pin_qua_nhiet()`<br>`co_the_bat_dau_sac()`<br>`giam_sat_xe_va_cong()`<br>`kiem_tra_sr03_nhiet_do()` | `verification/harness/req_temp_01.c` | `reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json`<br>`evidence/production_verification/req_temp_01.json` |
| `REQ-PORT-01` | `PORT-01` | `connected`, `port_occupied`, `charging`, `vehicle_id` | `charging && !connected` | `vehicle_connect -> port_occupied`; `port_occupied -> start_charging`; `connection_lost -> blocked/stopped` | `AG(!req_port_01_violation)` | `ket_noi_xe_vao_cong()`<br>`ket_noi_xe_vao_tram()`<br>`co_the_bat_dau_sac()` | `verification/harness/req_port_01.c` | `reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json`<br>`evidence/production_verification/req_port_01.json` |
| `REQ-PORT-02` | `PORT-04`, `PORT-05` | `occupied`, `vehicle_id`, `assigned_port`, `port_multi_vehicle` | `port_multi_vehicle` | `vehicle_connect -> assigned_port`; `second_vehicle_attempt -> reject`; `repeated_connect -> reject` | `AG(!req_port_02_violation)` | `ket_noi_xe_vao_cong()`<br>`ket_noi_xe_vao_tram()`<br>`kiem_tra_sr07_doc_quyen_cong()` | `verification/harness/req_port_02.c` | `reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json`<br>`evidence/production_verification/req_port_02.json` |
| `REQ-PORT-03` | `PORT-03` | `fault`, `charging`, `power_positive`, `power_zero` | `fault && (charging || power_positive)` | `charging -> fault_detected -> stopped`; `fault_detected -> power_zero` | `AG(!req_port_03_violation)` | `kich_hoat_dung_khan_cap_cong()`<br>`giam_sat_xe_va_cong()`<br>`kiem_tra_sr08_ma_loi()` | `verification/harness/req_port_03.c` | `reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json`<br>`evidence/production_verification/req_port_03.json` |
| `REQ-CHG-01` | `CHG-01`, `CHG-02`, `CHG-03`, `CHG-04`, `CHG-05`, `CHG-08` | `connected`, `authenticated`, `battery_safe`, `temperature_safe`, `port_ready`, `emergency`, `fault`, `safety_gate_valid`, `charging` | `charging && !safety_gate_valid` | `safety_conditions_satisfied -> start_charging`; unsafe input -> `start_blocked` | `AG(!req_chg_01_violation)` | `co_the_bat_dau_sac()`<br>`bat_dau_sac()`<br>`giam_sat_xe_va_cong()` | `verification/harness/req_chg_01.c` | `reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json`<br>`evidence/production_verification/req_chg_01.json` |
| `REQ-CHG-02` | `CHG-08` | `charging`, `safety_gate_valid`, `connected`, `authenticated`, `battery_safe`, `temperature_safe`, `port_ready`, `emergency`, `fault` | `charging && !safety_gate_valid` | `charging -> condition_lost -> stopped/blocked`; `monitor_tick -> stop_if_invalid` | `AG(!req_chg_02_violation)` | `co_the_bat_dau_sac()`<br>`kiem_tra_toan_bo_tram()` | `verification/harness/req_chg_02.c` | `reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json`<br>`evidence/production_verification/req_chg_02.json` |
| `REQ-EMG-01` | `CHG-06`, `CHG-07` | `emergency`, `fault`, `charging`, `power_positive`, `power_zero` | `(emergency || fault) && (charging || power_positive)` | `charging -> emergency_triggered -> stopped`; `charging -> fault_detected -> stopped`; `emergency_stop -> power_zero` | `AG(!req_emg_01_violation)` | `kich_hoat_dung_khan_cap_cong()`<br>`kich_hoat_dung_khan_cap_tram()`<br>`kiem_tra_sr05_khan_cap()` | `verification/harness/req_emg_01.c` | `reports/verification/formal_adapter_mapping.json`<br>`evidence/formal_verification/teacher_app_result.json`<br>`evidence/production_verification/req_emg_01.json` |

## Constraint Coverage

| Constraint group | Constraints | Requirements |
|---|---|---|
| AUTH | `AUTH-01`, `AUTH-02` | `REQ-AUTH-01` |
| AUTH | `AUTH-03`, `AUTH-04` | `REQ-AUTH-02` |
| BATTERY / SOC | `BAT-01` | `REQ-SOC-01` |
| BATTERY / SOC | `BAT-02` | `REQ-SOC-02` |
| TEMPERATURE | `BAT-03` | `REQ-TEMP-01` |
| PORT | `PORT-01` | `REQ-PORT-01` |
| PORT | `PORT-04`, `PORT-05` | `REQ-PORT-02` |
| PORT | `PORT-03` | `REQ-PORT-03` |
| CHARGING | `CHG-01`, `CHG-02`, `CHG-03`, `CHG-04`, `CHG-05`, `CHG-08` | `REQ-CHG-01` |
| CHARGING | `CHG-08` | `REQ-CHG-02` |
| EMERGENCY | `CHG-06`, `CHG-07` | `REQ-EMG-01` |

## Violation Label Coverage

| Requirement | Violation label | Formal property | Witness exists | Reachable in safe model |
|---|---|---|---|---|
| `REQ-AUTH-01` | `req_auth_01_violation` | `AG(!req_auth_01_violation)` | YES | NO |
| `REQ-AUTH-02` | `req_auth_02_violation` | `AG(!req_auth_02_violation)` | YES | NO |
| `REQ-SOC-01` | `req_soc_01_violation` | `AG(!req_soc_01_violation)` | YES | NO |
| `REQ-SOC-02` | `req_soc_02_violation` | `AG(!req_soc_02_violation)` | YES | NO |
| `REQ-TEMP-01` | `req_temp_01_violation` | `AG(!req_temp_01_violation)` | YES | NO |
| `REQ-PORT-01` | `req_port_01_violation` | `AG(!req_port_01_violation)` | YES | NO |
| `REQ-PORT-02` | `req_port_02_violation` | `AG(!req_port_02_violation)` | YES | NO |
| `REQ-PORT-03` | `req_port_03_violation` | `AG(!req_port_03_violation)` | YES | NO |
| `REQ-CHG-01` | `req_chg_01_violation` | `AG(!req_chg_01_violation)` | YES | NO |
| `REQ-CHG-02` | `req_chg_02_violation` | `AG(!req_chg_02_violation)` | YES | NO |
| `REQ-EMG-01` | `req_emg_01_violation` | `AG(!req_emg_01_violation)` | YES | NO |

## Phase 2 Gate

```yaml
Requirements mapped: 11/11
Constraints mapped: 100%
Formal mapping: 11/11
Production mapping: 11/11
Unmapped requirements: 0
Orphan violation labels: 0
Status: PASS
```
