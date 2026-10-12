# Transition and Sequence Coverage - Phase 5

Generated: `2026-09-28T14:54:49.037177+00:00`

## Summary

| Metric | Count |
|---|---:|
| Transitions total | 19 |
| Transitions reachable | 19 |
| Transitions covered by requirement | 19 |
| Transitions without requirement | 0 |
| Sequences generated | 9 |
| Safety sequences | 7 |
| Recovery sequences | 2 |
| Reachable states | 17 |
| Unreachable states | 0 |

## Required Sequences

| Sequence | Type | Path | Requirements | Status |
|---|---|---|---|---|
| `connect_auth_start_charging` | safety | `DISCONNECTED` -> `CONNECTED` -> `AUTHENTICATED` -> `CHARGING` | `REQ-AUTH-01`<br>`REQ-PORT-01`<br>`REQ-CHG-01`<br>`REQ-CHG-02` | `PASS` |
| `connect_authfail_startblocked` | safety | `DISCONNECTED` -> `CONNECTED` -> `AUTH_FAILED` -> `START_BLOCKED` | `REQ-AUTH-01`<br>`REQ-CHG-01` | `PASS` |
| `charging_socfull_stop` | safety | `CHARGING` -> `SOC_FULL` -> `STOPPED_SOC_FULL` | `REQ-SOC-02` | `PASS` |
| `charging_overheat_stop` | safety | `CHARGING` -> `OVERHEAT` -> `STOPPED_OVERHEAT` | `REQ-TEMP-01` | `PASS` |
| `charging_portfault_stop` | safety | `CHARGING` -> `PORT_FAULT` -> `STOPPED_PORT_FAULT` | `REQ-PORT-03`<br>`REQ-EMG-01` | `PASS` |
| `charging_emergency_stop` | safety | `CHARGING` -> `EMERGENCY` -> `STOPPED_EMERGENCY` | `REQ-EMG-01` | `PASS` |
| `charging_disconnect_stop` | safety | `CHARGING` -> `DISCONNECTING` -> `STOPPED_DISCONNECT` | `REQ-AUTH-02`<br>`REQ-PORT-01`<br>`REQ-CHG-02` | `PASS` |
| `fault_clear_safe` | recovery | `PORT_FAULT` -> `STOPPED_PORT_FAULT` -> `RECOVERED_SAFE` | `REQ-PORT-03`<br>`REQ-EMG-01`<br>`REQ-CHG-02` | `PASS` |
| `emergency_recovery_safe` | recovery | `EMERGENCY` -> `STOPPED_EMERGENCY` -> `RECOVERED_SAFE` | `REQ-EMG-01`<br>`REQ-CHG-02` | `PASS` |

## Transition Coverage

| Source | Event | Target | Requirements | Scenario |
|---|---|---|---|---|
| `DISCONNECTED` | `connect` | `CONNECTED` | `REQ-AUTH-01`<br>`REQ-PORT-01` | `normal_start` |
| `CONNECTED` | `auth_success` | `AUTHENTICATED` | `REQ-AUTH-01` | `normal_start` |
| `AUTHENTICATED` | `start` | `CHARGING` | `REQ-CHG-01`<br>`REQ-CHG-02` | `normal_start` |
| `CONNECTED` | `auth_fail` | `AUTH_FAILED` | `REQ-AUTH-01` | `auth_failure` |
| `AUTH_FAILED` | `start` | `START_BLOCKED` | `REQ-AUTH-01`<br>`REQ-CHG-01` | `auth_failure` |
| `CHARGING` | `soc_full` | `SOC_FULL` | `REQ-SOC-02` | `soc_full_stop` |
| `SOC_FULL` | `stop` | `STOPPED_SOC_FULL` | `REQ-SOC-02` | `soc_full_stop` |
| `CHARGING` | `overheat` | `OVERHEAT` | `REQ-TEMP-01` | `overheat_stop` |
| `OVERHEAT` | `stop` | `STOPPED_OVERHEAT` | `REQ-TEMP-01` | `overheat_stop` |
| `CHARGING` | `port_fault` | `PORT_FAULT` | `REQ-PORT-03`<br>`REQ-EMG-01` | `port_fault_stop` |
| `PORT_FAULT` | `stop` | `STOPPED_PORT_FAULT` | `REQ-PORT-03`<br>`REQ-EMG-01` | `port_fault_stop` |
| `CHARGING` | `emergency` | `EMERGENCY` | `REQ-EMG-01` | `emergency_stop` |
| `EMERGENCY` | `stop` | `STOPPED_EMERGENCY` | `REQ-EMG-01` | `emergency_stop` |
| `CHARGING` | `disconnect` | `DISCONNECTING` | `REQ-AUTH-02`<br>`REQ-PORT-01`<br>`REQ-CHG-02` | `disconnect_stop` |
| `DISCONNECTING` | `stop` | `STOPPED_DISCONNECT` | `REQ-AUTH-02` | `disconnect_stop` |
| `STOPPED_PORT_FAULT` | `clear_fault` | `RECOVERED_SAFE` | `REQ-PORT-03`<br>`REQ-EMG-01`<br>`REQ-CHG-02` | `fault_recovery` |
| `STOPPED_EMERGENCY` | `clear_emergency` | `RECOVERED_SAFE` | `REQ-EMG-01`<br>`REQ-CHG-02` | `emergency_recovery` |
| `STOPPED_OVERHEAT` | `temperature_recovered` | `RECOVERED_SAFE` | `REQ-TEMP-01`<br>`REQ-CHG-02` | `overheat_recovery` |
| `RECOVERED_SAFE` | `restart` | `CHARGING` | `REQ-CHG-01`<br>`REQ-CHG-02` | `restart_after_recovery` |

## Validation Gate

```yaml
missing initial state: False
invalid state reference: 0
failed required sequences: 0
transitions without requirement: 0
Status: PASS
```

## Phase 5 Gate

```yaml
Transitions total: 19
Transitions reachable: 19
Transitions covered by requirement: 19
Transitions without requirement: 0
Sequences generated: 9
Safety sequences: 7
Recovery sequences: 2
Status: PASS
```