#ifndef CAU_HINH_H
#define CAU_HINH_H

typedef struct {
    int so_xe;
    int so_cong;
    int so_tick;

    float cong_suat_tram_toi_da;
    float nhiet_do_toi_da;

    unsigned int random_seed;
} CauHinhHeThong;

void khoi_tao_cau_hinh_mac_dinh(CauHinhHeThong *cfg);
void in_cau_hinh(const CauHinhHeThong *cfg);

#endif /* CAU_HINH_H */
