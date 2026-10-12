# Negative Control Selectivity - Phase 7

Generated: `2026-09-28T16:14:11.279366+00:00`

Each negative-control spec injects exactly one reachable violation label. The expected result is selective: only the injected domain should report `VI PHAM`; all other domains should remain `DUNG`.

## Generated Files

| Domain | File | Injected label | Expected failing property | Validation |
|---|---|---|---|---|
| AUTH | `teacher_specs/negative_controls/auth_negative.json` | `req_auth_01_violation` | `AG(!req_auth_01_violation)` | `PASS` |
| SOC | `teacher_specs/negative_controls/soc_negative.json` | `req_soc_01_violation` | `AG(!req_soc_01_violation)` | `PASS` |
| TEMP | `teacher_specs/negative_controls/temp_negative.json` | `req_temp_01_violation` | `AG(!req_temp_01_violation)` | `PASS` |
| PORT | `teacher_specs/negative_controls/port_negative.json` | `req_port_03_violation` | `AG(!req_port_03_violation)` | `PASS` |
| CHARGING | `teacher_specs/negative_controls/charging_negative.json` | `req_chg_01_violation` | `AG(!req_chg_01_violation)` | `PASS` |
| EMERGENCY | `teacher_specs/negative_controls/emergency_negative.json` | `req_emg_01_violation` | `AG(!req_emg_01_violation)` | `PASS` |

## Expected Selectivity Matrix

| Model | AUTH | SOC | TEMP | PORT | CHARGING | EMERGENCY |
|---|---|---|---|---|---|---|
| `NORMAL` | DUNG | DUNG | DUNG | DUNG | DUNG | DUNG |
| `auth_negative.json` | VI PHAM | DUNG | DUNG | DUNG | DUNG | DUNG |
| `soc_negative.json` | DUNG | VI PHAM | DUNG | DUNG | DUNG | DUNG |
| `temp_negative.json` | DUNG | DUNG | VI PHAM | DUNG | DUNG | DUNG |
| `port_negative.json` | DUNG | DUNG | DUNG | VI PHAM | DUNG | DUNG |
| `charging_negative.json` | DUNG | DUNG | DUNG | DUNG | VI PHAM | DUNG |
| `emergency_negative.json` | DUNG | DUNG | DUNG | DUNG | DUNG | VI PHAM |

## Validation

```yaml
Negative controls: 6/6
Normal reachable violation labels: 0
Failed controls: 0
Status: PASS
```

## Phase 7 Gate

```yaml
AUTH negative: one injected violation
SOC negative: one injected violation
TEMP negative: one injected violation
PORT negative: one injected violation
CHARGING negative: one injected violation
EMERGENCY negative: one injected violation
Status: PASS
```