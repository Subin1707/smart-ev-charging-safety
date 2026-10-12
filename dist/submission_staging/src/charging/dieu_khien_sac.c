#include <stdio.h>
#include "dieu_khien_sac.h"
#include "hang_so.h"
#include <math.h>

static int g_session_counter = 1;

int co_the_bat_dau_sac(const XeDien *xe, const CongSac *cong) {
    if (!xe || !cong) {
        printf("[CHARGING CHECK] ERROR: Con tro xe hoac cong khong hop le.\n");
        return 0;
    }

    /* 1. Kiem tra ket noi */
    if (!xe->da_ket_noi || cong->vehicle_id != xe->id) {
        printf("[CHARGING CHECK] DENIED: Xe chua ket noi vao cong (da_ket_noi=%d, cong_vehicle_id=%d)\n",
               xe->da_ket_noi, cong->vehicle_id);
        return 0;
    }

    /* 2. Kiem tra xac thuc */
    if (!xe->da_xac_thuc) {
        printf("[CHARGING CHECK] DENIED: Xe %s chua duoc xac thuc.\n", xe->ma_xe);
        return 0;
    }

    if (xe->trang_thai == XE_LOI || !isfinite(xe->pin.soc) ||
        !isfinite(xe->pin.nhiet_do) || xe->pin.soc < 0.0f) return 0;
    /* 3. Kiem tra SOC < 100 */
    if (xe->pin.soc >= SOC_MAX) {
        printf("[CHARGING CHECK] DENIED: Pin xe %s da day (SOC=%.1f%%).\n", xe->ma_xe, xe->pin.soc);
        return 0;
    }

    /* 4. Kiem tra qua nhiet < 60 */
    if (xe->pin.nhiet_do >= NHIET_DO_TOI_DA) {
        printf("[CHARGING CHECK] DENIED: Pin xe %s qua nhiet (%.1f C >= %.1f C).\n",
               xe->ma_xe, xe->pin.nhiet_do, NHIET_DO_TOI_DA);
        return 0;
    }

    /* 5. Kiem tra dung khan cap */
    if (cong->dung_khan_cap) {
        printf("[CHARGING CHECK] DENIED: Cong %d dang trong trang thai dung khan cap.\n", cong->id);
        return 0;
    }

    /* 6. Kiem tra ma loi cong */
    if (cong->trang_thai == CONG_LOI || cong->ma_loi != 0) {
        printf("[CHARGING CHECK] DENIED: Cong %d dang bi loi (ma_loi=%d).\n", cong->id, cong->ma_loi);
        return 0;
    }

    return 1;
}

int bat_dau_sac(XeDien *xe, CongSac *cong, PhienSac *phien, float cong_suat_kw) {
    if (!isfinite(cong_suat_kw) || cong_suat_kw <= 0.0f) return 0;
    if (!co_the_bat_dau_sac(xe, cong)) {
        printf("[DENIED] Khong du dieu kien de bat dau sac xe %s tai cong %d.\n",
               xe ? xe->ma_xe : "NULL", cong ? cong->id : 0);
        return 0;
    }

    dat_cong_suat_cong(cong, cong_suat_kw);
    cong->trang_thai = CONG_DANG_SAC;
    xe->trang_thai = XE_DANG_SAC;

    if (phien) {
        khoi_tao_phien_sac(phien, g_session_counter++, xe->id, cong->id, xe->pin.soc);
    }

    printf("[CHARGING] Bat dau sac thanh cong cho xe %s tai Cong %d voi cong suat %.1f kW.\n",
           xe->ma_xe, cong->id, cong->cong_suat_kw);
    return 1;
}

int dung_sac(XeDien *xe, CongSac *cong, PhienSac *phien) {
    if (!cong) return 0;

    dat_cong_suat_cong(cong, 0.0f);
    cong->trang_thai = CONG_DUNG;

    if (xe) {
        xe->trang_thai = XE_DUNG_SAC;
    }

    if (phien && phien->dang_hoat_dong) {
        ket_thuc_phien_sac(phien, xe ? xe->pin.soc : 0.0f, xe ? xe->pin.nang_luong_da_nhan : 0.0f);
    }

    printf("[CHARGING] Da dung sac cho Cong %d.\n", cong->id);
    return 1;
}
