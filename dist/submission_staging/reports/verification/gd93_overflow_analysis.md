# GD9.3 — SOC Overflow Finding Analysis

**Finding:** `req_soc_01_overflow_check`
**Z3 result:** `SAT`
**Witness:** `{'soc_current': -1, 'soc_delta': -2147483648}`
**CWE classification:** CWE-190 (Integer Overflow or Wraparound)

## Classification: MISSING_PRECONDITION

**Reason:** The overflow_expr 'soc_current + soc_delta' was declared with int_vars=['soc_current','soc_delta']. Z3 uses unbounded integer domain by default. It found soc_current=-1 and soc_delta=INT32_MIN which satisfies the overflow condition. However, in production Smart EV: (1) soc_current is typed float [0.0, 100.0] bounded by SOC_MIN and SOC_MAX in hang_so.h. (2) co_the_bat_dau_sac() explicitly checks soc < 0.0f -> return 0 (line: 'xe->pin.soc < 0.0f'). (3) SOC is never stored as raw int32 — it is float. int32 overflow is not applicable to float SOC. Therefore: the overflow check is missing the production precondition 0<=soc_current<=100.

## Production Evidence
- File: `src/charging/dieu_khien_sac.c`
- Relevant check: `xe->pin.soc < 0.0f -> return 0`
- Type: float — not int32
- Domain: [0.0, 100.0]

## Corrected Probe (V2)

**Check:** `req_soc_01_overflow_v2_bounded`
**Condition:** `soc_current >= 0 and soc_current <= 100 and soc_delta >= 0 and soc_delta <= 100`
**Overflow expr:** `soc_current + soc_delta`
**Semantics:** With production bounds enforced, soc_current+soc_delta <= 200 which cannot overflow int32 (max ~2.1 billion). Z3 should report OVERFLOW_NOT_DETECTED or the CWE pipeline should produce no CWE-190 finding.

## Original Finding Status
KEEP as evidence — proves Z3 runs and CWE pipeline activates
