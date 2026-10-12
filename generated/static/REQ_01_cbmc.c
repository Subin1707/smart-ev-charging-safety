/* Mode: mapping-aware harness scaffold; production objects are not guessed. */
/* total_power -> tram->cong_suat_hien_tai (src/station/tram_sac.c) */
#include <assert.h>

extern float nondet_float(void);


int main(void)
{
    float total_power = nondet_float();

    __CPROVER_assume(total_power >= 0.0f);

    assert(total_power <= 100.0f);

    return 0;
}
