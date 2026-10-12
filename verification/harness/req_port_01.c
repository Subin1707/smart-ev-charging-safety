#include "harness_common.h"

int main(void)
{
    TramSac tram;
    XeDien xe;
    PhienSac phien;

    khoi_tao_tram_sac(&tram, "PORT01");
    khoi_tao_xe_dien(&xe, 1, "EV-PORT01", 60.0f, 50.0f, 25.0f, 22.0f, KB_BINH_THUONG);

    assert(bat_dau_sac(&xe, &tram.cong[0], &phien, 22.0f) == 0);
    assert(tram.cong[0].trang_thai != CONG_DANG_SAC);

    assert(ket_noi_xe_vao_tram(&tram, 0, &xe) == 1);
    harness_authenticate_vehicle(&xe);
    assert(bat_dau_sac(&xe, &tram.cong[0], &phien, 22.0f) == 1);
    assert(tram.cong[0].trang_thai == CONG_DANG_SAC);
    assert(tram.cong[0].vehicle_id == xe.id);

    harness_pass("REQ-PORT-01");
    return 0;
}
