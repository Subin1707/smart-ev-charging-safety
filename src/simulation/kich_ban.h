#ifndef KICH_BAN_H
#define KICH_BAN_H

#include "xe_dien.h"
#include "tram_sac.h"

#define SCENARIO_NAME_LENGTH 32

typedef enum {
    SCENARIO_NORMAL,
    SCENARIO_OVERHEAT,
    SCENARIO_AUTH_FAILURE,
    SCENARIO_UNEXPECTED_DISCONNECT,
    SCENARIO_POWER_OVERLOAD,
    SCENARIO_EMERGENCY_STOP,
    SCENARIO_MIXED,
    SCENARIO_CRITICAL_TEMPERATURE,
    SCENARIO_THERMAL_RUNAWAY,
    SCENARIO_FIRE_RISK
} LoaiScenario;

typedef struct {
    LoaiScenario loai;
    int vehicle_index;
    int trigger_tick;
    int da_kich_hoat;
    int da_load;
} KichBanMoPhong;

void khoi_tao_kich_ban(KichBanMoPhong *kich_ban);
int dat_kich_ban(KichBanMoPhong *kich_ban, const char *name, int vehicle_index);
const char *ten_kich_ban_scenario(LoaiScenario scenario);
void ap_dung_kich_ban_tick(KichBanMoPhong *kich_ban,
                           int tick,
                           TramSac *tram,
                           XeDien ds_xe[],
                           int so_xe);

#endif
