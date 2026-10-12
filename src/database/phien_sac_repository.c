#include <stdio.h>
#include "phien_sac_repository.h"
#include "database.h"

void tao_phien_sac_db(const PhienSac *phien) {
    if (!phien) return;

    char sql[256];
    snprintf(sql, sizeof(sql),
             "INSERT INTO phien_sac (id, vehicle_id, port_id, soc_bat_dau, dang_hoat_dong) "
             "VALUES (%d, %d, %d, %.2f, TRUE) "
             "ON CONFLICT (id) DO NOTHING;",
             phien->id, phien->vehicle_id, phien->port_id, phien->soc_bat_dau);
    thuc_thi_sql(sql);
}

void ket_thuc_phien_sac_db(const PhienSac *phien) {
    if (!phien) return;

    char sql[256];
    snprintf(sql, sizeof(sql),
             "UPDATE phien_sac SET soc_ket_thuc = %.2f, nang_luong_kwh = %.2f, dang_hoat_dong = FALSE, ended_at = CURRENT_TIMESTAMP "
             "WHERE id = %d;",
             phien->soc_ket_thuc, phien->nang_luong_kwh, phien->id);
    thuc_thi_sql(sql);
}
