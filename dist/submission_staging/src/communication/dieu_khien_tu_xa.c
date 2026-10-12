#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

#include "dieu_khien_tu_xa.h"
#include "dung_khan_cap.h"
#include "phat_hien_loi.h"
#include "su_kien_he_thong.h"
#include "dieu_phoi.h"

static void xoa_lenh(const char *duong_dan) {
    FILE *reset = fopen(duong_dan, "w");
    if (!reset) return;

    fputs("{\"command\":\"NONE\"}\n", reset);
    fclose(reset);
}

static int tim_gia_tri_chuoi(const char *json,
                                      const char *key,
                                      char *out,
                                      size_t out_size) {
     char pattern[64];
     if (!json || !key || !out || out_size == 0) return 0;

     snprintf(pattern, sizeof(pattern), "\"%s\"", key);
     const char *cursor = strstr(json, pattern);
     if (!cursor) return 0;

     cursor += strlen(pattern);
     while (*cursor && (isspace((unsigned char)*cursor) || *cursor == ':')) cursor++;
     if (*cursor != '"') return 0;
     cursor++;

     const char *end = strchr(cursor, '"');
     if (!end) return 0;

     size_t length = (size_t)(end - cursor);
     if (length >= out_size) length = out_size - 1;
     memcpy(out, cursor, length);
     out[length] = '\0';
     return 1;
}

static int tim_gia_tri_so(const char *json, const char *key, int *out) {
    char pattern[64];
    char *end = NULL;
    long value;

    if (!json || !key || !out) return 0;
    snprintf(pattern, sizeof(pattern), "\"%s\"", key);
    const char *cursor = strstr(json, pattern);
    if (!cursor) return 0;

    cursor += strlen(pattern);
    while (*cursor && (isspace((unsigned char)*cursor) || *cursor == ':')) cursor++;
    value = strtol(cursor, &end, 10);
    if (end == cursor) return 0;

    *out = (int)value;
    return 1;
}

void xu_ly_lenh_dieu_khien(const char *duong_dan,
                           TramSac *tram,
                           XeDien ds_xe[],
                           int so_xe,
                           int *tick,
                           DieuKhienMoPhong *dieu_khien,
                           KichBanMoPhong *kich_ban) {
    if (!duong_dan || !tram) return;

    FILE *file = fopen(duong_dan, "r");
    if (!file) return;

    char buffer[256] = {0};
    size_t bytes_read = fread(buffer, 1, sizeof(buffer) - 1, file);
    fclose(file);

    if (bytes_read == 0) return;

    char command[64] = {0};
    if (!tim_gia_tri_chuoi(buffer, "command", command, sizeof(command))) {
        xoa_lenh(duong_dan);
        return;
    }

    if (strcmp(command, "EMERGENCY_RELEASE") == 0) {
        if (khoi_phuc_khan_cap_tram(tram)) {
            them_su_kien(tick ? *tick : 0, "SAFETY", "INFO", "",
                         "EMERGENCY_RELEASE", "Emergency stop released");
        }
        xoa_lenh(duong_dan);
        return;
    }

    if (strcmp(command, "RESET") == 0) {
        khoi_tao_danh_sach_5_xe(ds_xe);
        for (int i = 0; i < so_xe; i++) ds_xe[i].kich_ban = KB_BINH_THUONG;
        if (kich_ban) khoi_tao_kich_ban(kich_ban);
        khoi_tao_tram_sac(tram, "STATION-01");
        if (tick) *tick = 0;
        if (dieu_khien) {
            dieu_khien->trang_thai = MO_PHONG_TAM_DUNG;
            dieu_khien->tick_hien_tai = 0;
            dieu_khien->yeu_cau_next_tick = 0;
        }
        khoi_tao_su_kien_he_thong();
        them_su_kien(0, "SYSTEM", "INFO", "", "RESET", "Simulation reset");
        xoa_lenh(duong_dan);
        return;
    }

    if (strcmp(command, "SET_SPEED") == 0) {
        int interval = 0;
        if (dieu_khien && tim_gia_tri_so(buffer, "intervalMs", &interval)
            && (interval == 2000 || interval == 1000 || interval == 500 || interval == 200)) {
            dieu_khien->tick_interval_ms = interval;
        }
        xoa_lenh(duong_dan);
        return;
    }

    if (strcmp(command, "START") == 0) {
        if (dieu_khien) dieu_khien->trang_thai = MO_PHONG_DANG_CHAY;
        xoa_lenh(duong_dan);
        return;
    }

    if (strcmp(command, "PAUSE") == 0) {
        if (dieu_khien) dieu_khien->trang_thai = MO_PHONG_TAM_DUNG;
        xoa_lenh(duong_dan);
        return;
    }

    if (strcmp(command, "NEXT_TICK") == 0) {
        if (dieu_khien) {
            dieu_khien->trang_thai = MO_PHONG_TAM_DUNG;
            dieu_khien->yeu_cau_next_tick = 1;
        }
        xoa_lenh(duong_dan);
        return;
    }

    if (strcmp(command, "VEHICLE_ARRIVED") == 0) {
        char vehicle_id[DO_DAI_MA_XE] = {0};
        int port_id = 0;
        if (!tim_gia_tri_chuoi(buffer, "vehicleId", vehicle_id, sizeof(vehicle_id))
            || !tim_gia_tri_so(buffer, "portId", &port_id)
            || port_id < 1 || port_id > SO_CONG_SAC) {
            xoa_lenh(duong_dan);
            return;
        }

        for (int i = 0; i < so_xe; i++) {
            if (strcmp(ds_xe[i].ma_xe, vehicle_id) != 0
                || ds_xe[i].assigned_port != port_id
                || tram->cong[port_id - 1].vehicle_id != ds_xe[i].id
                || tram->cong[port_id - 1].trang_thai != CONG_DA_DAT) {
                continue;
            }

            ket_noi_xe_vao_tram(tram, port_id - 1, &ds_xe[i]);
            them_su_kien(tick ? *tick : 0, "SCHEDULER", "INFO", vehicle_id,
                         "VEHICLE_ARRIVED_AT_PORT", "Vehicle arrived at assigned port");
            them_su_kien(tick ? *tick : 0, "SYSTEM", "INFO", vehicle_id,
                         "VEHICLE_CONNECTED", "Vehicle connected to charging station");
            break;
        }
        xoa_lenh(duong_dan);
        return;
    }

    if (strcmp(command, "LOAD_SCENARIO") == 0) {
        char scenario[64] = {0};
        char vehicle_id[DO_DAI_MA_XE] = {0};
        int vehicle_index = -1;
        if (!kich_ban || !tim_gia_tri_chuoi(buffer, "scenario", scenario, sizeof(scenario))) {
            xoa_lenh(duong_dan);
            return;
        }
        tim_gia_tri_chuoi(buffer, "vehicleId", vehicle_id, sizeof(vehicle_id));
        for (int i = 0; i < so_xe; i++) {
            if (strcmp(ds_xe[i].ma_xe, vehicle_id) == 0) {
                vehicle_index = i;
                break;
            }
        }
        if (dat_kich_ban(kich_ban, scenario, vehicle_index)) {
            kich_ban->trigger_tick = (tick ? *tick : 0) + 1;
            if (kich_ban->loai == SCENARIO_OVERHEAT && vehicle_index >= 0) {
                ds_xe[vehicle_index].pin.nhiet_do = 55.0f;
            }
            them_su_kien(tick ? *tick : 0, "SCENARIO", "INFO",
                         vehicle_index >= 0 ? ds_xe[vehicle_index].ma_xe : "",
                         "SCENARIO_LOADED", scenario);
        }
        xoa_lenh(duong_dan);
        return;
    }

    if (strcmp(command, "INJECT_FAULT") == 0) {
        char vehicle_id[DO_DAI_MA_XE] = {0};
        char fault_type[64] = {0};
        if (!tim_gia_tri_chuoi(buffer, "vehicleId", vehicle_id, sizeof(vehicle_id))
            || !tim_gia_tri_chuoi(buffer, "faultType", fault_type, sizeof(fault_type))) {
            xoa_lenh(duong_dan);
            return;
        }

        for (int i = 0; i < so_xe; i++) {
            if (strcmp(ds_xe[i].ma_xe, vehicle_id) != 0) continue;
            if (strcmp(fault_type, "OVERHEAT") == 0) {
                ds_xe[i].kich_ban = KB_QUA_NHIET;
                ds_xe[i].pin.nhiet_do = NHIET_DO_TOI_DA + 1.0f;
                ds_xe[i].trang_thai = XE_LOI;
                for (int port = 0; port < SO_CONG_SAC; port++) {
                    if (tram->cong[port].vehicle_id == ds_xe[i].id) {
                        tram->cong[port].cong_suat_kw = 0.0f;
                        tram->cong[port].dong_dien = 0.0f;
                        tram->cong[port].trang_thai = CONG_LOI;
                        tram->cong[port].ma_loi = LOI_PIN_QUA_NHIET;
                    }
                }
                them_su_kien(tick ? *tick : 0, "SAFETY", "CRITICAL", vehicle_id,
                             "OVERHEAT_INJECTED", "Overheat fault injected");
                them_su_kien(tick ? *tick : 0, "SAFETY", "CRITICAL", vehicle_id,
                             "OVERHEAT_TRIP", "Overheat detected, charging power cut");
            } else if (strcmp(fault_type, "AUTH_FAILURE") == 0) {
                ds_xe[i].da_xac_thuc = 0;
                ds_xe[i].trang_thai = XE_LOI;
                for (int port = 0; port < SO_CONG_SAC; port++) {
                    if (tram->cong[port].vehicle_id == ds_xe[i].id) {
                        tram->cong[port].cong_suat_kw = 0.0f;
                        tram->cong[port].dong_dien = 0.0f;
                        tram->cong[port].trang_thai = CONG_LOI;
                        tram->cong[port].ma_loi = LOI_CHUA_XAC_THUC;
                    }
                }
                them_su_kien(tick ? *tick : 0, "AUTH", "WARNING", vehicle_id,
                             "AUTH_FAILURE", "Authentication failure injected");
            } else if (strcmp(fault_type, "UNEXPECTED_DISCONNECT") == 0) {
                ds_xe[i].da_ket_noi = 0;
                ds_xe[i].trang_thai = XE_LOI;
                for (int port = 0; port < SO_CONG_SAC; port++) {
                    if (tram->cong[port].vehicle_id == ds_xe[i].id) {
                        tram->cong[port].cong_suat_kw = 0.0f;
                        tram->cong[port].dong_dien = 0.0f;
                        tram->cong[port].trang_thai = CONG_LOI;
                        tram->cong[port].ma_loi = LOI_CHUA_KET_NOI;
                    }
                }
                them_su_kien(tick ? *tick : 0, "SAFETY", "CRITICAL", vehicle_id,
                             "UNEXPECTED_DISCONNECT", "Unexpected vehicle disconnect detected");
            }
            break;
        }
        xoa_lenh(duong_dan);
        return;
    }

    if (strcmp(command, "EMERGENCY_STOP") == 0) {
        if (kich_hoat_dung_khan_cap_tram(tram, ds_xe, so_xe)) {
            them_su_kien(tick ? *tick : 0, "SAFETY", "CRITICAL", "",
                        "EMERGENCY_STOP", "Emergency stop command accepted");
        }
        xoa_lenh(duong_dan);
        return;
    }

    xoa_lenh(duong_dan);
}
