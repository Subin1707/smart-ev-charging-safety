from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


OUTPUT_DIR = Path("generated/static/gateway_auth")
LEGACY_OUTPUT_DIR = Path("generated/static")


@dataclass(frozen=True)
class GatewayConstraint:
    constraint_id: str
    description: str
    cbmc_assertion: str
    z3_counterexample: str


CONSTRAINTS = [
    GatewayConstraint(
        constraint_id="GA-C01",
        description="Authenticated implies Connected",
        cbmc_assertion="!authenticated || connected",
        z3_counterexample="And(authenticated, Not(connected))",
    ),
    GatewayConstraint(
        constraint_id="GA-C02",
        description="Authenticated implies Token Valid",
        cbmc_assertion="!authenticated || token_valid",
        z3_counterexample="And(authenticated, Not(token_valid))",
    ),
    GatewayConstraint(
        constraint_id="GA-C06",
        description="Emergency implies not Charging",
        cbmc_assertion="!emergency || !charging",
        z3_counterexample="And(emergency, charging)",
    ),
]

AGGREGATE_CONSTRAINTS = [
    GatewayConstraint(
        constraint_id="GA-C01",
        description="Authenticated implies Connected",
        cbmc_assertion="!authenticated || connected",
        z3_counterexample="And(authenticated, Not(connected))",
    ),
    GatewayConstraint(
        constraint_id="GA-C02",
        description="Authenticated implies Token Valid",
        cbmc_assertion="!authenticated || token_valid",
        z3_counterexample="And(authenticated, Not(token_valid))",
    ),
    GatewayConstraint(
        constraint_id="GA-C03",
        description="Charging implies Connected",
        cbmc_assertion="!charging || connected",
        z3_counterexample="And(charging, Not(connected))",
    ),
    GatewayConstraint(
        constraint_id="GA-C04",
        description="Charging implies Authenticated",
        cbmc_assertion="!charging || authenticated",
        z3_counterexample="And(charging, Not(authenticated))",
    ),
    GatewayConstraint(
        constraint_id="GA-C05",
        description="Charging implies Safety OK",
        cbmc_assertion="!charging || safety_ok",
        z3_counterexample="And(charging, Not(safety_ok))",
    ),
    GatewayConstraint(
        constraint_id="GA-C06",
        description="Emergency implies not Charging",
        cbmc_assertion="!emergency || !charging",
        z3_counterexample="And(emergency, charging)",
    ),
    GatewayConstraint(
        constraint_id="GA-C07",
        description="Disconnected implies not Authenticated",
        cbmc_assertion="connected || !authenticated",
        z3_counterexample="And(Not(connected), authenticated)",
    ),
    GatewayConstraint(
        constraint_id="GA-C08",
        description="START_ALLOWED requires all gateway and safety conditions",
        cbmc_assertion=(
            "!start_allowed || "
            "(connected && token_valid && authenticated && start_request && safety_ok && !emergency)"
        ),
        z3_counterexample=(
            "And(start_allowed, "
            "Not(And(connected, token_valid, authenticated, start_request, safety_ok, Not(emergency))))"
        ),
    ),
]


def artifact_name(constraint_id: str, suffix: str) -> str:
    safe_id = constraint_id.lower().replace("-", "_")
    return f"{safe_id}_{suffix}"


def render_cbmc(constraint: GatewayConstraint) -> str:
    return f"""/* Generated Gateway Auth CBMC harness.
 * Source constraint: {constraint.constraint_id}
 * Meaning: {constraint.description}
 */
#include <assert.h>
#include <stdbool.h>

extern bool nondet_bool(void);

int main(void)
{{
    bool connected = nondet_bool();
    bool token_valid = nondet_bool();
    bool authenticated = nondet_bool();
    bool start_request = nondet_bool();
    bool safety_ok = nondet_bool();
    bool emergency = nondet_bool();
    bool charging = nondet_bool();

    (void)connected;
    (void)token_valid;
    (void)authenticated;
    (void)start_request;
    (void)safety_ok;
    (void)emergency;
    (void)charging;

    assert({constraint.cbmc_assertion});

    return 0;
}}
"""


def render_z3(constraint: GatewayConstraint) -> str:
    return f'''# Generated Gateway Auth Z3 counterexample search.
# Source constraint: {constraint.constraint_id}
# Meaning: {constraint.description}
from z3 import Bool, Solver, And, Not

connected = Bool("connected")
token_valid = Bool("token_valid")
authenticated = Bool("authenticated")
start_request = Bool("start_request")
safety_ok = Bool("safety_ok")
emergency = Bool("emergency")
charging = Bool("charging")

s = Solver()

# A satisfiable result means the constraint can be violated.
s.add({constraint.z3_counterexample})

print(s.check())
print(s.model())
'''


def render_aggregate_cbmc() -> str:
    assertions = "\n".join(
        f"    assert({constraint.cbmc_assertion}); /* {constraint.constraint_id} */"
        for constraint in AGGREGATE_CONSTRAINTS
    )
    return f"""/* Generated Gateway Auth aggregate CBMC harness. */
#define assert(e) __CPROVER_assert((e), #e)

extern unsigned int nondet_uint(void);

int main(void)
{{
    unsigned int state = nondet_uint();
    __CPROVER_assume(state < 8);

    int connected = 0;
    int token_valid = 0;
    int authenticated = 0;
    int start_request = 0;
    int safety_ok = 0;
    int emergency = 0;
    int charging = 0;
    int start_allowed = 0;

    switch (state) {{
    case 0: /* WAITING */
        safety_ok = 1;
        break;
    case 1: /* CONNECTED */
        connected = 1;
        safety_ok = 1;
        break;
    case 2: /* AUTH_OK */
        connected = 1;
        token_valid = 1;
        authenticated = 1;
        safety_ok = 1;
        break;
    case 3: /* AUTH_FAIL */
        connected = 1;
        safety_ok = 1;
        break;
    case 4: /* CHARGING */
        connected = 1;
        token_valid = 1;
        authenticated = 1;
        start_request = 1;
        safety_ok = 1;
        charging = 1;
        start_allowed = 1;
        break;
    case 5: /* STOPPED */
        connected = 1;
        token_valid = 1;
        authenticated = 1;
        safety_ok = 1;
        break;
    case 6: /* FAULT */
        connected = 1;
        token_valid = 1;
        authenticated = 1;
        start_request = 1;
        break;
    case 7: /* EMERGENCY */
        connected = 1;
        token_valid = 1;
        authenticated = 1;
        start_request = 1;
        emergency = 1;
        break;
    }}

{assertions}

    return 0;
}}
"""


def render_aggregate_z3() -> str:
    checks = "\n".join(f'check("{constraint.constraint_id}", {constraint.z3_counterexample})' for constraint in AGGREGATE_CONSTRAINTS)
    return f'''# Generated Gateway Auth aggregate Z3 proof checks.
from z3 import Bool, BoolVal, Solver, And, Not, Or, unsat

connected = Bool("connected")
token_valid = Bool("token_valid")
authenticated = Bool("authenticated")
start_request = Bool("start_request")
safety_ok = Bool("safety_ok")
emergency = Bool("emergency")
charging = Bool("charging")
start_allowed = Bool("start_allowed")

gateway_states = [
    # C, T, A, R, S, E, charging, start_allowed
    (False, False, False, False, True,  False, False, False), # WAITING
    (True,  False, False, False, True,  False, False, False), # CONNECTED
    (True,  True,  True,  False, True,  False, False, False), # AUTH_OK
    (True,  False, False, False, True,  False, False, False), # AUTH_FAIL
    (True,  True,  True,  True,  True,  False, True,  True),  # CHARGING
    (True,  True,  True,  False, True,  False, False, False), # STOPPED
    (True,  True,  True,  True,  False, False, False, False), # FAULT
    (True,  True,  True,  True,  False, True,  False, False), # EMERGENCY
]

state_formula = Or(*[
    And(
        connected == BoolVal(C),
        token_valid == BoolVal(T),
        authenticated == BoolVal(A),
        start_request == BoolVal(R),
        safety_ok == BoolVal(S),
        emergency == BoolVal(E),
        charging == BoolVal(CH),
        start_allowed == BoolVal(SA),
    )
    for C, T, A, R, S, E, CH, SA in gateway_states
])

def check(constraint_id, violation_formula):
    solver = Solver()
    solver.add(state_formula)
    solver.add(violation_formula)
    result = solver.check()
    if result == unsat:
        print(f"{{constraint_id}} : PASS")
    else:
        print(f"{{constraint_id}} : FAIL {{solver.model()}}")

{checks}
'''


def generate(output_dir: Path = OUTPUT_DIR) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    for constraint in CONSTRAINTS:
        cbmc_path = output_dir / artifact_name(constraint.constraint_id, "cbmc.c")
        z3_path = output_dir / artifact_name(constraint.constraint_id, "z3.py")
        cbmc_path.write_text(render_cbmc(constraint), encoding="utf-8")
        z3_path.write_text(render_z3(constraint), encoding="utf-8")
        paths.extend([cbmc_path, z3_path])

    LEGACY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    aggregate_cbmc_path = LEGACY_OUTPUT_DIR / "gateway_auth_cbmc.c"
    aggregate_z3_path = LEGACY_OUTPUT_DIR / "gateway_auth_z3.py"
    aggregate_cbmc_path.write_text(render_aggregate_cbmc(), encoding="utf-8")
    aggregate_z3_path.write_text(render_aggregate_z3(), encoding="utf-8")
    paths.extend([aggregate_cbmc_path, aggregate_z3_path])

    return paths


def main() -> None:
    paths = generate()
    print("Generated Gateway Auth verification artifacts:")
    for path in paths:
        print(path.as_posix())


if __name__ == "__main__":
    main()
