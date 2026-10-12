#include <stdio.h>
#include <string.h>
#include "chi_so.h"

void khoi_tao_chi_so(ChiSoHeThong *chi_so, unsigned int seed) {
	if (!chi_so) return;

	memset(chi_so, 0, sizeof(*chi_so));
	chi_so->seed = seed;
}

void ghi_nhan_cong_suat(ChiSoHeThong *chi_so, float cong_suat) {
	if (!chi_so) return;

	if (cong_suat > chi_so->cong_suat_dinh) {
		chi_so->cong_suat_dinh = cong_suat;
	}
}

void in_tong_ket_mo_phong(const ChiSoHeThong *chi_so) {
	if (!chi_so) return;

	printf("\n================================================================\n");
	printf("                     SIMULATION SUMMARY\n");
	printf("================================================================\n\n");
	printf("Seed                    : %u\n", chi_so->seed);
	printf("Simulation ticks        : %d\n", chi_so->tong_tick);
	printf("Vehicles                : 5\n\n");
	printf("---------------------------------------------------------------\n\n");
	printf("Charging started        : %d\n", chi_so->so_lan_bat_dau_sac);
	printf("Completed normally      : %d\n", chi_so->sac_hoan_thanh);
	printf("Battery full stops      : %d\n", chi_so->dung_do_pin_day);
	printf("Authentication failures : %d\n", chi_so->loi_xac_thuc);
	printf("Overheat shutdowns      : %d\n", chi_so->qua_nhiet);
	printf("Emergency stops         : %d\n", chi_so->emergency_stop);
	printf("Disconnect events       : %d\n\n", chi_so->mat_ket_noi);
	printf("---------------------------------------------------------------\n\n");
	printf("Peak station power      : %.1f kW\n", chi_so->cong_suat_dinh);
	printf("Station power limit     : 100.0 kW\n");
	printf("Energy delivered        : %.2f kWh\n\n", chi_so->tong_nang_luong_kwh);
	printf("---------------------------------------------------------------\n\n");
	printf("Safety events           : %d\n", chi_so->so_su_kien_an_toan);
	printf("Safety interventions    : %d\n", chi_so->so_lan_can_thiep_an_toan);
	printf("Unresolved faults       : %d\n\n", chi_so->loi_chua_xu_ly);
	printf("SYSTEM RESULT           : %s\n",
		   chi_so->loi_chua_xu_ly == 0 ? "SAFE" : "WARNING");
	printf("================================================================\n");
}
