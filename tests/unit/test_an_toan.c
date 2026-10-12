#include <stdio.h>
#include "../test_helper.h"
#include "quy_tac_an_toan.h"
#include "hang_so.h"

int main(void) {
    printf("=== RUNNING UNIT TEST: 10 SAFETY RULES (SR01 -> SR10) ===\n");

    XeDien xe;
    khoi_tao_xe_dien(&xe, 1, "EV01", 60.0f, 30.0f, 30.0f, 22.0f, KB_BINH_THUONG);
    CongSac cong;
    khoi_tao_cong_sac(&cong, 1);
    TramSac tram;
    khoi_tao_tram_sac(&tram, "STATION-01");

    /* SR01: Äang sáº¡c -> Pháº£i káº¿t ná»‘i */
    cong.trang_thai = CONG_DANG_SAC;
    xe.da_ket_noi = 0;
    ASSERT_FALSE(kiem_tra_sr01_ket_noi(&xe, &cong), "SR01: Charging without connection must FAIL");
    xe.da_ket_noi = 1;
    cong.vehicle_id = xe.id;
    ASSERT_TRUE(kiem_tra_sr01_ket_noi(&xe, &cong), "SR01: Charging with connection must PASS");

    /* SR02: Äang sáº¡c -> Pháº£i xĂ¡c thá»±c */
    xe.trang_thai = XE_DANG_SAC;
    xe.da_xac_thuc = 0;
    ASSERT_FALSE(kiem_tra_sr02_xac_thuc(&xe), "SR02: Charging without auth must FAIL");
    xe.da_xac_thuc = 1;
    ASSERT_TRUE(kiem_tra_sr02_xac_thuc(&xe), "SR02: Charging with auth must PASS");

    /* SR03: Nhiá»‡t Ä‘á»™ >= 60 C -> Ngáº¯t sáº¡c */
    xe.pin.nhiet_do = 59.9f;
    ASSERT_TRUE(kiem_tra_sr03_nhiet_do(&xe), "SR03: Temp < 60C must PASS");
    xe.pin.nhiet_do = 60.0f;
    ASSERT_FALSE(kiem_tra_sr03_nhiet_do(&xe), "SR03: Temp >= 60C must FAIL");

    /* SR04: SOC >= 100% -> Ngáº¯t sáº¡c */
    xe.pin.soc = 99.9f;
    ASSERT_TRUE(kiem_tra_sr04_pin_day(&xe), "SR04: SOC < 100% must PASS");
    xe.pin.soc = 100.0f;
    ASSERT_FALSE(kiem_tra_sr04_pin_day(&xe), "SR04: SOC >= 100% must FAIL");

    /* SR05: Emergency -> Power = 0 */
    cong.dung_khan_cap = 1;
    cong.cong_suat_kw = 22.0f;
    ASSERT_FALSE(kiem_tra_sr05_khan_cap(&cong, &tram), "SR05: Emergency with power > 0 must FAIL");
    cong.cong_suat_kw = 0.0f;
    ASSERT_TRUE(kiem_tra_sr05_khan_cap(&cong, &tram), "SR05: Emergency with power = 0 must PASS");

    /* SR06: SOC in [0, 100] */
    xe.pin.soc = -0.1f;
    ASSERT_FALSE(kiem_tra_sr06_soc_hop_le(&xe), "SR06: SOC < 0 must FAIL");
    xe.pin.soc = 50.0f;
    ASSERT_TRUE(kiem_tra_sr06_soc_hop_le(&xe), "SR06: SOC in [0, 100] must PASS");

    /* SR07: Äá»™c quyá»n cá»•ng */
    cong.vehicle_id = 1;
    ASSERT_FALSE(kiem_tra_sr07_doc_quyen_cong(&cong, 2), "SR07: Port occupied by vehicle 1 must reject vehicle 2");

    /* SR08: Cá»•ng lá»—i -> Power = 0 */
    cong.trang_thai = CONG_LOI;
    cong.cong_suat_kw = 10.0f;
    ASSERT_FALSE(kiem_tra_sr08_ma_loi(&cong), "SR08: Fault port with power > 0 must FAIL");

    /* SR10: Tá»•ng cĂ´ng suáº¥t <= 100 kW */
    ASSERT_TRUE(kiem_tra_sr10_gioi_han_cong_suat_tram(100.0f, 100.0f), "SR10: Total 100 kW <= 100 kW must PASS");
    ASSERT_FALSE(kiem_tra_sr10_gioi_han_cong_suat_tram(100.1f, 100.0f), "SR10: Total 100.1 kW > 100 kW must FAIL");

    PRINT_TEST_RESULT("UNIT_SAFETY_RULES");
    return g_tests_failed > 0 ? 1 : 0;
}
