#ifndef DU_LIEU_GIAM_SAT_H
#define DU_LIEU_GIAM_SAT_H

#include <stdio.h>
#include "tram_sac.h"
#include "hang_cho.h"
#include "kich_ban.h"

void xuat_snapshot_json(FILE *output,
						int tick,
						const TramSac *tram,
						const XeDien ds_xe[],
						int so_xe,
						const HangChoSac *queue,
						const KichBanMoPhong *kich_ban);

int ghi_snapshot_json(const char *duong_dan,
					  int tick,
					  const TramSac *tram,
					  const XeDien ds_xe[],
					  int so_xe,
					  const HangChoSac *queue,
					  const KichBanMoPhong *kich_ban);

int ghi_snapshot_json_voi_trang_thai(const char *duong_dan,
								  int tick,
								  const char *trang_thai_mo_phong,
								  const TramSac *tram,
								  const XeDien ds_xe[],
								  int so_xe,
								  const HangChoSac *queue,
								  const KichBanMoPhong *kich_ban);

#endif /* DU_LIEU_GIAM_SAT_H */
