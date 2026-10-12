#ifndef CHE_DO_SAC_H
#define CHE_DO_SAC_H

typedef enum {
    SAC_TIEU_CHUAN,
    SAC_NHANH,
    SAC_TIET_KIEM
} CheDoSac;

const char* ten_che_do_sac(CheDoSac cd);

#endif /* CHE_DO_SAC_H */
