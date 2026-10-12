/* Generated from specification/battery.json */
#include <assert.h>
#include "tram_sac.h"
#include "xe_dien.h"
#include "dieu_khien_sac.h"

static void prepare_connected_authenticated(XeDien *xe, CongSac *cong)
{
    xe->da_ket_noi = 1;
    xe->da_xac_thuc = 1;
    xe->assigned_port = cong->id;
    cong->vehicle_id = xe->id;
    cong->trang_thai = CONG_DA_KET_NOI;
}

void test_battery(void)
{
    XeDien xe;
    CongSac cong;

    khoi_tao_xe_dien(&xe, 2, "EVGEN02", 60.0f, 50.0f, 25.0f, 22.0f, KB_BINH_THUONG);
    khoi_tao_cong_sac(&cong, 1);
    prepare_connected_authenticated(&xe, &cong);

    xe.pin.soc = 100.0f;
    assert(co_the_bat_dau_sac(&xe, &cong) == 0);

    xe.pin.soc = 50.0f;
    xe.pin.nhiet_do = 65.0f;
    assert(co_the_bat_dau_sac(&xe, &cong) == 0);
}

int main(void)
{
    test_battery();
    return 0;
}
