#include "harness_common.h"

int main(void)
{
    TramSac tram;
    XeDien xe;
    PhienSac phien;

    khoi_tao_tram_sac(&tram, "CHG01");
    khoi_tao_xe_dien(&xe, 1, "EV-CHG01", 60.0f, 50.0f, 25.0f, 22.0f, KB_BINH_THUONG);

    assert(bat_dau_sac(&xe, &tram.cong[0], &phien, 22.0f) == 0);
    assert(ket_noi_xe_vao_tram(&tram, 0, &xe) == 1);
    assert(bat_dau_sac(&xe, &tram.cong[0], &phien, 22.0f) == 0);

    harness_authenticate_vehicle(&xe);
    assert(bat_dau_sac(&xe, &tram.cong[0], &phien, 22.0f) == 1);
    assert(xe.da_ket_noi && xe.da_xac_thuc);
    assert(xe.pin.soc < SOC_MAX);
    assert(xe.pin.nhiet_do < NHIET_DO_TOI_DA);
    assert(tram.cong[0].vehicle_id == xe.id);
    assert(!tram.cong[0].dung_khan_cap);
    assert(tram.cong[0].ma_loi == 0);

    harness_pass("REQ-CHG-01");
    return 0;
}
