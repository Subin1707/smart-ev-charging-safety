#include <stdio.h>
#include "telemetry_repository.h"
#include "database.h"

void luu_telemetry(int session_id, int tick, const char *ma_xe, int port_id, float soc, float temp, float power, const char *state) {
    char sql[256];
    if (session_id > 0) {
        snprintf(sql, sizeof(sql),
                 "INSERT INTO telemetry (session_id, tick, vehicle_code, port_number, soc, temperature_c, power_kw, state) "
                 "VALUES (%d, %d, '%s', %d, %.2f, %.2f, %.2f, '%s');",
                 session_id, tick, ma_xe ? ma_xe : "--", port_id, soc, temp, power, state ? state : "UNKNOWN");
    } else {
        snprintf(sql, sizeof(sql),
                 "INSERT INTO telemetry (session_id, tick, vehicle_code, port_number, soc, temperature_c, power_kw, state) "
                 "VALUES (NULL, %d, '%s', %d, %.2f, %.2f, %.2f, '%s');",
                 tick, ma_xe ? ma_xe : "--", port_id, soc, temp, power, state ? state : "UNKNOWN");
    }
    thuc_thi_sql(sql);
}
