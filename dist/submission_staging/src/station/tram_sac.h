#ifndef TRAM_SAC_H
#define TRAM_SAC_H

#include "hang_so.h"
#include "cong_sac.h"
#include "xe_dien.h"

typedef struct {
    int id;
    char ma_tram[20];

    CongSac cong[SO_CONG_SAC];

    float cong_suat_toi_da;
    float cong_suat_hien_tai;

    int emergency;
} TramSac;

void khoi_tao_tram_sac(TramSac *tram, const char *ma_tram);
int ket_noi_xe_vao_tram(TramSac *tram, int port_idx, XeDien *xe);
int ngat_ket_noi_xe_khoi_tram(TramSac *tram, int port_idx, XeDien *xe);
float cap_nhat_tong_cong_suat_tram(TramSac *tram);
void hien_thi_dashboard(const TramSac *tram, const XeDien ds_xe[], int so_xe);
void in_trang_thai_tram(const TramSac *tram, const XeDien ds_xe[], int so_xe);

#endif /* TRAM_SAC_H */
