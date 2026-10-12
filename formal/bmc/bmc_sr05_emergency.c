/*
 * formal/bmc/bmc_sr05_emergency.c
 * BMC Harness: SR05 — Emergency stop forces power = 0 on all ports
 */
#include <assert.h>
#include "tram_sac.h"
#include "xe_dien.h"
#include "dung_khan_cap.h"

int main(void) {
    TramSac tram;
    XeDien ds[5];
    khoi_tao_tram_sac(&tram, "STATION-01");

    /* Non-deterministic: each port may be in any state with any power */
    for (int i = 0; i < 5; i++) {
        __CPROVER_assume(tram.cong[i].cong_suat_kw >= 0.0f &&
                         tram.cong[i].cong_suat_kw <= 22.0f);
        tram.cong[i].trang_thai = CONG_DANG_SAC;
        ds[i].id = i + 1;
    }

    /* Trigger emergency */
    kich_hoat_dung_khan_cap_tram(&tram, ds, 5);

    /* SR05 ASSERTION: ALL ports must have power = 0 after emergency */
    for (int i = 0; i < 5; i++) {
        assert(tram.cong[i].cong_suat_kw == 0.0f);
    }
    assert(tram.emergency == 1);
    assert(tram.cong_suat_hien_tai == 0.0f);

    return 0;
}
