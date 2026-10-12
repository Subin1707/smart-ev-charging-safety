# Formal Capability Analysis

This is the second capability pass, based on the original files extracted from `SpecVerificationLab.exe` under:

```text
teacher_app/extracted_static/dataset/specs/
```

No changes were made to `SpecVerificationLab.exe`, production source, or `reports/verification/integrated_verification.json`.

## Inputs Reviewed

- `FORMAT.md`
- `auth_rate_limit_spec.json`
- `elevator_control_spec.json`
- `file_upload_auth_spec.json`
- `iot_gateway_spec.json`
- `resource_pool_spec.json`
- `session_manager_fixed_spec.json`
- `session_manager_spec.json`

## Property Format

`FORMAT.md` documents `safety_properties` as a list of CTL formulas checked over `state_machine`.

Supported syntax stated by `FORMAT.md`:

```text
AG(p), EF(p), AF(p), EG(p), AX(p), EX(p), AG(!p)
```

Observed samples:

| File | `safety_properties` | `mutual_exclusion` |
|---|---|---|
| `auth_rate_limit_spec.json` | `EF(trusted)` | `{atom1: transient, atom2: trusted}` |
| `elevator_control_spec.json` | `AG(!violation)` | `null` |
| `file_upload_auth_spec.json` | `AG(!violation)` | `{atom1: p1, atom2: p2}` |
| `iot_gateway_spec.json` | `AG(!violation)`, `EF(main_locked)` | `{atom1: main_locked, atom2: log_locked}` |
| `resource_pool_spec.json` | empty | `null` |
| `session_manager_fixed_spec.json` | `AG(!violation)` | `{atom1: p1, atom2: p2}` |
| `session_manager_spec.json` | `AG(!violation)` | `{atom1: p1, atom2: p2}` |

## Operator Capability

| Operator | Status | Evidence |
|---|---|---|
| `AG` | SUPPORTED | `FORMAT.md` lists `AG(p)`; multiple samples use `AG(!violation)`. |
| `EF` | SUPPORTED | `FORMAT.md` lists `EF(p)`; `iot_gateway_spec.json` uses `EF(main_locked)`; `auth_rate_limit_spec.json` uses `EF(trusted)`. |
| `AF` | SUPPORTED | `FORMAT.md` lists `AF(p)`. No extracted sample uses it, but the format document explicitly says it is supported. |
| `EG` | SUPPORTED | `FORMAT.md` lists `EG(p)`. No extracted sample uses it. |
| `AX` | SUPPORTED | `FORMAT.md` lists `AX(p)`. No extracted sample uses it. |
| `EX` | SUPPORTED | `FORMAT.md` lists `EX(p)`. No extracted sample uses it. |
| `!` | SUPPORTED, LIMITED | `FORMAT.md` supports simple negation `AG(!p)`; samples use `AG(!violation)`. No evidence for arbitrary `!(a & b)` inside `safety_properties`. |
| `&&` | UNSUPPORTED | `FORMAT.md` does not list conjunction in `safety_properties`. Mutual exclusion is a separate field, not a general CTL parser feature. |
| `||` | UNSUPPORTED | `FORMAT.md` does not list disjunction; no extracted sample uses `||` or `|` in `safety_properties`. |
| `->` | UNSUPPORTED | `FORMAT.md` does not list implication; no extracted sample uses implication. |

## Atomic Propositions

Atomic propositions are string labels attached to states:

```json
"state_machine": {
  "states": ["s0", "s1"],
  "initial": ["s0"],
  "labeling": {
    "s0": ["safe"],
    "s1": ["p1", "violation"]
  },
  "transitions": [["s0", "s1"]]
}
```

Therefore, a domain predicate that needs `&&`, `||`, or `->` can be moved into the adapter/model generation phase as a new state label. The teacher app can then verify the supported shape:

```text
AG(!some_requirement_violation)
```

## JSON Fields

Safety properties:

```json
"safety_properties": [
  "AG(!violation)",
  "EF(main_locked)"
]
```

Mutual exclusion:

```json
"mutual_exclusion": {
  "atom1": "main_locked",
  "atom2": "log_locked"
}
```

`FORMAT.md` says this checks:

```text
AG(!(p1 & p2))
```

This is a dedicated JSON feature. It does not prove that the `safety_properties` parser supports `&` or `&&`.

## Smart EV Mapping Draft

| Requirement | Constraint | Proposed property | Supported by teacher app | Evidence | Limitation |
|---|---|---|---|---|---|
| `REQ-AUTH-01` | `A -> (C && T)` | `AG(!req_auth_01_violation)` | YES if labeled | `AG(!p)` is supported. | Adapter must label `authenticated && (!connected || !token_valid)` as `req_auth_01_violation`. |
| `REQ-AUTH-02` | disconnect clears authentication | `AG(!req_auth_02_violation)` | YES if labeled | `AG(!p)` is supported. | Adapter must label `disconnected && authenticated`. |
| `REQ-SOC-01` | `0 <= SOC <= 100` | `AG(!req_soc_01_violation)` | YES if labeled | `AG(!p)` is supported. | Numeric ranges are not CTL parser syntax; adapter must label SOC out-of-range. |
| `REQ-SOC-02` | full battery stops charging | `AG(!req_soc_02_violation)` | YES if labeled | `AG(!p)` is supported. | Adapter must label `soc_full && charging/power_positive`. |
| `REQ-TEMP-01` | overheat stops charging | `AG(!req_temp_01_violation)` | YES if labeled | `AG(!p)` is supported. | Adapter must label `overheat && charging`. |
| `REQ-PORT-01` | charging implies connected | `AG(!req_port_01_violation)` | YES if labeled | `AG(!p)` is supported. | Adapter must label `charging && !connected`. |
| `REQ-PORT-02` | one vehicle per port | `mutual_exclusion` or `AG(!req_port_02_violation)` | YES if field/label fits | `mutual_exclusion` field and `AG(!p)` are supported. | Built-in mutex is pairwise AP exclusion; one-port-many-vehicles may need an adapter violation label. |
| `REQ-PORT-03` | faulted port delivers no power | `AG(!req_port_03_violation)` | YES if labeled | `AG(!p)` is supported. | Adapter must label `fault && charging/power_positive`. |
| `REQ-CHG-01` | charging requires full safety gate | `AG(!req_chg_01_violation)` | YES if labeled | `AG(!p)` is supported. | Adapter must label `charging && !safety_gate_valid`. |
| `REQ-CHG-02` | safety gate remains valid while charging | `AG(!req_chg_02_violation)` | YES if labeled | `AG(!p)` is supported. | Adapter must label any charging state whose safety gate is false. |
| `REQ-EMG-01` | emergency/fault stops charging and power is zero | `AG(!req_emg_01_violation)` | YES if labeled | `AG(!p)` is supported. | Adapter must label `emergency_or_fault && charging/power_positive`. |

## Conclusion

The extracted format confirms that `AG(a -> b)` should not be used. The viable path is to keep the teacher engine simple and move Smart EV boolean logic into the adapter/state-labeling layer.

For each requirement, generate a requirement-specific violation label and verify:

```text
AG(!req_x_violation)
```

This is compatible with the documented `AG(!p)` syntax and avoids unsupported `&&`, `||`, and `->` inside CTL formulas. This report is only a capability/mapping draft; it does not change teacher specs or integrated verification results.
