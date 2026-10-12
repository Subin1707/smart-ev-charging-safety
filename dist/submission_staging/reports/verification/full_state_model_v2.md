# Full State Model V2 - Phase 4

Generated: `2026-09-28T14:52:49.423553+00:00`

Source formula: `C and A and B and T and P and (not E) and (not F)`

## Summary

| Metric | Count |
|---|---:|
| Generated states | 128 |
| Reachable states | 10 |
| Unreachable states | 118 |
| Safe states | 1 |
| Unsafe states | 127 |
| Boundary states | 96 |
| Violation candidate state labels | 414 |
| Transitions | 16 |

## Validation Gate

```yaml
missing initial state: False
invalid state reference: 0
unknown label: 0
orphan violation predicate: 0
Status: PASS
```

## Variables

| Symbol | Name | Source |
|---|---|---|
| `C` | `connected` | `AUTH` |
| `A` | `authenticated` | `AUTH` |
| `B` | `battery_safe` | `BATTERY` |
| `T` | `temperature_safe` | `BATTERY` |
| `P` | `port_ready` | `PORT` |
| `E` | `emergency` | `CHARGING` |
| `F` | `fault` | `PORT` |

## Reachable Semantic Path

| Source | Event | Target |
|---|---|---|
| `chg_0000000` | `connect` | `chg_1000000` |
| `chg_1000000` | `authenticate_success` | `chg_1100000` |
| `chg_1100000` | `battery_safe` | `chg_1110000` |
| `chg_1110000` | `temperature_safe` | `chg_1111000` |
| `chg_1111000` | `port_ready` | `chg_1111100` |
| `chg_1111100` | `temperature_unsafe` | `chg_1110100` |
| `chg_1111100` | `battery_unsafe` | `chg_1101100` |
| `chg_1111100` | `port_not_ready` | `chg_1111000` |
| `chg_1111100` | `emergency_triggered` | `chg_1111110` |
| `chg_1111100` | `fault_detected` | `chg_1111101` |
| `chg_1110100` | `temperature_recovered` | `chg_1111100` |
| `chg_1101100` | `battery_recovered` | `chg_1111100` |
| `chg_1111000` | `port_ready_restored` | `chg_1111100` |
| `chg_1111110` | `emergency_cleared` | `chg_0000000` |
| `chg_1111101` | `fault_cleared` | `chg_0000000` |
| `chg_1111100` | `stop_and_disconnect` | `chg_1000000` |

## Violation Candidate Counts

| Predicate label | Candidate states |
|---|---:|
| `req_auth_01_candidate` | 32 |
| `req_port_01_candidate` | 32 |
| `req_chg_01_candidate` | 127 |
| `req_chg_02_candidate` | 127 |
| `req_emg_01_candidate` | 96 |

## Phase 4 Gate

```yaml
Generated states: 128
Reachable states: 10
Unreachable states: 118
Safe states: 1
Unsafe states: 127
Boundary states: 96
Violation candidate states: 414
invalid state reference: 0
unknown label: 0
missing initial state: false
orphan violation predicate: 0
Status: PASS
```