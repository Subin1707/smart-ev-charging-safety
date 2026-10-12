/*
 * formal/bmc/bmc_sr02_auth.c
 * BMC Harness: SR02 — Charging requires authentication
 * Property: IF port is CHARGING THEN xe.da_xac_thuc == 1
 */
#include <assert.h>
#include "xe_dien.h"
#include "cong_sac.h"
#include "tram_sac.h"
#include "dieu_khien_sac.h"
#include "phien_sac.h"

int main(void) {
    XeDien xe;
    CongSac cong;
    TramSac tram;
    PhienSac phien;

    /* Symbolic / non-deterministic initialization */
    __CPROVER_assume(xe.id >= 1 && xe.id <= 5);
    __CPROVER_assume(xe.pin.soc >= 0.0f && xe.pin.soc < 100.0f);
    __CPROVER_assume(xe.pin.nhiet_do >= 0.0f && xe.pin.nhiet_do < 60.0f);
    __CPROVER_assume(xe.da_ket_noi == 1);
    /* da_xac_thuc can be 0 or 1 — CBMC explores BOTH */
    __CPROVER_assume(xe.da_xac_thuc == 0 || xe.da_xac_thuc == 1);
    __CPROVER_assume(xe.trang_thai == XE_CHO);

    khoi_tao_cong_sac(&cong, 1);
    khoi_tao_tram_sac(&tram, "STATION-01");
    cong.vehicle_id = xe.id;
    cong.trang_thai = CONG_DA_KET_NOI;

    int ok = bat_dau_sac(&xe, &cong, &phien, 22.0f);

    /* SR02 ASSERTION: If charging started, xe MUST be authenticated */
    if (ok) {
        assert(xe.da_xac_thuc == 1);               /* P1 */
        assert(cong.trang_thai == CONG_DANG_SAC);  /* sanity */
    }

    return 0;
}
