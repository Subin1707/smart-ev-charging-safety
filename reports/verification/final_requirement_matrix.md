# GD12.4 Final Teacher-Production E2E Integration Matrix

| REQ | CTL | Semantic Contract/Z3 | Production Function | Harness | Boundary/Dynamic | Sanitizer | Negative Control | Teacher Tool Capability | Final |
|---|---|---|---|---|---|---|---|---|---|
| REQ-AUTH-01 | PASS | NOT_APPLICABLE | xac_thuc_xe; ket_noi_xe_vao_tram; kiem_tra_sr02_xac_thuc | PASS | PASS | PASS | PASS | Ch2 safe token buffer probe; Ch4 token-ratio divide probe. TOOL_CAPABILITY_EVIDENCE / PROBE_ONLY. | PASS |
| REQ-AUTH-02 | PASS | NOT_APPLICABLE | ngat_ket_noi_xe_khoi_tram; ngat_ket_noi_cong | PASS | PASS | PASS | PASS | None; production PASS is based on formal/SMT/production evidence. | PASS |
| REQ-SOC-01 | PASS | PASS | soc_hop_le; cap_nhat_pin; kiem_tra_sr06_soc_hop_le | PASS | PASS | PASS | PASS | None; production PASS is based on formal/SMT/production evidence. | PASS |
| REQ-SOC-02 | PASS | PASS | co_the_bat_dau_sac; giam_sat_xe_va_cong; kiem_tra_sr04_pin_day | PASS | PASS | PASS | PASS | None; production PASS is based on formal/SMT/production evidence. | PASS |
| REQ-TEMP-01 | PASS | PASS | co_the_bat_dau_sac; giam_sat_xe_va_cong; kiem_tra_sr03_nhiet_do; pin_qua_nhiet | PASS | PASS | PASS | PASS | None; production PASS is based on formal/SMT/production evidence. | PASS |
| REQ-PORT-01 | PASS | NOT_APPLICABLE | ket_noi_xe_vao_cong; ket_noi_xe_vao_tram; co_the_bat_dau_sac | PASS | PASS | PASS | PASS | Ch2 double-free probe. BUG_INJECTED_PROBE / PROBE_ONLY. | PASS |
| REQ-PORT-02 | PASS | NOT_APPLICABLE | ket_noi_xe_vao_cong; ket_noi_xe_vao_tram; kiem_tra_sr07_doc_quyen_cong | PASS | PASS | PASS | PASS | None; production PASS is based on formal/SMT/production evidence. | PASS |
| REQ-PORT-03 | PASS | NOT_APPLICABLE | kich_hoat_dung_khan_cap_cong; giam_sat_xe_va_cong; kiem_tra_sr08_ma_loi | PASS | PASS | PASS | PASS | Ch2 double-free probe. BUG_INJECTED_PROBE / PROBE_ONLY. | PASS |
| REQ-CHG-01 | PASS | PASS | co_the_bat_dau_sac; bat_dau_sac; giam_sat_xe_va_cong | PASS | PASS | PASS | PASS | Ch2 overflow/leak probes; Ch4 divide probe. TOOL_CAPABILITY_EVIDENCE / PROBE_ONLY. | PASS |
| REQ-CHG-02 | PASS | NOT_APPLICABLE | co_the_bat_dau_sac; kiem_tra_toan_bo_tram | PASS | PASS | PASS | PASS | None; production PASS is based on formal/SMT/production evidence. | PASS |
| REQ-EMG-01 | PASS | PASS | kich_hoat_dung_khan_cap_cong; kich_hoat_dung_khan_cap_tram; kiem_tra_sr05_khan_cap | PASS | PASS | PASS | PASS | Ch2 use-after-free probe; Ch4 magic-value probe. BUG_INJECTED_PROBE / PROBE_ONLY. | PASS |

Ch2/Ch4 teacher tool capability is preserved as `TOOL_CAPABILITY_EVIDENCE / PROBE_ONLY` and is not used to decide production PASS.
Negative controls are preserved as confidence evidence and are not counted as ordinary requirement pass tests.
Static/security triage is integrated into sanitizer/static evidence; Ch2/Ch4 CWE probes and tool-model limitations are not counted as production defects.
