#include <stdio.h>
#include "tram_repository.h"
#include "database.h"

void luu_tram_sac(const TramSac *tram) {
    if (!tram) return;

    char sql[256];
    snprintf(sql, sizeof(sql),
             "INSERT INTO tram_sac (id, ma_tram, so_cong, cong_suat_toi_da_kw, trang_thai) "
             "VALUES (%d, '%s', 5, %.2f, '%s') "
             "ON CONFLICT (ma_tram) DO UPDATE SET trang_thai = EXCLUDED.trang_thai;",
             tram->id, tram->ma_tram, tram->cong_suat_toi_da,
             tram->emergency ? "EMERGENCY" : "OPERATIONAL");
    thuc_thi_sql(sql);
}
