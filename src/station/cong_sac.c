#include <stdio.h>
#include "cong_sac.h"
#include "hang_so.h"

void khoi_tao_cong_sac(CongSac *cong, int id) {
    if (!cong) return;

    cong->id = id;
    cong->vehicle_id = -1;
    cong->trang_thai = CONG_RANH;
    cong->dien_ap = 400.0f; /* Chuáº©n 400V 3 pha */
    cong->dong_dien = 0.0f;
    cong->cong_suat_kw = 0.0f;
    cong->dung_khan_cap = 0;
    cong->ma_loi = 0;
}

int ket_noi_xe_vao_cong(CongSac *cong, int vehicle_id) {
    if (!cong) return 0;
    if (cong->vehicle_id != -1 && cong->vehicle_id != vehicle_id) {
        printf("[PORT %d] Error: Port already occupied by vehicle %d\n", cong->id, cong->vehicle_id);
        return 0;
    }

    cong->vehicle_id = vehicle_id;
    cong->trang_thai = CONG_DA_KET_NOI;
    return 1;
}

int ngat_ket_noi_cong(CongSac *cong) {
    if (!cong) return 0;

    cong->vehicle_id = -1;
    cong->cong_suat_kw = 0.0f;
    cong->dong_dien = 0.0f;
    cong->trang_thai = CONG_RANH;
    return 1;
}

void dat_cong_suat_cong(CongSac *cong, float cong_suat_kw) {
    if (!cong) return;

    if (cong_suat_kw > CONG_SUAT_CONG_TOI_DA) {
        cong_suat_kw = CONG_SUAT_CONG_TOI_DA;
    }
    if (cong_suat_kw < 0.0f) {
        cong_suat_kw = 0.0f;
    }

    cong->cong_suat_kw = cong_suat_kw;
    if (cong->dien_ap > 0.0f) {
        cong->dong_dien = (cong_suat_kw * 1000.0f) / cong->dien_ap;
    }
}

const char* ten_trang_thai_cong(TrangThaiCong tt) {
    switch (tt) {
        case CONG_RANH:        return "IDLE";
        case CONG_DA_DAT:      return "RESERVED";
        case CONG_DA_KET_NOI: return "CONNECTED";
        case CONG_SAN_SANG:   return "READY";
        case CONG_DANG_SAC:   return "CHARGING";
        case CONG_DUNG:       return "STOPPED";
        case CONG_LOI:        return "FAULT";
        default:              return "UNKNOWN";
    }
}
