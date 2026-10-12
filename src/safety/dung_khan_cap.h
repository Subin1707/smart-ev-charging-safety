#ifndef DUNG_KHAN_CAP_H
#define DUNG_KHAN_CAP_H

#include "cong_sac.h"
#include "tram_sac.h"
#include "xe_dien.h"

int kich_hoat_dung_khan_cap_cong(CongSac *cong, XeDien *xe);
int kich_hoat_dung_khan_cap_tram(TramSac *tram, XeDien ds_xe[], int so_xe);
int khoi_phuc_khan_cap_tram(TramSac *tram);

#endif /* DUNG_KHAN_CAP_H */
