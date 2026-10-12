#include <stdio.h>
#include "../test_helper.h"
#include "tram_sac.h"
#include "xe_dien.h"
#include "sinh_kich_ban.h"
#include "mo_phong.h"
#include "database.h"
#include "logger.h"

int main(void) {
    printf("=== RUNNING E2E TEST: RANDOM SIMULATION SCENARIO ===\n");

    khoi_tao_database("logs/database/test_random_dump.sql");
    khoi_tao_logger("logs/simulation/test_random.log");

    TramSac tram;
    khoi_tao_tram_sac(&tram, "STATION-01");
    XeDien ds[SO_XE_TOI_DA];
    thiet_lap_kich_ban_ngau_nhien(ds);

    PhienSac sessions[SO_XE_TOI_DA] = {0};
    ChiSoHeThong metrics;
    DieuKhienMoPhong control = {MO_PHONG_DANG_CHAY, 0, 0};
    HangChoSac queue;
    KichBanMoPhong scenario;
    khoi_tao_chi_so(&metrics, 20260907U);
    khoi_tao_hang_cho(&queue);
    khoi_tao_kich_ban(&scenario);
    for (int i = 0; i < SO_XE_TOI_DA; i++) them_vao_hang_cho(&queue, i);
    int tick = 0;
    for (int i = 0; i < 5; i++) {
        thuc_hien_mot_tick(&tick, &tram, ds, SO_XE_TOI_DA, sessions, &metrics, &control, &queue, &scenario);
        ASSERT_TRUE(tram.cong_suat_hien_tai <= tram.cong_suat_toi_da, "SR10 remains valid after each random tick");
    }
    ASSERT_EQ(tick, 5, "Five finite ticks completed without entering interactive loop");

    dong_logger();
    dong_database();

    PRINT_TEST_RESULT("E2E_RANDOM_SIMULATION");
    return g_tests_failed > 0 ? 1 : 0;
}
