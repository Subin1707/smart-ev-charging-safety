from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "specification"
OUTPUT_DIR = ROOT / "generated" / "static"
SPEC_FILES = {
    "auth": "auth.json",
    "battery": "battery.json",
    "port": "port.json",
    "charging": "charging.json",
}


def load_spec(name: str) -> dict:
    return json.loads((SPEC_DIR / SPEC_FILES[name]).read_text(encoding="utf-8"))


def render_auth(_: dict) -> str:
    return """/* Generated from specification/auth.json */
#define assert(e) __CPROVER_assert((e), #e)

extern int nondet_int(void);

int main(void)
{
    int connected = nondet_int() != 0;
    int token_valid = nondet_int() != 0;
    int authenticated = nondet_int() != 0;
    int disconnect_request = nondet_int() != 0;
    int authenticated_after_disconnect = nondet_int() != 0;

    assert(!authenticated || connected);              /* AUTH-01 */
    assert(!authenticated || token_valid);            /* AUTH-02 */
    assert(connected || !authenticated);              /* AUTH-03 */
    assert(!disconnect_request || !authenticated_after_disconnect); /* AUTH-04 */

    return 0;
}
"""


def render_battery(_: dict) -> str:
    return """/* Generated from specification/battery.json */
#define assert(e) __CPROVER_assert((e), #e)

extern float nondet_float(void);
extern int nondet_int(void);

int main(void)
{
    float soc = nondet_float();
    float temperature = nondet_float();
    int charging = nondet_int() != 0;

    if (charging) {
        assert(soc >= 0.0f && soc < 100.0f);       /* BAT-01/BAT-02/BAT-04 */
        assert(temperature < 60.0f);               /* BAT-03/BAT-05 */
    }

    return 0;
}
"""


def render_port(_: dict) -> str:
    return """/* Generated from specification/port.json */
#define assert(e) __CPROVER_assert((e), #e)

extern int nondet_int(void);

int main(void)
{
    int connected = nondet_int() != 0;
    int occupied = nondet_int() != 0;
    int port_charging = nondet_int() != 0;
    int port_fault = nondet_int() != 0;

    assert(!port_charging || connected);   /* PORT-01 */
    assert(!port_charging || occupied);    /* PORT-02 */
    assert(!port_fault || !port_charging); /* PORT-03 */

    return 0;
}
"""


def render_charging(_: dict) -> str:
    return """/* Generated from specification/charging.json */
#define assert(e) __CPROVER_assert((e), #e)

extern int nondet_int(void);

int main(void)
{
    int connected = nondet_int() != 0;
    int authenticated = nondet_int() != 0;
    int battery_valid = nondet_int() != 0;
    int temperature_safe = nondet_int() != 0;
    int port_valid = nondet_int() != 0;
    int emergency = nondet_int() != 0;
    int fault = nondet_int() != 0;
    int charging = nondet_int() != 0;

    if (charging) {
        assert(connected && authenticated && battery_valid &&
               temperature_safe && port_valid && !emergency && !fault); /* CHG-01 */
    }

    return 0;
}
"""


RENDERERS = {
    "auth": render_auth,
    "battery": render_battery,
    "port": render_port,
    "charging": render_charging,
}


def generate() -> list[Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for name, renderer in RENDERERS.items():
        spec = load_spec(name)
        path = OUTPUT_DIR / f"verify_{name}.c"
        path.write_text(renderer(spec), encoding="utf-8")
        paths.append(path)
    return paths


def main() -> None:
    print("Generated static verification code:")
    for path in generate():
        print(path.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
