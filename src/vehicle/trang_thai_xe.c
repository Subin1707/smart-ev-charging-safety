#include "trang_thai_xe.h"

const char* ten_trang_thai_xe(TrangThaiXe tt) {
    switch (tt) {
        case XE_CHO:          return "WAITING";
        case XE_DA_KET_NOI:   return "CONNECTED";
        case XE_DA_XAC_THUC:  return "AUTHENTICATED";
        case XE_SAN_SANG:     return "READY";
        case XE_DANG_SAC:     return "CHARGING";
        case XE_DA_DAY:       return "FULL";
        case XE_DUNG_SAC:     return "STOPPED";
        case XE_DA_NGAT_KET_NOI: return "DISCONNECTED";
        case XE_LOI:          return "FAULT";
        default:              return "UNKNOWN";
    }
}

const char* ten_kich_ban(LoaiKichBan kb) {
    switch (kb) {
        case KB_BINH_THUONG:         return "NORMAL";
        case KB_PIN_THAP:            return "LOW_BATTERY";
        case KB_PIN_DAY:             return "BATTERY_FULL";
        case KB_QUA_NHIET:           return "OVERHEAT";
        case KB_LOI_XAC_THUC:        return "AUTH_FAILURE";
        case KB_DUNG_KHAN_CAP:       return "EMERGENCY";
        case KB_MAT_KET_NOI:         return "DISCONNECT";
        case KB_SOC_KHONG_HOP_LE:    return "INVALID_SOC";
        case KB_QUA_TAI_CONG_SUAT:   return "POWER_OVERLOAD";
        default:                     return "UNKNOWN";
    }
}
