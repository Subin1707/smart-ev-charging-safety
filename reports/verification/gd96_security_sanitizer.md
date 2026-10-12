# GD9.6 — Security Triage + Sanitizer

Generated: 2026-09-29T13:28:33.219863+00:00

## Static Finding Triage

| Classification | Tool/Rule | Location | Function | Requirement | Code | Conclusion Evidence |
|---|---|---|---|---|---|---|
| MITIGATED | project_pattern_scanner / `dangerous_c_string_api` | `src/database/database.c:55` | `khoi_tao_database` | NOT_APPLICABLE | `strcpy(g_sql_path, "logs/database/persistence.sql");` | Destination is static char g_sql_path[256]; source literal is logs/database/persistence.sql. No Smart EV external input reaches this fallback copy. The code copies a fixed literal into static char g_sql_path[256]; caller-controlled paths use strncpy with explicit NUL termination in the preceding branch. |
| MITIGATED | project_pattern_scanner / `dangerous_c_string_api` | `src/logging/logger.c:50` | `ghi_log` | NOT_APPLICABLE | `strcpy(thoi_gian_str, "00:00:00");` | Destination is char thoi_gian_str[32]; source literal is 8 characters plus NUL. Fallback executes only when localtime() fails. The source is the fixed literal 00:00:00 copied into char thoi_gian_str[32], so no attacker-controlled overflow path exists in Smart EV flows. |
| MITIGATED | project_pattern_scanner / `dangerous_c_string_api` | `src/station/tram_sac.c:16` | `khoi_tao_tram_sac` | REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02 | `strcpy(tram->ma_tram, "STATION01");` | Destination is TramSac.ma_tram[20]; source literal is STATION01. The strcpy branch is used only when ma_tram is NULL and copies the fixed default station ID STATION01 into char ma_tram[20]. Non-null station IDs use strncpy with explicit NUL termination. |

## Sanitizer

- Native MinGW ASan: UNAVAILABLE
- Native MinGW UBSan: UNAVAILABLE
- Linux/Docker ASan: PASS
- Linux/Docker UBSan: PASS
- Sanitizer test cases executed: 142
- ASan findings: 0
- UBSan findings: 0
- Crashes: 0
- Docker note: Docker sanitizer run completed.

## Status

Canonical production modified: NO
GĐ9.6 STATUS: PASS
