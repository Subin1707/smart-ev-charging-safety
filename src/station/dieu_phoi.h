#ifndef DIEU_PHOI_H
#define DIEU_PHOI_H

#include "tram_sac.h"
#include "xe_dien.h"

int tim_cong_ranh(const TramSac *tram);
int tim_cong_sac_ranh(const TramSac *tram);
int gan_cong_sac_tu_dong(TramSac *tram, XeDien *xe);
void sap_xep_xe_theo_soc(const TramSac *tram,
						 const XeDien ds_xe[],
						 int so_xe,
						 int thu_tu_cong[],
						 int *so_cong);

#endif /* DIEU_PHOI_H */
