#include <stdio.h>
#include "../test_helper.h"
#include "tram_sac.h"
#include "xe_dien.h"
#include "token.h"
#include "xac_thuc.h"
#include "phien_sac.h"
#include "dieu_khien_sac.h"
#include "dung_khan_cap.h"

int main(void) {
    printf("=== RUNNING INTEGRATION TEST: CONNECT -> AUTH -> CHARGE ===\n");

    TramSac tram;
    khoi_tao_tram_sac(&tram, "STATION-01");

    XeDien xe1, xe2, xe4;
    khoi_tao_xe_dien(&xe1, 1, "EV01", 60.0f, 25.0f, 30.0f, 22.0f, KB_BINH_THUONG);
    khoi_tao_xe_dien(&xe2, 2, "EV02", 60.0f, 30.0f, 30.0f, 22.0f, KB_LOI_XAC_THUC);
    khoi_tao_xe_dien(&xe4, 4, "EV04", 60.0f, 40.0f, 30.0f, 22.0f, KB_BINH_THUONG);

    /* CASE 1: Xe 1 há»£p lá»‡: CONNECT -> AUTH OK -> START CHARGE */
    ASSERT_TRUE(ket_noi_xe_vao_tram(&tram, 0, &xe1), "EV01 connected to Port 1");
    char token1[DO_DAI_TOKEN];
    sinh_token_xe(xe1.ma_xe, token1, sizeof(token1));
    ASSERT_TRUE(xac_thuc_xe(&xe1, token1), "EV01 authenticated with correct token");

    PhienSac phien1;
    ASSERT_TRUE(bat_dau_sac(&xe1, &tram.cong[0], &phien1, 22.0f), "EV01 starts charging successfully");
    ASSERT_EQ(tram.cong[0].trang_thai, CONG_DANG_SAC, "Port 1 state is CONG_DANG_SAC");

    /* CASE 2: Xe 2 sai token: CONNECT -> AUTH FAIL -> CHARGING DENIED */
    ASSERT_TRUE(ket_noi_xe_vao_tram(&tram, 1, &xe2), "EV02 connected to Port 2");
    ASSERT_FALSE(xac_thuc_xe(&xe2, "WRONG_TOKEN"), "EV02 auth fails with WRONG_TOKEN");

    PhienSac phien2;
    ASSERT_FALSE(bat_dau_sac(&xe2, &tram.cong[1], &phien2, 22.0f), "EV02 charging is DENIED due to unauthenticated state");
    ASSERT_EQ(tram.cong[1].trang_thai, CONG_DA_KET_NOI, "Port 2 remains in CONG_DA_KET_NOI without charging");

    /* CASE 3: CONNECT -> AUTH OK -> START -> EMERGENCY -> CHARGING STOP + POWER 0 */
    cap_nhat_tong_cong_suat_tram(&tram);
    ASSERT_FLOAT_EQ(tram.cong[0].cong_suat_kw, 22.0f, 0.01f, "EV01 has allocated charging power before emergency");
    kich_hoat_dung_khan_cap_tram(&tram, &xe1, 1);
    ASSERT_EQ(tram.emergency, 1, "Emergency flag is set after emergency stop");
    ASSERT_FLOAT_EQ(tram.cong_suat_hien_tai, 0.0f, 0.01f, "Emergency cuts total station power to 0");
    ASSERT_FLOAT_EQ(tram.cong[0].cong_suat_kw, 0.0f, 0.01f, "Emergency cuts charging port power to 0");
    ASSERT_EQ(tram.cong[0].trang_thai, CONG_DUNG, "Charging port transitions to stopped after emergency");
    tram.emergency = 0;

    /* CASE 4: CONNECT -> AUTH OK -> DISCONNECT -> authenticated resets to 0 */
    ASSERT_TRUE(ket_noi_xe_vao_tram(&tram, 3, &xe4), "EV04 connected to Port 4");
    char token4[DO_DAI_TOKEN];
    sinh_token_xe(xe4.ma_xe, token4, sizeof(token4));
    ASSERT_TRUE(xac_thuc_xe(&xe4, token4), "EV04 authenticated before disconnect");
    ASSERT_EQ(xe4.da_xac_thuc, 1, "EV04 auth flag is set before disconnect");
    ASSERT_TRUE(ngat_ket_noi_xe_khoi_tram(&tram, 3, &xe4), "EV04 disconnected from Port 4");
    ASSERT_EQ(xe4.da_ket_noi, 0, "EV04 connected flag resets after disconnect");
    ASSERT_EQ(xe4.da_xac_thuc, 0, "EV04 authenticated flag resets after disconnect");

    XeDien disconnected;
    khoi_tao_xe_dien(&disconnected, 3, "EV03", 60, 12, 35, 22, KB_BINH_THUONG);
    char token3[DO_DAI_TOKEN];
    sinh_token_xe(disconnected.ma_xe, token3, sizeof(token3));
    ASSERT_FALSE(xac_thuc_xe(&disconnected, token3), "SR01 rejects authentication before connection");
    xe1.trang_thai = XE_LOI;
    ASSERT_FALSE(bat_dau_sac(&xe1, &tram.cong[0], &phien1, 22), "SR06 rejects direct FAULT to CHARGING");
    PRINT_TEST_RESULT("INTEGRATION_CONNECT_AUTH_CHARGE");
    return g_tests_failed > 0 ? 1 : 0;
}
