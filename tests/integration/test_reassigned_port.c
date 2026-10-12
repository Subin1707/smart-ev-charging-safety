#include "../test_helper.h"
#include "mo_phong.h"
#include "dieu_khien_sac.h"
#include "xac_thuc.h"
#include "token.h"

int main(void) {
    TramSac tram;
    XeDien vehicles[SO_XE_TOI_DA];
    PhienSac sessions[SO_CONG_SAC] = {0};
    ChiSoHeThong metrics;
    HangChoSac queue;
    KichBanMoPhong scenario;
    DieuKhienMoPhong control = {MO_PHONG_DANG_CHAY, 0, 0};
    khoi_tao_tram_sac(&tram, "TEST");
    khoi_tao_danh_sach_5_xe(vehicles);
    khoi_tao_chi_so(&metrics, 1);
    khoi_tao_hang_cho(&queue);
    khoi_tao_kich_ban(&scenario);
    ASSERT_TRUE(ket_noi_xe_vao_tram(&tram, 0, &vehicles[5]), "EV06 takes released port 1");
    char token[DO_DAI_TOKEN];
    sinh_token_xe(vehicles[5].ma_xe, token, sizeof(token));
    ASSERT_TRUE(xac_thuc_xe(&vehicles[5], token), "Authenticate EV06");
    ASSERT_TRUE(bat_dau_sac(&vehicles[5], &tram.cong[0], &sessions[0], 22), "EV06 starts");
    float old_owner_soc = vehicles[0].pin.soc;
    float new_owner_soc = vehicles[5].pin.soc;
    int tick = 0;
    thuc_hien_mot_tick(&tick, &tram, vehicles, SO_XE_TOI_DA, sessions, &metrics, &control, &queue, &scenario);
    ASSERT_TRUE(vehicles[5].pin.soc > new_owner_soc, "Charge current owner EV06");
    ASSERT_FLOAT_EQ(vehicles[0].pin.soc, old_owner_soc, 0.001f, "Do not charge EV01 by array index");
    vehicles[5].pin.nhiet_do = 61;
    thuc_hien_mot_tick(&tick, &tram, vehicles, SO_XE_TOI_DA, sessions, &metrics, &control, &queue, &scenario);
    ASSERT_EQ(vehicles[5].trang_thai, XE_LOI, "Monitor faults current owner");
    ASSERT_FLOAT_EQ(tram.cong[0].cong_suat_kw, 0, 0.001f, "Fault removes power on actual port");
    PRINT_TEST_RESULT("REASSIGNED_PORT");
    return g_tests_failed ? 1 : 0;
}
