#include "che_do_sac.h"

const char* ten_che_do_sac(CheDoSac cd) {
    switch (cd) {
        case SAC_TIEU_CHUAN: return "STANDARD";
        case SAC_NHANH:      return "FAST";
        case SAC_TIET_KIEM:  return "ECO";
        default:             return "UNKNOWN";
    }
}
