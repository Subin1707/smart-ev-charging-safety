#include <stdio.h>
#include "dieu_khien_sac.h"
#include "xe_dien.h"
#include "cong_sac.h"
int main(void) {
    int command, auth, temperature, soc, power, port;
    while (scanf("%d %d %d %d %d %d", &command, &auth, &temperature, &soc, &power, &port) == 6) {
        XeDien xe = {0};
        CongSac cong;
        khoi_tao_cong_sac(&cong, port);
        xe.id = 3;
        xe.da_ket_noi = 1;
        xe.da_xac_thuc = auth == 1;
        xe.pin.soc = (float)soc;
        xe.pin.nhiet_do = (float)temperature;
        xe.trang_thai = XE_DA_KET_NOI;
        cong.vehicle_id = xe.id;
        int valid = command == 1 && port >= 1 && port <= 5 && power > 0 && power <= 22;
        int target = valid && auth == 1 && temperature >= 60 && soc >= 0 && soc < 100;
        int accepted = valid && co_the_bat_dau_sac(&xe, &cong);
        int violation = accepted && (!xe.da_xac_thuc || temperature >= 60 || soc < 0 || soc >= 100);
        printf("RESULT %d %d %d\n", accepted, target, violation);
    }
    return 0;
}
