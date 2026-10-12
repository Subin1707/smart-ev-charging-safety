#ifndef QUAN_LY_CONG_SUAT_H
#define QUAN_LY_CONG_SUAT_H

#include "tram_sac.h"
#include "xe_dien.h"

void phan_phoi_cong_suat_chia_deu(TramSac *tram);
void phan_phoi_cong_suat_theo_soc(TramSac *tram, XeDien ds_xe[], int so_xe);
void xu_ly_qua_tai_cong_suat(TramSac *tram, XeDien ds_xe[], int so_xe);
void chay_demo_qua_tai_cong_suat(TramSac *tram, XeDien ds_xe[], int so_xe);

#endif /* QUAN_LY_CONG_SUAT_H */
