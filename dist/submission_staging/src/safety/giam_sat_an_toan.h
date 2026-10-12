#ifndef GIAM_SAT_AN_TOAN_H
#define GIAM_SAT_AN_TOAN_H

#include "xe_dien.h"
#include "cong_sac.h"
#include "tram_sac.h"
#include "phat_hien_loi.h"

typedef struct {
    int an_toan;
    MaLoiHeThong ma_loi;
    const char *mo_ta;
} KetQuaGiamSat;

KetQuaGiamSat giam_sat_xe_va_cong(XeDien *xe, CongSac *cong, TramSac *tram);
int kiem_tra_toan_bo_tram(TramSac *tram, XeDien ds_xe[], int so_xe);

#endif /* GIAM_SAT_AN_TOAN_H */
