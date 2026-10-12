#include <stdio.h>
#include <stdarg.h>
#include <time.h>
#include <string.h>
#include "logger.h"

static FILE *g_log_file = NULL;

static const char* ten_muc_log(MucLog muc) {
    switch (muc) {
        case LOG_INFO:     return "INFO";
        case LOG_WARNING:  return "WARNING";
        case LOG_ERROR:    return "ERROR";
        case LOG_CRITICAL: return "CRITICAL";
        case LOG_SAFETY:   return "SAFETY";
        default:           return "LOG";
    }
}

int khoi_tao_logger(const char *duong_dan_file) {
    if (g_log_file) {
        fclose(g_log_file);
        g_log_file = NULL;
    }

    if (duong_dan_file) {
        g_log_file = fopen(duong_dan_file, "w");
        if (!g_log_file) {
            printf("[LOGGER] Khong the mo file log: %s\n", duong_dan_file);
            return 0;
        }
    }
    return 1;
}

void dong_logger(void) {
    if (g_log_file) {
        fclose(g_log_file);
        g_log_file = NULL;
    }
}

void ghi_log(MucLog muc, const char *dinh_dang, ...) {
    char thoi_gian_str[32];
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    if (tm_info) {
        strftime(thoi_gian_str, sizeof(thoi_gian_str), "%H:%M:%S", tm_info);
    } else {
        strcpy(thoi_gian_str, "00:00:00");
    }

    va_list args;

    /* In ra man hinh console */
    printf("[%s][%s] ", thoi_gian_str, ten_muc_log(muc));
    va_start(args, dinh_dang);
    vprintf(dinh_dang, args);
    va_end(args);
    printf("\n");

    /* Ghi vao tep log neu da mo */
    if (g_log_file) {
        fprintf(g_log_file, "[%s][%s] ", thoi_gian_str, ten_muc_log(muc));
        va_start(args, dinh_dang);
        vfprintf(g_log_file, dinh_dang, args);
        va_end(args);
        fprintf(g_log_file, "\n");
        fflush(g_log_file);
    }
}
