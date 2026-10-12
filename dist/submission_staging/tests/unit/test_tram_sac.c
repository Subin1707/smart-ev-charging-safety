#include <stdio.h>
#include "../test_helper.h"
#include "tram_sac.h"

int main(void) {
    printf("=== RUNNING UNIT TEST: TRAM SAC ===\n");

    TramSac tram;
    khoi_tao_tram_sac(&tram, "STATION-01");

    ASSERT_EQ(tram.id, 1, "Station ID should be 1");
    ASSERT_FLOAT_EQ(tram.cong_suat_toi_da, 100.0f, 0.01f, "Station max power should be 100.0 kW");
    ASSERT_FLOAT_EQ(tram.cong_suat_hien_tai, 0.0f, 0.01f, "Initial current power should be 0.0 kW");
    ASSERT_EQ(tram.emergency, 0, "Initial emergency should be 0");

    /* Thu dat cong suat 2 cong va cap nhat tong */
    dat_cong_suat_cong(&tram.cong[0], 22.0f);
    dat_cong_suat_cong(&tram.cong[1], 18.0f);
    float tong = cap_nhat_tong_cong_suat_tram(&tram);

    ASSERT_FLOAT_EQ(tong, 40.0f, 0.01f, "Total station power should be 40.0 kW");

    XeDien xe = {0}, other = {0};
    xe.id = 42;
    other.id = 43;
    ASSERT_EQ(ket_noi_xe_vao_tram(&tram, 0, &xe), 1, "Connect first port");
    ASSERT_EQ(ket_noi_xe_vao_tram(&tram, 1, &xe), 0, "SR08 one vehicle cannot occupy two ports");
    ASSERT_EQ(ket_noi_xe_vao_tram(&tram, 0, &other), 0, "SR07 one port cannot serve two vehicles");
    ASSERT_EQ(ngat_ket_noi_xe_khoi_tram(&tram, 0, &other), 0, "Wrong vehicle cannot disconnect owner");
    xe.da_xac_thuc = 1;
    ASSERT_EQ(ngat_ket_noi_xe_khoi_tram(&tram, 0, &xe), 1, "Owner disconnects");
    ASSERT_EQ(xe.da_xac_thuc, 0, "Disconnect invalidates authentication");
    PRINT_TEST_RESULT("UNIT_TRAM_SAC");
    return g_tests_failed > 0 ? 1 : 0;
}
