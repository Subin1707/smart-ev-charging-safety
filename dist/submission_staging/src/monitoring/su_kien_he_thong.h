#ifndef SU_KIEN_HE_THONG_H
#define SU_KIEN_HE_THONG_H

#define SO_SU_KIEN_HE_THONG_TOI_DA 100
#define DO_DAI_LOAI_SU_KIEN 32
#define DO_DAI_MUC_DO_SU_KIEN 16
#define DO_DAI_MA_SU_KIEN 64
#define DO_DAI_THONG_DIEP_SU_KIEN 160

typedef struct {
    int tick;
    char type[DO_DAI_LOAI_SU_KIEN];
    char severity[DO_DAI_MUC_DO_SU_KIEN];
    char vehicle_id[16];
    char code[DO_DAI_MA_SU_KIEN];
    char message[DO_DAI_THONG_DIEP_SU_KIEN];
} SuKienHeThong;

void khoi_tao_su_kien_he_thong(void);
void them_su_kien(int tick,
                  const char *type,
                  const char *severity,
                  const char *vehicle_id,
                  const char *code,
                  const char *message);
int lay_su_kien_he_thong(const SuKienHeThong **su_kien);
int da_co_su_kien(const char *vehicle_id, const char *code);

#endif /* SU_KIEN_HE_THONG_H */
