#ifndef DIEU_KHIEN_SAC_H
#define DIEU_KHIEN_SAC_H

#include "xe_dien.h"
#include "cong_sac.h"
#include "phien_sac.h"

int co_the_bat_dau_sac(const XeDien *xe, const CongSac *cong);
int bat_dau_sac(XeDien *xe, CongSac *cong, PhienSac *phien, float cong_suat_kw);
int dung_sac(XeDien *xe, CongSac *cong, PhienSac *phien);

#endif /* DIEU_KHIEN_SAC_H */
