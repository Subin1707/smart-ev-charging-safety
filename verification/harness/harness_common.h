#ifndef VERIFICATION_HARNESS_COMMON_H
#define VERIFICATION_HARNESS_COMMON_H

#include <assert.h>
#include <math.h>
#include <stdio.h>

#include "dieu_khien_sac.h"
#include "dung_khan_cap.h"
#include "giam_sat_an_toan.h"
#include "hang_so.h"
#include "phien_sac.h"
#include "quy_tac_an_toan.h"
#include "token.h"
#include "tram_sac.h"
#include "xac_thuc.h"
#include "xe_dien.h"

static void harness_setup_connected_vehicle(TramSac *tram, XeDien *xe, int port_idx)
{
    khoi_tao_tram_sac(tram, "HARNESS");
    khoi_tao_xe_dien(xe, 1, "EV-HARNESS", 60.0f, 50.0f, 25.0f, 22.0f, KB_BINH_THUONG);
    assert(ket_noi_xe_vao_tram(tram, port_idx, xe) == 1);
}

static void harness_authenticate_vehicle(XeDien *xe)
{
    char token[DO_DAI_TOKEN];
    sinh_token_xe(xe->ma_xe, token, sizeof(token));
    assert(xac_thuc_xe(xe, token) == 1);
}

static void harness_prepare_ready_to_charge(TramSac *tram, XeDien *xe, int port_idx)
{
    harness_setup_connected_vehicle(tram, xe, port_idx);
    harness_authenticate_vehicle(xe);
    tram->cong[port_idx].trang_thai = CONG_SAN_SANG;
}

static void harness_pass(const char *name)
{
    printf("[HARNESS PASS] %s\n", name);
}

#endif /* VERIFICATION_HARNESS_COMMON_H */
