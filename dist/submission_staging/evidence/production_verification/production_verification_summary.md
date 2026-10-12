# Production Verification Evidence

Generated : 2026-09-29T08:46:32.676990+00:00
Total     : 11
Pass      : 11
Fail      : 0

## Requirement Results

| Requirement | Constraint | Production Functions | Compile | Run | Status |
|---|---|---|---|---|---|
| REQ-AUTH-01 | `A -> (C && T)  [authenticated implies connected and tok` | `xac_thuc_xe, ket_noi_xe_vao_tram, kiem_tra_token_hop_le` | PASS | PASS | **PASS** |
| REQ-AUTH-02 | `!C -> !A  [disconnect clears authentication]` | `ngat_ket_noi_xe_khoi_tram` | PASS | PASS | **PASS** |
| REQ-CHG-01 | `CHARGING -> C && A && B && T && P && !E && !F` | `co_the_bat_dau_sac, bat_dau_sac` | PASS | PASS | **PASS** |
| REQ-CHG-02 | `VALID = C && A && B && T && P && !E && !F` | `co_the_bat_dau_sac` | PASS | PASS | **PASS** |
| REQ-EMG-01 | `E -> power == 0  [emergency forces all ports to zero po` | `kich_hoat_dung_khan_cap_tram` | PASS | PASS | **PASS** |
| REQ-PORT-01 | `P -> C  [port charging implies vehicle connected]` | `ket_noi_xe_vao_tram, bat_dau_sac` | PASS | PASS | **PASS** |
| REQ-PORT-02 | `exclusive(port.vehicle_id)  [one vehicle per port]` | `ket_noi_xe_vao_tram` | PASS | PASS | **PASS** |
| REQ-PORT-03 | `F -> power == 0  [fault port delivers no power]` | `giam_sat_xe_va_cong` | PASS | PASS | **PASS** |
| REQ-SOC-01 | `0 <= SOC <= 100  [SOC must remain in valid range]` | `khoi_tao_pin, cap_nhat_pin` | PASS | PASS | **PASS** |
| REQ-SOC-02 | `SOC_FULL -> power == 0  [full battery stops charging]` | `co_the_bat_dau_sac, bat_dau_sac, giam_sat_xe_va_cong, pin_da_day` | PASS | PASS | **PASS** |
| REQ-TEMP-01 | `TEMP >= 60C -> !CHARGING  [overheat stops charging]` | `pin_qua_nhiet, co_the_bat_dau_sac, bat_dau_sac, giam_sat_xe_va_cong` | PASS | PASS | **PASS** |

## Negative Control Mutation Test

- Description  : Intentionally broken harness: asserts that 60C < 999C (mutant threshold) implies charging_allowed == 0. Since 60 < 999 is true, result=1, so assert(result==0) FAILS -> proves test infrastructure detects defects.
- Mutant threshold : 999.0C  (real = 60.0C)
- Compile      : PASS
- Run          : FAIL
- Conclusion   : **MUTATION_DETECTED**

> MUTATION_DETECTED = harness correctly caught the introduced defect. This proves harnesses are not trivially always-PASS.
