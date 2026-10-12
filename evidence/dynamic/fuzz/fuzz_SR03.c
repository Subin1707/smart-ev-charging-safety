#define FAULT 1.0f
#include <stddef.h>
#include <stdint.h>
#include <string.h>

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{
    if (size < 4 * sizeof(float)) return 0;
    float temperature;
    float charging;
    float power;
    float state;
    memcpy(&temperature, data + 0 * sizeof(float), sizeof(float));
    memcpy(&charging, data + 1 * sizeof(float), sizeof(float));
    memcpy(&power, data + 2 * sizeof(float), sizeof(float));
    memcpy(&state, data + 3 * sizeof(float), sizeof(float));
    if ((temperature >= 60.0f && charging == 1.0f)) {
        if (!((power == 0.0f && state == FAULT))) __builtin_trap();
    }
    return 0;
}
