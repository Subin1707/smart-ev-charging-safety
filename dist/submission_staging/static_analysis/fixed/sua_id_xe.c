#include <stdio.h>
#include <string.h>

typedef struct {
    char ma_xe[20];
    int vehicle_id;
    int is_authorized;
} HoSoXeAnToan;

int cap_nhat_id_xe_an_toan(HoSoXeAnToan *xe, const char *input_id) {
    if (!xe || !input_id) return 0;

    /* KIEM TRA VA FIX: Su dung snprintf voi gioi han sizeof(xe->ma_xe) */
    if (strlen(input_id) >= sizeof(xe->ma_xe)) {
        printf("[FIXED][SECURITY] Canh bao: Input vuot qua kich thuoc dem (len=%zu >= %zu). Tu dong cat ngan an toan!\n",
               strlen(input_id), sizeof(xe->ma_xe));
    }

    snprintf(xe->ma_xe, sizeof(xe->ma_xe), "%s", input_id);
    return 1;
}

int main(int argc, char *argv[]) {
    HoSoXeAnToan xe;
    xe.vehicle_id = 1;
    xe.is_authorized = 0;

    const char *chuoi_dau_vao = "EVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
    if (argc > 1) {
        chuoi_dau_vao = argv[1];
    }

    printf("[FIXED] Dang nap ID xe an toan: %s\n", chuoi_dau_vao);
    cap_nhat_id_xe_an_toan(&xe, chuoi_dau_vao);
    printf("[FIXED] ID xe duoc luu an toan: '%s' (Authorized: %d)\n", xe.ma_xe, xe.is_authorized);

    return 0;
}
