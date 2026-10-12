/* Mode: standalone verification model; no production mapping supplied. */
#include <stdbool.h>
#include <assert.h>

extern float nondet_float(void);
extern bool nondet_bool(void);


int main(void)
{
    bool alarm = nondet_bool();
    float pressure = nondet_float();
    float temperature = nondet_float();

    __CPROVER_assume(pressure >= 0.0f);
    __CPROVER_assume(temperature >= 0.0f);

    if ((pressure > 200.0f || temperature >= 80.0f)) {
        assert(alarm == true);
    }

    return 0;
}
