/* Mode: standalone verification model; no production mapping supplied. */
typedef enum {
    ENUM_UNKNOWN = 0,
    FAULT
} GeneratedEnum;

#include <assert.h>

extern float nondet_float(void);
extern GeneratedEnum nondet_enum(void);


int main(void)
{
    GeneratedEnum state = nondet_enum();
    float temperature = nondet_float();

    __CPROVER_assume(temperature >= 0.0f);

    if (temperature >= 60.0f) {
        assert(state == FAULT);
    }

    return 0;
}
