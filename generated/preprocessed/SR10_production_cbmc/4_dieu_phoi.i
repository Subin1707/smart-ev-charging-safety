# 1 "E:\\smart-ev-charging-safety\\src\\station\\dieu_phoi.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "E:\\smart-ev-charging-safety\\src\\station\\dieu_phoi.c"
# 1 "E:\\smart-ev-charging-safety\\src\\station\\dieu_phoi.h" 1



# 1 "E:\\smart-ev-charging-safety\\src\\station\\tram_sac.h" 1



# 1 "E:\\smart-ev-charging-safety\\src\\core/hang_so.h" 1
# 5 "E:\\smart-ev-charging-safety\\src\\station\\tram_sac.h" 2
# 1 "E:\\smart-ev-charging-safety\\src\\station\\cong_sac.h" 1



# 1 "E:\\smart-ev-charging-safety\\src\\core/kieu_du_lieu.h" 1




typedef enum {
    XE_CHO,
    XE_DA_KET_NOI,
    XE_DA_XAC_THUC,
    XE_SAN_SANG,
    XE_DANG_SAC,
    XE_DA_DAY,
    XE_DUNG_SAC,
    XE_DA_NGAT_KET_NOI,
    XE_LOI
} TrangThaiXe;


typedef enum {
    CONG_RANH,
    CONG_DA_DAT,
    CONG_DA_KET_NOI,
    CONG_SAN_SANG,
    CONG_DANG_SAC,
    CONG_DUNG,
    CONG_LOI
} TrangThaiCong;


typedef enum {
    KB_BINH_THUONG,
    KB_PIN_THAP,
    KB_PIN_DAY,
    KB_QUA_NHIET,
    KB_LOI_XAC_THUC,
    KB_DUNG_KHAN_CAP,
    KB_MAT_KET_NOI,
    KB_SOC_KHONG_HOP_LE,
    KB_QUA_TAI_CONG_SUAT
} LoaiKichBan;


typedef enum {
    MUC_THONG_TIN,
    MUC_CANH_BAO,
    MUC_NGHIEM_TRONG,
    MUC_KHAN_CAP
} MucDoSuCo;
# 5 "E:\\smart-ev-charging-safety\\src\\station\\cong_sac.h" 2

typedef struct {
    int id;
    int vehicle_id;

    TrangThaiCong trang_thai;

    float dien_ap;
    float dong_dien;
    float cong_suat_kw;

    int dung_khan_cap;
    int ma_loi;
} CongSac;

void khoi_tao_cong_sac(CongSac *cong, int id);
int ket_noi_xe_vao_cong(CongSac *cong, int vehicle_id);
int ngat_ket_noi_cong(CongSac *cong);
void dat_cong_suat_cong(CongSac *cong, float cong_suat_kw);
const char* ten_trang_thai_cong(TrangThaiCong tt);
# 6 "E:\\smart-ev-charging-safety\\src\\station\\tram_sac.h" 2
# 1 "E:\\smart-ev-charging-safety\\src\\vehicle/xe_dien.h" 1





# 1 "E:\\smart-ev-charging-safety\\src\\vehicle/pin.h" 1



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
# 7 "E:\\smart-ev-charging-safety\\src\\vehicle/xe_dien.h" 2

typedef struct {
    int id;
    char ma_xe[20];

    Pin pin;

    float cong_suat_sac_toi_da;

    int assigned_port;
    int da_ket_noi;
    int da_xac_thuc;

    TrangThaiXe trang_thai;
    LoaiKichBan kich_ban;
} XeDien;

void khoi_tao_xe_dien(XeDien *xe,
                      int id,
                      const char *ma_xe,
                      float dung_luong,
                      float soc,
                      float nhiet_do,
                      float cong_suat_max,
                      LoaiKichBan kich_ban);

void khoi_tao_danh_sach_5_xe(XeDien danh_sach[]);

void in_thong_tin_xe(const XeDien *xe);
void in_danh_sach_xe(const XeDien danh_sach[], int so_luong);
# 7 "E:\\smart-ev-charging-safety\\src\\station\\tram_sac.h" 2

typedef struct {
    int id;
    char ma_tram[20];

    CongSac cong[5];

    float cong_suat_toi_da;
    float cong_suat_hien_tai;

    int emergency;
} TramSac;

void khoi_tao_tram_sac(TramSac *tram, const char *ma_tram);
int ket_noi_xe_vao_tram(TramSac *tram, int port_idx, XeDien *xe);
int ngat_ket_noi_xe_khoi_tram(TramSac *tram, int port_idx, XeDien *xe);
float cap_nhat_tong_cong_suat_tram(TramSac *tram);
void hien_thi_dashboard(const TramSac *tram, const XeDien ds_xe[], int so_xe);
void in_trang_thai_tram(const TramSac *tram, const XeDien ds_xe[], int so_xe);
# 5 "E:\\smart-ev-charging-safety\\src\\station\\dieu_phoi.h" 2


int tim_cong_ranh(const TramSac *tram);
int tim_cong_sac_ranh(const TramSac *tram);
int gan_cong_sac_tu_dong(TramSac *tram, XeDien *xe);
void sap_xep_xe_theo_soc(const TramSac *tram,
       const XeDien ds_xe[],
       int so_xe,
       int thu_tu_cong[],
       int *so_cong);
# 2 "E:\\smart-ev-charging-safety\\src\\station\\dieu_phoi.c" 2
# 1 "E:\\smart-ev-charging-safety\\src\\monitoring/su_kien_he_thong.h" 1
# 10 "E:\\smart-ev-charging-safety\\src\\monitoring/su_kien_he_thong.h"
typedef struct {
    int tick;
    char type[32];
    char severity[16];
    char vehicle_id[16];
    char code[64];
    char message[160];
} SuKienHeThong;

void khoi_tao_su_kien_he_thong(void);
void them_su_kien(int tick,
                  const char *type,
                  const char *severity,
                  const char *vehicle_id,
                  const char *code,
                  const char *message);
int lay_su_kien_he_thong(const SuKienHeThong **su_kien);
int da_co_su_kien(const char *vehicle_id, const char *code);
# 3 "E:\\smart-ev-charging-safety\\src\\station\\dieu_phoi.c" 2

int tim_cong_ranh(const TramSac *tram) {
    if (!tram) return -1;

    for (int i = 0; i < 5; i++) {
        if (tram->cong[i].trang_thai == CONG_RANH && tram->cong[i].vehicle_id == -1) {
            return i;
        }
    }
    return -1;
}

int tim_cong_sac_ranh(const TramSac *tram) {
    if (!tram) return -1;

    for (int i = 0; i < 5; i++) {
        if (tram->cong[i].trang_thai == CONG_RANH
            && tram->cong[i].vehicle_id == -1) {
            return i;
        }
    }
    return -1;
}

int gan_cong_sac_tu_dong(TramSac *tram, XeDien *xe) {
    if (!tram || !xe || xe->assigned_port > 0) return -1;

    int port = tim_cong_sac_ranh(tram);
    if (port < 0) return -1;

    xe->assigned_port = port + 1;
    tram->cong[port].vehicle_id = xe->id;
    tram->cong[port].trang_thai = CONG_DA_DAT;
    them_su_kien(0, "SCHEDULER", "INFO", xe->ma_xe,
                 "PORT_ASSIGNED", "Vehicle assigned to charging port");
    return port;
}

void sap_xep_xe_theo_soc(const TramSac *tram,
                         const XeDien ds_xe[],
                         int so_xe,
                         int thu_tu_cong[],
                         int *so_cong) {
    if (!tram || !ds_xe || so_xe <= 0 || !thu_tu_cong || !so_cong) return;

    *so_cong = 0;
    for (int i = 0; i < 5; i++) {
        const CongSac *cong = &tram->cong[i];
        if (cong->trang_thai == CONG_DANG_SAC &&
            !cong->dung_khan_cap && cong->ma_loi == 0) {
            thu_tu_cong[*so_cong] = i;
            (*so_cong)++;
        }
    }

    for (int i = 0; i < *so_cong - 1; i++) {
        for (int j = i + 1; j < *so_cong; j++) {
            int cong_i = thu_tu_cong[i];
            int cong_j = thu_tu_cong[j];
            float soc_i = 101.0f;
            float soc_j = 101.0f;

            for (int v = 0; v < so_xe; v++) {
                if (ds_xe[v].id == tram->cong[cong_i].vehicle_id) soc_i = ds_xe[v].pin.soc;
                if (ds_xe[v].id == tram->cong[cong_j].vehicle_id) soc_j = ds_xe[v].pin.soc;
            }

            if (soc_j < soc_i) {
                int temp = thu_tu_cong[i];
                thu_tu_cong[i] = thu_tu_cong[j];
                thu_tu_cong[j] = temp;
            }
        }
    }
}
