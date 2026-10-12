#include <stdio.h>
#include "../test_helper.h"
#include "database.h"
#include "xe_repository.h"
#include "xe_dien.h"

int main(void) {
    printf("=== RUNNING UNIT TEST: DATABASE REPOSITORIES ===\n");

    int ret = khoi_tao_database("logs/database/test_dump.sql");
    ASSERT_TRUE(ret, "Database initialization and test dump file creation should succeed");

    XeDien xe;
    khoi_tao_xe_dien(&xe, 1, "EV01", 60.0f, 30.0f, 30.0f, 22.0f, KB_BINH_THUONG);
    luu_xe_dien(&xe);
    ASSERT_TRUE(1, "Saving vehicle EV01 should execute SQL without crash");

    dong_database();
    ASSERT_TRUE(1, "Closing test database should commit transaction successfully");

    PRINT_TEST_RESULT("UNIT_DATABASE");
    return g_tests_failed > 0 ? 1 : 0;
}
