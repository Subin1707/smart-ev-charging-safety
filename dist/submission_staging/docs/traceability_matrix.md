# Ma trận truy vết

Các ô chỉ vị trí kiểm tra, không tự động khẳng định đã PASS. Kết quả lần chạy
nằm trong `evidence/summary.json`; bằng chứng thô nằm cạnh báo cáo từng bước.

| SR | Mã thực thi | Mô hình / SMT / BMC | Kiểm tra thực thi |
|---|---|---|---|
| SR01 | auth/xac_thuc.c | Kripke CONNECTED -> AUTH_OK | integration/test_ket_noi_xac_thuc_sac.c |
| SR02 | charging/dieu_khien_sac.c | Kripke P1; BMC sr02_auth | integration/test_ket_noi_xac_thuc_sac.c; E2E auth failure |
| SR03 | safety/giam_sat_an_toan.c | Kripke P2; SMT temperature; BMC sr03_overheat | test_luong_qua_nhiet.c; test_overheat.py; fuzz_charging_gate.c |
| SR04 | charging/dieu_khien_sac.c; safety/giam_sat_an_toan.c | Kripke P3; BMC sr04_full | test_luong_pin_day.c; test_battery_full_disconnect.py |
| SR05 | safety/dung_khan_cap.c | Kripke P4; BMC sr05_emergency | test_dung_khan_cap.c; test_emergency_stop.py |
| SR06 | charging/dieu_khien_sac.c | Kripke P5 (abstract fault) | integration/test_ket_noi_xac_thuc_sac.c |
| SR07 | station/tram_sac.c; station/cong_sac.c | BMC sr07_exclusivity (isolated model) | unit/test_tram_sac.c |
| SR08 | station/tram_sac.c | No full multi-vehicle proof | unit/test_tram_sac.c |
| SR09 | vehicle/pin.c | SMT soc | unit/test_pin.c; fuzz_charging_gate.c |
| SR10 | station/quan_ly_cong_suat.c | SMT power; BMC sr10_power_limit | test_phan_phoi_cong_suat.c; test_scenario_power_overload.py |
| SR11 | station/quan_ly_cong_suat.c; simulation/mo_phong.c | SMT soc_priority | unit/test_quan_ly_cong_suat.c (30 kW, xe SOC thấp ở cổng cuối) |

Static/memory evidence: `evidence/02_static/` compares vulnerable/fixed teaching
fixtures; cppcheck also scans `src/`. ASan/UBSan fixtures do not establish
sanitizer coverage of every production path. `production_memory.txt` bổ sung
ASan/UBSan trên mã C thực cho trường hợp EV06 vào P01, cập nhật pin và quá nhiệt.

BMC: six separate C abstractions, unwind 12, unwinding assertions enabled.
Expected vulnerable exit 10 **and** VERIFICATION FAILED; fixed exit 0 **and**
VERIFICATION SUCCESSFUL. Compiler/parser failures never count as counterexamples.
SMT: five isolated mathematical models; SAT before and UNSAT after (priority
has only a fixed model). See individual scripts for domains and assumptions.

Fuzz comparison: same production charging guard, deterministic seed, 10,000
random inputs versus four Z3 solutions. Target means exercising an overheat
request, while safety violation means incorrectly accepting it. These are
different metrics. Timings include generation and execution, not compilation.

Golden chain and outstanding external checks: [verification guide](verification_guide.md).
