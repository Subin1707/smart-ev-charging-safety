#include <stdio.h>
#include <string.h>
#include "xe_dien.h"
#include "trang_thai_xe.h"

void khoi_tao_xe_dien(XeDien *xe,
                      int id,
                      const char *ma_xe,
                      float dung_luong,
                      float soc,
                      float nhiet_do,
                      float cong_suat_max,
                      LoaiKichBan kich_ban) {
    if (!xe) return;

    xe->id = id;
    if (ma_xe) {
        strncpy(xe->ma_xe, ma_xe, sizeof(xe->ma_xe) - 1);
        xe->ma_xe[sizeof(xe->ma_xe) - 1] = '\0';
    } else {
        snprintf(xe->ma_xe, sizeof(xe->ma_xe), "EV%02d", id);
    }

    khoi_tao_pin(&xe->pin, dung_luong, soc, nhiet_do);
    xe->cong_suat_sac_toi_da = (cong_suat_max > 0.0f) ? cong_suat_max : 22.0f;
    xe->assigned_port = -1;
    xe->da_ket_noi = 0;
    xe->da_xac_thuc = 0;
    xe->trang_thai = XE_CHO;
    xe->kich_ban = kich_ban;
}

void khoi_tao_danh_sach_5_xe(XeDien danh_sach[]) {
    if (!danh_sach) return;

    /* EV01: Ká»‹ch báº£n bĂ¬nh thÆ°á»ng */
    khoi_tao_xe_dien(&danh_sach[0], 1, "EV01", 60.0f, 25.0f, 31.0f, 22.0f, KB_BINH_THUONG);

    /* EV02: Ká»‹ch báº£n kiá»ƒm tra quĂ¡ nhiá»‡t */
    khoi_tao_xe_dien(&danh_sach[1], 2, "EV02", 75.0f, 48.0f, 32.0f, 22.0f, KB_QUA_NHIET);

    /* EV03: Ká»‹ch báº£n kiá»ƒm tra lá»—i xĂ¡c thá»±c token */
    khoi_tao_xe_dien(&danh_sach[2], 3, "EV03", 50.0f, 72.0f, 29.5f, 22.0f, KB_LOI_XAC_THUC);

    /* EV04: Ká»‹ch báº£n kiá»ƒm tra pin Ä‘áº§y */
    khoi_tao_xe_dien(&danh_sach[3], 4, "EV04", 80.0f, 100.0f, 33.0f, 22.0f, KB_PIN_DAY);

    /* EV05: Ká»‹ch báº£n kiá»ƒm tra dá»«ng kháº©n cáº¥p */
    khoi_tao_xe_dien(&danh_sach[4], 5, "EV05", 100.0f, 15.0f, 30.0f, 22.0f, KB_DUNG_KHAN_CAP);

    khoi_tao_xe_dien(&danh_sach[5], 6, "EV06", 70.0f, 20.0f, 30.0f, 22.0f, KB_BINH_THUONG);
    khoi_tao_xe_dien(&danh_sach[6], 7, "EV07", 70.0f, 20.0f, 30.0f, 22.0f, KB_BINH_THUONG);
}

void in_thong_tin_xe(const XeDien *xe) {
    if (!xe) return;

    printf("%s\n", xe->ma_xe);
    printf("------------------------\n");
    printf("Battery Capacity : %.1f kWh\n", xe->pin.dung_luong_kwh);
    printf("SOC              : %.1f %%\n", xe->pin.soc);
    printf("Temperature      : %.1f C\n", xe->pin.nhiet_do);
    printf("Max Power        : %.1f kW\n", xe->cong_suat_sac_toi_da);
    printf("Connected        : %s\n", xe->da_ket_noi ? "YES" : "NO");
    printf("Authenticated    : %s\n", xe->da_xac_thuc ? "YES" : "NO");
    printf("State            : %s\n", ten_trang_thai_xe(xe->trang_thai));
    printf("Scenario         : %s\n", ten_kich_ban(xe->kich_ban));
}

void in_danh_sach_xe(const XeDien danh_sach[], int so_luong) {
    if (!danh_sach || so_luong <= 0) return;

    printf("========================================================================================\n");
    printf("                              DANH SACH XE DIEN MAU\n");
    printf("========================================================================================\n");
    printf("%-6s %-12s %-10s %-12s %-12s %-14s %-15s\n",
           "ID", "CAPACITY", "SOC", "TEMP", "MAX POWER", "STATE", "SCENARIO");
    printf("----------------------------------------------------------------------------------------\n");

    for (int i = 0; i < so_luong; i++) {
        const XeDien *xe = &danh_sach[i];
        printf("%-6s %5.1f kWh    %5.1f %%    %5.1f C     %5.1f kW     %-14s %-15s\n",
               xe->ma_xe,
               xe->pin.dung_luong_kwh,
               xe->pin.soc,
               xe->pin.nhiet_do,
               xe->cong_suat_sac_toi_da,
               ten_trang_thai_xe(xe->trang_thai),
               ten_kich_ban(xe->kich_ban));
    }
    printf("========================================================================================\n");
}
