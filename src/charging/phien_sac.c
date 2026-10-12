#include <stdio.h>
#include "phien_sac.h"

void khoi_tao_phien_sac(PhienSac *phien, int id, int vehicle_id, int port_id, float soc_bat_dau) {
    if (!phien) return;

    phien->id = id;
    phien->vehicle_id = vehicle_id;
    phien->port_id = port_id;
    phien->soc_bat_dau = soc_bat_dau;
    phien->soc_ket_thuc = soc_bat_dau;
    phien->nang_luong_kwh = 0.0f;
    phien->dang_hoat_dong = 1;
}

void ket_thuc_phien_sac(PhienSac *phien, float soc_ket_thuc, float nang_luong) {
    if (!phien) return;

    phien->soc_ket_thuc = soc_ket_thuc;
    phien->nang_luong_kwh = nang_luong;
    phien->dang_hoat_dong = 0;
}
