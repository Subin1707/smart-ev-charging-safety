#ifndef PHIEN_SAC_H
#define PHIEN_SAC_H

typedef struct {
    int id;
    int vehicle_id;
    int port_id;

    float soc_bat_dau;
    float soc_ket_thuc;

    float nang_luong_kwh;
    int dang_hoat_dong;
} PhienSac;

void khoi_tao_phien_sac(PhienSac *phien, int id, int vehicle_id, int port_id, float soc_bat_dau);
void ket_thuc_phien_sac(PhienSac *phien, float soc_ket_thuc, float nang_luong);

#endif /* PHIEN_SAC_H */
