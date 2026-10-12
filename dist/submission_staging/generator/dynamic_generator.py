from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "generated" / "dynamic"


TESTS = {
    "auth": r'''/* Generated from specification/auth.json */
#include <assert.h>
#include "tram_sac.h"
#include "xe_dien.h"
#include "token.h"
#include "xac_thuc.h"

void test_auth(void)
{
    TramSac tram;
    XeDien xe;
    char token[DO_DAI_TOKEN];

    khoi_tao_tram_sac(&tram, "STATION-GEN");
    khoi_tao_xe_dien(&xe, 1, "EVGEN01", 60.0f, 30.0f, 25.0f, 22.0f, KB_BINH_THUONG);

    sinh_token_xe(xe.ma_xe, token, sizeof(token));
    assert(xac_thuc_xe(&xe, token) == 0);

    assert(ket_noi_xe_vao_tram(&tram, 0, &xe) == 1);
    assert(xac_thuc_xe(&xe, token) == 1);
    assert(xe.da_xac_thuc == 1);
    assert(ngat_ket_noi_xe_khoi_tram(&tram, 0, &xe) == 1);
    assert(xe.da_xac_thuc == 0);
}

int main(void)
{
    test_auth();
    return 0;
}
''',
    "battery": r'''/* Generated from specification/battery.json */
#include <assert.h>
#include "tram_sac.h"
#include "xe_dien.h"
#include "dieu_khien_sac.h"

static void prepare_connected_authenticated(XeDien *xe, CongSac *cong)
{
    xe->da_ket_noi = 1;
    xe->da_xac_thuc = 1;
    xe->assigned_port = cong->id;
    cong->vehicle_id = xe->id;
    cong->trang_thai = CONG_DA_KET_NOI;
}

void test_battery(void)
{
    XeDien xe;
    CongSac cong;

    khoi_tao_xe_dien(&xe, 2, "EVGEN02", 60.0f, 50.0f, 25.0f, 22.0f, KB_BINH_THUONG);
    khoi_tao_cong_sac(&cong, 1);
    prepare_connected_authenticated(&xe, &cong);

    xe.pin.soc = 100.0f;
    assert(co_the_bat_dau_sac(&xe, &cong) == 0);

    xe.pin.soc = 50.0f;
    xe.pin.nhiet_do = 65.0f;
    assert(co_the_bat_dau_sac(&xe, &cong) == 0);
}

int main(void)
{
    test_battery();
    return 0;
}
''',
    "port": r'''/* Generated from specification/port.json */
#include <assert.h>
#include "tram_sac.h"
#include "xe_dien.h"

void test_port(void)
{
    TramSac tram;
    XeDien xe1;
    XeDien xe2;

    khoi_tao_tram_sac(&tram, "STATION-GEN");
    khoi_tao_xe_dien(&xe1, 3, "EVGEN03", 60.0f, 40.0f, 25.0f, 22.0f, KB_BINH_THUONG);
    khoi_tao_xe_dien(&xe2, 4, "EVGEN04", 60.0f, 40.0f, 25.0f, 22.0f, KB_BINH_THUONG);

    assert(ket_noi_xe_vao_tram(&tram, 0, &xe1) == 1);
    assert(ket_noi_xe_vao_tram(&tram, 0, &xe2) == 0);
    assert(ket_noi_xe_vao_tram(&tram, 1, &xe1) == 0);
}

int main(void)
{
    test_port();
    return 0;
}
''',
    "charging": r'''/* Generated from specification/charging.json */
#include <assert.h>
#include "tram_sac.h"
#include "xe_dien.h"
#include "token.h"
#include "xac_thuc.h"
#include "phien_sac.h"
#include "dieu_khien_sac.h"

void test_charging(void)
{
    TramSac tram;
    XeDien xe;
    PhienSac phien;
    char token[DO_DAI_TOKEN];

    khoi_tao_tram_sac(&tram, "STATION-GEN");
    khoi_tao_xe_dien(&xe, 5, "EVGEN05", 60.0f, 30.0f, 25.0f, 22.0f, KB_BINH_THUONG);
    assert(ket_noi_xe_vao_tram(&tram, 0, &xe) == 1);
    assert(bat_dau_sac(&xe, &tram.cong[0], &phien, 22.0f) == 0);

    sinh_token_xe(xe.ma_xe, token, sizeof(token));
    assert(xac_thuc_xe(&xe, token) == 1);
    assert(bat_dau_sac(&xe, &tram.cong[0], &phien, 22.0f) == 1);
}

int main(void)
{
    test_charging();
    return 0;
}
''',
}


def generate() -> list[Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for name, content in TESTS.items():
        path = OUTPUT_DIR / f"test_{name}.c"
        path.write_text(content, encoding="utf-8")
        paths.append(path)
    return paths


def main() -> None:
    print("Generated dynamic verification tests:")
    for path in generate():
        print(path.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
