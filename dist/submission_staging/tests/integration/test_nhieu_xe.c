#include <stdio.h>
#include "../test_helper.h"
#include "tram_sac.h"
#include "xe_dien.h"

int main(void) {
    printf("=== RUNNING INTEGRATION TEST: 5 VEHICLES SIMULTANEOUS CONNECTION ===\n");

    TramSac tram;
    khoi_tao_tram_sac(&tram, "STATION-01");
    XeDien ds_xe[SO_XE_TOI_DA];
    khoi_tao_danh_sach_5_xe(ds_xe);

    for (int i = 0; i < SO_CONG_SAC; i++) {
        ASSERT_TRUE(ket_noi_xe_vao_tram(&tram, i, &ds_xe[i]), "Vehicle successfully assigned to designated port");
        ASSERT_EQ(tram.cong[i].vehicle_id, ds_xe[i].id, "Port vehicle ID matches");
    }
    for (int i = SO_CONG_SAC; i < SO_XE_TOI_DA; i++) {
        ASSERT_FALSE(ket_noi_xe_vao_tram(&tram, i, &ds_xe[i]), "Overflow vehicles must wait instead of accessing nonexistent ports");
        ASSERT_EQ(ds_xe[i].da_ket_noi, 0, "Waiting vehicle remains disconnected");
    }

    PRINT_TEST_RESULT("INTEGRATION_MULTI_VEHICLE");
    return g_tests_failed > 0 ? 1 : 0;
}
