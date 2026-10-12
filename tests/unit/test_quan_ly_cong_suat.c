#include <stdio.h>
#include "../test_helper.h"
#include "quan_ly_cong_suat.h"
#include "tram_sac.h"

int main(void) {
    printf("=== RUNNING UNIT TEST: QUAN LY CONG SUAT (BVA 99, 100, 101 kW) ===\n");

    TramSac tram;
    khoi_tao_tram_sac(&tram, "STATION-01");

    /* BVA Power: 99.0 kW, 100.0 kW, 101.0 kW */
    ASSERT_TRUE(tram.cong_suat_toi_da >= 99.0f, "BVA: 99.0 kW is within station limit");
    ASSERT_TRUE(tram.cong_suat_toi_da >= 100.0f, "BVA: 100.0 kW is exactly at station limit");
    ASSERT_FALSE(101.0f <= tram.cong_suat_toi_da, "BVA: 101.0 kW exceeds station limit");

    /* Test phan phoi chia deu khi 5 cong deu dang sac */
    for (int i = 0; i < SO_CONG_SAC; i++) {
        tram.cong[i].trang_thai = CONG_DANG_SAC;
        tram.cong[i].cong_suat_kw = 22.0f;
    }

    phan_phoi_cong_suat_chia_deu(&tram);

    for (int i = 0; i < SO_CONG_SAC; i++) {
        ASSERT_FLOAT_EQ(tram.cong[i].cong_suat_kw, 20.0f, 0.01f, "Each port should receive 20.0 kW");
    }
    ASSERT_FLOAT_EQ(tram.cong_suat_hien_tai, 100.0f, 0.01f, "Total station power must be exactly 100.0 kW");

    XeDien vehicles[SO_XE_TOI_DA];
    khoi_tao_danh_sach_5_xe(vehicles);
    for (int i = 0; i < SO_CONG_SAC; i++) {
        tram.cong[i].vehicle_id = vehicles[i].id;
        vehicles[i].pin.soc = 70;
    }
    vehicles[4].pin.soc = 10;
    tram.cong_suat_toi_da = 30;
    phan_phoi_cong_suat_theo_soc(&tram, vehicles, SO_XE_TOI_DA);
    ASSERT_FLOAT_EQ(tram.cong[4].cong_suat_kw, 22, 0.001f, "SR11 low SOC gets priority even on last port");
    ASSERT_FLOAT_EQ(tram.cong[0].cong_suat_kw, 2, 0.001f, "Other vehicles share remaining capacity");
    ASSERT_FLOAT_EQ(tram.cong_suat_hien_tai, 30, 0.001f, "SR10 limited supply is respected");
    PRINT_TEST_RESULT("UNIT_POWER_MANAGER");
    return g_tests_failed > 0 ? 1 : 0;
}
