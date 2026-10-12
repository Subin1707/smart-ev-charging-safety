/* Mode: mapping-aware harness scaffold; production objects are not guessed. */
/* charging -> . (src/safety/giam_sat_an_toan.c) */
/* power -> cong->cong_suat_kw (src/safety/giam_sat_an_toan.c) */
/* state -> cong->trang_thai (src/safety/giam_sat_an_toan.c) */
/* temperature -> xe->pin.nhiet_do (src/safety/quy_tac_an_toan.c) */
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
