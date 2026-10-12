#include <stdio.h>
#include "../test_helper.h"
#include "cong_sac.h"

int main(void) {
    printf("=== RUNNING UNIT TEST: CONG SAC ===\n");

    CongSac cong;
    khoi_tao_cong_sac(&cong, 1);

    ASSERT_EQ(cong.id, 1, "Port ID should be 1");
    ASSERT_EQ(cong.vehicle_id, -1, "Port should be empty (vehicle_id = -1)");
    ASSERT_EQ(cong.trang_thai, CONG_RANH, "Initial state should be CONG_RANH");

    /* Ket noi xe 1 */
    int ret1 = ket_noi_xe_vao_cong(&cong, 1);
    ASSERT_TRUE(ret1, "Connecting vehicle 1 to empty port should succeed");
    ASSERT_EQ(cong.vehicle_id, 1, "Port vehicle_id should be 1");

    /* Thu ket noi xe 2 vao cong da co xe 1 -> Phai that bai (doc quyen cong) */
    int ret2 = ket_noi_xe_vao_cong(&cong, 2);
    ASSERT_FALSE(ret2, "Connecting vehicle 2 to occupied port should FAIL (SR07)");

    /* Dat cong suat */
    dat_cong_suat_cong(&cong, 20.0f);
    ASSERT_FLOAT_EQ(cong.cong_suat_kw, 20.0f, 0.01f, "Port power should be 20.0 kW");
    ASSERT_FLOAT_EQ(cong.dong_dien, 50.0f, 0.1f, "Current should be 50.0 A at 400V");

    /* Ngat ket noi */
    ngat_ket_noi_cong(&cong);
    ASSERT_EQ(cong.vehicle_id, -1, "Port vehicle_id should reset to -1");
    ASSERT_FLOAT_EQ(cong.cong_suat_kw, 0.0f, 0.01f, "Port power should reset to 0.0 kW");

    PRINT_TEST_RESULT("UNIT_CONG_SAC");
    return g_tests_failed > 0 ? 1 : 0;
}
