# Formal Checker Negative Control

Requirement: `REQ-TEMP-01`

Property: `AG(!req_temp_01_violation)`

Test type: Formal Checker Negative Control

Injected violation: reachable

Expected teacher result: SAI

Actual teacher result: PENDING

## Purpose

This negative-control specification checks whether `SpecVerificationLab.exe` can detect a reachable CTL violation instead of always returning `DUNG`.

The original formal verification spec is not modified:

```text
teacher_specs/smart_ev_formal_verification.json
```

The negative-control spec is:

```text
teacher_specs/smart_ev_formal_negative_test.json
```

## Injection

Only one formal-model change is injected: a reachable state labeled with `req_temp_01_violation`.

The property remains unchanged:

```text
AG(!req_temp_01_violation)
```

Injected state:

```text
injected_req_temp_01_violation
```

Reachable path:

```text
ok_0000 -> injected_req_temp_01_violation
```

## Validation

- JSON is valid.
- Initial state exists: `ok_0000`.
- Injected state exists: `injected_req_temp_01_violation`.
- Injected state has label: `req_temp_01_violation`.
- A path exists from initial state to injected state.
- Property remains: `AG(!req_temp_01_violation)`.

## Expected Interpretation

When loaded into `SpecVerificationLab.exe`, this negative-control model should make `AG(!req_temp_01_violation)` fail because a reachable state contains `req_temp_01_violation`.

The expected result is `SAI`. The actual teacher-app result is intentionally left as `PENDING` until the app is run.
