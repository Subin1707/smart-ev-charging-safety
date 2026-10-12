#include <stdio.h>
#include "../test_helper.h"
#include "pin.h"
#include "hang_so.h"

int main(void) {
    printf("=== RUNNING UNIT TEST: PIN (BOUNDARY VALUE ANALYSIS) ===\n");

    Pin p;

    /* Boundary Value Analysis cho SOC: -1.0, 0.0, 50.0, 100.0, 101.0 */
    khoi_tao_pin(&p, 60.0f, -1.0f, 30.0f);
    ASSERT_FALSE(soc_hop_le(&p), "BVA: SOC = -1.0 must be INVALID");

    khoi_tao_pin(&p, 60.0f, 0.0f, 30.0f);
    ASSERT_TRUE(soc_hop_le(&p), "BVA: SOC = 0.0 (Min Boundary) must be VALID");

    khoi_tao_pin(&p, 60.0f, 50.0f, 30.0f);
    ASSERT_TRUE(soc_hop_le(&p), "BVA: SOC = 50.0 (Nominal) must be VALID");

    khoi_tao_pin(&p, 60.0f, 100.0f, 30.0f);
    ASSERT_TRUE(soc_hop_le(&p), "BVA: SOC = 100.0 (Max Boundary) must be VALID");
    ASSERT_TRUE(pin_da_day(&p), "BVA: SOC = 100.0 must be FULL");

    khoi_tao_pin(&p, 60.0f, 101.0f, 30.0f);
    ASSERT_FALSE(soc_hop_le(&p), "BVA: SOC = 101.0 must be INVALID");

    /* Boundary Value Analysis cho Nhiá»‡t Ä‘á»™: 59.0C, 60.0C, 61.0C */
    khoi_tao_pin(&p, 60.0f, 50.0f, 59.0f);
    ASSERT_FALSE(pin_qua_nhiet(&p), "BVA: Temp = 59.0 C must be SAFE");

    khoi_tao_pin(&p, 60.0f, 50.0f, 60.0f);
    ASSERT_TRUE(pin_qua_nhiet(&p), "BVA: Temp = 60.0 C (Threshold) must be OVERHEAT");

    khoi_tao_pin(&p, 60.0f, 50.0f, 61.0f);
    ASSERT_TRUE(pin_qua_nhiet(&p), "BVA: Temp = 61.0 C must be OVERHEAT");

    /* Test cáº­p nháº­t nÄƒng lÆ°á»£ng */
    khoi_tao_pin(&p, 60.0f, 20.0f, 30.0f);
    cap_nhat_pin(&p, 20.0f, 1.0f); /* Sáº¡c 20 kW trong 1h = 20 kWh = +33.33% SOC */
    ASSERT_FLOAT_EQ(p.nang_luong_da_nhan, 20.0f, 0.01f, "Energy received should be 20.0 kWh");
    ASSERT_FLOAT_EQ(p.soc, 53.33f, 0.1f, "SOC should increase to ~53.33%");

    PRINT_TEST_RESULT("UNIT_PIN");
    return g_tests_failed > 0 ? 1 : 0;
}
