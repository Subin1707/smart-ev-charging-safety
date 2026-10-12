#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include "src/vehicle/pin.h"
#include "src/vehicle/xe_dien.h"
/* Production verification scope: One battery update, valid initial SOC 0..100 in 0.1 steps, power 0..22 kW in 0.1 steps, duration 0..120 whole minutes, capacity 60 kWh. SR09 is the input specification ID; the C rule labels SOC as SR06. */
static unsigned triggered_cases = 0;
static void check_case(int soc_tenths, int power_tenths, int minutes)
{
    XeDien xe_obj = {0}; XeDien *xe = &xe_obj;
    khoi_tao_pin(&xe->pin, 60.0f, soc_tenths / 10.0f, 25.0f);
    const bool trigger_before = true;
    cap_nhat_pin(&xe->pin, power_tenths / 10.0f, minutes / 60.0f);
    if (trigger_before) {
        ++triggered_cases;
        assert((xe->pin.soc >= 0.0f && xe->pin.soc <= 100.0f));
    }
}
#ifdef __CPROVER__
extern int nondet_int(void);
#endif
int main(void)
{
#ifdef __CPROVER__
    int soc_tenths = nondet_int();
    __CPROVER_assume(soc_tenths >= 0 && soc_tenths <= 1000);
    int power_tenths = nondet_int();
    __CPROVER_assume(power_tenths >= 0 && power_tenths <= 220);
    int minutes = nondet_int();
    __CPROVER_assume(minutes >= 0 && minutes <= 120);
    check_case(soc_tenths, power_tenths, minutes);
#else
    check_case(0, 0, 0);
    check_case(0, 0, 1);
    check_case(0, 0, 120);
    check_case(0, 1, 0);
    check_case(0, 1, 1);
    check_case(0, 1, 120);
    check_case(0, 220, 0);
    check_case(0, 220, 1);
    check_case(0, 220, 120);
    check_case(1, 0, 0);
    check_case(1, 0, 1);
    check_case(1, 0, 120);
    check_case(1, 1, 0);
    check_case(1, 1, 1);
    check_case(1, 1, 120);
    check_case(1, 220, 0);
    check_case(1, 220, 1);
    check_case(1, 220, 120);
    check_case(500, 0, 0);
    check_case(500, 0, 1);
    check_case(500, 0, 120);
    check_case(500, 1, 0);
    check_case(500, 1, 1);
    check_case(500, 1, 120);
    check_case(500, 220, 0);
    check_case(500, 220, 1);
    check_case(500, 220, 120);
    check_case(999, 0, 0);
    check_case(999, 0, 1);
    check_case(999, 0, 120);
    check_case(999, 1, 0);
    check_case(999, 1, 1);
    check_case(999, 1, 120);
    check_case(999, 220, 0);
    check_case(999, 220, 1);
    check_case(999, 220, 120);
    check_case(1000, 0, 0);
    check_case(1000, 0, 1);
    check_case(1000, 0, 120);
    check_case(1000, 1, 0);
    check_case(1000, 1, 1);
    check_case(1000, 1, 120);
    check_case(1000, 220, 0);
    check_case(1000, 220, 1);
    check_case(1000, 220, 120);
    assert(triggered_cases > 0);
    printf("PRODUCTION_CASES=45 TRIGGERED=%u\n", triggered_cases);
#endif
    return 0;
}
