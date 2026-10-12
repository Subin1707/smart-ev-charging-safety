# Smart EV Charging Traceability

This document maps the normalized specification JSON files to production C code and verification evidence.

Pipeline:

```text
Requirement -> JSON constraint -> C source/function -> verification method
```

## Summary

| Requirement | JSON constraints | C implementation | Verification |
|---|---|---|---|
| REQ-AUTH-01 | AUTH-01, AUTH-02 | `src/auth/xac_thuc.c:xac_thuc_xe`, `src/station/tram_sac.c:ket_noi_xe_vao_tram`, `src/safety/quy_tac_an_toan.c:kiem_tra_sr02_xac_thuc` | state generation, `generated/static/verify_auth.c`, `generated/dynamic/test_auth.c`, integration auth flow |
| REQ-AUTH-02 | AUTH-03, AUTH-04 | `src/station/tram_sac.c:ngat_ket_noi_xe_khoi_tram`, `src/station/cong_sac.c:ngat_ket_noi_cong` | auth transition model, generated dynamic auth test |
| REQ-SOC-01 | BAT-01 | `src/vehicle/pin.c:soc_hop_le`, `src/vehicle/pin.c:cap_nhat_pin`, `src/safety/quy_tac_an_toan.c:kiem_tra_sr06_soc_hop_le` | battery partition model, SMT SOC checks, generated battery tests |
| REQ-SOC-02 | BAT-02 | `src/charging/dieu_khien_sac.c:co_the_bat_dau_sac`, `src/safety/giam_sat_an_toan.c:giam_sat_xe_va_cong`, `src/safety/quy_tac_an_toan.c:kiem_tra_sr04_pin_day` | `verify_battery.c`, `test_battery.c`, full-battery E2E/BMC |
| REQ-TEMP-01 | BAT-03 | `src/charging/dieu_khien_sac.c:co_the_bat_dau_sac`, `src/safety/giam_sat_an_toan.c:giam_sat_xe_va_cong`, `src/safety/quy_tac_an_toan.c:kiem_tra_sr03_nhiet_do`, `src/vehicle/pin.c:pin_qua_nhiet` | `verify_battery.c`, overheat E2E/BMC, SMT temperature |
| REQ-PORT-01 | PORT-01 | `src/station/cong_sac.c:ket_noi_xe_vao_cong`, `src/station/tram_sac.c:ket_noi_xe_vao_tram`, `src/charging/dieu_khien_sac.c:co_the_bat_dau_sac` | port state generation, `verify_port.c`, unit/dynamic port tests |
| REQ-PORT-02 | PORT-04, PORT-05 | `src/station/cong_sac.c:ket_noi_xe_vao_cong`, `src/station/tram_sac.c:ket_noi_xe_vao_tram`, `src/safety/quy_tac_an_toan.c:kiem_tra_sr07_doc_quyen_cong` | global exclusivity, SR07 BMC, integration/e2e port tests |
| REQ-PORT-03 | PORT-03 | `src/safety/dung_khan_cap.c:kich_hoat_dung_khan_cap_cong`, `src/safety/giam_sat_an_toan.c:giam_sat_xe_va_cong`, `src/safety/quy_tac_an_toan.c:kiem_tra_sr08_ma_loi` | port state rejection, `verify_port.c`, emergency/fault tests |
| REQ-CHG-01 | CHG-01..CHG-05, CHG-08 | `src/charging/dieu_khien_sac.c:co_the_bat_dau_sac`, `src/charging/dieu_khien_sac.c:bat_dau_sac`, `src/safety/giam_sat_an_toan.c:giam_sat_xe_va_cong` | 128-state charging generation, `verify_charging.c`, `test_charging.c`, integration charging flow |
| REQ-CHG-02 | CHG-08 | `src/charging/dieu_khien_sac.c:co_the_bat_dau_sac`, `src/safety/giam_sat_an_toan.c:kiem_tra_toan_bo_tram` | VALID-derived classification, teacher `charging_teacher.json` model |
| REQ-EMG-01 | CHG-06, CHG-07 | `src/safety/dung_khan_cap.c:kich_hoat_dung_khan_cap_cong`, `src/safety/dung_khan_cap.c:kich_hoat_dung_khan_cap_tram`, `src/safety/quy_tac_an_toan.c:kiem_tra_sr05_khan_cap` | `verify_charging.c`, emergency BMC, integration/e2e emergency tests |

## Artifacts

- Machine-readable traceability: `reports/traceability/spec_traceability.json`
- Source specifications: `specification/auth.json`, `specification/battery.json`, `specification/port.json`, `specification/charging.json`
- Teacher adapter: `tools/convert_to_teacher_spec.py`
- Teacher specs: `teacher_specs/*.json`
- Internal state generator: `generator/state_generator.py`

## Notes

- `CHARGING` is not a 7-bit safety input in `charging.json`; it is the behavior being checked against `VALID`.
- `charging_teacher.json` expands the safety gate into 128 states for the teacher app.
- Global port exclusivity constraints (`PORT-04`, `PORT-05`) are mapped to production connection guards and SR07 BMC/e2e evidence instead of a single-state expression.
