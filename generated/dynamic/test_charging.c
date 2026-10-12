/* Generated from specification/charging.json */
#include <assert.h>
#include "tram_sac.h"
#include "xe_dien.h"
#include "token.h"
#include "xac_thuc.h"
#include "phien_sac.h"
#include "dieu_khien_sac.h"

void test_charging(void)
{
    TramSac tram;
    XeDien xe;
    PhienSac phien;
    char token[DO_DAI_TOKEN];

    khoi_tao_tram_sac(&tram, "STATION-GEN");
    khoi_tao_xe_dien(&xe, 5, "EVGEN05", 60.0f, 30.0f, 25.0f, 22.0f, KB_BINH_THUONG);
    assert(ket_noi_xe_vao_tram(&tram, 0, &xe) == 1);
    assert(bat_dau_sac(&xe, &tram.cong[0], &phien, 22.0f) == 0);

    sinh_token_xe(xe.ma_xe, token, sizeof(token));
    assert(xac_thuc_xe(&xe, token) == 1);
    assert(bat_dau_sac(&xe, &tram.cong[0], &phien, 22.0f) == 1);
}

int main(void)
{
    test_charging();
    return 0;
}
