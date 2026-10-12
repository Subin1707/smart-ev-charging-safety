#include <stdio.h>
#include "su_kien_an_toan_repository.h"
#include "database.h"

void luu_su_kien_an_toan_db(int tick, const char *ma_xe, int port_id, const char *event_type, const char *severity, const char *description) {
    if (database_dang_ket_noi()) {
        luu_su_kien_an_toan_postgresql(tick, ma_xe, port_id, event_type, severity, description);
        return;
    }

    char sql[512];
    snprintf(sql, sizeof(sql),
             "INSERT INTO su_kien_an_toan (tick, vehicle_code, port_number, event_type, severity, description) "
             "VALUES (%d, '%s', %d, '%s', '%s', '%s');",
             tick, ma_xe ? ma_xe : "--", port_id,
             event_type ? event_type : "UNKNOWN",
             severity ? severity : "INFO",
             description ? description : "");
    thuc_thi_sql(sql);
}
