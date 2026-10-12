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
    printf("=== RUNNING E2E TEST: OVERHEAT SAFETY INTERVENTION ===\n");

    TramSac tram;
    khoi_tao_tram_sac(&tram, "STATION-01");
    XeDien xe;
    khoi_tao_xe_dien(&xe, 2, "EV02", 75.0f, 45.0f, 32.0f, 22.0f, KB_QUA_NHIET);

    ket_noi_xe_vao_tram(&tram, 1, &xe);
    char token[DO_DAI_TOKEN];
    sinh_token_xe(xe.ma_xe, token, sizeof(token));
    xac_thuc_xe(&xe, token);

    PhienSac phien;
    bat_dau_sac(&xe, &tram.cong[1], &phien, 22.0f);
    ASSERT_EQ(tram.cong[1].trang_thai, CONG_DANG_SAC, "Port 2 is charging");

    /* Nhiá»‡t Ä‘á»™ tÄƒng vá»t lĂªn 65 C */
    xe.pin.nhiet_do = 65.0f;
    KetQuaGiamSat kq = giam_sat_xe_va_cong(&xe, &tram.cong[1], &tram);

    ASSERT_FALSE(kq.an_toan, "Safety monitor detects overheat violation (SR03)");
    ASSERT_EQ(tram.cong[1].trang_thai, CONG_LOI, "Port 2 automatically transitions to FAULT");
    ASSERT_FLOAT_EQ(tram.cong[1].cong_suat_kw, 0.0f, 0.01f, "Port 2 power immediately cut off to 0 kW");

    PRINT_TEST_RESULT("E2E_OVERHEAT_FLOW");
    return g_tests_failed > 0 ? 1 : 0;
}
