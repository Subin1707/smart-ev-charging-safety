#include <stdio.h>
#include "quy_tac_an_toan.h"
#include "hang_so.h"

/* SR01: Äang sáº¡c -> Báº¯t buá»™c pháº£i káº¿t ná»‘i */
int kiem_tra_sr01_ket_noi(const XeDien *xe, const CongSac *cong) {
    if (!xe || !cong) return 0;
    if (cong->trang_thai == CONG_DANG_SAC && (!xe->da_ket_noi || cong->vehicle_id != xe->id)) {
        return 0;
    }
    return 1;
}

/* SR02: Äang sáº¡c -> Báº¯t buá»™c Ä‘Ă£ xĂ¡c thá»±c */
int kiem_tra_sr02_xac_thuc(const XeDien *xe) {
    if (!xe) return 0;
    if (xe->trang_thai == XE_DANG_SAC && !xe->da_xac_thuc) {
        return 0;
    }
    return 1;
}

/* SR03: Nhiá»‡t Ä‘á»™ >= 60 C -> Báº¯t buá»™c ngáº¯t sáº¡c (Power = 0) */
int kiem_tra_sr03_nhiet_do(const XeDien *xe) {
    if (!xe) return 0;
    if (xe->pin.nhiet_do >= NHIET_DO_TOI_DA) {
        return 0; /* Vi pháº¡m an toĂ n quĂ¡ nhiá»‡t */
    }
    return 1;
}

/* SR04: SOC >= 100% -> Ngáº¯t sáº¡c */
int kiem_tra_sr04_pin_day(const XeDien *xe) {
    if (!xe) return 0;
    if (xe->pin.soc >= SOC_MAX) {
        return 0; /* Pin Ä‘Ă£ Ä‘áº§y, khĂ´ng sáº¡c tiáº¿p */
    }
    return 1;
}

/* SR05: Emergency -> CĂ´ng suáº¥t = 0 */
int kiem_tra_sr05_khan_cap(const CongSac *cong, const TramSac *tram) {
    if (tram && tram->emergency) {
        if (cong && cong->cong_suat_kw > 0.0f) return 0;
    }
    if (cong && cong->dung_khan_cap) {
        if (cong->cong_suat_kw > 0.0f) return 0;
    }
    return 1;
}

/* SR06: SOC thuá»™c Ä‘oáº¡n [0, 100] */
int kiem_tra_sr06_soc_hop_le(const XeDien *xe) {
    if (!xe) return 0;
    return (xe->pin.soc >= SOC_MIN && xe->pin.soc <= SOC_MAX);
}

/* SR07: Má»—i cá»•ng chá»‰ cĂ³ tá»‘i Ä‘a 1 xe */
int kiem_tra_sr07_doc_quyen_cong(const CongSac *cong, int vehicle_id) {
    if (!cong) return 0;
    if (cong->vehicle_id != -1 && cong->vehicle_id != vehicle_id) {
        return 0; /* Cá»•ng Ä‘Ă£ bá»‹ xe khĂ¡c chiáº¿m giá»¯ */
    }
    return 1;
}

/* SR08: Cá»•ng cĂ³ lá»—i -> CĂ´ng suáº¥t = 0 */
int kiem_tra_sr08_ma_loi(const CongSac *cong) {
    if (!cong) return 0;
    if (cong->trang_thai == CONG_LOI && cong->cong_suat_kw > 0.0f) {
        return 0;
    }
    return 1;
}

/* SR09: Xe ngáº¯t káº¿t ná»‘i -> Ngáº¯t sáº¡c láº­p tá»©c */
int kiem_tra_sr09_ngat_ket_noi(const XeDien *xe, const CongSac *cong) {
    if (!xe || !cong) return 0;
    if (!xe->da_ket_noi && cong->cong_suat_kw > 0.0f) {
        return 0;
    }
    return 1;
}

/* SR10: Tá»•ng cĂ´ng suáº¥t <= CĂ´ng suáº¥t tá»‘i Ä‘a cá»§a tráº¡m */
int kiem_tra_sr10_gioi_han_cong_suat_tram(float tong_cong_suat, float max_cong_suat) {
    return (tong_cong_suat <= max_cong_suat + 0.001f);
}
