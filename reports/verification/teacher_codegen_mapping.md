# Teacher CodeGen Mapping - Phase 7.5-B

Generated: `2026-09-28T15:16:14.389747+00:00`

This report maps Smart EV requirements to the teacher app Ch2 `functions[]` schema without fabricating unrelated code-generation functions.

## Summary

```yaml
Requirements: 11
Directly supported: 0
Partially supported: 0
Experimental: 2
Unsupported: 9
Teacher codegen semantic coverage: 0.00
Fake mappings: 0
Semantic mismatches: 0
READY_FOR_TEACHER_CODEGEN: NO
```

## Status Separation

```yaml
SMART_EV_SPEC_STATUS: PASS
TEACHER_CODEGEN_COMPATIBILITY: NO_DIRECT_SEMANTIC_MAPPING
```

## Mapping Matrix

| Requirement | Domain | Production functions | Support | Teacher kind | Semantic match | Reason |
|---|---|---|---|---|---|---|
| `REQ-AUTH-01` | AUTH | `xac_thuc_xe()`<br>`ket_noi_xe_vao_tram()`<br>`kiem_tra_sr02_xac_thuc()` | `UNSUPPORTED` | `None` | NO_VALID_KIND | Confirmed teacher Ch2 generator kinds are template-based buffer/memory/Python fuzz generators and do not semantically express this Smart EV boolean/state-transition safety requirement. |
| `REQ-AUTH-02` | AUTH | `ngat_ket_noi_xe_khoi_tram()`<br>`ngat_ket_noi_cong()` | `UNSUPPORTED` | `None` | NO_VALID_KIND | Confirmed teacher Ch2 generator kinds are template-based buffer/memory/Python fuzz generators and do not semantically express this Smart EV boolean/state-transition safety requirement. |
| `REQ-SOC-01` | SOC | `soc_hop_le()`<br>`cap_nhat_pin()`<br>`kiem_tra_sr06_soc_hop_le()` | `EXPERIMENTAL` | `c/arithmetic` | PARTIAL | SOC range checking is numeric, but documented C arithmetic only generates simple arithmetic functions and is not runtime-confirmed. |
| `REQ-SOC-02` | SOC | `co_the_bat_dau_sac()`<br>`giam_sat_xe_va_cong()`<br>`kiem_tra_sr04_pin_day()` | `UNSUPPORTED` | `None` | NO_VALID_KIND | Confirmed teacher Ch2 generator kinds are template-based buffer/memory/Python fuzz generators and do not semantically express this Smart EV boolean/state-transition safety requirement. |
| `REQ-TEMP-01` | TEMP | `co_the_bat_dau_sac()`<br>`giam_sat_xe_va_cong()`<br>`kiem_tra_sr03_nhiet_do()`<br>`pin_qua_nhiet()` | `EXPERIMENTAL` | `c/arithmetic` | PARTIAL | Temperature threshold checking is numeric, but documented C arithmetic does not prove support for threshold predicates and is not runtime-confirmed. |
| `REQ-PORT-01` | PORT | `ket_noi_xe_vao_cong()`<br>`ket_noi_xe_vao_tram()`<br>`co_the_bat_dau_sac()` | `UNSUPPORTED` | `None` | NO_VALID_KIND | Confirmed teacher Ch2 generator kinds are template-based buffer/memory/Python fuzz generators and do not semantically express this Smart EV boolean/state-transition safety requirement. |
| `REQ-PORT-02` | PORT | `ket_noi_xe_vao_cong()`<br>`ket_noi_xe_vao_tram()`<br>`kiem_tra_sr07_doc_quyen_cong()` | `UNSUPPORTED` | `None` | NO_VALID_KIND | Confirmed teacher Ch2 generator kinds are template-based buffer/memory/Python fuzz generators and do not semantically express this Smart EV boolean/state-transition safety requirement. |
| `REQ-PORT-03` | PORT | `kich_hoat_dung_khan_cap_cong()`<br>`giam_sat_xe_va_cong()`<br>`kiem_tra_sr08_ma_loi()` | `UNSUPPORTED` | `None` | NO_VALID_KIND | Confirmed teacher Ch2 generator kinds are template-based buffer/memory/Python fuzz generators and do not semantically express this Smart EV boolean/state-transition safety requirement. |
| `REQ-CHG-01` | CHARGING | `co_the_bat_dau_sac()`<br>`bat_dau_sac()`<br>`giam_sat_xe_va_cong()` | `UNSUPPORTED` | `None` | NO_VALID_KIND | Confirmed teacher Ch2 generator kinds are template-based buffer/memory/Python fuzz generators and do not semantically express this Smart EV boolean/state-transition safety requirement. |
| `REQ-CHG-02` | CHARGING | `co_the_bat_dau_sac()`<br>`kiem_tra_toan_bo_tram()` | `UNSUPPORTED` | `None` | NO_VALID_KIND | Confirmed teacher Ch2 generator kinds are template-based buffer/memory/Python fuzz generators and do not semantically express this Smart EV boolean/state-transition safety requirement. |
| `REQ-EMG-01` | EMERGENCY | `kich_hoat_dung_khan_cap_cong()`<br>`kich_hoat_dung_khan_cap_tram()`<br>`kiem_tra_sr05_khan_cap()` | `UNSUPPORTED` | `None` | NO_VALID_KIND | Confirmed teacher Ch2 generator kinds are template-based buffer/memory/Python fuzz generators and do not semantically express this Smart EV boolean/state-transition safety requirement. |

## Official CodeGen Spec

`teacher_specs/smart_ev_codegen.json` is intentionally valid but contains no `functions[]` entries unless a requirement has a DIRECTLY_SUPPORTED semantic mapping.

When no requirement is directly supported, the artifact states the limitation instead of inserting fake template functions.

## Experimental Probe

`teacher_specs/codegen_experiments/arithmetic_probe.json` is separated from official coverage. It exists only to test whether documented C `arithmetic` is actually supported by Ch2 at runtime.

## Phase 7.5-B Gate

```yaml
Requirements total: 11
Directly supported: 0
Unsupported/partial/experimental: 11
Fake mappings: 0
Semantic mismatches: 0
READY_FOR_TEACHER_CODEGEN: NO
Status: PASS
```