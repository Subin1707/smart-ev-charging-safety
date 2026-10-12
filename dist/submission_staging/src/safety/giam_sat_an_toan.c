#include <stdio.h>
#include "giam_sat_an_toan.h"
#include "quy_tac_an_toan.h"

KetQuaGiamSat giam_sat_xe_va_cong(XeDien *xe, CongSac *cong, TramSac *tram) {
    KetQuaGiamSat kq = {1, LOI_KHONG_CO, "SAFE"};

    if (!cong) {
        kq.an_toan = 0;
        kq.ma_loi = LOI_KHONG_CO;
        kq.mo_ta = "NULL pointer";
        return kq;
    }

    /* Neu cong dang trong trang thai khan cap hoac tram khan cap */
    if (!kiem_tra_sr05_khan_cap(cong, tram)) {
        kq.an_toan = 0;
        kq.ma_loi = LOI_DUNG_KHAN_CAP;
        kq.mo_ta = "SR05: Emergency active with power > 0";
        cong->cong_suat_kw = 0.0f;
        return kq;
    }

    if (!xe) return kq;

    /* Kiem tra SR03: Qua nhiet */
    if (!kiem_tra_sr03_nhiet_do(xe)) {
        kq.an_toan = 0;
        kq.ma_loi = LOI_PIN_QUA_NHIET;
        kq.mo_ta = "SR03: Battery Overheat (>= 60C)";

        /* Tu dong cat nguon ngay lap tuc */
        cong->cong_suat_kw = 0.0f;
        cong->dong_dien = 0.0f;
        cong->trang_thai = CONG_LOI;
        cong->ma_loi = LOI_PIN_QUA_NHIET;
        xe->trang_thai = XE_LOI;

        printf("[SAFETY][CRITICAL] %s battery overheat (%.1f C >= 60.0 C)! PORT %d power disabled -> FAULT\n",
               xe->ma_xe, xe->pin.nhiet_do, cong->id);
        return kq;
    }

    /* Kiem tra SR04: Pin day */
    if (cong->trang_thai == CONG_DANG_SAC && !kiem_tra_sr04_pin_day(xe)) {
        kq.an_toan = 1;
        kq.ma_loi = LOI_PIN_DA_DAY;
        kq.mo_ta = "SR04: Battery Full (>= 100%)";

        cong->cong_suat_kw = 0.0f;
        cong->dong_dien = 0.0f;
        cong->trang_thai = CONG_DUNG;
        xe->trang_thai = XE_DUNG_SAC;

        printf("[SAFETY][INFO] %s battery full (100%%). PORT %d power off -> STOPPED\n",
               xe->ma_xe, cong->id);
        return kq;
    }

    /* Kiem tra SR01 & SR09: Mat ket noi */
    if (!kiem_tra_sr01_ket_noi(xe, cong) || !kiem_tra_sr09_ngat_ket_noi(xe, cong)) {
        kq.an_toan = 0;
        kq.ma_loi = LOI_CHUA_KET_NOI;
        kq.mo_ta = "SR01/SR09: Charging without valid connection";

        cong->cong_suat_kw = 0.0f;
        cong->trang_thai = CONG_LOI;
        return kq;
    }

    /* Kiem tra SR02: Chua xac thuc ma dang sac */
    if (!kiem_tra_sr02_xac_thuc(xe)) {
        kq.an_toan = 0;
        kq.ma_loi = LOI_CHUA_XAC_THUC;
        kq.mo_ta = "SR02: Charging without authentication";

        cong->cong_suat_kw = 0.0f;
        cong->trang_thai = CONG_LOI;
        return kq;
    }

    return kq;
}

int kiem_tra_toan_bo_tram(TramSac *tram, XeDien ds_xe[], int so_xe) {
    if (!tram) return 0;

    int so_su_co = 0;
    for (int i = 0; i < SO_CONG_SAC; i++) {
        CongSac *cong = &tram->cong[i];
        if (cong->vehicle_id != -1 && ds_xe && so_xe > 0) {
            for (int v = 0; v < so_xe; v++) {
                if (ds_xe[v].id == cong->vehicle_id) {
                    KetQuaGiamSat kq = giam_sat_xe_va_cong(&ds_xe[v], cong, tram);
                    if (!kq.an_toan) {
                        so_su_co++;
                    }
                    break;
                }
            }
        }
    }
    cap_nhat_tong_cong_suat_tram(tram);
    return so_su_co;
}
