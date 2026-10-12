# System Function Parameter-to-Verification Specification

This document summarizes the formal path required by the report:

```text
function -> parameters -> candidate state space -> constraints -> requirements -> verification code
```

It complements the deeper Gateway Authentication model in `formal/gateway_auth/`.

## Generated Specification Inputs

The first generation step is now represented by four JSON specifications:

```text
specification/auth.json
specification/battery.json
specification/port.json
specification/charging.json
```

Run the state-space generator:

```sh
python generator/state_generator.py
```

Current state-space evidence:

```text
reports/state-space/system_state_space.txt
```

The 4-module generators are:

```text
generator/static_generator.py
generator/dynamic_generator.py
```

They generate:

```text
generated/static/verify_auth.c
generated/static/verify_battery.c
generated/static/verify_port.c
generated/static/verify_charging.c
generated/dynamic/test_auth.c
generated/dynamic/test_battery.c
generated/dynamic/test_port.c
generated/dynamic/test_charging.c
```

Generation evidence is recorded in:

```text
reports/static-testing/generated_module_verification.yaml
```

## F01: Vehicle Entry/Exit Authentication

Scope: vehicle connects, token is checked, authentication succeeds or fails, and disconnect invalidates authentication.

| Symbol | Meaning | Domain |
|---|---|---|
| `C` | Connected | `{0,1}` |
| `T` | Token valid | `{0,1}` |
| `A` | Authenticated | `{0,1}` |
| `D` | Disconnect event | `{0,1}` |

Raw candidate state space: `2^4 = 16`.

Constraints:

```text
F01-C01: A -> C
F01-C02: A -> T
F01-C03: D -> !C
F01-C04: D -> !A
```

Requirements: `SR01`, `SR02`.

Verification code:

```text
Static:  generated/static/gateway_auth_cbmc.c
Static:  generated/static/gateway_auth_z3.py
Dynamic: tests/integration/test_ket_noi_xac_thuc_sac.c
Dynamic: tests/e2e/test_luong_loi_xac_thuc.c
```

## F02: Vehicle Condition Check

Scope: temperature, energy/SOC level, finite sensor values, and fault-state validity.

| Symbol | Meaning | Domain |
|---|---|---|
| `TEMP_OK` | Temperature below limit | `{0,1}` |
| `SOC_OK` | SOC finite and in `[0,100]` | `{0,1}` |
| `NOT_FULL` | SOC below 100% | `{0,1}` |
| `NO_FAULT` | Vehicle is not in fault state | `{0,1}` |

Raw candidate state space: `2^4 = 16`.

Constraints:

```text
F02-C01: CHARGING -> TEMP_OK
F02-C02: CHARGING -> SOC_OK
F02-C03: CHARGING -> NOT_FULL
F02-C04: CHARGING -> NO_FAULT
```

Requirements: `SR03`, `SR04`, `SR06`, `SR09`.

Verification code:

```text
Static:  formal/bmc/sr03_overheat_fixed.c
Static:  formal/bmc/sr04_full_fixed.c
Static:  generated/static/SR03_cbmc.c
Static:  generated/static/SR03_z3.py
Dynamic: tests/e2e/test_luong_qua_nhiet.c
Dynamic: tests/e2e/test_luong_pin_day.c
Dynamic: tests/unit/test_an_toan.c
```

## F03: Charging Port Connection State

Scope: port connection, ownership, exclusivity, and disconnect/release.

| Symbol | Meaning | Domain |
|---|---|---|
| `C` | Vehicle connected | `{0,1}` |
| `P` | Port occupied | `{0,1}` |
| `OWNER` | Connected vehicle owns the port | `{0,1}` |
| `UNIQUE` | Vehicle appears on at most one port | `{0,1}` |

Raw candidate state space: `2^4 = 16`.

Constraints:

```text
F03-C01: CHARGING -> C
F03-C02: CHARGING -> P
F03-C03: P -> OWNER
F03-C04: CONNECT_ACCEPTED -> UNIQUE
```

Requirements: `SR07`, `SR08`.

Verification code:

```text
Static:  formal/bmc/sr07_exclusivity_fixed.c
Dynamic: tests/unit/test_cong_sac.c
Dynamic: tests/unit/test_tram_sac.c
Dynamic: tests/integration/test_nhieu_xe.c
Dynamic: tests/e2e/test_auto_port_assignment.py
```

## F04: Charging Validity

Scope: charging can start only when authentication, connection, port, safety, emergency, and capacity conditions are valid.

| Symbol | Meaning | Domain |
|---|---|---|
| `C` | Connected | `{0,1}` |
| `A` | Authenticated | `{0,1}` |
| `R` | Start request | `{0,1}` |
| `S` | Safety OK | `{0,1}` |
| `E` | Emergency | `{0,1}` |
| `CAP` | Capacity available | `{0,1}` |
| `PWR_OK` | Power within bounds | `{0,1}` |

Raw candidate state space: `2^7 = 128`.

Constraints:

```text
F04-C01: START_ALLOWED -> C && A && R && S && !E && CAP
F04-C02: CHARGING -> C
F04-C03: CHARGING -> A
F04-C04: CHARGING -> S
F04-C05: E -> !CHARGING
F04-C06: E -> POWER_ZERO
F04-C07: CHARGING -> PWR_OK
```

Requirements: `SR02`, `SR03`, `SR04`, `SR05`, `SR10`.

Verification code:

```text
Static:  generated/static/gateway_auth_cbmc.c
Static:  generated/static/gateway_auth_z3.py
Static:  formal/bmc/sr05_emergency_fixed.c
Static:  formal/bmc/sr10_power_limit_fixed.c
Dynamic: tests/integration/test_ket_noi_xac_thuc_sac.c
Dynamic: tests/integration/test_dung_khan_cap.c
Dynamic: tests/integration/test_phan_phoi_cong_suat.c
Dynamic: tests/e2e/test_emergency_stop.py
```

## Evidence

```text
reports/static-testing/gateway_auth_static_testing.yaml
reports/dynamic-testing/gateway_auth_dynamic_testing.yaml
```
