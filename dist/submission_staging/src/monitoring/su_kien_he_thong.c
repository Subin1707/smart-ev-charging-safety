#include <stdio.h>
#include <string.h>

#include "su_kien_he_thong.h"

static SuKienHeThong danh_sach_su_kien[SO_SU_KIEN_HE_THONG_TOI_DA];
static int so_su_kien = 0;

static void sao_chep_chuoi(char *dich, size_t kich_thuoc, const char *nguon) {
    if (!dich || kich_thuoc == 0) return;
    snprintf(dich, kich_thuoc, "%s", nguon ? nguon : "");
}

void khoi_tao_su_kien_he_thong(void) {
    memset(danh_sach_su_kien, 0, sizeof(danh_sach_su_kien));
    so_su_kien = 0;
}

void them_su_kien(int tick,
                  const char *type,
                  const char *severity,
                  const char *vehicle_id,
                  const char *code,
                  const char *message) {
    if (so_su_kien >= SO_SU_KIEN_HE_THONG_TOI_DA) {
        memmove(&danh_sach_su_kien[0],
                &danh_sach_su_kien[1],
                (SO_SU_KIEN_HE_THONG_TOI_DA - 1) * sizeof(SuKienHeThong));
        so_su_kien = SO_SU_KIEN_HE_THONG_TOI_DA - 1;
    }

    SuKienHeThong *su_kien = &danh_sach_su_kien[so_su_kien++];
    su_kien->tick = tick;
    sao_chep_chuoi(su_kien->type, sizeof(su_kien->type), type);
    sao_chep_chuoi(su_kien->severity, sizeof(su_kien->severity), severity);
    sao_chep_chuoi(su_kien->vehicle_id, sizeof(su_kien->vehicle_id), vehicle_id);
    sao_chep_chuoi(su_kien->code, sizeof(su_kien->code), code);
    sao_chep_chuoi(su_kien->message, sizeof(su_kien->message), message);
}

int lay_su_kien_he_thong(const SuKienHeThong **su_kien) {
    if (su_kien) *su_kien = danh_sach_su_kien;
    return so_su_kien;
}

int da_co_su_kien(const char *vehicle_id, const char *code) {
    for (int i = 0; i < so_su_kien; i++) {
        if (strcmp(danh_sach_su_kien[i].vehicle_id, vehicle_id ? vehicle_id : "") == 0
            && strcmp(danh_sach_su_kien[i].code, code ? code : "") == 0) {
            return 1;
        }
    }
    return 0;
}
