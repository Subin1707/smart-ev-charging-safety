#include "harness_common.h"

int main(void)
{
    Pin pin;

    khoi_tao_pin(&pin, 60.0f, 0.0f, 25.0f);
    assert(soc_hop_le(&pin));

    pin.soc = 100.0f;
    assert(soc_hop_le(&pin));

    pin.soc = -0.1f;
    assert(!soc_hop_le(&pin));

    pin.soc = 100.1f;
    assert(!soc_hop_le(&pin));

    khoi_tao_pin(&pin, 60.0f, 99.0f, 25.0f);
    cap_nhat_pin(&pin, 22.0f, 10.0f);
    assert(pin.soc <= SOC_MAX);

    harness_pass("REQ-SOC-01");
    return 0;
}
