#include <stdio.h>
#include "../test_helper.h"
#include "tram_sac.h"
#include "xe_dien.h"
#include "quan_ly_cong_suat.h"

int main(void) {
    printf("=== RUNNING INTEGRATION TEST: POWER OVERLOAD PROTECTION ===\n");

    TramSac tram;
    khoi_tao_tram_sac(&tram, "STATION-01");
    XeDien ds[SO_XE_TOI_DA];
    khoi_tao_danh_sach_5_xe(ds);

    for (int i = 0; i < SO_XE_TOI_DA; i++) {
        tram.cong[i].trang_thai = CONG_DANG_SAC;
        tram.cong[i].cong_suat_kw = 22.0f;
    }

    xu_ly_qua_tai_cong_suat(&tram, ds, SO_XE_TOI_DA);

    ASSERT_FLOAT_EQ(tram.cong_suat_hien_tai, 100.0f, 0.01f, "Total power after overload management must be <= 100 kW");

    PRINT_TEST_RESULT("INTEGRATION_POWER_DISTRIBUTION");
    return g_tests_failed > 0 ? 1 : 0;
}
