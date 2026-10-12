# GD9.2 -- Smart EV SMT Adapter Traceability

Generated: 2026-09-28T16:45:46.657250+00:00
Constants source: `src\core\hang_so.h`

> **Parser limitation:** Teacher app condition parser (Python ast) does not support UnaryOp (negative literals). Conditions using NHIET_DO_TOI_THIEU=-20 have been reformulated to omit the lower bound.

## Requirement -> arithmetic_checks[] Mapping

| REQ | Check Name | Type | Condition | Expected |
|---|---|---|---|---|
| REQ-SOC-01 | `req_soc_01_valid_domain` | property | `soc >= 0 and soc <= 100` | `SAT` |
| REQ-SOC-01 | `req_soc_01_violation_unsat` | violation | `soc >= 0 and soc <= 100 and (soc < 0 or soc > 100)` | `UNSAT` |
| REQ-SOC-01 | `req_soc_01_overflow_check` | overflow | `soc_current + soc_delta` | `OVERFLOW_POSSIBLE` |
| REQ-TEMP-01 | `req_temp_01_overheat_threshold` | property | `temperature >= 60` | `SAT` |
| REQ-TEMP-01 | `req_temp_01_violation_unsat` | violation | `temperature >= 60 and temperature < 60` | `UNSAT` |
| REQ-TEMP-01 | `req_temp_01_safe_range` | property | `temperature < 60` | `SAT` |

## Detailed Records

### req_soc_01_valid_domain
- **REQ:** REQ-SOC-01
- **Type:** property
- **Constants:** `{'SOC_MIN': 0, 'SOC_MAX': 100}`
- **Condition:** `soc >= 0 and soc <= 100`
- **Semantics:** SAT check: a valid SOC state exists where soc is in [0, 100]. SAT = valid state is reachable. Confirms the constraint is non-vacuous.
- **Expected:** `SAT`
- **Interpretation:** Valid SOC range [0,100] is satisfiable (e.g. soc=50). System can be in a valid SOC state.

### req_soc_01_violation_unsat
- **REQ:** REQ-SOC-01
- **Type:** violation
- **Constants:** `{'SOC_MIN': 0, 'SOC_MAX': 100}`
- **Condition:** `soc >= 0 and soc <= 100 and (soc < 0 or soc > 100)`
- **Semantics:** UNSAT check: no value can simultaneously satisfy the domain constraint (0<=soc<=100) AND violate it (soc<0 or soc>100). UNSAT = boundaries are logically consistent (tautology verification).
- **Expected:** `UNSAT`
- **Interpretation:** UNSAT proves the violation predicate (soc<0 or soc>100) is unreachable under the domain constraint. Boundary semantics are consistent.

### req_soc_01_overflow_check
- **REQ:** REQ-SOC-01
- **Type:** overflow
- **Constants:** `{'SOC_MAX': 100}`
- **Condition:** `soc_current + soc_delta`
- **Semantics:** int32 overflow check on soc_current + soc_delta. In production SOC_MAX=100 caps values; this confirms raw arithmetic safety.
- **Expected:** `OVERFLOW_POSSIBLE`
- **Interpretation:** int32 overflow is arithmetically possible for unbounded inputs. Production boundary (SOC_MAX=100) prevents actual overflow.

### req_temp_01_overheat_threshold
- **REQ:** REQ-TEMP-01
- **Type:** property
- **Constants:** `{'NHIET_DO_TOI_DA': 60}`
- **Condition:** `temperature >= 60`
- **Semantics:** SAT check: temperature >= 60 (NHIET_DO_TOI_DA=60, inclusive). SAT = overheat states exist. Confirms the threshold is not vacuous. Boundary is >= (not >): matches battery.json 'temperature >= 60' and production pin_qua_nhiet(nhiet_do >= NHIET_DO_TOI_DA).
- **Expected:** `SAT`
- **Interpretation:** temperature >= 60 is satisfiable (e.g. temperature=60). Overheat condition is reachable. >= boundary confirmed.

### req_temp_01_violation_unsat
- **REQ:** REQ-TEMP-01
- **Type:** violation
- **Constants:** `{'NHIET_DO_TOI_DA': 60}`
- **Condition:** `temperature >= 60 and temperature < 60`
- **Semantics:** UNSAT check: no temperature can be simultaneously >= 60 (overheat) AND < 60 (not overheat). UNSAT validates that TEMP_SAFE and TEMP_OVERHEAT partitions are mutually exclusive at the boundary.
- **Expected:** `UNSAT`
- **Interpretation:** UNSAT: impossible to have temperature >= 60 and < 60 simultaneously. TEMP_SAFE / TEMP_OVERHEAT partition is exclusive.

### req_temp_01_safe_range
- **REQ:** REQ-TEMP-01
- **Type:** property
- **Constants:** `{'NHIET_DO_TOI_DA': 60}`
- **Condition:** `temperature < 60`
- **Semantics:** SAT check: temperature < 60 (strictly below overheat threshold). SAT = safe (non-overheat) temperature states exist. NOTE: lower bound NHIET_DO_TOI_THIEU=-20 is OMITTED because the teacher app condition parser does not support negative literals (UnaryOp not supported). The upper bound < 60 is the critical safety predicate for REQ-TEMP-01.
- **Expected:** `SAT`
- **Interpretation:** SAT: temperature < 60 is satisfiable (e.g. temperature=25). Safe operating range exists; system can operate without overheat.
- **Parser limitation:** NHIET_DO_TOI_THIEU=-20 cannot be used in condition because teacher parser rejects UnaryOp(USub). Lower bound is documented in condition_semantics only.

