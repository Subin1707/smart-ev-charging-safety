#include <stdio.h>
#include <string.h>
#include "../test_helper.h"
#include "xe_dien.h"
#include "trang_thai_xe.h"

int main(void) {
    printf("=== RUNNING UNIT TEST: XE DIEN ===\n");

    XeDien xe;
    khoi_tao_xe_dien(&xe, 1, "EV01", 60.0f, 35.0f, 30.0f, 22.0f, KB_BINH_THUONG);

    ASSERT_EQ(xe.id, 1, "Vehicle ID should be 1");
    ASSERT_TRUE(strcmp(xe.ma_xe, "EV01") == 0, "Vehicle code should be EV01");
    ASSERT_FLOAT_EQ(xe.pin.soc, 35.0f, 0.01f, "Initial SOC should be 35.0%");
    ASSERT_EQ(xe.da_ket_noi, 0, "Initial connected state should be NO");
    ASSERT_EQ(xe.da_xac_thuc, 0, "Initial auth state should be NO");
    ASSERT_EQ(xe.trang_thai, XE_CHO, "Initial state should be XE_CHO");

    XeDien ds[SO_XE_TOI_DA];
    khoi_tao_danh_sach_5_xe(ds);
    ASSERT_TRUE(strcmp(ds[0].ma_xe, "EV01") == 0, "First vehicle should be EV01");
    ASSERT_TRUE(strcmp(ds[4].ma_xe, "EV05") == 0, "Fifth vehicle should be EV05");

    PRINT_TEST_RESULT("UNIT_XE_DIEN");
    return g_tests_failed > 0 ? 1 : 0;
}
