#include <stdio.h>
#include "../test_helper.h"
#include "tram_sac.h"
#include "xe_dien.h"
#include "token.h"
#include "xac_thuc.h"
#include "phien_sac.h"
#include "dieu_khien_sac.h"
#include "giam_sat_an_toan.h"

int main(void) {
    printf("=== RUNNING E2E TEST: FULL BATTERY CUTOFF ===\n");

    TramSac tram;
    khoi_tao_tram_sac(&tram, "STATION-01");
    XeDien xe;
    khoi_tao_xe_dien(&xe, 4, "EV04", 60.0f, 98.0f, 31.0f, 22.0f, KB_PIN_DAY);

    ket_noi_xe_vao_tram(&tram, 3, &xe);
    char token[DO_DAI_TOKEN];
    sinh_token_xe(xe.ma_xe, token, sizeof(token));
    xac_thuc_xe(&xe, token);

    PhienSac p;
    bat_dau_sac(&xe, &tram.cong[3], &p, 22.0f);

    /* Pin sáº¡c Ä‘áº§y 100% */
    xe.pin.soc = 100.0f;
    giam_sat_xe_va_cong(&xe, &tram.cong[3], &tram);

    ASSERT_EQ(tram.cong[3].trang_thai, CONG_DUNG, "Port transitions to CONG_DUNG on full battery (SR04)");
    ASSERT_FLOAT_EQ(tram.cong[3].cong_suat_kw, 0.0f, 0.01f, "Power cut off to 0 kW");

    PRINT_TEST_RESULT("E2E_BATTERY_FULL_FLOW");
    return g_tests_failed > 0 ? 1 : 0;
}
