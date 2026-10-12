# Specification Verification Report

## Summary

Total Requirements: 3

- PASS: 1
- FAIL: 1
- INCONCLUSIVE: 1
- NOT_MAPPED: 0
- NOT_VERIFIABLE: 0

## Coverage

- specification: 100.0%
- generation: 100.0%
- production_mapping: 100.0%
- verification: 100.0%

## SR10

**Result:** INCONCLUSIVE

**Specification:** total_power <= 100 AND port_power <= 22

**Property:** `invariant`
**Production mapping:** `MAPPED`

**Reason:** CBMC_TIMEOUT

### Evidence

- `evidence/static/cbmc/SR10_cbmc.c`
- `evidence/static/z3/SR10_z3.py`
- `evidence/dynamic/boundary/test_SR10.py`
- `evidence/production/SR10_production_cbmc.c`
- `evidence/generation/SR10_execution.json`

## SR03

**Result:** FAIL

**Specification:** If temperature >= 60 C AND charging == true, then power == 0 AND state == FAULT.

**Property:** `conditional`
**Production mapping:** `MAPPED`

**Reason:** PRODUCTION_MODEL_LIMITATION

### Counterexample

```text
["file C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/stddef.h line 18 function _CRTIMP: syntax error before 'extern'\n"]
```

### Evidence

- `evidence/static/cbmc/SR03_cbmc.c`
- `evidence/static/z3/SR03_z3.py`
- `evidence/dynamic/boundary/test_SR03.py`
- `evidence/dynamic/fuzz/fuzz_SR03.c`
- `evidence/production/SR03_production_cbmc.c`
- `evidence/generation/SR03_execution.json`

## SR09

**Result:** PASS

**Specification:** 0 <= SOC <= 100

**Property:** `range`
**Production mapping:** `MAPPED`

### Evidence

- `evidence/static/cbmc/SR09_cbmc.c`
- `evidence/static/z3/SR09_z3.py`
- `evidence/dynamic/boundary/test_SR09.py`
- `evidence/production/SR09_production_cbmc.c`
- `evidence/generation/SR09_execution.json`
