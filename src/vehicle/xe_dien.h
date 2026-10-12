#ifndef XE_DIEN_H
#define XE_DIEN_H

#include "hang_so.h"
#include "kieu_du_lieu.h"
#include "pin.h"

typedef struct {
    int id;
    char ma_xe[DO_DAI_MA_XE];

    Pin pin;

    float cong_suat_sac_toi_da;

    int assigned_port;
    int da_ket_noi;
    int da_xac_thuc;

    TrangThaiXe trang_thai;
    LoaiKichBan kich_ban;
} XeDien;

void khoi_tao_xe_dien(XeDien *xe,
                      int id,
                      const char *ma_xe,
                      float dung_luong,
                      float soc,
                      float nhiet_do,
                      float cong_suat_max,
                      LoaiKichBan kich_ban);

void khoi_tao_danh_sach_5_xe(XeDien danh_sach[]);

void in_thong_tin_xe(const XeDien *xe);
void in_danh_sach_xe(const XeDien danh_sach[], int so_luong);

#endif /* XE_DIEN_H */
