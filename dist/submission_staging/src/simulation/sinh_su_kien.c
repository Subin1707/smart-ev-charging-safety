#include <stdio.h>
#include "sinh_su_kien.h"
#include "logger.h"
#include "nhat_ky_su_kien.h"
#include "dung_khan_cap.h"

void xu_ly_su_kien_tick(int tick, TramSac *tram, XeDien ds_xe[], int so_xe) {
    if (!tram || !ds_xe || so_xe <= 0) return;

    for (int i = 0; i < so_xe; i++) {
        XeDien *xe = &ds_xe[i];
        int port = xe->assigned_port - 1;
        if (port < 0 || port >= SO_CONG_SAC || tram->cong[port].vehicle_id != xe->id) continue;
        CongSac *cong = &tram->cong[port];

        switch (xe->kich_ban) {
            case KB_QUA_NHIET:
                if (tick == 5 && cong->trang_thai == CONG_DANG_SAC) {
                    xe->pin.nhiet_do = 64.5f;
                    ghi_log(LOG_WARNING, "TICK %d: Pin %s tang dot bien len %.1f C!", tick, xe->ma_xe, xe->pin.nhiet_do);
                }
                break;

            case KB_DUNG_KHAN_CAP:
                if (tick == 8 && cong->trang_thai == CONG_DANG_SAC) {
                    ghi_log(LOG_CRITICAL, "TICK %d: Nhan tin hieu dung khan cap tu %s tai Cong %d!", tick, xe->ma_xe, cong->id);
                    kich_hoat_dung_khan_cap_cong(cong, xe);
                }
                break;

            default:
                break;
        }
    }
}
