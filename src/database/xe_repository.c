#include <stdio.h>
#include "xe_repository.h"
#include "database.h"
#include "trang_thai_xe.h"

void luu_xe_dien(const XeDien *xe) {
    if (!xe) return;

    char sql[512];
    snprintf(sql, sizeof(sql),
             "INSERT INTO xe_dien (id, ma_xe, dung_luong_kwh, soc_hien_tai, nhiet_do_c, cong_suat_sac_max_kw, trang_thai) "
             "VALUES (%d, '%s', %.2f, %.2f, %.2f, %.2f, '%s') "
             "ON CONFLICT (ma_xe) DO UPDATE SET soc_hien_tai = EXCLUDED.soc_hien_tai, nhiet_do_c = EXCLUDED.nhiet_do_c, trang_thai = EXCLUDED.trang_thai;",
             xe->id, xe->ma_xe, xe->pin.dung_luong_kwh, xe->pin.soc, xe->pin.nhiet_do,
             xe->cong_suat_sac_toi_da, ten_trang_thai_xe(xe->trang_thai));
    thuc_thi_sql(sql);
}

void cap_nhat_trang_thai_xe_db(const XeDien *xe) {
    if (!xe) return;

    char sql[256];
    snprintf(sql, sizeof(sql),
             "UPDATE xe_dien SET soc_hien_tai = %.2f, nhiet_do_c = %.2f, trang_thai = '%s' WHERE id = %d;",
             xe->pin.soc, xe->pin.nhiet_do, ten_trang_thai_xe(xe->trang_thai), xe->id);
    thuc_thi_sql(sql);
}
