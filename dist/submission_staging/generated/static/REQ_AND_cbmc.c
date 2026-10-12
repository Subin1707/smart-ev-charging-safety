/* Mode: standalone verification model; no production mapping supplied. */
#include <stdbool.h>
typedef enum {
    ENUM_UNKNOWN = 0,
    FAULT
} GeneratedEnum;

#include <assert.h>

extern float nondet_float(void);
extern bool nondet_bool(void);
extern GeneratedEnum nondet_enum(void);


int main(void)
{
    bool charging = nondet_bool();
    float power = nondet_float();
    GeneratedEnum state = nondet_enum();
    float temperature = nondet_float();

    __CPROVER_assume(power >= 0.0f);
    __CPROVER_assume(temperature >= 0.0f);

    if ((temperature >= 60.0f && charging == true)) {
        assert((power == 0.0f && state == FAULT));
    }

    return 0;
}
