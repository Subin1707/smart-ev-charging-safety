#ifndef LOGGER_H
#define LOGGER_H

typedef enum {
    LOG_INFO,
    LOG_WARNING,
    LOG_ERROR,
    LOG_CRITICAL,
    LOG_SAFETY
} MucLog;

int khoi_tao_logger(const char *duong_dan_file);
void dong_logger(void);
void ghi_log(MucLog muc, const char *dinh_dang, ...);

#endif /* LOGGER_H */
