#ifndef PIN_H
#define PIN_H

typedef struct {
    float dung_luong_kwh;
    float soc;
    float nhiet_do;
    float nang_luong_da_nhan;
} Pin;

void khoi_tao_pin(Pin *pin,
                  float dung_luong,
                  float soc,
                  float nhiet_do);

int soc_hop_le(const Pin *pin);
int pin_da_day(const Pin *pin);
int pin_qua_nhiet(const Pin *pin);

void cap_nhat_pin(Pin *pin,
                  float cong_suat_kw,
                  float thoi_gian_gio);

#endif /* PIN_H */
