#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include "src/station/quan_ly_cong_suat.h"
#include "src/station/tram_sac.h"
/* Production verification scope: All 32 active-port masks, both equal-share and SOC-priority allocation; station limit 100 kW, fixed vehicle SOCs 0/25/50/75/100; fresh initialized station. */
static unsigned triggered_cases = 0;
static void check_case(int active_mask, int allocator)
{
    TramSac tram_obj = {0}; TramSac *tram = &tram_obj;
    khoi_tao_tram_sac(tram, "PROOF");
    XeDien vehicles[SO_CONG_SAC] = {0};
    for (int i = 0; i < SO_CONG_SAC; ++i) { vehicles[i].id = i; vehicles[i].pin.soc = i * 25.0f; tram->cong[i].vehicle_id = i; tram->cong[i].trang_thai = (active_mask & (1 << i)) ? CONG_DANG_SAC : CONG_RANH; }
    const bool trigger_before = true;
    if (allocator == 0) phan_phoi_cong_suat_chia_deu(tram); else phan_phoi_cong_suat_theo_soc(tram, vehicles, SO_CONG_SAC);
    if (trigger_before) {
        ++triggered_cases;
        for (int port_index = 0; port_index < SO_CONG_SAC; ++port_index) {
            assert((tram->cong_suat_hien_tai <= 100.0f && tram->cong[port_index].cong_suat_kw <= 22.0f));
        }
    }
}
#ifdef __CPROVER__
extern int nondet_int(void);
#endif
int main(void)
{
#ifdef __CPROVER__
    int active_mask = nondet_int();
    __CPROVER_assume(active_mask >= 0 && active_mask <= 31);
    int allocator = nondet_int();
    __CPROVER_assume(allocator >= 0 && allocator <= 1);
    check_case(active_mask, allocator);
#else
    check_case(0, 0);
    check_case(0, 1);
    check_case(1, 0);
    check_case(1, 1);
    check_case(2, 0);
    check_case(2, 1);
    check_case(3, 0);
    check_case(3, 1);
    check_case(4, 0);
    check_case(4, 1);
    check_case(5, 0);
    check_case(5, 1);
    check_case(6, 0);
    check_case(6, 1);
    check_case(7, 0);
    check_case(7, 1);
    check_case(8, 0);
    check_case(8, 1);
    check_case(9, 0);
    check_case(9, 1);
    check_case(10, 0);
    check_case(10, 1);
    check_case(11, 0);
    check_case(11, 1);
    check_case(12, 0);
    check_case(12, 1);
    check_case(13, 0);
    check_case(13, 1);
    check_case(14, 0);
    check_case(14, 1);
    check_case(15, 0);
    check_case(15, 1);
    check_case(16, 0);
    check_case(16, 1);
    check_case(17, 0);
    check_case(17, 1);
    check_case(18, 0);
    check_case(18, 1);
    check_case(19, 0);
    check_case(19, 1);
    check_case(20, 0);
    check_case(20, 1);
    check_case(21, 0);
    check_case(21, 1);
    check_case(22, 0);
    check_case(22, 1);
    check_case(23, 0);
    check_case(23, 1);
    check_case(24, 0);
    check_case(24, 1);
    check_case(25, 0);
    check_case(25, 1);
    check_case(26, 0);
    check_case(26, 1);
    check_case(27, 0);
    check_case(27, 1);
    check_case(28, 0);
    check_case(28, 1);
    check_case(29, 0);
    check_case(29, 1);
    check_case(30, 0);
    check_case(30, 1);
    check_case(31, 0);
    check_case(31, 1);
    assert(triggered_cases > 0);
    printf("PRODUCTION_CASES=64 TRIGGERED=%u\n", triggered_cases);
#endif
    return 0;
}
