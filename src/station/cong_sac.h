#ifndef CONG_SAC_H
#define CONG_SAC_H

#include "kieu_du_lieu.h"

typedef struct {
    int id;             /* 1 Ä‘áº¿n 5 */
    int vehicle_id;     /* -1 náº¿u chÆ°a cĂ³ xe */

    TrangThaiCong trang_thai;

    float dien_ap;
    float dong_dien;
    float cong_suat_kw;

    int dung_khan_cap;
    int ma_loi;
} CongSac;

void khoi_tao_cong_sac(CongSac *cong, int id);
int ket_noi_xe_vao_cong(CongSac *cong, int vehicle_id);
int ngat_ket_noi_cong(CongSac *cong);
void dat_cong_suat_cong(CongSac *cong, float cong_suat_kw);
const char* ten_trang_thai_cong(TrangThaiCong tt);

#endif /* CONG_SAC_H */
