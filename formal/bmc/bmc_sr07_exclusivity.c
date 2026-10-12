/*
 * formal/bmc/bmc_sr07_exclusivity.c
 * BMC Harness: SR07 — One port can only serve ONE vehicle at a time
 */
#include <assert.h>
#include "cong_sac.h"

int main(void) {
    CongSac cong;
    khoi_tao_cong_sac(&cong, 1);

    /* Connect first vehicle */
    int vid1, vid2;
    __CPROVER_assume(vid1 >= 1 && vid1 <= 5);
    __CPROVER_assume(vid2 >= 1 && vid2 <= 5);
    __CPROVER_assume(vid1 != vid2); /* two different vehicles */

    int r1 = ket_noi_xe_vao_cong(&cong, vid1);
    assert(r1 == 1); /* first connection always succeeds on empty port */
    assert(cong.vehicle_id == vid1);

    /* Attempt to connect second vehicle — MUST FAIL (SR07) */
    int r2 = ket_noi_xe_vao_cong(&cong, vid2);
    assert(r2 == 0); /* must be rejected */
    assert(cong.vehicle_id == vid1); /* original vehicle still assigned */

    return 0;
}
