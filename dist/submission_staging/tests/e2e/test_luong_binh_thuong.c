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
    printf("=== RUNNING E2E TEST: NORMAL CHARGING LIFECYCLE ===\n");

    TramSac tram;
    khoi_tao_tram_sac(&tram, "STATION-01");
    XeDien xe;
    khoi_tao_xe_dien(&xe, 1, "EV01", 60.0f, 30.0f, 30.0f, 22.0f, KB_BINH_THUONG);

    /* 1. Arrive and connect */
    ASSERT_TRUE(ket_noi_xe_vao_tram(&tram, 0, &xe), "Step 1: Connected");

    /* 2. Authentication */
    char token[DO_DAI_TOKEN];
    sinh_token_xe(xe.ma_xe, token, sizeof(token));
    ASSERT_TRUE(xac_thuc_xe(&xe, token), "Step 2: Authenticated");

    /* 3. Safety Check before charge */
    KetQuaGiamSat kq = giam_sat_xe_va_cong(&xe, &tram.cong[0], &tram);
    ASSERT_TRUE(kq.an_toan, "Step 3: Initial safety check passed");

    /* 4. Start Charging */
    PhienSac phien;
    ASSERT_TRUE(bat_dau_sac(&xe, &tram.cong[0], &phien, 22.0f), "Step 4: Charging started");

    /* 5. Simulate 10 charging steps */
    for (int i = 0; i < 10; i++) {
        cap_nhat_pin(&xe.pin, 22.0f, 0.05f);
        kq = giam_sat_xe_va_cong(&xe, &tram.cong[0], &tram);
        ASSERT_TRUE(kq.an_toan, "Step 5: In-flight safety check passed");
    }

    /* 6. Stop charging */
    dung_sac(&xe, &tram.cong[0], &phien);
    ASSERT_EQ(tram.cong[0].trang_thai, CONG_DUNG, "Step 6: Stopped cleanly");

    PRINT_TEST_RESULT("E2E_NORMAL_FLOW");
    return g_tests_failed > 0 ? 1 : 0;
}
