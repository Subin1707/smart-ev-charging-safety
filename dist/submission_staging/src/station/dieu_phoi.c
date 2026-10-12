#include "dieu_phoi.h"
#include "su_kien_he_thong.h"

int tim_cong_ranh(const TramSac *tram) {
    if (!tram) return -1;

    for (int i = 0; i < SO_CONG_SAC; i++) {
        if (tram->cong[i].trang_thai == CONG_RANH && tram->cong[i].vehicle_id == -1) {
            return i; /* Chá»‰ sá»‘ tá»« 0 Ä‘áº¿n 4 */
        }
    }
    return -1; /* KhĂ´ng cĂ²n cá»•ng trá»‘ng */
}

int tim_cong_sac_ranh(const TramSac *tram) {
    if (!tram) return -1;

    for (int i = 0; i < SO_CONG_SAC; i++) {
        if (tram->cong[i].trang_thai == CONG_RANH
            && tram->cong[i].vehicle_id == -1) {
            return i;
        }
    }
    return -1;
}

int gan_cong_sac_tu_dong(TramSac *tram, XeDien *xe) {
    if (!tram || !xe || xe->assigned_port > 0) return -1;

    int port = tim_cong_sac_ranh(tram);
    if (port < 0) return -1;

    xe->assigned_port = port + 1;
    tram->cong[port].vehicle_id = xe->id;
    tram->cong[port].trang_thai = CONG_DA_DAT;
    them_su_kien(0, "SCHEDULER", "INFO", xe->ma_xe,
                 "PORT_ASSIGNED", "Vehicle assigned to charging port");
    return port;
}

void sap_xep_xe_theo_soc(const TramSac *tram,
                         const XeDien ds_xe[],
                         int so_xe,
                         int thu_tu_cong[],
                         int *so_cong) {
    if (!tram || !ds_xe || so_xe <= 0 || !thu_tu_cong || !so_cong) return;

    *so_cong = 0;
    for (int i = 0; i < SO_CONG_SAC; i++) {
        const CongSac *cong = &tram->cong[i];
        if (cong->trang_thai == CONG_DANG_SAC &&
            !cong->dung_khan_cap && cong->ma_loi == 0) {
            thu_tu_cong[*so_cong] = i;
            (*so_cong)++;
        }
    }

    for (int i = 0; i < *so_cong - 1; i++) {
        for (int j = i + 1; j < *so_cong; j++) {
            int cong_i = thu_tu_cong[i];
            int cong_j = thu_tu_cong[j];
            float soc_i = 101.0f;
            float soc_j = 101.0f;

            for (int v = 0; v < so_xe; v++) {
                if (ds_xe[v].id == tram->cong[cong_i].vehicle_id) soc_i = ds_xe[v].pin.soc;
                if (ds_xe[v].id == tram->cong[cong_j].vehicle_id) soc_j = ds_xe[v].pin.soc;
            }

            if (soc_j < soc_i) {
                int temp = thu_tu_cong[i];
                thu_tu_cong[i] = thu_tu_cong[j];
                thu_tu_cong[j] = temp;
            }
        }
    }
}
