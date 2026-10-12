#include <stdio.h>
#include "../test_helper.h"
#include "tram_sac.h"
#include "xe_dien.h"
#include "dung_khan_cap.h"

int main(void) {
    printf("=== RUNNING INTEGRATION TEST: EMERGENCY CUTOFF ===\n");

    TramSac tram;
    khoi_tao_tram_sac(&tram, "STATION-01");
    XeDien ds[SO_XE_TOI_DA];
    khoi_tao_danh_sach_5_xe(ds);

    for (int i = 0; i < SO_XE_TOI_DA; i++) {
        tram.cong[i].trang_thai = CONG_DANG_SAC;
        tram.cong[i].cong_suat_kw = 20.0f;
    }

    kich_hoat_dung_khan_cap_tram(&tram, ds, SO_XE_TOI_DA);

    ASSERT_EQ(tram.emergency, 1, "Station emergency flag should be TRUE");
    ASSERT_FLOAT_EQ(tram.cong_suat_hien_tai, 0.0f, 0.01f, "Total station power must be 0 kW");
    for (int i = 0; i < SO_CONG_SAC; i++) {
        ASSERT_FLOAT_EQ(tram.cong[i].cong_suat_kw, 0.0f, 0.01f, "All port power must be 0 kW");
        ASSERT_EQ(tram.cong[i].trang_thai, CONG_DUNG, "All ports should transition to CONG_DUNG");
    }

    PRINT_TEST_RESULT("INTEGRATION_EMERGENCY");
    return g_tests_failed > 0 ? 1 : 0;
}
