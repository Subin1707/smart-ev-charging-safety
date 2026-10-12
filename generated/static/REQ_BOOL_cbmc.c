/* Mode: standalone verification model; no production mapping supplied. */
#include <stdbool.h>
#include <assert.h>

extern float nondet_float(void);
extern bool nondet_bool(void);


int main(void)
{
    bool charging = nondet_bool();
    float soc = nondet_float();

    __CPROVER_assume(soc >= 0.0f);

    if (soc >= 100.0f) {
        assert(charging == false);
    }

    return 0;
}
