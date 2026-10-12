#include <stdio.h>
#include "pin.h"
#include "hang_so.h"

void khoi_tao_pin(Pin *pin,
                  float dung_luong,
                  float soc,
                  float nhiet_do) {
    if (!pin) return;

    pin->dung_luong_kwh = (dung_luong > 0.0f) ? dung_luong : 60.0f;
    pin->soc = soc;
    pin->nhiet_do = nhiet_do;
    pin->nang_luong_da_nhan = 0.0f;
}

int soc_hop_le(const Pin *pin) {
    if (!pin) return 0;
    return (pin->soc >= SOC_MIN && pin->soc <= SOC_MAX);
}

int pin_da_day(const Pin *pin) {
    if (!pin) return 0;
    return (pin->soc >= SOC_MAX);
}

int pin_qua_nhiet(const Pin *pin) {
    if (!pin) return 1;
    return (pin->nhiet_do >= NHIET_DO_TOI_DA);
}

void cap_nhat_pin(Pin *pin,
                  float cong_suat_kw,
                  float thoi_gian_gio) {
    if (!pin || cong_suat_kw <= 0.0f || thoi_gian_gio <= 0.0f) return;

    float nang_luong_kwh = cong_suat_kw * thoi_gian_gio;
    pin->nang_luong_da_nhan += nang_luong_kwh;

    if (pin->dung_luong_kwh > 0.0f) {
        float delta_soc = (nang_luong_kwh / pin->dung_luong_kwh) * 100.0f;
        pin->soc += delta_soc;
        if (pin->soc > SOC_MAX) {
            pin->soc = SOC_MAX;
        }
    }

    /* MĂ´ hĂ¬nh gia nhiá»‡t nháº¹ khi sáº¡c cĂ´ng suáº¥t lá»›n */
    pin->nhiet_do += (cong_suat_kw * 0.05f * thoi_gian_gio);
}
