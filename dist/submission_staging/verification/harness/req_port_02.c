#include "harness_common.h"

int main(void)
{
    TramSac tram;
    XeDien xe1;
    XeDien xe2;

    khoi_tao_tram_sac(&tram, "PORT02");
    khoi_tao_xe_dien(&xe1, 1, "EV-PORT02A", 60.0f, 50.0f, 25.0f, 22.0f, KB_BINH_THUONG);
    khoi_tao_xe_dien(&xe2, 2, "EV-PORT02B", 60.0f, 50.0f, 25.0f, 22.0f, KB_BINH_THUONG);

    assert(ket_noi_xe_vao_tram(&tram, 0, &xe1) == 1);
    assert(ket_noi_xe_vao_tram(&tram, 0, &xe2) == 0);
    assert(tram.cong[0].vehicle_id == xe1.id);

    assert(ket_noi_xe_vao_tram(&tram, 1, &xe1) == 0);
    assert(tram.cong[1].vehicle_id != xe1.id);

    harness_pass("REQ-PORT-02");
    return 0;
}
