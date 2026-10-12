#include <stdio.h>
#include <string.h>
#include "hang_so.h"
#include "kieu_du_lieu.h"
#include "cau_hinh.h"
#include "he_thong.h"
#include "pin.h"
#include "xe_dien.h"
#include "trang_thai_xe.h"
#include "tram_sac.h"
#include "cong_sac.h"
#include "quan_ly_cong_suat.h"
#include "dieu_khien_sac.h"
#include "xac_thuc.h"
#include "dung_khan_cap.h"
#include "phien_sac.h"
#include "logger.h"
#include "nhat_ky_su_kien.h"
#include "sinh_kich_ban.h"
#include "ngau_nhien.h"
#include "mo_phong.h"
#include "database.h"

static void xoa_dong_nhap(void) {
    char dong[128];
    fgets(dong, sizeof(dong), stdin);
}

static void nhan_enter_quay_lai(void) {
    printf("\nNhan Enter de quay lai menu...");
    xoa_dong_nhap();
}

static void in_kich_ban_ngau_nhien(const XeDien ds_xe[], int so_xe, unsigned int seed) {
    printf("\n============================================================\n");
    printf("                  RANDOM SIMULATION\n");
    printf("============================================================\n");
    printf("\nSimulation Seed: %u\n", seed);
    printf("------------------------------------------------------------\n");
    for (int i = 0; i < so_xe; i++) {
        printf("%-5s -> %-14s | SOC %5.1f%% | Temp %5.1f C\n",
               ds_xe[i].ma_xe,
               ten_kich_ban(ds_xe[i].kich_ban),
               ds_xe[i].pin.soc,
               ds_xe[i].pin.nhiet_do);
    }
    printf("------------------------------------------------------------\n\n");
}

static void in_menu_chinh(void) {
    printf("\n============================================================\n");
    printf("       SMART EV CHARGING SAFETY SYSTEM\n");
    printf("============================================================\n");
    printf("1. Mo phong ngau nhien 5 xe\n");
    printf("2. Chay kich ban demo an toan\n");
    printf("3. Xem trang thai tram\n");
    printf("4. Xem thong tin 5 xe\n");
    printf("5. Dieu khien thu cong\n");
    printf("6. Xem su kien an toan\n");
    printf("7. Power Overload Demo\n");
    printf("8. Xem lich su su kien an toan\n");
    printf("9. Xem lich su su kien tu PostgreSQL\n");
    printf("0. Thoat\n");
    printf("\nLua chon: ");
}

static int tim_xe(const XeDien ds_xe[], const char *ma_xe) {
    if (!ds_xe || !ma_xe) return -1;

    for (int i = 0; i < SO_XE_TOI_DA; i++) {
        if (strcmp(ds_xe[i].ma_xe, ma_xe) == 0) return i;
    }
    return -1;
}

static int nhap_cong(void) {
    int cong;
    if (scanf("%d", &cong) != 1) {
        xoa_dong_nhap();
        return -1;
    }
    xoa_dong_nhap();
    return (cong >= 1 && cong <= SO_CONG_SAC) ? cong - 1 : -1;
}

static int tim_xe_tren_cong(const TramSac *tram, const XeDien ds_xe[], int cong_idx) {
    if (!tram || !ds_xe || cong_idx < 0 || cong_idx >= SO_CONG_SAC) return -1;

    for (int i = 0; i < SO_XE_TOI_DA; i++) {
        if (ds_xe[i].id == tram->cong[cong_idx].vehicle_id) return i;
    }
    return -1;
}

static void nhap_ma_xe(char *ma_xe, size_t kich_thuoc) {
    if (!fgets(ma_xe, kich_thuoc, stdin)) {
        ma_xe[0] = '\0';
        return;
    }
    ma_xe[strcspn(ma_xe, "\r\n")] = '\0';
}

static void dieu_khien_thu_cong(TramSac *tram, XeDien ds_xe[], PhienSac ds_phien[]) {
    int lua_chon = -1;

    while (lua_chon != 0) {
        printf("\n================================================\n");
        printf("         DIEU KHIEN TRAM SAC THU CONG\n");
        printf("================================================\n");
        printf("1. Ket noi xe vao cong\n");
        printf("2. Xac thuc xe\n");
        printf("3. Bat dau sac\n");
        printf("4. Dung sac\n");
        printf("5. Ngat ket noi\n");
        printf("6. Dung khan cap\n");
        printf("7. Xem trang thai\n");
        printf("0. Quay lai\n");
        printf("\nChon: ");

        if (scanf("%d", &lua_chon) != 1) {
            xoa_dong_nhap();
            printf("[ERROR] Vui long nhap mot so.\n");
            continue;
        }
        xoa_dong_nhap();

        if (lua_chon == 1) {
            char ma_xe[DO_DAI_MA_XE];
            printf("Nhap xe: ");
            nhap_ma_xe(ma_xe, sizeof(ma_xe));
            int xe_idx = tim_xe(ds_xe, ma_xe);
            printf("Nhap cong (1-%d): ", SO_CONG_SAC);
            int cong_idx = nhap_cong();
            if (xe_idx < 0) {
                printf("[ERROR] Khong tim thay xe %s.\n", ma_xe);
            } else if (cong_idx < 0 || !ket_noi_xe_vao_tram(tram, cong_idx, &ds_xe[xe_idx])) {
                printf("[ERROR] Khong the ket noi %s vao cong.\n", ma_xe);
            } else {
                printf("[OK] %s da ket noi vao Cong %d.\n", ma_xe, cong_idx + 1);
            }
        } else if (lua_chon == 2) {
            char ma_xe[DO_DAI_MA_XE];
            char token[DO_DAI_TOKEN];
            printf("Nhap xe: ");
            nhap_ma_xe(ma_xe, sizeof(ma_xe));
            int xe_idx = tim_xe(ds_xe, ma_xe);
            if (xe_idx < 0) {
                printf("[ERROR] Khong tim thay xe %s.\n", ma_xe);
                continue;
            }
            printf("Nhap token: ");
            nhap_ma_xe(token, sizeof(token));
            if (!xac_thuc_xe(&ds_xe[xe_idx], token)) {
                ghi_su_kien_an_toan(0, ds_xe[xe_idx].ma_xe, 0,
                                    "AUTH_FAILURE", MUC_WARNING, "ACCESS_DENIED");
                luu_su_kien_an_toan_postgresql(0, ds_xe[xe_idx].ma_xe, 0,
                                               "AUTH_FAILURE", "WARNING", "ACCESS_DENIED");
            }
        } else if (lua_chon == 3) {
            char ma_xe[DO_DAI_MA_XE];
            printf("Nhap xe: ");
            nhap_ma_xe(ma_xe, sizeof(ma_xe));
            int xe_idx = tim_xe(ds_xe, ma_xe);
            int cong_idx = -1;
            if (xe_idx >= 0) {
                for (int i = 0; i < SO_CONG_SAC; i++) {
                    if (tram->cong[i].vehicle_id == ds_xe[xe_idx].id) cong_idx = i;
                }
            }
            if (xe_idx < 0) {
                printf("[ERROR] Khong tim thay xe %s.\n", ma_xe);
            } else if (cong_idx < 0) {
                printf("[ERROR] Xe chua duoc ket noi vao cong.\n");
            } else {
                if (!bat_dau_sac(&ds_xe[xe_idx], &tram->cong[cong_idx], &ds_phien[cong_idx],
                                 ds_xe[xe_idx].cong_suat_sac_toi_da)) {
                    ghi_su_kien_an_toan(0, ds_xe[xe_idx].ma_xe, cong_idx + 1,
                                        "START_BLOCKED", MUC_WARNING, "CHARGING_DENIED");
                    luu_su_kien_an_toan_postgresql(0, ds_xe[xe_idx].ma_xe, cong_idx + 1,
                                                   "START_BLOCKED", "WARNING", "CHARGING_DENIED");
                }
                cap_nhat_tong_cong_suat_tram(tram);
            }
        } else if (lua_chon == 4) {
            printf("Nhap cong (1-%d): ", SO_CONG_SAC);
            int cong_idx = nhap_cong();
            int xe_idx = tim_xe_tren_cong(tram, ds_xe, cong_idx);
            if (cong_idx < 0) {
                printf("[ERROR] Cong khong hop le.\n");
            } else {
                dung_sac(xe_idx >= 0 ? &ds_xe[xe_idx] : NULL,
                         &tram->cong[cong_idx], &ds_phien[cong_idx]);
                cap_nhat_tong_cong_suat_tram(tram);
            }
        } else if (lua_chon == 5) {
            printf("Nhap cong (1-%d): ", SO_CONG_SAC);
            int cong_idx = nhap_cong();
            int xe_idx = tim_xe_tren_cong(tram, ds_xe, cong_idx);
            if (cong_idx < 0) {
                printf("[ERROR] Cong khong hop le.\n");
            } else {
                if (xe_idx >= 0 && tram->cong[cong_idx].trang_thai == CONG_DANG_SAC) {
                    dung_sac(&ds_xe[xe_idx], &tram->cong[cong_idx], &ds_phien[cong_idx]);
                }
                ngat_ket_noi_xe_khoi_tram(tram, cong_idx,
                                           xe_idx >= 0 ? &ds_xe[xe_idx] : NULL);
                printf("[OK] Da ngat ket noi Cong %d.\n", cong_idx + 1);
            }
        } else if (lua_chon == 6) {
            printf("Nhap cong dung khan cap (1-%d): ", SO_CONG_SAC);
            int cong_idx = nhap_cong();
            int xe_idx = tim_xe_tren_cong(tram, ds_xe, cong_idx);
            if (cong_idx < 0) {
                printf("[ERROR] Cong khong hop le.\n");
            } else {
                kich_hoat_dung_khan_cap_cong(&tram->cong[cong_idx],
                                              xe_idx >= 0 ? &ds_xe[xe_idx] : NULL);
                ghi_su_kien_an_toan(0,
                                    xe_idx >= 0 ? ds_xe[xe_idx].ma_xe : "--",
                                    cong_idx + 1,
                                    "MANUAL_EMERGENCY",
                                    MUC_CRITICAL,
                                    "POWER_CUT");
                luu_su_kien_an_toan_postgresql(0,
                                               xe_idx >= 0 ? ds_xe[xe_idx].ma_xe : "--",
                                               cong_idx + 1,
                                               "MANUAL_EMERGENCY", "CRITICAL", "POWER_CUT");
                cap_nhat_tong_cong_suat_tram(tram);
            }
        } else if (lua_chon == 7) {
            hien_thi_dashboard(tram, ds_xe, SO_XE_TOI_DA);
        } else if (lua_chon != 0) {
            printf("[ERROR] Lua chon khong hop le.\n");
        }
    }
}

int main(void) {
    khoi_tao_he_thong();
    khoi_tao_nhat_ky();

    /* 1. Khoi tao logger va database persistence */
    khoi_tao_logger("logs/simulation/run_demo.log");
    khoi_tao_database("logs/database/persistence.sql");
    ket_noi_postgresql();

    XeDien ds_xe[SO_XE_TOI_DA];
    PhienSac ds_phien[SO_CONG_SAC] = {0};
    TramSac tram;
    khoi_tao_danh_sach_5_xe(ds_xe);
    khoi_tao_tram_sac(&tram, "STATION-01");

    int lua_chon = -1;
    while (lua_chon != 0) {
        in_menu_chinh();
        if (scanf("%d", &lua_chon) != 1) {
            xoa_dong_nhap();
            printf("[ERROR] Vui long nhap mot so.\n");
            continue;
        }
        xoa_dong_nhap();

        if (lua_chon == 1) {
            unsigned int seed;
            khoi_tao_danh_sach_5_xe(ds_xe);
            khoi_tao_tram_sac(&tram, "STATION-01");

            printf("\nNhap seed (0 = tu dong): ");
            if (scanf("%u", &seed) != 1) {
                seed = 0;
            }
            xoa_dong_nhap();

            seed = khoi_tao_ngau_nhien(seed);
            thiet_lap_kich_ban_ngau_nhien(ds_xe);
            in_kich_ban_ngau_nhien(ds_xe, SO_XE_TOI_DA, seed);
            chay_mo_phong(&tram, ds_xe, SO_XE_TOI_DA, 10, 0, seed);
            nhan_enter_quay_lai();
        } else if (lua_chon == 2) {
            khoi_tao_danh_sach_5_xe(ds_xe);
            khoi_tao_tram_sac(&tram, "STATION-01");
            printf(">>> KICH HOAT FIXED SAFETY DEMONSTRATION (10 TICKS) <<<\n");
            thiet_lap_kich_ban_co_dinh(ds_xe);
            chay_mo_phong(&tram, ds_xe, SO_XE_TOI_DA, 10, 1, 0);
            nhan_enter_quay_lai();
        } else if (lua_chon == 3) {
            hien_thi_dashboard(&tram, ds_xe, SO_XE_TOI_DA);
            nhan_enter_quay_lai();
        } else if (lua_chon == 4) {
            in_danh_sach_xe(ds_xe, SO_XE_TOI_DA);
            nhan_enter_quay_lai();
        } else if (lua_chon == 5) {
            dieu_khien_thu_cong(&tram, ds_xe, ds_phien);
        } else if (lua_chon == 6) {
            in_tong_ket_nhat_ky();
            nhan_enter_quay_lai();
        } else if (lua_chon == 7) {
            chay_demo_qua_tai_cong_suat(&tram, ds_xe, SO_XE_TOI_DA);
            nhan_enter_quay_lai();
        } else if (lua_chon == 8) {
            in_lich_su_su_kien_an_toan();
            nhan_enter_quay_lai();
        } else if (lua_chon == 9) {
            in_lich_su_su_kien_postgresql();
            nhan_enter_quay_lai();
        } else if (lua_chon != 0) {
            printf("[ERROR] Lua chon khong hop le.\n");
        }
    }

    printf("\nThoat chuong trinh.\n");

    /* Dong file database snapshot va dong bo vao PostgreSQL */
    dong_database();
    printf("\n[DATABASE] Dang nap du lieu vao PostgreSQL database...\n");
    dong_bo_vao_postgresql();
    ngat_ket_noi_postgresql();

    dong_logger();
    giai_phong_he_thong();

    return 0;
}
