#ifndef PHAT_HIEN_LOI_H
#define PHAT_HIEN_LOI_H

typedef enum {
    LOI_KHONG_CO = 0,
    LOI_CHUA_KET_NOI = 101,
    LOI_CHUA_XAC_THUC = 102,
    LOI_PIN_QUA_NHIET = 103,
    LOI_PIN_DA_DAY = 104,
    LOI_DUNG_KHAN_CAP = 105,
    LOI_SOC_KHONG_HOP_LE = 106,
    LOI_CONG_DA_CO_XE = 107,
    LOI_QUA_TAI_CONG_SUAT = 108
} MaLoiHeThong;

const char* ten_ma_loi(MaLoiHeThong ma_loi);

#endif /* PHAT_HIEN_LOI_H */
