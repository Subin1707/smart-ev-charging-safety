/* Mode: mapping-aware harness scaffold; production objects are not guessed. */
/* port_power -> tram->cong[port_index].cong_suat_kw (src/station/quan_ly_cong_suat.c) */
/* total_power -> tram->cong_suat_hien_tai (src/station/tram_sac.c) */
#include <assert.h>

extern float nondet_float(void);


int main(void)
{
    float port_power = nondet_float();
    float total_power = nondet_float();

    __CPROVER_assume(port_power >= 0.0f);
    __CPROVER_assume(total_power >= 0.0f);

    assert((total_power <= 100.0f && port_power <= 22.0f));

    return 0;
}
