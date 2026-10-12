# Final App Run + Explainer + Report - Phase 8

Generated: `2026-09-28T16:12:27.165451+00:00`

## Pipeline

```text
teacher_specs/smart_ev_formal_verification_v2.json
  -> SpecVerificationLab.exe
  -> evidence/formal_verification/teacher_app_result_v2.json
  -> verification/formal_result_explainer.py
  -> reports/verification/formal_explained_result_v2.md
```

## Phase Gates

| Phase | Artifact | Status |
|---:|---|---|
| 1 | `reports/verification/requirement_audit.md` | `PASS` |
| 2 | `reports/verification/coverage_matrix.md` | `PASS` |
| 3 | `reports/verification/boundary_coverage.json` | `PASS` |
| 4 | `reports/verification/full_state_model_v2.json` | `PASS` |
| 5 | `reports/verification/transition_sequence_coverage.json` | `PASS` |
| 6 | `reports/verification/formal_property_suite_v2.json` | `PASS` |
| 7 | `reports/verification/negative_control_selectivity.json` | `PASS` |

## Final Spec

```yaml
Spec: teacher_specs/smart_ev_formal_verification_v2.json
States: 28
Transitions: 47
Properties: 16
```

## Teacher App Result

```yaml
Raw result path: evidence/formal_verification/teacher_app_result_v2.json
Raw result status: PASS
PASS: 16
FAIL: 0
UNKNOWN: 0
```

## Explained Result

Explainer output: `reports/verification/formal_explained_result_v2.md`
Counterexamples: `reports/verification/counterexamples_v2`

## Phase 8 Gate

```yaml
Phase 1-7 gates pass: true
Teacher app raw result present: true
Explainer ran: true
Status: PASS
```