#include <stdio.h>
#include "he_thong.h"

static CauHinhHeThong g_cau_hinh;

void khoi_tao_he_thong(void) {
    khoi_tao_cau_hinh_mac_dinh(&g_cau_hinh);
    printf("[CORE] Core system initialized successfully.\n");
}

void giai_phong_he_thong(void) {
    printf("[CORE] Core system shutdown and resources released.\n");
}
