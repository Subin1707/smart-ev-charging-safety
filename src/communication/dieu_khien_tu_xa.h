#ifndef DIEU_KHIEN_TU_XA_H
#define DIEU_KHIEN_TU_XA_H

#include "tram_sac.h"
#include "xe_dien.h"
#include "kich_ban.h"

typedef enum {
	MO_PHONG_TAM_DUNG,
	MO_PHONG_DANG_CHAY
} TrangThaiMoPhong;

typedef struct {
	TrangThaiMoPhong trang_thai;
	int tick_hien_tai;
	int yeu_cau_next_tick;
	int tick_interval_ms;
} DieuKhienMoPhong;

void xu_ly_lenh_dieu_khien(const char *duong_dan,
                           TramSac *tram,
                           XeDien ds_xe[],
                           int so_xe,
                           int *tick,
						   DieuKhienMoPhong *dieu_khien,
						   KichBanMoPhong *kich_ban);

#endif /* DIEU_KHIEN_TU_XA_H */