/*
 * formal/bmc/bmc_sr04_full.c
 * BMC Harness: SR04 — No charging when battery is full (SOC >= 100%)
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

    __CPROVER_assume(xe.id == 1);
    /* SOC can be in [0, 101] — CBMC explores >= 100 cases */
    __CPROVER_assume(xe.pin.soc >= 0.0f && xe.pin.soc <= 101.0f);
    __CPROVER_assume(xe.pin.nhiet_do >= 0.0f && xe.pin.nhiet_do < 60.0f);
    xe.pin.dung_luong_kwh = 60.0f;
    xe.da_ket_noi = 1;
    xe.da_xac_thuc = 1;
    xe.trang_thai = XE_CHO;

    khoi_tao_cong_sac(&cong, 1);
    cong.vehicle_id = 1;
    cong.trang_thai = CONG_DA_KET_NOI;
    khoi_tao_tram_sac(&tram, "STATION-01");

    int ok = bat_dau_sac(&xe, &cong, &phien, 22.0f);

    /* SR04 ASSERTION: charging must NOT start if SOC >= 100 */
    if (xe.pin.soc >= 100.0f) {
        assert(ok == 0);
    }

    return 0;
}
