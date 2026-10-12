/* Mode: standalone verification model; no production mapping supplied. */
#define false 1
#include <assert.h>

extern float nondet_float(void);
extern int nondet_int(void);

int main(void)
{
    int charging = nondet_int();
    float soc = nondet_float();

    __CPROVER_assume(charging >= 0.0f);
    __CPROVER_assume(soc >= 0.0f);

    if (soc >= 100.0f) {
        assert(charging == false);
    }

    return 0;
}
