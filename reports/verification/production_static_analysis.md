# GD9.5 Production Static Analysis

Generated: 2026-09-29T08:47:12.142689+00:00

- Production source compiled: PASS
- Compiler errors: 0
- Compiler warnings: 0
- Cppcheck executed: YES
- Static security findings: 3

| Tool | Severity | File | Line | Requirement | Classification | Message |
|---|---|---|---:|---|---|---|
| cppcheck | INFORMATION | `src/auth/token.c` | 1 | REQ-AUTH-01 | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/auth/token.c` | 2 | REQ-AUTH-01 | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/auth/xac_thuc.c` | 1 | REQ-AUTH-01 | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/charging/dieu_khien_sac.c` | 1 | REQ-CHG-01,REQ-CHG-02,REQ-PORT-01,REQ-SOC-02,REQ-TEMP-01 | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/charging/dieu_khien_sac.c` | 4 | REQ-CHG-01,REQ-CHG-02,REQ-PORT-01,REQ-SOC-02,REQ-TEMP-01 | `missingIncludeSystem` | Include file: <math.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/charging/dieu_khien_sac.c` |  | REQ-CHG-01,REQ-CHG-02,REQ-PORT-01,REQ-SOC-02,REQ-TEMP-01 | `normalCheckLevelMaxBranches` | Limiting analysis of branches. Use --check-level=exhaustive to analyze all branches. |
| cppcheck | INFORMATION | `src/charging/phien_sac.c` | 1 | REQ-CHG-01,REQ-CHG-02,REQ-PORT-01,REQ-SOC-02,REQ-TEMP-01 | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/communication/dieu_khien_tu_xa.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/communication/dieu_khien_tu_xa.c` | 2 | UNTRACEABLE | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/communication/dieu_khien_tu_xa.c` | 3 | UNTRACEABLE | `missingIncludeSystem` | Include file: <ctype.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/communication/dieu_khien_tu_xa.c` | 4 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdlib.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/communication/dieu_khien_tu_xa.c` |  | UNTRACEABLE | `normalCheckLevelMaxBranches` | Limiting analysis of branches. Use --check-level=exhaustive to analyze all branches. |
| cppcheck | INFORMATION | `src/communication/message.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdlib.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/communication/message.c` | 2 | UNTRACEABLE | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/communication/message.h` | 4 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stddef.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/communication/message.c` |  | UNTRACEABLE | `normalCheckLevelMaxBranches` | Limiting analysis of branches. Use --check-level=exhaustive to analyze all branches. |
| cppcheck | INFORMATION | `src/communication/protocol.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/core/cau_hinh.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/core/he_thong.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/database/cong_sac_repository.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/database/database.c` | 4 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/database/database.c` | 5 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdlib.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/database/database.c` | 6 | UNTRACEABLE | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/database/database.c` |  | UNTRACEABLE | `normalCheckLevelMaxBranches` | Limiting analysis of branches. Use --check-level=exhaustive to analyze all branches. |
| cppcheck | INFORMATION | `src/database/database.c` | 11 | UNTRACEABLE | `missingIncludeSystem` | Include file: <libpq-fe.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/database/phien_sac_repository.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/database/su_kien_an_toan_repository.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/database/telemetry_repository.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/database/tram_repository.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/database/xe_repository.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/logging/logger.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/logging/logger.c` | 2 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdarg.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/logging/logger.c` | 3 | UNTRACEABLE | `missingIncludeSystem` | Include file: <time.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/logging/logger.c` | 4 | UNTRACEABLE | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | STYLE | `src/logging/logger.c` | 46 | UNTRACEABLE | `constVariablePointer` | Variable 'tm_info' can be declared as pointer to const |
| cppcheck | INFORMATION | `src/logging/nhat_ky_su_kien.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/logging/nhat_ky_su_kien.c` | 2 | UNTRACEABLE | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/main.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/main.c` | 2 | UNTRACEABLE | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/main.c` |  | UNTRACEABLE | `normalCheckLevelMaxBranches` | Limiting analysis of branches. Use --check-level=exhaustive to analyze all branches. |
| cppcheck | INFORMATION | `src/monitoring/chi_so.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/monitoring/chi_so.c` | 2 | UNTRACEABLE | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/monitoring/du_lieu_giam_sat.h` | 4 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/monitoring/du_lieu_giam_sat.c` |  | UNTRACEABLE | `normalCheckLevelMaxBranches` | Limiting analysis of branches. Use --check-level=exhaustive to analyze all branches. |
| cppcheck | INFORMATION | `src/monitoring/du_lieu_giam_sat.c` | 7 | UNTRACEABLE | `missingIncludeSystem` | Include file: <windows.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/monitoring/su_kien_he_thong.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/monitoring/su_kien_he_thong.c` | 2 | UNTRACEABLE | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/safety/dung_khan_cap.c` | 1 | REQ-CHG-02,REQ-EMG-01,REQ-PORT-03,REQ-SOC-02,REQ-TEMP-01 | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/safety/giam_sat_an_toan.c` | 1 | REQ-CHG-02,REQ-EMG-01,REQ-PORT-03,REQ-SOC-02,REQ-TEMP-01 | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/safety/giam_sat_an_toan.c` |  | REQ-CHG-02,REQ-EMG-01,REQ-PORT-03,REQ-SOC-02,REQ-TEMP-01 | `normalCheckLevelMaxBranches` | Limiting analysis of branches. Use --check-level=exhaustive to analyze all branches. |
| cppcheck | STYLE | `src/safety/giam_sat_an_toan.c` | 5 | REQ-CHG-02,REQ-EMG-01,REQ-PORT-03,REQ-SOC-02,REQ-TEMP-01 | `constParameterPointer` | Parameter 'tram' can be declared as pointer to const |
| cppcheck | INFORMATION | `src/safety/quy_tac_an_toan.c` | 1 | REQ-CHG-02,REQ-EMG-01,REQ-PORT-03,REQ-SOC-02,REQ-TEMP-01 | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/simulation/kich_ban.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/simulation/kich_ban.c` |  | UNTRACEABLE | `normalCheckLevelMaxBranches` | Limiting analysis of branches. Use --check-level=exhaustive to analyze all branches. |
| cppcheck | INFORMATION | `src/simulation/mo_phong.c` | 5 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/simulation/mo_phong.c` | 6 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdlib.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/simulation/mo_phong.c` | 7 | UNTRACEABLE | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/simulation/mo_phong.c` | 11 | UNTRACEABLE | `missingIncludeSystem` | Include file: <time.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/simulation/mo_phong.c` |  | UNTRACEABLE | `normalCheckLevelMaxBranches` | Limiting analysis of branches. Use --check-level=exhaustive to analyze all branches. |
| cppcheck | STYLE | `src/simulation/mo_phong.c` | 201 | UNTRACEABLE | `duplicateCondition` | The if condition is the same as the previous if condition |
| cppcheck | INFORMATION | `src/simulation/mo_phong.c` | 9 | UNTRACEABLE | `missingIncludeSystem` | Include file: <windows.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/simulation/ngau_nhien.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdlib.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/simulation/ngau_nhien.c` | 2 | UNTRACEABLE | `missingIncludeSystem` | Include file: <time.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/simulation/sinh_kich_ban.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/simulation/sinh_kich_ban.c` | 4 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdlib.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/simulation/sinh_kich_ban.c` | 5 | UNTRACEABLE | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/simulation/sinh_su_kien.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/station/cong_sac.c` | 1 | REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02 | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/station/dieu_phoi.c` |  | REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02 | `normalCheckLevelMaxBranches` | Limiting analysis of branches. Use --check-level=exhaustive to analyze all branches. |
| cppcheck | INFORMATION | `src/station/quan_ly_cong_suat.c` | 1 | REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02 | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/station/quan_ly_cong_suat.c` |  | REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02 | `normalCheckLevelMaxBranches` | Limiting analysis of branches. Use --check-level=exhaustive to analyze all branches. |
| cppcheck | STYLE | `src/station/quan_ly_cong_suat.c` | 99 | REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02 | `constVariablePointer` | Variable 'cong' can be declared as pointer to const |
| cppcheck | INFORMATION | `src/station/tram_sac.c` | 1 | REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02 | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/station/tram_sac.c` | 2 | REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02 | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/station/tram_sac.c` |  | REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02 | `normalCheckLevelMaxBranches` | Limiting analysis of branches. Use --check-level=exhaustive to analyze all branches. |
| cppcheck | INFORMATION | `src/vehicle/pin.c` | 1 | REQ-SOC-01,REQ-TEMP-01 | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/vehicle/xe_dien.c` | 1 | UNTRACEABLE | `missingIncludeSystem` | Include file: <stdio.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | INFORMATION | `src/vehicle/xe_dien.c` | 2 | UNTRACEABLE | `missingIncludeSystem` | Include file: <string.h> not found. Please note: Standard library headers do not need to be provided to get proper results. |
| cppcheck | STYLE | `src/charging/che_do_sac.c` | 3 | REQ-CHG-01,REQ-CHG-02,REQ-PORT-01,REQ-SOC-02,REQ-TEMP-01 | `unusedFunction` | The function 'ten_che_do_sac' is never used. |
| cppcheck | STYLE | `src/communication/message.c` | 13 | UNTRACEABLE | `unusedFunction` | The function 'parse_protocol_message' is never used. |
| cppcheck | STYLE | `src/communication/protocol.c` | 4 | UNTRACEABLE | `unusedFunction` | The function 'protocol_message_is_safe' is never used. |
| cppcheck | STYLE | `src/core/cau_hinh.c` | 16 | UNTRACEABLE | `unusedFunction` | The function 'in_cau_hinh' is never used. |
| cppcheck | STYLE | `src/logging/nhat_ky_su_kien.c` | 50 | UNTRACEABLE | `unusedFunction` | The function 'them_su_kien_nhat_ky' is never used. |
| cppcheck | STYLE | `src/monitoring/du_lieu_giam_sat.c` | 208 | UNTRACEABLE | `unusedFunction` | The function 'ghi_snapshot_json' is never used. |
| cppcheck | STYLE | `src/safety/quy_tac_an_toan.c` | 53 | REQ-CHG-02,REQ-EMG-01,REQ-PORT-03,REQ-SOC-02,REQ-TEMP-01 | `unusedFunction` | The function 'kiem_tra_sr06_soc_hop_le' is never used. |
| cppcheck | STYLE | `src/safety/quy_tac_an_toan.c` | 59 | REQ-CHG-02,REQ-EMG-01,REQ-PORT-03,REQ-SOC-02,REQ-TEMP-01 | `unusedFunction` | The function 'kiem_tra_sr07_doc_quyen_cong' is never used. |
| cppcheck | STYLE | `src/safety/quy_tac_an_toan.c` | 68 | REQ-CHG-02,REQ-EMG-01,REQ-PORT-03,REQ-SOC-02,REQ-TEMP-01 | `unusedFunction` | The function 'kiem_tra_sr08_ma_loi' is never used. |
| cppcheck | STYLE | `src/safety/quy_tac_an_toan.c` | 86 | REQ-CHG-02,REQ-EMG-01,REQ-PORT-03,REQ-SOC-02,REQ-TEMP-01 | `unusedFunction` | The function 'kiem_tra_sr10_gioi_han_cong_suat_tram' is never used. |
| cppcheck | STYLE | `src/station/dieu_phoi.c` | 4 | REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02 | `unusedFunction` | The function 'tim_cong_ranh' is never used. |
| cppcheck | STYLE | `src/station/tram_sac.c` | 160 | REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02 | `unusedFunction` | The function 'in_trang_thai_tram' is never used. |
| cppcheck | STYLE | `src/vehicle/pin.c` | 17 | REQ-SOC-01,REQ-TEMP-01 | `unusedFunction` | The function 'soc_hop_le' is never used. |
| cppcheck | STYLE | `src/vehicle/pin.c` | 22 | REQ-SOC-01,REQ-TEMP-01 | `unusedFunction` | The function 'pin_da_day' is never used. |
| cppcheck | STYLE | `src/vehicle/pin.c` | 27 | REQ-SOC-01,REQ-TEMP-01 | `unusedFunction` | The function 'pin_qua_nhiet' is never used. |
| cppcheck | STYLE | `src/vehicle/xe_dien.c` | 55 | UNTRACEABLE | `unusedFunction` | The function 'in_thong_tin_xe' is never used. |
| cppcheck | STYLE | `src/charging/dieu_khien_sac.c` | 8 | REQ-CHG-01,REQ-CHG-02,REQ-PORT-01,REQ-SOC-02,REQ-TEMP-01 | `staticFunction` | The function 'co_the_bat_dau_sac' should have static linkage since it is not used outside of its translation unit. |
| cppcheck | STYLE | `src/monitoring/du_lieu_giam_sat.c` | 73 | UNTRACEABLE | `staticFunction` | The function 'xuat_snapshot_json' should have static linkage since it is not used outside of its translation unit. |
| cppcheck | STYLE | `src/safety/giam_sat_an_toan.c` | 5 | REQ-CHG-02,REQ-EMG-01,REQ-PORT-03,REQ-SOC-02,REQ-TEMP-01 | `staticFunction` | The function 'giam_sat_xe_va_cong' should have static linkage since it is not used outside of its translation unit. |
| cppcheck | STYLE | `src/simulation/mo_phong.c` | 39 | UNTRACEABLE | `staticFunction` | The function 'in_dashboard_tick' should have static linkage since it is not used outside of its translation unit. |
| cppcheck | STYLE | `src/simulation/mo_phong.c` | 74 | UNTRACEABLE | `staticFunction` | The function 'thuc_hien_mot_tick' should have static linkage since it is not used outside of its translation unit. |
| cppcheck | STYLE | `src/station/quan_ly_cong_suat.c` | 6 | REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02 | `staticFunction` | The function 'phan_phoi_cong_suat_chia_deu' should have static linkage since it is not used outside of its translation unit. |
| cppcheck | STYLE | `src/station/quan_ly_cong_suat.c` | 91 | REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02 | `staticFunction` | The function 'xu_ly_qua_tai_cong_suat' should have static linkage since it is not used outside of its translation unit. |
| cppcheck | INFORMATION | `nofile` |  | UNTRACEABLE | `checkersReport` | Active checkers: 119/186 (use --checkers-report=<filename> to see details) |
| project_pattern_scanner | SECURITY | `src/database/database.c` | 55 | UNTRACEABLE | `dangerous_c_string_api` | Potential unsafe C string API token `strcpy` in: strcpy(g_sql_path, "logs/database/persistence.sql"); |
| project_pattern_scanner | SECURITY | `src/logging/logger.c` | 50 | UNTRACEABLE | `dangerous_c_string_api` | Potential unsafe C string API token `strcpy` in: strcpy(thoi_gian_str, "00:00:00"); |
| project_pattern_scanner | SECURITY | `src/station/tram_sac.c` | 16 | REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02 | `dangerous_c_string_api` | Potential unsafe C string API token `strcpy` in: strcpy(tram->ma_tram, "STATION01"); |
