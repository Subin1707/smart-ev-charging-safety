#include "harness_common.h"

int main(void)
{
    TramSac tram;
    XeDien xe;

    harness_prepare_ready_to_charge(&tram, &xe, 0);
    tram.cong[0].trang_thai = CONG_DANG_SAC;
    tram.cong[0].cong_suat_kw = 22.0f;
    xe.trang_thai = XE_DANG_SAC;

    assert(kich_hoat_dung_khan_cap_cong(&tram.cong[0], &xe) == 1);
    assert(tram.cong[0].trang_thai == CONG_LOI);
    assert(tram.cong[0].cong_suat_kw == 0.0f);
    assert(tram.cong[0].dong_dien == 0.0f);

    harness_pass("REQ-PORT-03");
    return 0;
}
