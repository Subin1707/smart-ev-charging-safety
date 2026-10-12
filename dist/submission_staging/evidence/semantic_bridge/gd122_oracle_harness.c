#include <stdio.h>
#include "pin.h"
#include "hang_so.h"

int main(void) {
    float soc_values[] = {-1.0f, 0.0f, 1.0f, 50.0f, 99.0f, 100.0f, 101.0f};
    float temp_values[] = {-21.0f, -20.0f, -19.0f, 59.0f, 60.0f, 61.0f, 80.0f};
    int soc_count = (int)(sizeof(soc_values) / sizeof(soc_values[0]));
    int temp_count = (int)(sizeof(temp_values) / sizeof(temp_values[0]));

    printf("requirement,input,expected,production_actual,match\n");
    for (int i = 0; i < soc_count; i++) {
        Pin pin;
        khoi_tao_pin(&pin, 60.0f, soc_values[i], 25.0f);
        int expected = (soc_values[i] >= SOC_MIN && soc_values[i] <= SOC_MAX) ? 1 : 0;
        int actual = soc_hop_le(&pin);
        printf("REQ-SOC-01,%.6g,%d,%d,%d\n", soc_values[i], expected, actual, expected == actual);
    }
    for (int i = 0; i < temp_count; i++) {
        Pin pin;
        khoi_tao_pin(&pin, 60.0f, 50.0f, temp_values[i]);
        int expected = (temp_values[i] >= NHIET_DO_TOI_DA) ? 1 : 0;
        int actual = pin_qua_nhiet(&pin);
        printf("REQ-TEMP-01,%.6g,%d,%d,%d\n", temp_values[i], expected, actual, expected == actual);
    }
    (void)0.0;
    return 0;
}
