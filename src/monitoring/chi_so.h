#ifndef CHI_SO_H
#define CHI_SO_H

typedef struct {
	unsigned int seed;
	int tong_tick;
	int so_lan_bat_dau_sac;
	int sac_hoan_thanh;
	int dung_do_pin_day;
	int loi_xac_thuc;
	int qua_nhiet;
	int emergency_stop;
	int mat_ket_noi;
	int so_su_kien_an_toan;
	int so_lan_can_thiep_an_toan;
	int loi_chua_xu_ly;
	float cong_suat_dinh;
	float tong_nang_luong_kwh;
} ChiSoHeThong;

void khoi_tao_chi_so(ChiSoHeThong *chi_so, unsigned int seed);
void ghi_nhan_cong_suat(ChiSoHeThong *chi_so, float cong_suat);
void in_tong_ket_mo_phong(const ChiSoHeThong *chi_so);

#endif /* CHI_SO_H */
