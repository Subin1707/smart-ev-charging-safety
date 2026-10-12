#include <stdio.h>
#include "sinh_kich_ban.h"
#include "ngau_nhien.h"
#include <stdlib.h>
#include <string.h>

void thiet_lap_kich_ban_co_dinh(XeDien ds_xe[]) {
    if (!ds_xe) return;

    /* EV01: NORMAL - sáº¡c á»•n Ä‘á»‹nh */
    khoi_tao_xe_dien(&ds_xe[0], 1, "EV01", 60.0f, 25.0f, 30.0f, 22.0f, KB_BINH_THUONG);

    /* EV02: OVERHEAT - gáº·p quĂ¡ nhiá»‡t táº¡i tick 5 */
    khoi_tao_xe_dien(&ds_xe[1], 2, "EV02", 75.0f, 45.0f, 32.0f, 22.0f, KB_QUA_NHIET);

    /* EV03: AUTH_FAILURE - sai token xĂ¡c thá»±c */
    khoi_tao_xe_dien(&ds_xe[2], 3, "EV03", 50.0f, 60.0f, 29.0f, 22.0f, KB_LOI_XAC_THUC);

    /* EV04: BATTERY_FULL - báº¯t Ä‘áº§u á»Ÿ 96% vĂ  Ä‘áº§y 100% táº¡i tick 6 */
    khoi_tao_xe_dien(&ds_xe[3], 4, "EV04", 60.0f, 96.0f, 31.0f, 22.0f, KB_PIN_DAY);

    /* EV05: EMERGENCY - kĂ­ch hoáº¡t dá»«ng kháº©n cáº¥p táº¡i tick 8 */
    khoi_tao_xe_dien(&ds_xe[4], 5, "EV05", 100.0f, 15.0f, 30.0f, 22.0f, KB_DUNG_KHAN_CAP);

    printf("[SCENARIO] Da nap ká»‹ch ban co dinh (Fixed Safety Demo):\n");
    const char *scenario = getenv("SMART_EV_SCENARIO");
    if (scenario && strcmp(scenario, "GOLDEN_OVERHEAT") == 0) {
        khoi_tao_xe_dien(&ds_xe[2], 3, "EV03", 50.0f, 12.0f, 35.0f, 22.0f, KB_BINH_THUONG);
        printf("[GOLDEN] EV03: SOC=12, temperature=35, valid token; inject overheat through API.\n");
    }
    printf("  EV01 -> NORMAL\n");
    printf("  EV02 -> OVERHEAT (su co qua nhiet tai Tick 5)\n");
    printf("  EV03 -> AUTH_FAILURE (sai token xac thuc)\n");
    printf("  EV04 -> BATTERY_FULL (day 100%% tai Tick 6)\n");
    printf("  EV05 -> EMERGENCY (dung khan cap tai Tick 8)\n\n");
}

void thiet_lap_kich_ban_ngau_nhien(XeDien ds_xe[]) {
    if (!ds_xe) return;

    LoaiKichBan cac_kb[] = {
        KB_BINH_THUONG,
        KB_PIN_THAP,
        KB_QUA_NHIET,
        KB_LOI_XAC_THUC,
        KB_DUNG_KHAN_CAP
    };

    for (int i = 0; i < SO_XE_TOI_DA; i++) {
        char ma_xe[16];
        snprintf(ma_xe, sizeof(ma_xe), "EV%02d", i + 1);

        float cap = (float)sinh_so_nguyen_ngau_nhien(50, 100);
        float soc = (float)sinh_so_nguyen_ngau_nhien(15, 80);
        float temp = sinh_so_thuc_ngau_nhien(28.0f, 35.0f);
        LoaiKichBan kb = cac_kb[sinh_so_nguyen_ngau_nhien(0, 4)];

        khoi_tao_xe_dien(&ds_xe[i], i + 1, ma_xe, cap, soc, temp, 22.0f, kb);
    }

    printf("[SCENARIO] Da sinh ngau nhien thong so cho 5 xe dien.\n\n");
}
