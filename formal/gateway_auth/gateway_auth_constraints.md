# Gateway Authentication Constraints

## State Variables

C = Connected
T = Token Valid
A = Authenticated
R = Start Request
S = Safety OK
E = Emergency

Raw state space:

N = 2^6 = 64 combinations.

CHARGING is not modeled as an independent Gateway Authentication input variable.
It is a transition result derived from gateway, safety, and emergency conditions.

## Constraints

GA-C01:
A -> C

A vehicle cannot be authenticated without being connected.

GA-C02:
A -> T

Authentication success requires a valid token.

GA-C03:
CHARGING -> C

A charging vehicle must remain connected.

GA-C04:
CHARGING -> A

A charging vehicle must be authenticated.

GA-C05:
CHARGING -> S

Charging is permitted only when safety conditions are satisfied.

GA-C06:
E -> !CHARGING

Emergency state prohibits charging.

GA-C07:
!C -> !A

Disconnecting invalidates authentication.

GA-C08:
START_ALLOWED -> C && T && A && R && S && !E

Charging can start only when all gateway and safety conditions hold.

## State-Space Enumeration

The initial Gateway Authentication enumeration uses only:

C T A R S E

This produces 64 candidate states. Applying the initial gateway constraints:

- GA-C01: A -> C
- GA-C02: A -> T

removes every candidate where A = 1 while C = 0 or T = 0.

Run:

```sh
python formal/gateway_auth/gateway_state_space.py
```

On Windows, if `python` is not available:

```sh
py formal/gateway_auth/gateway_state_space.py
```

The script is formal state-space analysis code, not charging-station runtime code.
Its purpose is to generate all candidate states, remove invalid states by
constraints, and provide the valid state space used to build the Kripke model.

Current result with GA-C01 and GA-C02:

- Candidate states: 64
- Valid states: 40
- Invalid states removed: 24

## Specialized Kripke Model

The specialized Gateway Authentication Kripke model is implemented in:

- `formal/gateway_auth/gateway_kripke.h`
- `formal/gateway_auth/gateway_kripke.c`

It keeps the existing abstract charging model in `formal/kripke` unchanged.

Formal structure:

K = (S, S0, R, L)

- S = {WAITING, CONNECTED, AUTH_OK, AUTH_FAIL, CHARGING, STOPPED, FAULT, EMERGENCY}
- S0 = WAITING
- R = transition relation implemented by `TRANSITIONS`
- L = labels over C,T,A,R,S,E implemented by `STATE_LABELS`

Example labels:

```makefile
CONNECTED:
C=1 T=0 A=0 R=0 S=1 E=0

AUTH_OK:
C=1 T=1 A=1 R=0 S=1 E=0

CHARGING:
C=1 T=1 A=1 R=1 S=1 E=0
```

## Verification Code Generation

Gateway Auth constraints are connected to generated verification artifacts by:

```sh
python formal/gateway_auth/generate_gateway_verification.py
```

The generator writes CBMC and Z3 files under:

```text
generated/static/gateway_auth/
```

Current generated mapping:

```text
GA-C01: A -> C
CBMC: assert(!authenticated || connected);

GA-C02: A -> T
CBMC: assert(!authenticated || token_valid);

GA-C06: E -> !CHARGING
CBMC: assert(!emergency || !charging);
```

The Z3 scripts search for counterexamples to the same implications. A `sat`
result means the isolated constraint can be violated without additional
assumptions; the CBMC harnesses assert that production or model constraints must
exclude that counterexample.

## Static Testing Evidence

Aggregate verification artifacts:

```text
generated/static/gateway_auth_cbmc.c
generated/static/gateway_auth_z3.py
```

Commands:

```sh
tools/cbmc/extracted/cbmc/bin/cbmc.exe --gcc generated/static/gateway_auth_cbmc.c
python generated/static/gateway_auth_z3.py
cppcheck --enable=all src/
```

Evidence summary:

```yaml
GA-C01: PASS
GA-C02: PASS
GA-C03: PASS
GA-C04: PASS
GA-C05: PASS
GA-C06: PASS
GA-C07: PASS
GA-C08: PASS
```

Detailed evidence is recorded in:

```text
reports/static-testing/gateway_auth_static_testing.yaml
```

## Dynamic Testing Evidence

After formal/static verification, runtime tests exercise the Gateway Auth flows:

```text
Connect -> invalid token -> Authentication FAIL -> Start charging -> DENY
Connect -> valid token -> Authentication SUCCESS -> Start -> Charging SUCCESS
Connect -> Authenticate -> Start charging -> Emergency -> Charging STOP -> Power = 0
Connect -> Authenticate -> Disconnect -> authenticated = 0
```

Primary dynamic test:

```text
tests/integration/test_ket_noi_xac_thuc_sac.c
```

Evidence summary:

```yaml
auth_failure_denies_charging: PASS
valid_auth_allows_charging: PASS
emergency_stops_charging: PASS
disconnect_resets_authentication: PASS
```

Detailed evidence is recorded in:

```text
reports/dynamic-testing/gateway_auth_dynamic_testing.yaml
```
