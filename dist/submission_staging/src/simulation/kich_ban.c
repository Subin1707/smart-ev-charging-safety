#include <string.h>

#include "kich_ban.h"
#include "dung_khan_cap.h"
#include "hang_so.h"
#include "phat_hien_loi.h"
#include "su_kien_he_thong.h"

static int tim_xe(const KichBanMoPhong *kich_ban, int so_xe) {
    if (!kich_ban || kich_ban->vehicle_index < 0 || kich_ban->vehicle_index >= so_xe) return -1;
    return kich_ban->vehicle_index;
}

void khoi_tao_kich_ban(KichBanMoPhong *kich_ban) {
    if (!kich_ban) return;
    kich_ban->loai = SCENARIO_NORMAL;
    kich_ban->vehicle_index = -1;
    kich_ban->trigger_tick = 5;
    kich_ban->da_kich_hoat = 0;
    kich_ban->da_load = 0;
}

const char *ten_kich_ban_scenario(LoaiScenario scenario) {
    switch (scenario) {
        case SCENARIO_NORMAL: return "NORMAL";
        case SCENARIO_OVERHEAT: return "OVERHEAT";
        case SCENARIO_AUTH_FAILURE: return "AUTH_FAILURE";
        case SCENARIO_UNEXPECTED_DISCONNECT: return "UNEXPECTED_DISCONNECT";
        case SCENARIO_POWER_OVERLOAD: return "POWER_OVERLOAD";
        case SCENARIO_EMERGENCY_STOP: return "EMERGENCY_STOP";
        case SCENARIO_MIXED: return "MIXED";
        case SCENARIO_CRITICAL_TEMPERATURE: return "CRITICAL_TEMPERATURE";
        case SCENARIO_THERMAL_RUNAWAY: return "THERMAL_RUNAWAY";
        case SCENARIO_FIRE_RISK: return "FIRE_RISK";
        default: return "NORMAL";
    }
}

int dat_kich_ban(KichBanMoPhong *kich_ban, const char *name, int vehicle_index) {
    if (!kich_ban || !name) return 0;

    LoaiScenario scenario = SCENARIO_NORMAL;
    if (strcmp(name, "OVERHEAT") == 0) scenario = SCENARIO_OVERHEAT;
    else if (strcmp(name, "AUTH_FAILURE") == 0) scenario = SCENARIO_AUTH_FAILURE;
    else if (strcmp(name, "UNEXPECTED_DISCONNECT") == 0) scenario = SCENARIO_UNEXPECTED_DISCONNECT;
    else if (strcmp(name, "POWER_OVERLOAD") == 0) scenario = SCENARIO_POWER_OVERLOAD;
    else if (strcmp(name, "EMERGENCY_STOP") == 0) scenario = SCENARIO_EMERGENCY_STOP;
    else if (strcmp(name, "MIXED") == 0) scenario = SCENARIO_MIXED;
    else if (strcmp(name, "CRITICAL_TEMPERATURE") == 0) scenario = SCENARIO_CRITICAL_TEMPERATURE;
    else if (strcmp(name, "THERMAL_RUNAWAY") == 0) scenario = SCENARIO_THERMAL_RUNAWAY;
    else if (strcmp(name, "FIRE_RISK") == 0) scenario = SCENARIO_FIRE_RISK;
    else if (strcmp(name, "NORMAL") != 0) return 0;

    kich_ban->loai = scenario;
    kich_ban->vehicle_index = vehicle_index;
    kich_ban->trigger_tick = 5;
    kich_ban->da_kich_hoat = 0;
    kich_ban->da_load = 1;
    return 1;
}

void ap_dung_kich_ban_tick(KichBanMoPhong *kich_ban,
                           int tick,
                           TramSac *tram,
                           XeDien ds_xe[],
                           int so_xe) {
    if (!kich_ban || !kich_ban->da_load || kich_ban->da_kich_hoat
        || tick < kich_ban->trigger_tick || !tram || !ds_xe) return;

    int vehicle_index = tim_xe(kich_ban, so_xe);
    if (vehicle_index < 0 && kich_ban->loai != SCENARIO_EMERGENCY_STOP
        && kich_ban->loai != SCENARIO_POWER_OVERLOAD) return;

    switch (kich_ban->loai) {
        case SCENARIO_CRITICAL_TEMPERATURE:
            ds_xe[vehicle_index].pin.nhiet_do = 70.0f;
            break;
        case SCENARIO_THERMAL_RUNAWAY:
            ds_xe[vehicle_index].pin.nhiet_do = 80.0f;
            break;
        case SCENARIO_FIRE_RISK:
            ds_xe[vehicle_index].pin.nhiet_do = 90.0f;
            kich_hoat_dung_khan_cap_tram(tram, ds_xe, so_xe);
            break;
        case SCENARIO_OVERHEAT:
            ds_xe[vehicle_index].pin.nhiet_do = NHIET_DO_TOI_DA + 1.0f;
            break;
        case SCENARIO_AUTH_FAILURE:
            ds_xe[vehicle_index].trang_thai = XE_LOI;
            ds_xe[vehicle_index].da_xac_thuc = 0;
            for (int port = 0; port < SO_CONG_SAC; port++) {
                if (tram->cong[port].vehicle_id == ds_xe[vehicle_index].id) {
                    tram->cong[port].cong_suat_kw = 0.0f;
                    tram->cong[port].dong_dien = 0.0f;
                    tram->cong[port].trang_thai = CONG_LOI;
                    tram->cong[port].ma_loi = LOI_CHUA_XAC_THUC;
                }
            }
            break;
        case SCENARIO_UNEXPECTED_DISCONNECT:
            ds_xe[vehicle_index].da_ket_noi = 0;
            ds_xe[vehicle_index].trang_thai = XE_LOI;
            for (int port = 0; port < SO_CONG_SAC; port++) {
                if (tram->cong[port].vehicle_id == ds_xe[vehicle_index].id) {
                    tram->cong[port].cong_suat_kw = 0.0f;
                    tram->cong[port].dong_dien = 0.0f;
                    tram->cong[port].trang_thai = CONG_LOI;
                    tram->cong[port].ma_loi = LOI_CHUA_KET_NOI;
                }
            }
            break;
        case SCENARIO_EMERGENCY_STOP:
            kich_hoat_dung_khan_cap_tram(tram, ds_xe, so_xe);
            break;
        case SCENARIO_POWER_OVERLOAD:
            for (int i = 0; i < so_xe; i++) ds_xe[i].cong_suat_sac_toi_da = 30.0f;
            break;
        case SCENARIO_NORMAL:
            if (vehicle_index >= 0) {
                ds_xe[vehicle_index].kich_ban = KB_BINH_THUONG;
                if (ds_xe[vehicle_index].trang_thai == XE_LOI) {
                    ds_xe[vehicle_index].trang_thai = XE_CHO;
                    ds_xe[vehicle_index].da_xac_thuc = 0;
                }
            }
            break;
        case SCENARIO_MIXED:
            if (vehicle_index >= 0) ds_xe[vehicle_index].pin.nhiet_do = NHIET_DO_TOI_DA + 1.0f;
            if (so_xe > 1) {
                int other = (vehicle_index + 1) % so_xe;
                ds_xe[other].da_xac_thuc = 0;
                ds_xe[other].trang_thai = XE_LOI;
            }
            break;
    }

    kich_ban->da_kich_hoat = 1;
    them_su_kien(tick, "SCENARIO", "INFO", vehicle_index >= 0 ? ds_xe[vehicle_index].ma_xe : "",
                 "SCENARIO_TRIGGERED", ten_kich_ban_scenario(kich_ban->loai));
}
