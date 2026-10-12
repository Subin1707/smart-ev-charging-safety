#ifndef KIEU_DU_LIEU_H
#define KIEU_DU_LIEU_H

/* Tráº¡ng thĂ¡i xe Ä‘iá»‡n */
typedef enum {
    XE_CHO,
    XE_DA_KET_NOI,
    XE_DA_XAC_THUC,
    XE_SAN_SANG,
    XE_DANG_SAC,
    XE_DA_DAY,
    XE_DUNG_SAC,
    XE_DA_NGAT_KET_NOI,
    XE_LOI
} TrangThaiXe;

/* Tráº¡ng thĂ¡i cá»•ng sáº¡c */
typedef enum {
    CONG_RANH,
    CONG_DA_DAT,
    CONG_DA_KET_NOI,
    CONG_SAN_SANG,
    CONG_DANG_SAC,
    CONG_DUNG,
    CONG_LOI
} TrangThaiCong;

/* Loáº¡i ká»‹ch báº£n mĂ´ phá»ng */
typedef enum {
    KB_BINH_THUONG,
    KB_PIN_THAP,
    KB_PIN_DAY,
    KB_QUA_NHIET,
    KB_LOI_XAC_THUC,
    KB_DUNG_KHAN_CAP,
    KB_MAT_KET_NOI,
    KB_SOC_KHONG_HOP_LE,
    KB_QUA_TAI_CONG_SUAT
} LoaiKichBan;

/* Má»©c Ä‘á»™ sá»± cá»‘ an toĂ n */
typedef enum {
    MUC_THONG_TIN,
    MUC_CANH_BAO,
    MUC_NGHIEM_TRONG,
    MUC_KHAN_CAP
} MucDoSuCo;

#endif /* KIEU_DU_LIEU_H */
