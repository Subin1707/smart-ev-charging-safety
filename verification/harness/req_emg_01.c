#include "harness_common.h"

int main(void)
{
    TramSac tram;
    XeDien vehicles[2];
    PhienSac phien;

    khoi_tao_tram_sac(&tram, "EMG01");
    khoi_tao_xe_dien(&vehicles[0], 1, "EV-EMG01A", 60.0f, 50.0f, 25.0f, 22.0f, KB_BINH_THUONG);
    khoi_tao_xe_dien(&vehicles[1], 2, "EV-EMG01B", 60.0f, 50.0f, 25.0f, 22.0f, KB_BINH_THUONG);

    assert(ket_noi_xe_vao_tram(&tram, 0, &vehicles[0]) == 1);
    harness_authenticate_vehicle(&vehicles[0]);
    assert(bat_dau_sac(&vehicles[0], &tram.cong[0], &phien, 22.0f) == 1);

    assert(kich_hoat_dung_khan_cap_tram(&tram, vehicles, 2) == 1);
    assert(tram.emergency == 1);
    for (int i = 0; i < SO_CONG_SAC; ++i) {
        assert(tram.cong[i].cong_suat_kw == 0.0f);
        assert(tram.cong[i].dong_dien == 0.0f);
        assert(tram.cong[i].trang_thai != CONG_DANG_SAC);
    }

    harness_pass("REQ-EMG-01");
    return 0;
}
