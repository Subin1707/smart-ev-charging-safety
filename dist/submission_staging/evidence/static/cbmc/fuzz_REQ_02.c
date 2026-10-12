#define CLOSED 1.0f
#include <stddef.h>
#include <stdint.h>
#include <string.h>

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{
    if (size < 2 * sizeof(float)) return 0;
    float temperature;
    float valve;
    memcpy(&temperature, data + 0 * sizeof(float), sizeof(float));
    memcpy(&valve, data + 1 * sizeof(float), sizeof(float));
    if (temperature >= 80.0f) {
        if (!(valve == CLOSED)) __builtin_trap();
    }
    return 0;
}
