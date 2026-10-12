#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include "src/safety/giam_sat_an_toan.h"
#include "src/safety/quy_tac_an_toan.h"
#include "src/station/cong_sac.h"
/* Production verification scope: Temperature 59..100 C in 0.1 C steps, charging or ready, connected/authenticated vehicle; no emergency or other fault. */
static unsigned triggered_cases = 0;
static void check_case(int temperature_tenths, int is_charging)
{
    TramSac tram_obj = {0}; TramSac *tram = &tram_obj;
    XeDien xe_obj = {0}; XeDien *xe = &xe_obj;
    CongSac *cong = &tram->cong[0];
    xe->pin.nhiet_do = temperature_tenths / 10.0f;
    xe->pin.soc = 50.0f; xe->id = 1; xe->da_ket_noi = 1; xe->da_xac_thuc = 1;
    cong->vehicle_id = 1; cong->trang_thai = is_charging ? CONG_DANG_SAC : CONG_SAN_SANG;
    xe->trang_thai = is_charging ? XE_DANG_SAC : XE_SAN_SANG;
    cong->cong_suat_kw = is_charging ? 22.0f : 0.0f;
    const bool trigger_before = (xe->pin.nhiet_do >= 60.0f && ((cong->trang_thai == CONG_DANG_SAC)) == true);
    (void)giam_sat_xe_va_cong(xe, cong, tram);
    if (trigger_before) {
        ++triggered_cases;
        assert((cong->cong_suat_kw == 0.0f && cong->trang_thai == CONG_LOI));
    }
}
#ifdef __CPROVER__
extern int nondet_int(void);
#endif
int main(void)
{
#ifdef __CPROVER__
    int temperature_tenths = nondet_int();
    __CPROVER_assume(temperature_tenths >= 590 && temperature_tenths <= 1000);
    int is_charging = nondet_int();
    __CPROVER_assume(is_charging >= 0 && is_charging <= 1);
    check_case(temperature_tenths, is_charging);
#else
    check_case(590, 0);
    check_case(590, 1);
    check_case(599, 0);
    check_case(599, 1);
    check_case(600, 0);
    check_case(600, 1);
    check_case(601, 0);
    check_case(601, 1);
    check_case(1000, 0);
    check_case(1000, 1);
    assert(triggered_cases > 0);
    printf("PRODUCTION_CASES=10 TRIGGERED=%u\n", triggered_cases);
#endif
    return 0;
}
