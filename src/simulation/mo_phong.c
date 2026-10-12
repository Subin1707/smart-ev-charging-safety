#ifndef _WIN32
#define _POSIX_C_SOURCE 200809L
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _WIN32
#include <windows.h>
#else
#include <time.h>
#endif
#include "mo_phong.h"
#include "hang_so.h"
#include "token.h"
#include "xac_thuc.h"
#include "phien_sac.h"
#include "dieu_khien_sac.h"
#include "quy_tac_an_toan.h"
#include "giam_sat_an_toan.h"
#include "quan_ly_cong_suat.h"
#include "sinh_su_kien.h"
#include "logger.h"
#include "nhat_ky_su_kien.h"
#include "database.h"
#include "xe_repository.h"
#include "tram_repository.h"
#include "cong_sac_repository.h"
#include "phien_sac_repository.h"
#include "telemetry_repository.h"
#include "su_kien_an_toan_repository.h"
#include "chi_so.h"
#include "du_lieu_giam_sat.h"
#include "dieu_khien_tu_xa.h"
#include "su_kien_he_thong.h"
#include "dieu_phoi.h"
#include "hang_cho.h"

void in_dashboard_tick(int tick, const TramSac *tram, const XeDien ds_xe[], int so_xe) {
    if (!tram) return;

    printf("\n============================= TICK %02d =============================\n", tick);
    printf("PORT   EV       SOC      TEMP      POWER        STATE\n");
    printf("--------------------------------------------------------------------\n");

    for (int i = 0; i < SO_CONG_SAC; i++) {
        const CongSac *c = &tram->cong[i];
        char str_ev[DO_DAI_MA_XE] = "--";
        char str_soc[16] = "--";
        char str_temp[16] = "--";

        if (c->vehicle_id != -1 && ds_xe && so_xe > 0) {
            for (int v = 0; v < so_xe; v++) {
                if (ds_xe[v].id == c->vehicle_id) {
                    snprintf(str_ev, sizeof(str_ev), "%s", ds_xe[v].ma_xe);
                    snprintf(str_soc, sizeof(str_soc), "%.1f %%", ds_xe[v].pin.soc);
                    snprintf(str_temp, sizeof(str_temp), "%.1f C", ds_xe[v].pin.nhiet_do);
                    break;
                }
            }
        }

        printf("%-6d %-8s %-8s %-9s %5.1f kW      %-14s\n",
               c->id, str_ev, str_soc, str_temp, c->cong_suat_kw,
               ten_trang_thai_cong(c->trang_thai));
    }
    printf("--------------------------------------------------------------------\n");
    printf("TOTAL POWER   : %.1f / %.1f kW\n", tram->cong_suat_hien_tai, tram->cong_suat_toi_da);
    printf("SAFETY EVENTS : %d\n", lay_tong_so_su_kien());
    printf("SYSTEM STATUS : %s\n", tram->emergency ? "EMERGENCY" : "OPERATIONAL");
    printf("====================================================================\n");
}

void thuc_hien_mot_tick(int *tick_hien_tai,
                        TramSac *tram,
                        XeDien ds_xe[],
                        int so_xe,
                        PhienSac ds_phien[],
                        ChiSoHeThong *chi_so,
                        const DieuKhienMoPhong *dieu_khien,
                        HangChoSac *queue,
                        KichBanMoPhong *kich_ban) {
    if (!tick_hien_tai || !tram || !ds_xe || !chi_so || so_xe <= 0) return;

    (*tick_hien_tai)++;
    int tick = *tick_hien_tai;
        chi_so->tong_tick = tick;

        ap_dung_kich_ban_tick(kich_ban, tick, tram, ds_xe, so_xe);

        for (int i = 0; i < so_xe; i++) {
            if (ds_xe[i].trang_thai == XE_CHO && ds_xe[i].assigned_port < 0) {
                if (!co_trong_hang_cho(queue, i)
                    && !them_vao_hang_cho(queue, i)) continue;
                them_su_kien(tick, "SCHEDULER", "INFO", ds_xe[i].ma_xe,
                             "QUEUE_ENTERED", "Vehicle entered charging queue");
            }
        }

        int assignments_this_tick = 0;
        while (queue && queue->count > 0 && assignments_this_tick < 1) {
            int port = tim_cong_sac_ranh(tram);
            if (port < 0) break;

            int vehicle_index = lay_xe_dau_hang(queue);
            if (vehicle_index < 0 || vehicle_index >= so_xe) continue;
            if (gan_cong_sac_tu_dong(tram, &ds_xe[vehicle_index]) >= 0) {
                assignments_this_tick++;
                them_su_kien(tick, "SCHEDULER", "INFO", ds_xe[vehicle_index].ma_xe,
                             "QUEUE_LEFT", "Vehicle left charging queue");
                them_su_kien(tick, "SCHEDULER", "INFO", ds_xe[vehicle_index].ma_xe,
                             "PORT_ASSIGNED_FROM_QUEUE", "Vehicle assigned to a released port");
            }
        }

        /* Full vehicles leave on the tick after charging is stopped. */
        for (int i = 0; i < so_xe; i++) {
            if (ds_xe[i].trang_thai != XE_DA_DAY) continue;

            for (int port = 0; port < SO_CONG_SAC; port++) {
                if (tram->cong[port].vehicle_id != ds_xe[i].id) continue;

                ngat_ket_noi_xe_khoi_tram(tram, port, &ds_xe[i]);
                them_su_kien(tick, "VEHICLE", "INFO", ds_xe[i].ma_xe,
                             "VEHICLE_DISCONNECTED",
                             "Charging completed and vehicle disconnected");
                break;
            }
        }

        /* Authenticate and charge only after arrival has connected the vehicle.
         * A vehicle that was authenticated in a prior tick must still be allowed
         * to pass the charging gate on the next tick; otherwise it remains stuck
         * in CONNECTED/AUTHENTICATED forever.
         */
        for (int i = 0; i < so_xe; i++) {
            int port = ds_xe[i].assigned_port - 1;
            if (port < 0 || port >= SO_CONG_SAC || !ds_xe[i].da_ket_noi
                || ds_xe[i].trang_thai == XE_LOI
                || ds_xe[i].trang_thai == XE_DANG_SAC
                || ds_xe[i].trang_thai == XE_DA_DAY) continue;

            if (!ds_xe[i].da_xac_thuc) {
                char token[DO_DAI_TOKEN];
                sinh_token_xe(ds_xe[i].ma_xe, token, sizeof(token));
                if (ds_xe[i].kich_ban == KB_LOI_XAC_THUC || !xac_thuc_xe(&ds_xe[i], token)) continue;
                tram->cong[port].trang_thai = CONG_SAN_SANG;
                ds_xe[i].trang_thai = XE_SAN_SANG;
                them_su_kien(tick, "AUTH", "INFO", ds_xe[i].ma_xe, "AUTH_SUCCESS", "Vehicle authenticated");
            }

            if (ds_xe[i].da_xac_thuc
                && bat_dau_sac(&ds_xe[i], &tram->cong[port], &ds_phien[port], ds_xe[i].cong_suat_sac_toi_da)) {
                tao_phien_sac_db(&ds_phien[port]);
                them_su_kien(tick, "CHARGING", "INFO", ds_xe[i].ma_xe, "CHARGING_STARTED", "Charging started");
            }
        }

        /* 1. Sinh su kien */
        xu_ly_su_kien_tick(tick, tram, ds_xe, so_xe);

        /* Kiem tra neu co dung khan cap o tick hien tai thi ghi DB */
        for (int i = 0; i < so_xe; i++) {
            int port = ds_xe[i].assigned_port - 1;
            if (port < 0 || port >= SO_CONG_SAC || tram->cong[port].vehicle_id != ds_xe[i].id) continue;
            if (tram->cong[port].dung_khan_cap && tram->cong[port].ma_loi == LOI_DUNG_KHAN_CAP && tick == 8) {
                chi_so->emergency_stop++;
                chi_so->so_su_kien_an_toan++;
                chi_so->so_lan_can_thiep_an_toan++;
                ghi_su_kien_an_toan(tick, ds_xe[i].ma_xe, port + 1,
                                    "EMERGENCY_STOP", MUC_CRITICAL,
                                    "EMERGENCY_SHUTDOWN");
                them_su_kien(tick, "SAFETY", "CRITICAL", ds_xe[i].ma_xe,
                             "EMERGENCY_STOP", "Emergency stop activated, charging power cut");
                luu_su_kien_an_toan_db(tick, ds_xe[i].ma_xe, port + 1, "EMERGENCY_STOP", "CRITICAL", "Emergency stop triggered by vehicle");
                if (ds_phien[port].id > 0 && ds_phien[port].dang_hoat_dong) {
                    ket_thuc_phien_sac(&ds_phien[port], ds_xe[i].pin.soc, ds_xe[i].pin.nang_luong_da_nhan);
                    ket_thuc_phien_sac_db(&ds_phien[port]);
                }
            }
        }

        /* 2. Kiem tra an toan toan bo tram */
        int su_co = kiem_tra_toan_bo_tram(tram, ds_xe, so_xe);
        if (su_co > 0) {
            for (int i = 0; i < so_xe; i++) {
            int port = ds_xe[i].assigned_port - 1;
            if (port < 0 || port >= SO_CONG_SAC || tram->cong[port].vehicle_id != ds_xe[i].id) continue;
                if (tram->cong[port].trang_thai == CONG_LOI && tram->cong[port].ma_loi == LOI_PIN_QUA_NHIET) {
                    int overheat_trip_moi = !da_co_su_kien(ds_xe[i].ma_xe, "OVERHEAT_TRIP");
                    if (overheat_trip_moi) {
                        chi_so->qua_nhiet++;
                        chi_so->so_su_kien_an_toan++;
                        chi_so->so_lan_can_thiep_an_toan++;
                        ghi_su_kien_an_toan(tick, ds_xe[i].ma_xe, port + 1,
                                            "OVERHEAT", MUC_CRITICAL,
                                            "POWER_CUT");
                        them_su_kien(tick, "SAFETY", "CRITICAL", ds_xe[i].ma_xe,
                                     "OVERHEAT_TRIP", "Overheat detected, charging power cut");
                    }
                    if (overheat_trip_moi) {
                        luu_su_kien_an_toan_db(tick, ds_xe[i].ma_xe, port + 1, "OVERHEAT", "CRITICAL", "Battery temperature exceeded 60C limit");
                        if (ds_phien[port].id > 0 && ds_phien[port].dang_hoat_dong) {
                            ket_thuc_phien_sac(&ds_phien[port], ds_xe[i].pin.soc, ds_xe[i].pin.nang_luong_da_nhan);
                            ket_thuc_phien_sac_db(&ds_phien[port]);
                        }
                    }
                }
            }
        }

        /* 3. Dieu phoi & quan ly cong suat */
        phan_phoi_cong_suat_theo_soc(tram, ds_xe, so_xe);

        /* 4. Cap nhat trang thai pin cua cac xe dang sac */
        float delta_t = 0.05f;
        for (int i = 0; i < so_xe; i++) {
            int port = ds_xe[i].assigned_port - 1;
            if (port < 0 || port >= SO_CONG_SAC || tram->cong[port].vehicle_id != ds_xe[i].id) continue;
            if (tram->cong[port].trang_thai == CONG_DANG_SAC && tram->cong[port].cong_suat_kw > 0.0f) {
                cap_nhat_pin(&ds_xe[i].pin, tram->cong[port].cong_suat_kw, delta_t);

                /* Kiem tra pin day */
                if (ds_xe[i].pin.soc >= SOC_MAX) {
                    chi_so->dung_do_pin_day++;
                    chi_so->so_su_kien_an_toan++;
                    chi_so->so_lan_can_thiep_an_toan++;
                    ds_xe[i].pin.soc = SOC_MAX;
                    tram->cong[port].cong_suat_kw = 0.0f;
                    tram->cong[port].trang_thai = CONG_DUNG;
                    ds_xe[i].trang_thai = XE_DA_DAY;
                    ghi_log(LOG_SAFETY, "TICK %d: %s da day pin 100%%! Cong %d tu dong ngat dien.",
                            tick, ds_xe[i].ma_xe, port + 1);
                    ghi_su_kien_an_toan(tick, ds_xe[i].ma_xe, port + 1,
                                        "BATTERY_FULL", MUC_INFO, "CHARGING_STOPPED");
                    them_su_kien(tick, "SAFETY", "INFO", ds_xe[i].ma_xe,
                                 "BATTERY_FULL", "Battery full, charging stopped");
                    them_su_kien(tick, "CHARGING", "INFO", ds_xe[i].ma_xe,
                                 "CHARGING_STOPPED", "Charging stopped at target SOC");
                    luu_su_kien_an_toan_db(tick, ds_xe[i].ma_xe, port + 1, "BATTERY_FULL", "INFO", "Battery reached 100 percent SOC");
                    if (ds_phien[port].id > 0 && ds_phien[port].dang_hoat_dong) {
                        ket_thuc_phien_sac(&ds_phien[port], ds_xe[i].pin.soc, ds_xe[i].pin.nang_luong_da_nhan);
                        ket_thuc_phien_sac_db(&ds_phien[port]);
                    }
                }
            }

            /* Ghi telemetry cho moi xe tai tick nay */
            int session_to_log = (ds_phien[port].id > 0) ? ds_phien[port].id : 0;
            luu_telemetry(session_to_log, tick, ds_xe[i].ma_xe, port + 1, ds_xe[i].pin.soc,
                          ds_xe[i].pin.nhiet_do, tram->cong[port].cong_suat_kw,
                          ten_trang_thai_cong(tram->cong[port].trang_thai));

            /* Cap nhat DB cho cong sac va xe */
            cap_nhat_cong_sac_db(tram->id, &tram->cong[port]);
            cap_nhat_trang_thai_xe_db(&ds_xe[i]);
        }

        cap_nhat_tong_cong_suat_tram(tram);
        ghi_nhan_cong_suat(chi_so, tram->cong_suat_hien_tai);
        chi_so->tong_nang_luong_kwh += tram->cong_suat_hien_tai * (1.0f / 60.0f);

        /* 5. In dashboard */
        in_dashboard_tick(tick, tram, ds_xe, so_xe);
        ghi_snapshot_json_voi_trang_thai(
            "logs/telemetry/latest_state.json", tick,
            dieu_khien && dieu_khien->trang_thai == MO_PHONG_DANG_CHAY ? "RUNNING" : "PAUSED",
            tram, ds_xe, so_xe, queue, kich_ban);
}

void chay_mo_phong(TramSac *tram,
                   XeDien ds_xe[],
                   int so_xe,
                   int tong_so_tick,
                   int is_fixed_demo,
                   unsigned int seed) {
    if (!tram || !ds_xe || so_xe <= 0) return;

    const char *scenario_env = getenv("SMART_EV_SCENARIO");
    int interactive = is_fixed_demo && (!scenario_env || strcmp(scenario_env, "GOLDEN_OVERHEAT") != 0);
    if (interactive) {
        for (int i = 0; i < so_xe; i++) ds_xe[i].kich_ban = KB_BINH_THUONG;
    }
    FILE *command_file = fopen("logs/control/command.json", "w");
    if (command_file) {
        fputs("{\"command\":\"NONE\"}\n", command_file);
        fclose(command_file);
    }
    ChiSoHeThong chi_so;
    khoi_tao_chi_so(&chi_so, seed);
    khoi_tao_su_kien_he_thong();
    PhienSac ds_phien[SO_CONG_SAC] = {0};
    HangChoSac queue;
    khoi_tao_hang_cho(&queue);
    KichBanMoPhong kich_ban;
    khoi_tao_kich_ban(&kich_ban);
    int tick = 0;
    DieuKhienMoPhong dieu_khien = {
        .trang_thai = MO_PHONG_TAM_DUNG,
        .tick_hien_tai = 0,
        .yeu_cau_next_tick = 0
    };

    ghi_log(LOG_INFO, "=== BAT DAU PHIEN MO PHONG (Tong tick: %d) ===", tong_so_tick);
    luu_tram_sac(tram);
    for (int i = 0; i < so_xe; i++) {
        luu_xe_dien(&ds_xe[i]);
    }

    for (int i = 0; i < so_xe; i++) {
        if (interactive) continue;

        int assigned_port = gan_cong_sac_tu_dong(tram, &ds_xe[i]);
        if (assigned_port < 0) continue;

        ket_noi_xe_vao_tram(tram, assigned_port, &ds_xe[i]);
        them_su_kien(0, "SYSTEM", "INFO", ds_xe[i].ma_xe,
                     "VEHICLE_CONNECTED", "Vehicle connected to charging station");
        char token[DO_DAI_TOKEN];
        ds_phien[assigned_port].id = 0;

        if (ds_xe[i].kich_ban == KB_LOI_XAC_THUC) {
            snprintf(token, sizeof(token), "INVALID_TOKEN");
        } else {
            sinh_token_xe(ds_xe[i].ma_xe, token, sizeof(token));
        }

        if (xac_thuc_xe(&ds_xe[i], token)) {
            tram->cong[assigned_port].trang_thai = CONG_SAN_SANG;
            ds_xe[i].trang_thai = XE_SAN_SANG;
            ghi_log(LOG_INFO, "%s xac thuc thanh cong tai Cong %d", ds_xe[i].ma_xe, assigned_port + 1);
            them_su_kien(0, "AUTH", "INFO", ds_xe[i].ma_xe,
                         "AUTH_SUCCESS", "Vehicle authentication succeeded");
        } else {
            chi_so.loi_xac_thuc++;
            chi_so.so_su_kien_an_toan++;
            ghi_log(LOG_WARNING, "%s xac thuc that bai tai Cong %d!", ds_xe[i].ma_xe, i + 1);
            ghi_su_kien_an_toan(0, ds_xe[i].ma_xe, assigned_port + 1,
                                "AUTH_FAILURE", MUC_WARNING, "ACCESS_DENIED");
            them_su_kien(0, "AUTH", "WARNING", ds_xe[i].ma_xe,
                         "AUTH_FAILURE", "Vehicle authentication failed");
            luu_su_kien_an_toan_db(1, ds_xe[i].ma_xe, assigned_port + 1,
                                   "AUTH_FAILED", "WARNING", "Token verification failed");
        }
    }

    for (int i = 0; i < so_xe; i++) {
        int assigned_port = ds_xe[i].assigned_port - 1;
        if (assigned_port < 0 || assigned_port >= SO_CONG_SAC) continue;

        if (ds_xe[i].da_xac_thuc
            && bat_dau_sac(&ds_xe[i], &tram->cong[assigned_port], &ds_phien[assigned_port], ds_xe[i].cong_suat_sac_toi_da)) {
            chi_so.so_lan_bat_dau_sac++;
            ghi_log(LOG_INFO, "%s bat dau sac tai Cong %d (%.1f kW)",
                    ds_xe[i].ma_xe, assigned_port + 1, tram->cong[assigned_port].cong_suat_kw);
                them_su_kien(0, "CHARGING", "INFO", ds_xe[i].ma_xe,
                     "CHARGING_STARTED", "Charging started");
            tao_phien_sac_db(&ds_phien[assigned_port]);
        }
    }

    phan_phoi_cong_suat_theo_soc(tram, ds_xe, so_xe);
    ghi_snapshot_json_voi_trang_thai(
        "logs/telemetry/latest_state.json", tick, "PAUSED", tram, ds_xe, so_xe, &queue, &kich_ban);

    int elapsed_ms = 0;
    while (1) {
        xu_ly_lenh_dieu_khien("logs/control/command.json", tram, ds_xe, so_xe,
                              &tick, &dieu_khien, &kich_ban);
        if (tick == 0 && queue.count > 0) {
            khoi_tao_hang_cho(&queue);
        }
        dieu_khien.tick_hien_tai = tick;


        ghi_snapshot_json_voi_trang_thai(
            "logs/telemetry/latest_state.json", tick,
            dieu_khien.trang_thai == MO_PHONG_DANG_CHAY ? "RUNNING" : "PAUSED",
            tram, ds_xe, so_xe, &queue, &kich_ban);

        int interval_ms = dieu_khien.tick_interval_ms > 0 ? dieu_khien.tick_interval_ms : 1000;
        if (dieu_khien.trang_thai == MO_PHONG_TAM_DUNG) elapsed_ms = 0;
        if ((dieu_khien.trang_thai == MO_PHONG_DANG_CHAY && elapsed_ms >= interval_ms)
            || dieu_khien.yeu_cau_next_tick) {
            elapsed_ms = 0;
            thuc_hien_mot_tick(&tick, tram, ds_xe, so_xe, ds_phien, &chi_so, &dieu_khien, &queue, &kich_ban);
            dieu_khien.yeu_cau_next_tick = 0;
            dieu_khien.tick_hien_tai = tick;
        }

#ifdef _WIN32
    Sleep(50);
#else
    struct timespec ts = {
        .tv_sec = 0,
        .tv_nsec = 50000000
    };
    nanosleep(&ts, NULL);
#endif
        elapsed_ms += 50;
    }

    ghi_log(LOG_INFO, "=== PHIEN MO PHONG KET THUC ===");
    in_tong_ket_nhat_ky();
    in_tong_ket_mo_phong(&chi_so);
}
