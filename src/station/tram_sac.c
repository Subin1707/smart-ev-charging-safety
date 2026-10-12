#include <stdio.h>
#include <string.h>
#include "tram_sac.h"
#include "trang_thai_xe.h"
#include "nhat_ky_su_kien.h"
#include "database.h"

void khoi_tao_tram_sac(TramSac *tram, const char *ma_tram) {
    if (!tram) return;

    tram->id = 1;
    if (ma_tram) {
        strncpy(tram->ma_tram, ma_tram, sizeof(tram->ma_tram) - 1);
        tram->ma_tram[sizeof(tram->ma_tram) - 1] = '\0';
    } else {
        strcpy(tram->ma_tram, "STATION01");
    }

    for (int i = 0; i < SO_CONG_SAC; i++) {
        khoi_tao_cong_sac(&tram->cong[i], i + 1);
    }

    tram->cong_suat_toi_da = CONG_SUAT_TRAM_TOI_DA;
    tram->cong_suat_hien_tai = 0.0f;
    tram->emergency = 0;
}

int ket_noi_xe_vao_tram(TramSac *tram, int port_idx, XeDien *xe) {
    if (!tram || !xe) return 0;
    if (port_idx < 0 || port_idx >= SO_CONG_SAC) return 0;

    if (tram->emergency || xe->id < 0) return 0;
    for (int i = 0; i < SO_CONG_SAC; i++) {
        if (tram->cong[i].vehicle_id == xe->id) {
            if (i == port_idx && tram->cong[i].trang_thai == CONG_DA_DAT &&
                xe->assigned_port == i + 1 && !xe->da_ket_noi) continue;
            /* Repeated CONNECT must not reset an active charging session. */
            return i == port_idx && xe->da_ket_noi && xe->assigned_port == i + 1;
        }
    }
    if (xe->da_ket_noi) return 0;

    if (ket_noi_xe_vao_cong(&tram->cong[port_idx], xe->id)) {
        if (tram->cong[port_idx].trang_thai == CONG_DA_DAT
            || tram->cong[port_idx].trang_thai == CONG_DA_KET_NOI) {
            xe->assigned_port = port_idx + 1;
        }
        xe->da_ket_noi = 1;
        xe->trang_thai = XE_DA_KET_NOI;
        return 1;
    }
    return 0;
}

int ngat_ket_noi_xe_khoi_tram(TramSac *tram, int port_idx, XeDien *xe) {
    if (!tram) return 0;
    if (port_idx < 0 || port_idx >= SO_CONG_SAC) return 0;
    if (xe && tram->cong[port_idx].vehicle_id != xe->id) return 0;

    ngat_ket_noi_cong(&tram->cong[port_idx]);
    if (xe) {
        xe->assigned_port = -1;
        xe->da_ket_noi = 0;
        xe->da_xac_thuc = 0;
        xe->trang_thai = XE_DA_NGAT_KET_NOI;
    }
    cap_nhat_tong_cong_suat_tram(tram);
    return 1;
}

float cap_nhat_tong_cong_suat_tram(TramSac *tram) {
    if (!tram) return 0.0f;

    float total = 0.0f;
    for (int i = 0; i < SO_CONG_SAC; i++) {
        total += tram->cong[i].cong_suat_kw;
    }
    tram->cong_suat_hien_tai = total;
    return total;
}

void hien_thi_dashboard(const TramSac *tram, const XeDien ds_xe[], int so_xe) {
    if (!tram) return;

    int xe_ket_noi = 0;
    int cong_dang_sac = 0;
    float tong_cong_suat = 0.0f;

    for (int v = 0; v < so_xe; v++) {
        if (ds_xe && ds_xe[v].da_ket_noi) xe_ket_noi++;
    }
    for (int i = 0; i < SO_CONG_SAC; i++) {
        if (tram->cong[i].trang_thai == CONG_DANG_SAC) cong_dang_sac++;
        tong_cong_suat += tram->cong[i].cong_suat_kw;
    }

    float cong_suat_con_lai = tram->cong_suat_toi_da - tong_cong_suat;
    if (cong_suat_con_lai < 0.0f) cong_suat_con_lai = 0.0f;

    const char *trang_thai_he_thong = "SAFE";
    if (tram->emergency) {
        trang_thai_he_thong = "EMERGENCY";
    } else if (tong_cong_suat > tram->cong_suat_toi_da) {
        trang_thai_he_thong = "WARNING";
    }

    printf("\n=======================================================================\n");
    printf("                  SMART EV CHARGING STATION\n");
    printf("=======================================================================\n");
    printf("Station       : %s\n", tram->ma_tram);
    printf("Status        : ACTIVE\n");
    printf("Emergency     : %s\n", tram->emergency ? "YES" : "NO");
    printf("Database      : %s\n", database_dang_ket_noi() ? "CONNECTED" : "OFFLINE");
    printf("-----------------------------------------------------------------------\n");
    printf("%-6s %-9s %-7s %-9s %-9s %-9s %-12s\n",
           "PORT", "VEHICLE", "SOC", "TEMP", "POWER", "AUTH", "STATE");
    printf("-----------------------------------------------------------------------\n");

    for (int i = 0; i < SO_CONG_SAC; i++) {
        const CongSac *c = &tram->cong[i];
        char str_xe[DO_DAI_MA_XE] = "--";
        char str_soc[16] = "--";
        char str_temp[16] = "--";
        const char *auth = "--";
        const char *state = ten_trang_thai_cong(c->trang_thai);

        if (c->vehicle_id != -1 && ds_xe && so_xe > 0) {
            for (int v = 0; v < so_xe; v++) {
                if (ds_xe[v].id == c->vehicle_id) {
                    snprintf(str_xe, sizeof(str_xe), "%s", ds_xe[v].ma_xe);
                    snprintf(str_soc, sizeof(str_soc), "%.1f%%", ds_xe[v].pin.soc);
                    snprintf(str_temp, sizeof(str_temp), "%.1f C", ds_xe[v].pin.nhiet_do);
                    auth = ds_xe[v].da_xac_thuc ? "YES" : "NO";
                    state = ten_trang_thai_xe(ds_xe[v].trang_thai);
                    break;
                }
            }
        }

        printf("%-6d %-9s %-7s %-9s %5.1f kW %-9s %-12s\n",
               c->id,
               str_xe,
               str_soc,
               str_temp,
               c->cong_suat_kw,
               auth,
               state);
    }
    printf("-----------------------------------------------------------------------\n");
    printf("Active Ports       : %d / %d\n", cong_dang_sac, SO_CONG_SAC);
    printf("Connected Vehicles : %d / %d\n", xe_ket_noi, so_xe);
    printf("Current Power      : %.1f kW\n", tong_cong_suat);
    printf("Station Limit      : %.1f kW\n", tram->cong_suat_toi_da);
    printf("Available Power    : %.1f kW\n", cong_suat_con_lai);
    printf("Safety Events      : %d\n", lay_tong_so_su_kien());
    printf("SYSTEM STATUS      : %s\n", trang_thai_he_thong);
    printf("=======================================================================\n\n");
}

void in_trang_thai_tram(const TramSac *tram, const XeDien ds_xe[], int so_xe) {
    hien_thi_dashboard(tram, ds_xe, so_xe);
}
