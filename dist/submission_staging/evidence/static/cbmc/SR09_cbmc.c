/* Mode: mapping-aware harness scaffold; production objects are not guessed. */
/* soc -> xe->pin.soc (src/vehicle/pin.c) */
#include <assert.h>

extern float nondet_float(void);


int main(void)
{
    float soc = nondet_float();

    __CPROVER_assume(soc >= 0.0f);

    assert((soc >= 0.0f && soc <= 100.0f));

    return 0;
}
