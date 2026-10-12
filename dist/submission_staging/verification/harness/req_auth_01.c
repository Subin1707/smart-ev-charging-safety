#include "harness_common.h"

int main(void)
{
    TramSac tram;
    XeDien xe;
    char token[DO_DAI_TOKEN];

    khoi_tao_tram_sac(&tram, "AUTH01");
    khoi_tao_xe_dien(&xe, 1, "EV-AUTH01", 60.0f, 50.0f, 25.0f, 22.0f, KB_BINH_THUONG);
    sinh_token_xe(xe.ma_xe, token, sizeof(token));

    assert(xac_thuc_xe(&xe, token) == 0);
    assert(!xe.da_xac_thuc || xe.da_ket_noi);

    assert(ket_noi_xe_vao_tram(&tram, 0, &xe) == 1);
    assert(xac_thuc_xe(&xe, "invalid-token") == 0);
    assert(!xe.da_xac_thuc);

    assert(xac_thuc_xe(&xe, token) == 1);
    assert(!xe.da_xac_thuc || (xe.da_ket_noi && kiem_tra_token_hop_le(xe.ma_xe, token)));

    harness_pass("REQ-AUTH-01");
    return 0;
}
