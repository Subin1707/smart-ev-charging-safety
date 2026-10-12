#include <stdio.h>
#include "quan_ly_cong_suat.h"
#include "dieu_phoi.h"
#include "hang_so.h"

void phan_phoi_cong_suat_chia_deu(TramSac *tram) {
    if (!tram) return;

    int so_xe_dang_sac = 0;
    for (int i = 0; i < SO_CONG_SAC; i++) {
        if (tram->cong[i].trang_thai == CONG_DANG_SAC && !tram->cong[i].dung_khan_cap && tram->cong[i].ma_loi == 0) {
            so_xe_dang_sac++;
        }
    }

    if (so_xe_dang_sac == 0) {
        cap_nhat_tong_cong_suat_tram(tram);
        return;
    }

    float cong_suat_moi_xe = tram->cong_suat_toi_da / (float)so_xe_dang_sac;
    if (cong_suat_moi_xe > CONG_SUAT_CONG_TOI_DA) {
        cong_suat_moi_xe = CONG_SUAT_CONG_TOI_DA;
    }

    for (int i = 0; i < SO_CONG_SAC; i++) {
        if (tram->cong[i].trang_thai == CONG_DANG_SAC && !tram->cong[i].dung_khan_cap && tram->cong[i].ma_loi == 0) {
            dat_cong_suat_cong(&tram->cong[i], cong_suat_moi_xe);
        } else {
            dat_cong_suat_cong(&tram->cong[i], 0.0f);
        }
    }
    cap_nhat_tong_cong_suat_tram(tram);
}

void phan_phoi_cong_suat_theo_soc(TramSac *tram, XeDien ds_xe[], int so_xe) {
    if (!tram || !ds_xe || so_xe <= 0) return;

    int thu_tu_cong[SO_CONG_SAC];
    int so_cong = 0;
    sap_xep_xe_theo_soc(tram, ds_xe, so_xe, thu_tu_cong, &so_cong);

    if (so_cong == 0) {
        cap_nhat_tong_cong_suat_tram(tram);
        return;
    }

    for (int i = 0; i < SO_CONG_SAC; i++) {
        dat_cong_suat_cong(&tram->cong[i], 0.0f);
    }

    float cong_suat_con_lai = tram->cong_suat_toi_da;
    int so_xe_con_lai = 0;

    for (int k = 0; k < so_cong; k++) {
        CongSac *cong = &tram->cong[thu_tu_cong[k]];
        int xe_idx = -1;
        for (int v = 0; v < so_xe; v++) {
            if (ds_xe[v].id == cong->vehicle_id) {
                xe_idx = v;
                break;
            }
        }
        if (xe_idx >= 0 && ds_xe[xe_idx].pin.soc < 50.0f) {
            float cap_phat = cong_suat_con_lai;
            if (cap_phat > CONG_SUAT_CONG_TOI_DA) cap_phat = CONG_SUAT_CONG_TOI_DA;
            dat_cong_suat_cong(cong, cap_phat);
            cong_suat_con_lai -= cap_phat;
        } else if (xe_idx >= 0) {
            so_xe_con_lai++;
        }
    }

    if (so_xe_con_lai > 0 && cong_suat_con_lai > 0.0f) {
        float chia = cong_suat_con_lai / (float)so_xe_con_lai;
        if (chia > CONG_SUAT_CONG_TOI_DA) chia = CONG_SUAT_CONG_TOI_DA;
        for (int k = 0; k < so_cong; k++) {
            CongSac *cong = &tram->cong[thu_tu_cong[k]];
            for (int v = 0; v < so_xe; v++) {
                if (ds_xe[v].id == cong->vehicle_id && ds_xe[v].pin.soc >= 50.0f) {
                    dat_cong_suat_cong(cong, chia);
                    break;
                }
            }
        }
    }

    cap_nhat_tong_cong_suat_tram(tram);
}

void xu_ly_qua_tai_cong_suat(TramSac *tram, XeDien ds_xe[], int so_xe) {
    (void)ds_xe;
    (void)so_xe;
    if (!tram) return;

    float tong_yeu_cau = 0.0f;
    int so_cong_hoat_dong = 0;
    for (int i = 0; i < SO_CONG_SAC; i++) {
        CongSac *cong = &tram->cong[i];
        if ((cong->trang_thai == CONG_DANG_SAC ||
             cong->trang_thai == CONG_SAN_SANG) &&
            !cong->dung_khan_cap && cong->ma_loi == 0) {
            tong_yeu_cau += CONG_SUAT_CONG_TOI_DA;
            so_cong_hoat_dong++;
        }
    }

    printf("\n============================================================\n");
    printf("                 POWER MANAGER ANALYSIS\n");
    printf("============================================================\n");
    printf("So xe yeu cau sac       : %d\n", so_cong_hoat_dong);
    printf("Cong suat moi xe        : %.1f kW\n", CONG_SUAT_CONG_TOI_DA);
    printf("Tong cong suat yeu cau  : %.1f kW\n", tong_yeu_cau);
    printf("Gioi han tram           : %.1f kW\n", tram->cong_suat_toi_da);
    printf("------------------------------------------------------------\n");

    if (tong_yeu_cau > tram->cong_suat_toi_da) {
        printf("[WARNING] POWER OVERLOAD DETECTED!\n");
        printf("[POWER MANAGER] %.1f kW > %.1f kW\n",
               tong_yeu_cau, tram->cong_suat_toi_da);
        printf("\nDang tai phan phoi cong suat...\n");

        phan_phoi_cong_suat_chia_deu(tram);

        float cong_suat_moi_xe = 0.0f;
        if (so_cong_hoat_dong > 0) {
            cong_suat_moi_xe = tram->cong_suat_toi_da / (float)so_cong_hoat_dong;
            if (cong_suat_moi_xe > CONG_SUAT_CONG_TOI_DA) {
                cong_suat_moi_xe = CONG_SUAT_CONG_TOI_DA;
            }
        }

        printf("\n[POWER MANAGER] Tai phan phoi thanh cong.\n");
        printf("Cong suat moi xe        : %.1f kW\n", cong_suat_moi_xe);
        printf("Tong cong suat sau xu ly: %.1f kW\n", tram->cong_suat_hien_tai);
        if (tram->cong_suat_hien_tai <= tram->cong_suat_toi_da) {
            printf("[SAFE] Tong cong suat nam trong gioi han cho phep.\n");
        } else {
            printf("[ERROR] Van con vuot gioi han cong suat!\n");
        }
    } else {
        printf("[SAFE] Khong phat hien qua tai.\n");
        for (int i = 0; i < SO_CONG_SAC; i++) {
            CongSac *cong = &tram->cong[i];
            if (cong->trang_thai == CONG_DANG_SAC &&
                !cong->dung_khan_cap && cong->ma_loi == 0) {
                dat_cong_suat_cong(cong, CONG_SUAT_CONG_TOI_DA);
            }
        }
        cap_nhat_tong_cong_suat_tram(tram);
    }

    printf("============================================================\n");
}

void chay_demo_qua_tai_cong_suat(TramSac *tram, XeDien ds_xe[], int so_xe) {
    if (!tram || !ds_xe || so_xe < SO_CONG_SAC) {
        printf("[POWER DEMO] Du lieu khong hop le.\n");
        return;
    }

    printf("\n====================================================================\n");
    printf("                    POWER OVERLOAD DEMO\n");
    printf("====================================================================\n");
    printf("Mo phong 5 xe cung yeu cau sac tai cong suat toi da.\n");
    printf("Moi xe yeu cau: %.1f kW\n", CONG_SUAT_CONG_TOI_DA);
    printf("Gioi han tram : %.1f kW\n", tram->cong_suat_toi_da);
    printf("====================================================================\n\n");

    khoi_tao_tram_sac(tram, "STATION-01");
    khoi_tao_danh_sach_5_xe(ds_xe);

    for (int i = 0; i < SO_CONG_SAC; i++) {
        ds_xe[i].pin.soc = 20.0f + (float)(i * 5);

        if (!ket_noi_xe_vao_tram(tram, i, &ds_xe[i])) {
            printf("[ERROR] Khong the ket noi %s vao Cong %d.\n",
                   ds_xe[i].ma_xe, i + 1);
            continue;
        }

        ds_xe[i].da_xac_thuc = 1;
        ds_xe[i].trang_thai = XE_DANG_SAC;
        tram->cong[i].trang_thai = CONG_DANG_SAC;
        dat_cong_suat_cong(&tram->cong[i], CONG_SUAT_CONG_TOI_DA);
    }

    cap_nhat_tong_cong_suat_tram(tram);

    printf("TRANG THAI TRUOC KHI POWER MANAGER XU LY\n");
    printf("--------------------------------------------------------------------\n");
    for (int i = 0; i < SO_CONG_SAC; i++) {
        printf("%s -> Cong %d -> Yeu cau %.1f kW\n",
               ds_xe[i].ma_xe, tram->cong[i].id, tram->cong[i].cong_suat_kw);
    }
    printf("--------------------------------------------------------------------\n");
    printf("Tong yeu cau : %.1f kW\n", tram->cong_suat_hien_tai);
    printf("Gioi han tram: %.1f kW\n", tram->cong_suat_toi_da);
    if (tram->cong_suat_hien_tai > tram->cong_suat_toi_da) {
        printf("\n>>> TRAM DANG O TRANG THAI QUA TAI GIA LAP <<<\n");
    }

    xu_ly_qua_tai_cong_suat(tram, ds_xe, so_xe);

    printf("\n====================================================================\n");
    printf("               SMART SOC PRIORITY ALLOCATION\n");
    printf("====================================================================\n");

    ds_xe[0].pin.soc = 15.0f;
    ds_xe[1].pin.soc = 30.0f;
    ds_xe[2].pin.soc = 55.0f;
    ds_xe[3].pin.soc = 75.0f;
    ds_xe[4].pin.soc = 90.0f;

    for (int i = 0; i < SO_CONG_SAC; i++) {
        dat_cong_suat_cong(&tram->cong[i], CONG_SUAT_CONG_TOI_DA);
    }
    cap_nhat_tong_cong_suat_tram(tram);

    printf("\nSOC truoc khi phan phoi:\n");
    printf("------------------------------------------------------------\n");
    for (int i = 0; i < SO_CONG_SAC; i++) {
        printf("%s : SOC %.1f%% -> Yeu cau %.1f kW\n",
               ds_xe[i].ma_xe, ds_xe[i].pin.soc,
               tram->cong[i].cong_suat_kw);
    }
    printf("------------------------------------------------------------\n");
    printf("Tong yeu cau : %.1f kW\n", tram->cong_suat_hien_tai);
    printf("\n[SMART POWER MANAGER]\n");
    printf("Uu tien xe co SOC thap...\n");

    phan_phoi_cong_suat_theo_soc(tram, ds_xe, so_xe);

    printf("\nKET QUA PHAN PHOI THEO SOC\n");
    printf("------------------------------------------------------------\n");
    for (int i = 0; i < SO_CONG_SAC; i++) {
        int xe_idx = -1;
        for (int v = 0; v < so_xe; v++) {
            if (ds_xe[v].id == tram->cong[i].vehicle_id) {
                xe_idx = v;
                break;
            }
        }
        if (xe_idx >= 0) {
            printf("%s | SOC %5.1f%% | %.1f kW\n",
                   ds_xe[xe_idx].ma_xe,
                   ds_xe[xe_idx].pin.soc,
                   tram->cong[i].cong_suat_kw);
        }
    }
    printf("------------------------------------------------------------\n");
    printf("Tong cong suat: %.1f / %.1f kW\n",
           tram->cong_suat_hien_tai, tram->cong_suat_toi_da);
    if (tram->cong_suat_hien_tai <= tram->cong_suat_toi_da) {
        printf("[PASS] Smart allocation van dam bao gioi han tram.\n");
    } else {
        printf("[FAIL] Smart allocation vuot gioi han tram!\n");
    }

    printf("\nTRANG THAI SAU KHI SMART POWER MANAGER XU LY\n");
    hien_thi_dashboard(tram, ds_xe, so_xe);

    printf("KET QUA DEMO\n");
    printf("--------------------------------------------------------------------\n");
    if (tram->cong_suat_hien_tai <= tram->cong_suat_toi_da) {
        printf("[PASS] POWER OVERLOAD DA DUOC XU LY AN TOAN.\n");
        printf("[PASS] %.1f kW <= %.1f kW\n",
               tram->cong_suat_hien_tai, tram->cong_suat_toi_da);
    } else {
        printf("[FAIL] Tram van dang vuot cong suat toi da!\n");
    }
    printf("====================================================================\n\n");
}

