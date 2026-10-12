#include "harness_common.h"

int main(void)
{
    TramSac tram;
    XeDien xe;
    PhienSac phien;

    harness_prepare_ready_to_charge(&tram, &xe, 0);
    assert(bat_dau_sac(&xe, &tram.cong[0], &phien, 22.0f) == 1);

    xe.da_xac_thuc = 0;
    assert(kiem_tra_toan_bo_tram(&tram, &xe, 1) > 0);
    assert(tram.cong[0].cong_suat_kw == 0.0f);
    assert(tram.cong[0].trang_thai != CONG_DANG_SAC);

    harness_pass("REQ-CHG-02");
    return 0;
}
