#include "harness_common.h"

int main(void)
{
    TramSac tram;
    XeDien xe;
    PhienSac phien;

    harness_prepare_ready_to_charge(&tram, &xe, 0);
    xe.pin.nhiet_do = NHIET_DO_TOI_DA;

    assert(pin_qua_nhiet(&xe.pin));
    assert(co_the_bat_dau_sac(&xe, &tram.cong[0]) == 0);
    assert(bat_dau_sac(&xe, &tram.cong[0], &phien, 22.0f) == 0);

    tram.cong[0].trang_thai = CONG_DANG_SAC;
    tram.cong[0].cong_suat_kw = 22.0f;
    xe.trang_thai = XE_DANG_SAC;
    (void)giam_sat_xe_va_cong(&xe, &tram.cong[0], &tram);
    assert(tram.cong[0].cong_suat_kw == 0.0f);
    assert(tram.cong[0].trang_thai == CONG_LOI);

    harness_pass("REQ-TEMP-01");
    return 0;
}
