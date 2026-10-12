# Formal Property Suite V2 - Phase 6

Generated: `2026-09-28T14:56:49.580114+00:00`

This suite keeps the 11 existing `AG(!req_x_violation)` safety properties and adds only properties with explicit semantics, involved states, involved transitions, and supported parser operators.

## Summary

```yaml
Properties total: 16
Safety baseline: 11/11
Reachability: 3
Recovery: 1
Recovery/Liveness: 1
Supported operators used: AF, AG, EF
Status: PASS
```

## Property Index

| Property ID | Requirement | Group | Formula | States | Transitions |
|---|---|---|---|---:|---:|
| `FP-AUTH_01-SAFETY` | `REQ-AUTH-01` | SAFETY | `AG(!req_auth_01_violation)` | 2 | 4 |
| `FP-AUTH_02-SAFETY` | `REQ-AUTH-02` | SAFETY | `AG(!req_auth_02_violation)` | 1 | 2 |
| `FP-SOC_01-SAFETY` | `REQ-SOC-01` | SAFETY | `AG(!req_soc_01_violation)` | 1 | 0 |
| `FP-SOC_02-SAFETY` | `REQ-SOC-02` | SAFETY | `AG(!req_soc_02_violation)` | 1 | 2 |
| `FP-TEMP_01-SAFETY` | `REQ-TEMP-01` | SAFETY | `AG(!req_temp_01_violation)` | 1 | 3 |
| `FP-PORT_01-SAFETY` | `REQ-PORT-01` | SAFETY | `AG(!req_port_01_violation)` | 7 | 2 |
| `FP-PORT_02-SAFETY` | `REQ-PORT-02` | SAFETY | `AG(!req_port_02_violation)` | 1 | 0 |
| `FP-PORT_03-SAFETY` | `REQ-PORT-03` | SAFETY | `AG(!req_port_03_violation)` | 1 | 3 |
| `FP-CHG_01-SAFETY` | `REQ-CHG-01` | SAFETY | `AG(!req_chg_01_violation)` | 7 | 3 |
| `FP-CHG_02-SAFETY` | `REQ-CHG-02` | SAFETY | `AG(!req_chg_02_violation)` | 7 | 6 |
| `FP-EMG_01-SAFETY` | `REQ-EMG-01` | SAFETY | `AG(!req_emg_01_violation)` | 2 | 6 |
| `FP-CHG-01-REACH-CHARGING` | `REQ-CHG-01` | REACHABILITY | `EF(charging)` | 1 | 10 |
| `FP-CHG-01-REACH-START-BLOCKED` | `REQ-CHG-01` | REACHABILITY | `EF(start_blocked)` | 1 | 6 |
| `FP-STOP-REACH-STOPPED` | `REQ-CHG-02` | REACHABILITY | `EF(stopped)` | 5 | 15 |
| `FP-RECOVERY-REACH-RECOVERED` | `REQ-CHG-02` | RECOVERY | `EF(recovered)` | 1 | 12 |
| `FP-SAFE-LIVENESS-AF-SAFE` | `REQ-CHG-02` | RECOVERY_LIVENESS | `AF(safe)` | 12 | 15 |

## FP-AUTH_01-SAFETY

```yaml
Requirement ID: REQ-AUTH-01
Group: SAFETY
Formula: AG(!req_auth_01_violation)
Meaning: >
  No reachable execution may enter a state labeled req_auth_01_violation.
Expected semantics: >
  authenticated && (!connected || !token_valid)
States involved:
  - witness_0000
  - witness_0001
Transitions involved:
  - AUTH_FAILED->START_BLOCKED:start
  - CONNECTED->AUTHENTICATED:auth_success
  - CONNECTED->AUTH_FAILED:auth_fail
  - DISCONNECTED->CONNECTED:connect
```

## FP-AUTH_02-SAFETY

```yaml
Requirement ID: REQ-AUTH-02
Group: SAFETY
Formula: AG(!req_auth_02_violation)
Meaning: >
  No reachable execution may enter a state labeled req_auth_02_violation.
Expected semantics: >
  disconnected && authenticated
States involved:
  - witness_0001
Transitions involved:
  - CHARGING->DISCONNECTING:disconnect
  - DISCONNECTING->STOPPED_DISCONNECT:stop
```

## FP-SOC_01-SAFETY

```yaml
Requirement ID: REQ-SOC-01
Group: SAFETY
Formula: AG(!req_soc_01_violation)
Meaning: >
  No reachable execution may enter a state labeled req_soc_01_violation.
Expected semantics: >
  soc_out_of_range
States involved:
  - witness_0002
Transitions involved:
```

## FP-SOC_02-SAFETY

```yaml
Requirement ID: REQ-SOC-02
Group: SAFETY
Formula: AG(!req_soc_02_violation)
Meaning: >
  No reachable execution may enter a state labeled req_soc_02_violation.
Expected semantics: >
  soc_full && (charging || power_positive)
States involved:
  - witness_0003
Transitions involved:
  - CHARGING->SOC_FULL:soc_full
  - SOC_FULL->STOPPED_SOC_FULL:stop
```

## FP-TEMP_01-SAFETY

```yaml
Requirement ID: REQ-TEMP-01
Group: SAFETY
Formula: AG(!req_temp_01_violation)
Meaning: >
  No reachable execution may enter a state labeled req_temp_01_violation.
Expected semantics: >
  overheat && charging
States involved:
  - witness_0004
Transitions involved:
  - CHARGING->OVERHEAT:overheat
  - OVERHEAT->STOPPED_OVERHEAT:stop
  - STOPPED_OVERHEAT->RECOVERED_SAFE:temperature_recovered
```

## FP-PORT_01-SAFETY

```yaml
Requirement ID: REQ-PORT-01
Group: SAFETY
Formula: AG(!req_port_01_violation)
Meaning: >
  No reachable execution may enter a state labeled req_port_01_violation.
Expected semantics: >
  charging && !connected
States involved:
  - witness_0003
  - witness_0004
  - witness_0005
  - witness_0007
  - witness_0008
  - witness_0009
  - witness_0010
Transitions involved:
  - CHARGING->DISCONNECTING:disconnect
  - DISCONNECTED->CONNECTED:connect
```

## FP-PORT_02-SAFETY

```yaml
Requirement ID: REQ-PORT-02
Group: SAFETY
Formula: AG(!req_port_02_violation)
Meaning: >
  No reachable execution may enter a state labeled req_port_02_violation.
Expected semantics: >
  port_multi_vehicle
States involved:
  - witness_0006
Transitions involved:
```

## FP-PORT_03-SAFETY

```yaml
Requirement ID: REQ-PORT-03
Group: SAFETY
Formula: AG(!req_port_03_violation)
Meaning: >
  No reachable execution may enter a state labeled req_port_03_violation.
Expected semantics: >
  fault && (charging || power_positive)
States involved:
  - witness_0007
Transitions involved:
  - CHARGING->PORT_FAULT:port_fault
  - PORT_FAULT->STOPPED_PORT_FAULT:stop
  - STOPPED_PORT_FAULT->RECOVERED_SAFE:clear_fault
```

## FP-CHG_01-SAFETY

```yaml
Requirement ID: REQ-CHG-01
Group: SAFETY
Formula: AG(!req_chg_01_violation)
Meaning: >
  No reachable execution may enter a state labeled req_chg_01_violation.
Expected semantics: >
  charging && !safety_gate_valid
States involved:
  - witness_0003
  - witness_0004
  - witness_0005
  - witness_0007
  - witness_0008
  - witness_0009
  - witness_0010
Transitions involved:
  - AUTHENTICATED->CHARGING:start
  - AUTH_FAILED->START_BLOCKED:start
  - RECOVERED_SAFE->CHARGING:restart
```

## FP-CHG_02-SAFETY

```yaml
Requirement ID: REQ-CHG-02
Group: SAFETY
Formula: AG(!req_chg_02_violation)
Meaning: >
  No reachable execution may enter a state labeled req_chg_02_violation.
Expected semantics: >
  charging && !safety_gate_valid
States involved:
  - witness_0003
  - witness_0004
  - witness_0005
  - witness_0007
  - witness_0008
  - witness_0009
  - witness_0010
Transitions involved:
  - AUTHENTICATED->CHARGING:start
  - CHARGING->DISCONNECTING:disconnect
  - RECOVERED_SAFE->CHARGING:restart
  - STOPPED_EMERGENCY->RECOVERED_SAFE:clear_emergency
  - STOPPED_OVERHEAT->RECOVERED_SAFE:temperature_recovered
  - STOPPED_PORT_FAULT->RECOVERED_SAFE:clear_fault
```

## FP-EMG_01-SAFETY

```yaml
Requirement ID: REQ-EMG-01
Group: SAFETY
Formula: AG(!req_emg_01_violation)
Meaning: >
  No reachable execution may enter a state labeled req_emg_01_violation.
Expected semantics: >
  (emergency || fault) && (charging || power_positive)
States involved:
  - witness_0007
  - witness_0010
Transitions involved:
  - CHARGING->EMERGENCY:emergency
  - CHARGING->PORT_FAULT:port_fault
  - EMERGENCY->STOPPED_EMERGENCY:stop
  - PORT_FAULT->STOPPED_PORT_FAULT:stop
  - STOPPED_EMERGENCY->RECOVERED_SAFE:clear_emergency
  - STOPPED_PORT_FAULT->RECOVERED_SAFE:clear_fault
```

## FP-CHG-01-REACH-CHARGING

```yaml
Requirement ID: REQ-CHG-01
Group: REACHABILITY
Formula: EF(charging)
Meaning: >
  There exists a valid connect/auth/start execution that reaches CHARGING.
Expected semantics: >
  The normal start sequence is feasible when all safety-gate inputs are valid.
States involved:
  - CHARGING
Transitions involved:
  - AUTHENTICATED->CHARGING:start
  - AUTH_FAILED->START_BLOCKED:start
  - CHARGING->DISCONNECTING:disconnect
  - CONNECTED->AUTHENTICATED:auth_success
  - CONNECTED->AUTH_FAILED:auth_fail
  - DISCONNECTED->CONNECTED:connect
  - RECOVERED_SAFE->CHARGING:restart
  - STOPPED_EMERGENCY->RECOVERED_SAFE:clear_emergency
  - STOPPED_OVERHEAT->RECOVERED_SAFE:temperature_recovered
  - STOPPED_PORT_FAULT->RECOVERED_SAFE:clear_fault
```

## FP-CHG-01-REACH-START-BLOCKED

```yaml
Requirement ID: REQ-CHG-01
Group: REACHABILITY
Formula: EF(start_blocked)
Meaning: >
  There exists an invalid start execution that reaches START_BLOCKED instead of CHARGING.
Expected semantics: >
  The model includes the auth-failure/start-blocked branch required by the safety gate.
States involved:
  - START_BLOCKED
Transitions involved:
  - AUTHENTICATED->CHARGING:start
  - AUTH_FAILED->START_BLOCKED:start
  - CONNECTED->AUTHENTICATED:auth_success
  - CONNECTED->AUTH_FAILED:auth_fail
  - DISCONNECTED->CONNECTED:connect
  - RECOVERED_SAFE->CHARGING:restart
```

## FP-STOP-REACH-STOPPED

```yaml
Requirement ID: REQ-CHG-02
Group: REACHABILITY
Formula: EF(stopped)
Meaning: >
  There exists at least one fault, emergency, SOC-full, overheat, or disconnect path that reaches a stopped safe state.
Expected semantics: >
  Unsafe charging conditions have modeled stop outcomes.
States involved:
  - STOPPED_SOC_FULL
  - STOPPED_OVERHEAT
  - STOPPED_PORT_FAULT
  - STOPPED_EMERGENCY
  - STOPPED_DISCONNECT
Transitions involved:
  - AUTHENTICATED->CHARGING:start
  - CHARGING->DISCONNECTING:disconnect
  - CHARGING->EMERGENCY:emergency
  - CHARGING->OVERHEAT:overheat
  - CHARGING->PORT_FAULT:port_fault
  - CHARGING->SOC_FULL:soc_full
  - DISCONNECTING->STOPPED_DISCONNECT:stop
  - EMERGENCY->STOPPED_EMERGENCY:stop
  - OVERHEAT->STOPPED_OVERHEAT:stop
  - PORT_FAULT->STOPPED_PORT_FAULT:stop
  - RECOVERED_SAFE->CHARGING:restart
  - SOC_FULL->STOPPED_SOC_FULL:stop
  - STOPPED_EMERGENCY->RECOVERED_SAFE:clear_emergency
  - STOPPED_OVERHEAT->RECOVERED_SAFE:temperature_recovered
  - STOPPED_PORT_FAULT->RECOVERED_SAFE:clear_fault
```

## FP-RECOVERY-REACH-RECOVERED

```yaml
Requirement ID: REQ-CHG-02
Group: RECOVERY
Formula: EF(recovered)
Meaning: >
  There exists a recovery execution from stopped fault/emergency/overheat into a recovered safe state.
Expected semantics: >
  Recovery sequences modeled in Phase 5 are reachable.
States involved:
  - RECOVERED_SAFE
Transitions involved:
  - AUTHENTICATED->CHARGING:start
  - CHARGING->DISCONNECTING:disconnect
  - CHARGING->EMERGENCY:emergency
  - CHARGING->OVERHEAT:overheat
  - CHARGING->PORT_FAULT:port_fault
  - EMERGENCY->STOPPED_EMERGENCY:stop
  - OVERHEAT->STOPPED_OVERHEAT:stop
  - PORT_FAULT->STOPPED_PORT_FAULT:stop
  - RECOVERED_SAFE->CHARGING:restart
  - STOPPED_EMERGENCY->RECOVERED_SAFE:clear_emergency
  - STOPPED_OVERHEAT->RECOVERED_SAFE:temperature_recovered
  - STOPPED_PORT_FAULT->RECOVERED_SAFE:clear_fault
```

## FP-SAFE-LIVENESS-AF-SAFE

```yaml
Requirement ID: REQ-CHG-02
Group: RECOVERY_LIVENESS
Formula: AF(safe)
Meaning: >
  Along modeled executions from the initial lifecycle state, a safe state is eventually encountered.
Expected semantics: >
  The lifecycle starts safe and all modeled stop/recovery branches return to safe labeled states.
States involved:
  - DISCONNECTED
  - CONNECTED
  - AUTHENTICATED
  - AUTH_FAILED
  - START_BLOCKED
  - CHARGING
  - STOPPED_SOC_FULL
  - STOPPED_OVERHEAT
  - STOPPED_PORT_FAULT
  - STOPPED_EMERGENCY
  - STOPPED_DISCONNECT
  - RECOVERED_SAFE
Transitions involved:
  - AUTHENTICATED->CHARGING:start
  - CHARGING->DISCONNECTING:disconnect
  - CHARGING->EMERGENCY:emergency
  - CHARGING->OVERHEAT:overheat
  - CHARGING->PORT_FAULT:port_fault
  - CHARGING->SOC_FULL:soc_full
  - DISCONNECTING->STOPPED_DISCONNECT:stop
  - EMERGENCY->STOPPED_EMERGENCY:stop
  - OVERHEAT->STOPPED_OVERHEAT:stop
  - PORT_FAULT->STOPPED_PORT_FAULT:stop
  - RECOVERED_SAFE->CHARGING:restart
  - SOC_FULL->STOPPED_SOC_FULL:stop
  - STOPPED_EMERGENCY->RECOVERED_SAFE:clear_emergency
  - STOPPED_OVERHEAT->RECOVERED_SAFE:temperature_recovered
  - STOPPED_PORT_FAULT->RECOVERED_SAFE:clear_fault
```

## Phase 6 Gate

```yaml
Safety baseline preserved: 11/11
Unsupported syntax errors: 0
Missing states/transitions errors: 0
Status: PASS
```