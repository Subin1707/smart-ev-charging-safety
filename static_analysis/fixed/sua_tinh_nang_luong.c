#include <stdio.h>
#include <limits.h>
#include <stdint.h>

/* FIX: Su dung 64-bit int va saturated arithmetic de ngan tran so */
int64_t tinh_micro_watt_an_toan(int cong_suat_kw) {
    if (cong_suat_kw < 0) return 0;

    int64_t p_kw_64 = (int64_t)cong_suat_kw;
    int64_t he_so = 1000000000LL;

    /* Kiem tra tran so truoc khi thuc hien phep nhan */
    if (p_kw_64 > INT64_MAX / he_so) {
        printf("[SECURITY] Phat hien nguy co tran so! Tra ve INT64_MAX.\n");
        return INT64_MAX;
    }

    return p_kw_64 * he_so;
}

int main(void) {
    int p_kw = 3; /* 3 kW */
    printf("[FIXED] Tinh toan micro-Watt an toan cho cong suat %d kW...\n", p_kw);
    int64_t micro_watt = tinh_micro_watt_an_toan(p_kw);
    printf("[FIXED] Ket qua chinh xac: %lld micro-Watt (KHONG CON TRAN SO)\n", (long long)micro_watt);

    return 0;
}
