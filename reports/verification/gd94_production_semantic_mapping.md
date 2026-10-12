# GD9.4 — Production-Semantic Static/Fuzz Mapping

Generated: 2026-09-29T07:47:41.322404+00:00

## Summary

- Production functions analyzed: 10
- Teacher kinds confirmed: 5
- Exact semantic matches: 0
- Semantic subsets: 2
- Probe only: 2
- Unsupported: 8
- Ch2 production-semantic path: NO
- Ch4 production-semantic path: NO
- READY_FOR_PRODUCTION_E2E_ADAPTER: NO

## Production Function Inventory

| Function | Signature | Source | Req IDs | Conditions | Loops | Memory ops | Arithmetic ops | Classification |
|---|---|---|---|---|---|---|---|---|
| `xac_thuc_xe` | `int xac_thuc_xe(XeDien *xe, const char *token)` | `src/auth/xac_thuc.c` | REQ-AUTH-01 | !xe || !xe->da_ket_noi -> return 0<br>token && kiem_tra_token_hop_le(xe->ma_xe, token) -> authenticate<br>else clear da_xac_thuc | None | Reads token pointer; delegates token comparison to token.c; no local copy. | None | `UNSUPPORTED` |
| `soc_hop_le` | `int soc_hop_le(const Pin *pin)` | `src/vehicle/pin.c` | REQ-SOC-01 | !pin -> return 0<br>pin->soc >= SOC_MIN && pin->soc <= SOC_MAX | None | Pointer null check only. | Float comparisons against SOC_MIN=0.0f and SOC_MAX=100.0f. | `SEMANTIC_SUBSET` |
| `pin_qua_nhiet` | `int pin_qua_nhiet(const Pin *pin)` | `src/vehicle/pin.c` | REQ-TEMP-01 | !pin -> return 1<br>pin->nhiet_do >= NHIET_DO_TOI_DA | None | Pointer null check only. | Float comparison against NHIET_DO_TOI_DA=60.0f. | `SEMANTIC_SUBSET` |
| `co_the_bat_dau_sac` | `int co_the_bat_dau_sac(const XeDien *xe, const CongSac *cong)` | `src/charging/dieu_khien_sac.c` | REQ-SOC-02, REQ-TEMP-01, REQ-PORT-01, REQ-CHG-01, REQ-CHG-02 | Rejects null pointers<br>Requires vehicle connected and port vehicle_id match<br>Requires authenticated vehicle<br>Rejects XE_LOI, non-finite SOC/temp, negative SOC<br>Rejects SOC >= SOC_MAX<br>Rejects temperature >= NHIET_DO_TOI_DA<br>Rejects emergency, fault state, and nonzero port error code | None | Pointer null checks only. | Float comparisons; isfinite checks. | `UNSUPPORTED` |
| `bat_dau_sac` | `int bat_dau_sac(XeDien *xe, CongSac *cong, PhienSac *phien, float cong_suat_kw)` | `src/charging/dieu_khien_sac.c` | REQ-CHG-01 | Rejects non-finite or <=0 power<br>Calls co_the_bat_dau_sac before state mutation<br>Initializes session when phien is non-null | None | Pointer guarded writes to xe/cong/phien. | g_session_counter++<br>float power comparisons. | `UNSUPPORTED` |
| `ket_noi_xe_vao_cong` | `int ket_noi_xe_vao_cong(CongSac *cong, int vehicle_id)` | `src/station/cong_sac.c` | REQ-PORT-01, REQ-PORT-02 | !cong -> return 0<br>Rejects different vehicle when port occupied<br>Sets vehicle_id and connected state | None | Pointer guarded struct writes. | Comparison with sentinel -1. | `UNSUPPORTED` |
| `ket_noi_xe_vao_tram` | `int ket_noi_xe_vao_tram(TramSac *tram, int port_idx, XeDien *xe)` | `src/station/tram_sac.c` | REQ-AUTH-01, REQ-PORT-01, REQ-PORT-02 | Rejects nulls/out-of-range port<br>Rejects emergency and negative vehicle id<br>Rejects duplicate vehicle assignment except idempotent same-port connection | for i in SO_CONG_SAC checks duplicate vehicle assignment | Pointer guarded writes; calls ket_noi_xe_vao_cong. | port_idx bounds; i + 1 assigned_port. | `UNSUPPORTED` |
| `ngat_ket_noi_xe_khoi_tram` | `int ngat_ket_noi_xe_khoi_tram(TramSac *tram, int port_idx, XeDien *xe)` | `src/station/tram_sac.c` | REQ-AUTH-02 | Rejects null tram/out-of-range port<br>Rejects mismatched vehicle id<br>Clears port and vehicle connection/authentication state | None | Pointer guarded writes; calls ngat_ket_noi_cong. | port_idx bounds; cap_nhat_tong_cong_suat_tram aggregation after disconnect. | `UNSUPPORTED` |
| `giam_sat_xe_va_cong` | `KetQuaGiamSat giam_sat_xe_va_cong(XeDien *xe, CongSac *cong, TramSac *tram)` | `src/safety/giam_sat_an_toan.c` | REQ-SOC-02, REQ-TEMP-01, REQ-PORT-01, REQ-PORT-03, REQ-CHG-01, REQ-EMG-01 | Rejects null port<br>Cuts power on emergency, overheat, full battery, invalid connection, or unauthenticated charging | None | Pointer guarded writes to CongSac and XeDien. | Sets power/current to 0.0f; delegates predicate checks. | `UNSUPPORTED` |
| `kiem_tra_toan_bo_tram` | `int kiem_tra_toan_bo_tram(TramSac *tram, XeDien ds_xe[], int so_xe)` | `src/safety/giam_sat_an_toan.c` | REQ-CHG-02 | !tram -> return 0<br>Monitors occupied ports only<br>Increments incident count when monitor result is unsafe | Nested for over SO_CONG_SAC ports and so_xe vehicles. | Array indexing into tram->cong and ds_xe; guarded by bounds/inputs. | so_su_co++<br>cap_nhat_tong_cong_suat_tram sums float power. | `UNSUPPORTED` |

## Teacher Kind Comparison

| Kind | Production-semantic result |
|---|---|
| `buffer_copy` | C fixed local buffer copy template; Ch2 checks strcpy/strncpy-style memory patterns. No exact Smart EV production requirement match found in the analyzed function set. |
| `alloc_release` | C malloc/free lifecycle template; Ch2 checks leak/double-free/use-after-free patterns. No exact Smart EV production requirement match found in the analyzed function set. |
| `arithmetic` | C int addition template; Ch3 can extract simple addition expressions. No exact Smart EV production requirement match found in the analyzed function set. |
| `divide` | Python integer floor-division template; Ch4 fuzzes for divide-by-zero crashes. No exact Smart EV production requirement match found in the analyzed function set. |
| `magic_value` | Python nested magic-value branch template; Ch4 concolic fuzz target. No exact Smart EV production requirement match found in the analyzed function set. |

## Ch2 Mapping

No analyzed production requirement operation legitimately maps to Ch2 generated memory templates. Token authentication must not be mapped to buffer_copy merely because it accepts a string.

## Ch4 Mapping

`compute_charging_rate` classification: `PROBE_ONLY`.
Crash trigger: time_hours == 0, causing Python ZeroDivisionError in return energy_kwh // time_hours.

## SOC Overflow

- Bounded condition output: `req_soc_01_overflow_v2_bounded: sat model={'soc_current': 0, 'soc_delta': 0}`
- Heuristic overflow output: `req_soc_01_overflow_v2_bounded (int32 overflow?): sat model={'soc_current': -1, 'soc_delta': -2147483648}`
- Classification: `TOOL_MODEL_LIMITATION`
- Reason: The condition query preserves bounded values, but the overflow heuristic builds a separate int32-overflow query over the raw overflow_expr and loses the condition preconditions. Production SOC is float-bounded by SOC_MIN/SOC_MAX, so this is not a production CWE-190 finding.

## Conclusion

Fake requirement mappings: `0`.
Next action: Keep teacher Ch2/Ch4 probes separate from production evidence; build production-native static/dynamic verification for real C, or only create GD9.5 if a future exact semantic match is found.
