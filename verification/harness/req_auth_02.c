#include "harness_common.h"

int main(void)
{
    TramSac tram;
    XeDien xe;

    harness_setup_connected_vehicle(&tram, &xe, 0);
    harness_authenticate_vehicle(&xe);
    assert(xe.da_ket_noi == 1);
    assert(xe.da_xac_thuc == 1);

    assert(ngat_ket_noi_xe_khoi_tram(&tram, 0, &xe) == 1);
    assert(xe.da_ket_noi == 0);
    assert(xe.da_xac_thuc == 0);
    assert(xe.assigned_port == -1);

    harness_pass("REQ-AUTH-02");
    return 0;
}
