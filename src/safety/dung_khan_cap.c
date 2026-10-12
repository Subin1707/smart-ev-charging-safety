#include <stdio.h>
#include "dung_khan_cap.h"
#include "phat_hien_loi.h"

int kich_hoat_dung_khan_cap_cong(CongSac *cong, XeDien *xe) {
    if (!cong) return 0;

    cong->dung_khan_cap = 1;
    cong->cong_suat_kw = 0.0f;
    cong->dong_dien = 0.0f;
    cong->trang_thai = CONG_LOI;
    cong->ma_loi = LOI_DUNG_KHAN_CAP;

    if (xe) {
        xe->trang_thai = XE_LOI;
    }

    printf("[EMERGENCY][PORT %d] Emergency stop activated! Port power cut off to 0 kW.\n", cong->id);
    return 1;
}

int kich_hoat_dung_khan_cap_tram(TramSac *tram, XeDien ds_xe[], int so_xe) {
    if (!tram) return 0;

    tram->emergency = 1;
    tram->cong_suat_hien_tai = 0.0f;

    printf("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n");
    printf("[STATION EMERGENCY] KICH HOAT DUNG KHAN CAP TOAN BO TRAM SAC!\n");
    printf("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n");

    for (int i = 0; i < SO_CONG_SAC; i++) {
        tram->cong[i].dung_khan_cap = 1;
        tram->cong[i].cong_suat_kw = 0.0f;
        tram->cong[i].dong_dien = 0.0f;
        tram->cong[i].trang_thai = CONG_DUNG;

        if (tram->cong[i].vehicle_id != -1 && ds_xe && so_xe > 0) {
            for (int v = 0; v < so_xe; v++) {
                if (ds_xe[v].id == tram->cong[i].vehicle_id) {
                    ds_xe[v].trang_thai = XE_DUNG_SAC;
                    break;
                }
            }
        }
    }

    printf("[STATION EMERGENCY] Tat ca cac cong da ngat cong suat ve 0 kW.\n\n");
    return 1;
}

int khoi_phuc_khan_cap_tram(TramSac *tram) {
    if (!tram) return 0;

    tram->emergency = 0;
    for (int i = 0; i < SO_CONG_SAC; i++) {
        tram->cong[i].dung_khan_cap = 0;
        tram->cong[i].ma_loi = 0;
        if (tram->cong[i].vehicle_id == -1) {
            tram->cong[i].trang_thai = CONG_RANH;
        } else {
            tram->cong[i].trang_thai = CONG_DA_KET_NOI;
        }
    }

    printf("[STATION] Khoi phuc thanh cong he thong sau dung khan cap.\n");
    return 1;
}
