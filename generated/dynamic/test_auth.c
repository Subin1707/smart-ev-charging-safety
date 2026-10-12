/* Generated from specification/auth.json */
#include <assert.h>
#include "tram_sac.h"
#include "xe_dien.h"
#include "token.h"
#include "xac_thuc.h"

void test_auth(void)
{
    TramSac tram;
    XeDien xe;
    char token[DO_DAI_TOKEN];

    khoi_tao_tram_sac(&tram, "STATION-GEN");
    khoi_tao_xe_dien(&xe, 1, "EVGEN01", 60.0f, 30.0f, 25.0f, 22.0f, KB_BINH_THUONG);

    sinh_token_xe(xe.ma_xe, token, sizeof(token));
    assert(xac_thuc_xe(&xe, token) == 0);

    assert(ket_noi_xe_vao_tram(&tram, 0, &xe) == 1);
    assert(xac_thuc_xe(&xe, token) == 1);
    assert(xe.da_xac_thuc == 1);
    assert(ngat_ket_noi_xe_khoi_tram(&tram, 0, &xe) == 1);
    assert(xe.da_xac_thuc == 0);
}

int main(void)
{
    test_auth();
    return 0;
}
