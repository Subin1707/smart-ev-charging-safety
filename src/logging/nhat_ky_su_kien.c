#include <stdio.h>
#include <string.h>
#include "nhat_ky_su_kien.h"

#define MAX_SU_KIEN SO_SU_KIEN_TOI_DA

static SuKeAnToanLog g_ds_su_kien[MAX_SU_KIEN];
static int g_so_luong_su_kien = 0;

static const char *ten_muc_do(MucDoSuKien muc_do) {
    switch (muc_do) {
        case MUC_INFO: return "INFO";
        case MUC_WARNING: return "WARNING";
        case MUC_CRITICAL: return "CRITICAL";
        default: return "UNKNOWN";
    }
}

static MucDoSuKien muc_do_tu_chuoi(const char *muc_do) {
    if (muc_do && strcmp(muc_do, "CRITICAL") == 0) return MUC_CRITICAL;
    if (muc_do && strcmp(muc_do, "WARNING") == 0) return MUC_WARNING;
    return MUC_INFO;
}

void khoi_tao_nhat_ky(void) {
    g_so_luong_su_kien = 0;
}

void ghi_su_kien_an_toan(int tick,
                         const char *ma_xe,
                         int port_id,
                         const char *loai_su_kien,
                         MucDoSuKien muc_do,
                         const char *hanh_dong) {
    if (g_so_luong_su_kien >= MAX_SU_KIEN) return;

    SuKeAnToanLog *item = &g_ds_su_kien[g_so_luong_su_kien];
    item->id = g_so_luong_su_kien + 1;
    item->tick = tick;
    item->port_id = port_id;
    item->muc_do = muc_do;
    snprintf(item->ma_xe, sizeof(item->ma_xe), "%s", ma_xe ? ma_xe : "--");
    snprintf(item->su_kien, sizeof(item->su_kien), "%s",
             loai_su_kien ? loai_su_kien : "UNKNOWN");
    snprintf(item->hanh_dong, sizeof(item->hanh_dong), "%s",
             hanh_dong ? hanh_dong : "--");
    g_so_luong_su_kien++;
}

void them_su_kien_nhat_ky(int tick, const char *ma_xe, int port_id, const char *su_kien, const char *muc_do) {
    ghi_su_kien_an_toan(tick, ma_xe, port_id, su_kien,
                        muc_do_tu_chuoi(muc_do), "SAFETY_ACTION");
}

int lay_tong_so_su_kien(void) {
    return g_so_luong_su_kien;
}

void in_lich_su_su_kien_an_toan(void) {
    int critical = 0;
    int warning = 0;
    int info = 0;

    printf("\n=======================================================================\n");
    printf("                     SAFETY EVENT HISTORY\n");
    printf("=======================================================================\n");
    if (g_so_luong_su_kien == 0) {
        printf("Chua co su kien an toan nao duoc ghi nhan.\n");
        printf("=======================================================================\n");
        return;
    }

    printf("%-4s %-6s %-9s %-20s %-10s %-22s\n",
           "ID", "TICK", "VEHICLE", "EVENT", "LEVEL", "ACTION");
    printf("-----------------------------------------------------------------------\n");
    for (int i = 0; i < g_so_luong_su_kien; i++) {
        const SuKeAnToanLog *item = &g_ds_su_kien[i];
        printf("%-4d %-6d %-9s %-20s %-10s %-22s\n",
               item->id, item->tick, item->ma_xe, item->su_kien,
               ten_muc_do(item->muc_do), item->hanh_dong);
        if (item->muc_do == MUC_CRITICAL) critical++;
        else if (item->muc_do == MUC_WARNING) warning++;
        else info++;
    }
    printf("-----------------------------------------------------------------------\n");
    printf("Total events : %d\n", g_so_luong_su_kien);
    printf("Critical     : %d\n", critical);
    printf("Warning      : %d\n", warning);
    printf("Info         : %d\n", info);
    printf("=======================================================================\n");
}

void in_tong_ket_nhat_ky(void) {
    printf("\n====================================================================\n");
    printf("                  TONG HOP NHAT KY SU KIEN AN TOAN                 \n");
    printf("====================================================================\n");
    printf("%-6s %-8s %-6s %-25s %-12s\n", "TICK", "XE", "CONG", "SU KIEN", "MUC DO");
    printf("--------------------------------------------------------------------\n");
    for (int i = 0; i < g_so_luong_su_kien; i++) {
        const SuKeAnToanLog *item = &g_ds_su_kien[i];
        printf("%-6d %-8s %-6d %-25s %-12s\n",
               item->tick, item->ma_xe, item->port_id, item->su_kien,
               ten_muc_do(item->muc_do));
    }
    printf("--------------------------------------------------------------------\n");
    printf("Tong so su kien an toan da ghi nhan: %d\n", g_so_luong_su_kien);
    printf("====================================================================\n\n");
}
