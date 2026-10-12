#ifndef MO_PHONG_H
#define MO_PHONG_H

#include "tram_sac.h"
#include "xe_dien.h"
#include "phien_sac.h"
#include "chi_so.h"
#include "dieu_khien_tu_xa.h"
#include "hang_cho.h"
#include "kich_ban.h"

void in_dashboard_tick(int tick, const TramSac *tram, const XeDien ds_xe[], int so_xe);
void thuc_hien_mot_tick(int *tick_hien_tai,
						TramSac *tram,
						XeDien ds_xe[],
						int so_xe,
						PhienSac ds_phien[],
						ChiSoHeThong *chi_so,
						const DieuKhienMoPhong *dieu_khien,
						HangChoSac *queue,
						KichBanMoPhong *kich_ban);
void chay_mo_phong(TramSac *tram,
				   XeDien ds_xe[],
				   int so_xe,
				   int tong_so_tick,
				   int is_fixed_demo,
				   unsigned int seed);

#endif /* MO_PHONG_H */
