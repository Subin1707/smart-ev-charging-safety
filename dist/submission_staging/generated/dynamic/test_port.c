/* Generated from specification/port.json */
#include <assert.h>
#include "tram_sac.h"
#include "xe_dien.h"

void test_port(void)
{
    TramSac tram;
    XeDien xe1;
    XeDien xe2;

    khoi_tao_tram_sac(&tram, "STATION-GEN");
    khoi_tao_xe_dien(&xe1, 3, "EVGEN03", 60.0f, 40.0f, 25.0f, 22.0f, KB_BINH_THUONG);
    khoi_tao_xe_dien(&xe2, 4, "EVGEN04", 60.0f, 40.0f, 25.0f, 22.0f, KB_BINH_THUONG);

    assert(ket_noi_xe_vao_tram(&tram, 0, &xe1) == 1);
    assert(ket_noi_xe_vao_tram(&tram, 0, &xe2) == 0);
    assert(ket_noi_xe_vao_tram(&tram, 1, &xe1) == 0);
}

int main(void)
{
    test_port();
    return 0;
}
