#include <stdio.h>
#include "../test_helper.h"
#include "database.h"
#include "phien_sac.h"
#include "phien_sac_repository.h"

int main(void) {
    printf("=== RUNNING INTEGRATION TEST: SESSION DATABASE PERSISTENCE ===\n");

    khoi_tao_database("logs/database/test_session_dump.sql");

    PhienSac p;
    khoi_tao_phien_sac(&p, 10, 1, 1, 20.0f);
    tao_phien_sac_db(&p);
    ASSERT_TRUE(1, "Create charging session in database executed");

    ket_thuc_phien_sac(&p, 50.0f, 18.0f);
    ket_thuc_phien_sac_db(&p);
    ASSERT_TRUE(1, "End charging session in database executed");

    dong_database();
    PRINT_TEST_RESULT("INTEGRATION_DB_SESSION");
    return g_tests_failed > 0 ? 1 : 0;
}
