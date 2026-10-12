
#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "harness_common.h"

static int boundary_cases = 0;
static int boolean_cases = 0;

static void setup_vehicle(TramSac *tram, XeDien *xe, int port_idx, const char *id)
{
    khoi_tao_tram_sac(tram, "GD95");
    khoi_tao_xe_dien(xe, 1, id, 60.0f, 50.0f, 25.0f, 22.0f, KB_BINH_THUONG);
    assert(ket_noi_xe_vao_tram(tram, port_idx, xe) == 1);
}

static void auth_vehicle(XeDien *xe)
{
    char token[DO_DAI_TOKEN];
    sinh_token_xe(xe->ma_xe, token, sizeof(token));
    assert(xac_thuc_xe(xe, token) == 1);
}

static void test_soc_boundaries(void)
{
    float values[] = {-1.0f, 0.0f, 1.0f, 50.0f, 99.0f, 100.0f, 101.0f};
    for (int i = 0; i < 7; i++) {
        Pin pin;
        khoi_tao_pin(&pin, 60.0f, values[i], 25.0f);
        int expected = values[i] >= SOC_MIN && values[i] <= SOC_MAX;
        assert(soc_hop_le(&pin) == expected);
        boundary_cases++;
    }
}

static void test_temperature_boundaries(void)
{
    float values[] = {-21.0f, -20.0f, -19.0f, 59.0f, 60.0f, 61.0f, 80.0f};
    for (int i = 0; i < 7; i++) {
        Pin pin;
        khoi_tao_pin(&pin, 60.0f, 50.0f, values[i]);
        int expected = values[i] >= NHIET_DO_TOI_DA;
        assert(pin_qua_nhiet(&pin) == expected);
        boundary_cases++;
    }
}

static void test_authentication(void)
{
    TramSac tram;
    XeDien xe;
    char token[DO_DAI_TOKEN];
    setup_vehicle(&tram, &xe, 0, "EV-GD95-AUTH");
    assert(xac_thuc_xe(&xe, "bad-token") == 0);
    assert(xe.da_xac_thuc == 0);
    sinh_token_xe(xe.ma_xe, token, sizeof(token));
    assert(xac_thuc_xe(&xe, token) == 1);
    assert(xe.da_xac_thuc == 1);
    assert(xac_thuc_xe(NULL, token) == 0);
}

static void test_disconnect_clears_authentication(void)
{
    TramSac tram;
    XeDien xe;
    setup_vehicle(&tram, &xe, 0, "EV-GD95-DISC");
    auth_vehicle(&xe);
    assert(ngat_ket_noi_xe_khoi_tram(&tram, 0, &xe) == 1);
    assert(xe.da_ket_noi == 0);
    assert(xe.da_xac_thuc == 0);
}

static void test_port_and_charging(void)
{
    TramSac tram;
    XeDien xe1;
    XeDien xe2;
    PhienSac phien;
    setup_vehicle(&tram, &xe1, 0, "EV-GD95-P1");
    khoi_tao_xe_dien(&xe2, 2, "EV-GD95-P2", 60.0f, 50.0f, 25.0f, 22.0f, KB_BINH_THUONG);
    assert(ket_noi_xe_vao_cong(&tram.cong[0], xe2.id) == 0);
    assert(bat_dau_sac(&xe1, &tram.cong[0], &phien, 22.0f) == 0);
    auth_vehicle(&xe1);
    tram.cong[0].trang_thai = CONG_SAN_SANG;
    assert(bat_dau_sac(&xe1, &tram.cong[0], &phien, 22.0f) == 1);
    assert(tram.cong[0].cong_suat_kw > 0.0f);
}

static void test_soc_full_and_temperature_monitoring(void)
{
    TramSac tram;
    XeDien xe;
    PhienSac phien;
    setup_vehicle(&tram, &xe, 0, "EV-GD95-MON");
    auth_vehicle(&xe);
    tram.cong[0].trang_thai = CONG_SAN_SANG;
    xe.pin.soc = 100.0f;
    assert(co_the_bat_dau_sac(&xe, &tram.cong[0]) == 0);
    tram.cong[0].trang_thai = CONG_DANG_SAC;
    tram.cong[0].cong_suat_kw = 11.0f;
    (void)phien;
    (void)giam_sat_xe_va_cong(&xe, &tram.cong[0], &tram);
    assert(tram.cong[0].cong_suat_kw == 0.0f);

    setup_vehicle(&tram, &xe, 0, "EV-GD95-HOT");
    auth_vehicle(&xe);
    xe.pin.nhiet_do = 60.0f;
    assert(co_the_bat_dau_sac(&xe, &tram.cong[0]) == 0);
    tram.cong[0].trang_thai = CONG_DANG_SAC;
    tram.cong[0].cong_suat_kw = 11.0f;
    (void)giam_sat_xe_va_cong(&xe, &tram.cong[0], &tram);
    assert(tram.cong[0].cong_suat_kw == 0.0f);
    assert(tram.cong[0].trang_thai == CONG_LOI);
}

static void test_fault_emergency_and_station_monitor(void)
{
    TramSac tram;
    XeDien xe;
    XeDien ds[1];
    setup_vehicle(&tram, &xe, 0, "EV-GD95-EMG");
    auth_vehicle(&xe);
    tram.cong[0].trang_thai = CONG_DANG_SAC;
    tram.cong[0].cong_suat_kw = 22.0f;
    assert(kich_hoat_dung_khan_cap_cong(&tram.cong[0], &xe) == 1);
    assert(tram.cong[0].cong_suat_kw == 0.0f);

    setup_vehicle(&tram, &ds[0], 0, "EV-GD95-ALL");
    auth_vehicle(&ds[0]);
    tram.cong[0].trang_thai = CONG_DANG_SAC;
    tram.cong[0].cong_suat_kw = 22.0f;
    tram.cong[0].vehicle_id = ds[0].id;
    ds[0].pin.nhiet_do = 80.0f;
    assert(kiem_tra_toan_bo_tram(&tram, ds, 1) >= 1);
    assert(tram.cong[0].cong_suat_kw == 0.0f);

    setup_vehicle(&tram, &ds[0], 0, "EV-GD95-STP");
    auth_vehicle(&ds[0]);
    tram.cong[0].trang_thai = CONG_DANG_SAC;
    tram.cong[0].cong_suat_kw = 22.0f;
    assert(kich_hoat_dung_khan_cap_tram(&tram, ds, 1) == 1);
    assert(tram.cong[0].cong_suat_kw == 0.0f);
}

static void test_boolean_gate_enumeration(void)
{
    for (int mask = 0; mask < 128; mask++) {
        TramSac tram;
        XeDien xe;
        khoi_tao_tram_sac(&tram, "BOOL");
        khoi_tao_xe_dien(&xe, 1, "EV-GATE", 60.0f, 50.0f, 25.0f, 22.0f, KB_BINH_THUONG);
        int connected = (mask >> 0) & 1;
        int authenticated = (mask >> 1) & 1;
        int soc_safe = (mask >> 2) & 1;
        int temp_safe = (mask >> 3) & 1;
        int port_match = (mask >> 4) & 1;
        int emergency = (mask >> 5) & 1;
        int fault = (mask >> 6) & 1;
        xe.da_ket_noi = connected;
        xe.da_xac_thuc = authenticated;
        xe.pin.soc = soc_safe ? 50.0f : 100.0f;
        xe.pin.nhiet_do = temp_safe ? 25.0f : 60.0f;
        tram.cong[0].vehicle_id = port_match ? xe.id : -1;
        tram.cong[0].dung_khan_cap = emergency;
        tram.cong[0].trang_thai = fault ? CONG_LOI : CONG_SAN_SANG;
        tram.cong[0].ma_loi = fault ? 1 : 0;
        int expected = connected && authenticated && soc_safe && temp_safe && port_match && !emergency && !fault;
        assert(co_the_bat_dau_sac(&xe, &tram.cong[0]) == expected);
        boolean_cases++;
    }
}

int main(void)
{
    test_soc_boundaries();
    test_temperature_boundaries();
    test_authentication();
    test_disconnect_clears_authentication();
    test_port_and_charging();
    test_soc_full_and_temperature_monitoring();
    test_fault_emergency_and_station_monitor();
    test_boolean_gate_enumeration();
    printf("BOUNDARY_CASES=%d\n", boundary_cases);
    printf("BOOLEAN_COMBINATIONS=%d\n", boolean_cases);
    printf("GD95_DYNAMIC_PASS\n");
    return 0;
}
