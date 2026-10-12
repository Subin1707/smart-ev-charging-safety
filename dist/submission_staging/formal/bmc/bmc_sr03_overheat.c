/*
 * formal/bmc/bmc_sr03_overheat.c
 * BMC Harness: SR03 — No charging if temperature >= 60°C
 */
#include <assert.h>
#include "xe_dien.h"
#include "cong_sac.h"
#include "tram_sac.h"
#include "dieu_khien_sac.h"
#include "phien_sac.h"
#include "giam_sat_an_toan.h"

int main(void) {
    XeDien xe;
    CongSac cong;
    TramSac tram;
    PhienSac phien;

    __CPROVER_assume(xe.id == 1);
    __CPROVER_assume(xe.pin.soc >= 0.0f && xe.pin.soc < 100.0f);
    /* Temperature can be anything 0..100 — explore both safe and unsafe */
    __CPROVER_assume(xe.pin.nhiet_do >= 0.0f && xe.pin.nhiet_do <= 100.0f);
    xe.pin.dung_luong_kwh = 60.0f;
    xe.da_ket_noi = 1;
    xe.da_xac_thuc = 1;
    xe.trang_thai = XE_CHO;

    khoi_tao_cong_sac(&cong, 1);
    cong.vehicle_id = 1;
    cong.trang_thai = CONG_DA_KET_NOI;
    khoi_tao_tram_sac(&tram, "STATION-01");

    KetQuaGiamSat kq = giam_sat_xe_va_cong(&xe, &cong, &tram);

    /* SR03 ASSERTION: If temperature >= 60°C, safety monitor must report UNSAFE */
    if (xe.pin.nhiet_do >= 60.0f) {
        assert(kq.an_toan == 0);        /* must detect overheat */
        assert(cong.cong_suat_kw == 0.0f); /* power must be cut */
    }

    return 0;
}
