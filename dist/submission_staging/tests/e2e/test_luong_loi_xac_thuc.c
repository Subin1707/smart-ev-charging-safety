#include <stdio.h>
#include "../test_helper.h"
#include "tram_sac.h"
#include "xe_dien.h"
#include "xac_thuc.h"
#include "phien_sac.h"
#include "dieu_khien_sac.h"

int main(void) {
    printf("=== RUNNING E2E TEST: AUTH FAILURE REJECTION ===\n");

    TramSac tram;
    khoi_tao_tram_sac(&tram, "STATION-01");
    XeDien xe;
    khoi_tao_xe_dien(&xe, 3, "EV03", 50.0f, 60.0f, 29.0f, 22.0f, KB_LOI_XAC_THUC);

    ket_noi_xe_vao_tram(&tram, 2, &xe);
    ASSERT_FALSE(xac_thuc_xe(&xe, "BAD_TOKEN"), "Token check rejected");

    PhienSac p;
    ASSERT_FALSE(bat_dau_sac(&xe, &tram.cong[2], &p, 22.0f), "Charging refused for unauthenticated vehicle");
    ASSERT_FLOAT_EQ(tram.cong[2].cong_suat_kw, 0.0f, 0.01f, "No power allocated");

    PRINT_TEST_RESULT("E2E_AUTH_FAIL_FLOW");
    return g_tests_failed > 0 ? 1 : 0;
}
