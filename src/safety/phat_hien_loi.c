#include "phat_hien_loi.h"

const char* ten_ma_loi(MaLoiHeThong ma_loi) {
    switch (ma_loi) {
        case LOI_KHONG_CO:          return "NO_ERROR";
        case LOI_CHUA_KET_NOI:      return "ERR_NOT_CONNECTED";
        case LOI_CHUA_XAC_THUC:     return "ERR_UNAUTHENTICATED";
        case LOI_PIN_QUA_NHIET:     return "ERR_BATTERY_OVERHEAT";
        case LOI_PIN_DA_DAY:        return "ERR_BATTERY_FULL";
        case LOI_DUNG_KHAN_CAP:     return "ERR_EMERGENCY_STOP";
        case LOI_SOC_KHONG_HOP_LE:  return "ERR_INVALID_SOC";
        case LOI_CONG_DA_CO_XE:     return "ERR_PORT_OCCUPIED";
        case LOI_QUA_TAI_CONG_SUAT: return "ERR_POWER_OVERLOAD";
        default:                    return "ERR_UNKNOWN";
    }
}
