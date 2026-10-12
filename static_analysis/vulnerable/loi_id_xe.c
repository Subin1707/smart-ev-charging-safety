#include <stdio.h>
#include <string.h>

/* VULN-01: Vehicle ID buffer overflow
   char ma_xe[20] bi tran khi sao chep chuoi dai bang strcpy */
typedef struct {
    char ma_xe[20];
    int vehicle_id;
    int is_authorized;
} HoSoXeLoi;

void cap_nhat_id_xe_nguy_hiem(HoSoXeLoi *xe, const char *input_id) {
    /* NGUY HIEM: strcpy khong kiem tra do dai dau vao -> Tran dem stack */
    strcpy(xe->ma_xe, input_id);
}

int main(int argc, char *argv[]) {
    HoSoXeLoi xe;
    xe.vehicle_id = 1;
    xe.is_authorized = 0;

    const char *chuoi_dau_vao = "EVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
    if (argc > 1) {
        chuoi_dau_vao = argv[1];
    }

    printf("[VULNERABLE] Dang nap ID xe: %s\n", chuoi_dau_vao);
    cap_nhat_id_xe_nguy_hiem(&xe, chuoi_dau_vao);
    printf("[VULNERABLE] ID xe sau khi nap: %s (Authorized: %d)\n", xe.ma_xe, xe.is_authorized);

    return 0;
}
