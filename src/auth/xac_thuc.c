#include <stdio.h>
#include "xac_thuc.h"
#include "token.h"

int xac_thuc_xe(XeDien *xe, const char *token) {
    if (!xe || !xe->da_ket_noi) return 0;

    printf("[AUTH] Dang xac thuc xe %s voi token: '%s'...\n", xe->ma_xe, token ? token : "NULL");

    if (token && kiem_tra_token_hop_le(xe->ma_xe, token)) {
        xe->da_xac_thuc = 1;
        xe->trang_thai = XE_DA_XAC_THUC;
        printf("[AUTH][SUCCESS] Xe %s xac thuc thanh cong!\n", xe->ma_xe);
        return 1;
    } else {
        xe->da_xac_thuc = 0;
        printf("[AUTH][FAILED] Xe %s xac thuc that bai! Token khong hop le.\n", xe->ma_xe);
        return 0;
    }
}
