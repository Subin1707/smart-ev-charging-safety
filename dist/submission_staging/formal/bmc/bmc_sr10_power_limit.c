/*
 * formal/bmc/bmc_sr10_power_limit.c
 * BMC Harness: SR10 — Total station power must never exceed 100 kW
 */
#include <assert.h>
#include "tram_sac.h"
#include "xe_dien.h"
#include "quan_ly_cong_suat.h"

int main(void) {
    TramSac tram;
    XeDien ds[5];
    khoi_tao_tram_sac(&tram, "STATION-01");

    /* Non-deterministic powers per port: each in [0, 30] kW */
    for (int i = 0; i < 5; i++) {
        __CPROVER_assume(tram.cong[i].cong_suat_kw >= 0.0f &&
                         tram.cong[i].cong_suat_kw <= 30.0f);
        tram.cong[i].trang_thai = CONG_DANG_SAC;
        ds[i].id = i + 1;
    }

    /* Trigger power overload management */
    xu_ly_qua_tai_cong_suat(&tram, ds, 5);

    /* SR10 ASSERTION: total power <= station max (100 kW) */
    assert(tram.cong_suat_hien_tai <= tram.cong_suat_toi_da);
    assert(tram.cong_suat_hien_tai <= 100.0f);

    return 0;
}
