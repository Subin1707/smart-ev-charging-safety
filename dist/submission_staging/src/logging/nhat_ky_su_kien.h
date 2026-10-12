#ifndef NHAT_KY_SU_KIEN_H
#define NHAT_KY_SU_KIEN_H

#define SO_SU_KIEN_TOI_DA 100

typedef enum {
    MUC_INFO = 0,
    MUC_WARNING,
    MUC_CRITICAL
} MucDoSuKien;

typedef struct {
    int id;
    int tick;
    char ma_xe[32];
    int port_id;
    char su_kien[64];
    char hanh_dong[64];
    MucDoSuKien muc_do;
} SuKeAnToanLog;

void khoi_tao_nhat_ky(void);
void ghi_su_kien_an_toan(int tick,
                         const char *ma_xe,
                         int port_id,
                         const char *loai_su_kien,
                         MucDoSuKien muc_do,
                         const char *hanh_dong);
void them_su_kien_nhat_ky(int tick, const char *ma_xe, int port_id, const char *su_kien, const char *muc_do);
int lay_tong_so_su_kien(void);
void in_lich_su_su_kien_an_toan(void);
void in_tong_ket_nhat_ky(void);

#endif /* NHAT_KY_SU_KIEN_H */
