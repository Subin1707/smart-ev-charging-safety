#include <stdio.h>
#include "cong_sac_repository.h"
#include "database.h"

void cap_nhat_cong_sac_db(int tram_id, const CongSac *cong) {
    if (!cong) return;

    char sql[256];
    snprintf(sql, sizeof(sql),
             "UPDATE cong_sac SET trang_thai = '%s', dien_ap_v = %.2f, dong_dien_a = %.2f, cong_suat_kw = %.2f, ma_loi = %d "
             "WHERE tram_id = %d AND port_number = %d;",
             ten_trang_thai_cong(cong->trang_thai), cong->dien_ap, cong->dong_dien,
             cong->cong_suat_kw, cong->ma_loi, tram_id, cong->id);
    thuc_thi_sql(sql);
}
