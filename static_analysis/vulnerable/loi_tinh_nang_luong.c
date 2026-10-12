#include <stdio.h>
#include <limits.h>

/* VULN-03: Integer overflow energy calculation
   Chuyen doi cong suat kW -> micro-Watt gay tran so nguyen 32-bit co dau */
int tinh_micro_watt_nguy_hiem(int cong_suat_kw) {
    /* 1 kW = 1,000,000,000 micro-Watt
       Neu cong_suat_kw >= 3 -> 3 * 1,000,000,000 = 3,000,000,000 > INT_MAX (2,147,483,647)
       Dan den so am (Signed Integer Overflow) */
    return cong_suat_kw * 1000000000;
}

int main(void) {
    int p_kw = 3; /* 3 kW */
    printf("[VULNERABLE] Tinh toan micro-Watt cho cong suat %d kW...\n", p_kw);
    int micro_watt = tinh_micro_watt_nguy_hiem(p_kw);
    printf("[VULNERABLE] Ket qua: %d micro-Watt (BI TRAN SO THANH SO AM!)\n", micro_watt);

    return 0;
}
