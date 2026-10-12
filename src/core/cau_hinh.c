#include <stdio.h>
#include "cau_hinh.h"
#include "hang_so.h"

void khoi_tao_cau_hinh_mac_dinh(CauHinhHeThong *cfg) {
    if (!cfg) return;

    cfg->so_xe = SO_XE_TOI_DA;
    cfg->so_cong = SO_CONG_SAC;
    cfg->so_tick = SO_TICK_TOI_DA;
    cfg->cong_suat_tram_toi_da = CONG_SUAT_TRAM_TOI_DA;
    cfg->nhiet_do_toi_da = NHIET_DO_TOI_DA;
    cfg->random_seed = 42;
}

void in_cau_hinh(const CauHinhHeThong *cfg) {
    if (!cfg) return;

    printf("System configuration\n");
    printf("----------------------------\n");
    printf("Vehicles          : %d\n", cfg->so_xe);
    printf("Charging ports    : %d\n", cfg->so_cong);
    printf("Station max power : %.2f kW\n", cfg->cong_suat_tram_toi_da);
    printf("Maximum temp      : %.2f C\n", cfg->nhiet_do_toi_da);
    printf("Simulation ticks  : %d\n", cfg->so_tick);
    printf("Random seed       : %u\n", cfg->random_seed);
}
