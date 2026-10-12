#ifndef QUY_TAC_AN_TOAN_H
#define QUY_TAC_AN_TOAN_H

#include "xe_dien.h"
#include "cong_sac.h"
#include "tram_sac.h"

/* 10 Quy tac an toan cot loi (SR01 -> SR10) */
int kiem_tra_sr01_ket_noi(const XeDien *xe, const CongSac *cong);
int kiem_tra_sr02_xac_thuc(const XeDien *xe);
int kiem_tra_sr03_nhiet_do(const XeDien *xe);
int kiem_tra_sr04_pin_day(const XeDien *xe);
int kiem_tra_sr05_khan_cap(const CongSac *cong, const TramSac *tram);
int kiem_tra_sr06_soc_hop_le(const XeDien *xe);
int kiem_tra_sr07_doc_quyen_cong(const CongSac *cong, int vehicle_id);
int kiem_tra_sr08_ma_loi(const CongSac *cong);
int kiem_tra_sr09_ngat_ket_noi(const XeDien *xe, const CongSac *cong);
int kiem_tra_sr10_gioi_han_cong_suat_tram(float tong_cong_suat, float max_cong_suat);

#endif /* QUY_TAC_AN_TOAN_H */
