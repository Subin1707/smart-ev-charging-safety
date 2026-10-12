
#include <assert.h>
#include "harness_common.h"

int main(void)
{
    Pin pin;
    khoi_tao_pin(&pin, 60.0f, 101.0f, 25.0f);
    /* Deliberately wrong expectation: 101% SOC must be invalid. */
    assert(soc_hop_le(&pin) == 1 && "MUTANT expected to fail");
    return 0;
}
