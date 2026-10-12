# GĐ7.5-D — Teacher CodeGen: Compile + Semantic Validation

Generated : 2026-09-28T16:06:45.718015+00:00

## Teacher CodeGen Capability

```
Teacher CodeGen Capability
──────────────────────────────────
C arithmetic runtime            CONFIRMED
Generated C                     YES
Generated C compile             PASS

Smart EV requirements           2
Direct semantic support          0
Unsupported                     2
Fake mappings                    0
Semantic mismatches              0  (note: no fake mappings were inserted)

Teacher CodeGen Compatibility   LIMITED
```

> **Note:** 'Semantic mismatches: 0' means no incorrect mappings were inserted
> into the official spec. It does NOT mean arithmetic matches the requirements.

## Per-Requirement Analysis

### REQ-SOC-01

- Teacher kind    : `c/arithmetic`
- Runtime support : `CONFIRMED`
- Compilation     : `PASS`
- Semantic match  : `NO`
- Status          : **UNSUPPORTED**

**Generated function:**
```c
probe_soc_delta(...) { return soc + soc_max; }
```

**Required semantics:**
```c
// Function must be a range predicate: returns true(1) when 0 <= soc <= soc_max, false(0) otherwise.
return (soc >= 0) && (soc <= soc_max);
```

**Reason:** Generated function computes soc + soc_max (addition). This is an arithmetic expression, NOT a range check. It does not evaluate whether soc is within [0, soc_max]. For example, soc=-10 and soc_max=100 returns 90 (truthy), but -10 is outside the valid range. The requirement is UNSUPPORTED by the generated code.

**Negative-control test:** SEMANTIC_MISMATCH_CONFIRMED
> Verify that generated function incorrectly passes invalid SOC=-10
> Generated result: `-10 + 100 = 90  (truthy -> function says SOC is valid)`
> Correct result  : `(-10 >= 0) && (-10 <= 100) = 0  (false -> SOC is INVALID)`

### REQ-TEMP-01

- Teacher kind    : `c/arithmetic`
- Runtime support : `CONFIRMED`
- Compilation     : `PASS`
- Semantic match  : `NO`
- Status          : **UNSUPPORTED**

**Generated function:**
```c
probe_temperature_delta(...) { return temperature + temperature_limit; }
```

**Required semantics:**
```c
// Function must be a threshold predicate: returns true(1) when temperature <= temperature_limit (safe), false(0) when overheating.
return temperature <= temperature_limit;
```

**Reason:** Generated function computes temperature + temperature_limit (addition). This returns a raw numeric sum, NOT a safety predicate. For example, temperature=70 and temperature_limit=60 returns 130 (truthy), but 70 > 60 means the temperature is UNSAFE and charging must stop. The function will never return 0 for any positive inputs, meaning it can never signal 'stop charging'. The requirement is UNSUPPORTED by the generated code.

**Negative-control test:** SEMANTIC_MISMATCH_CONFIRMED
> Verify that generated function incorrectly passes overheat temperature=70
> Generated result: `70 + 60 = 130  (truthy -> function says temperature is safe)`
> Correct result  : `(70 <= 60) = 0  (false -> temperature is UNSAFE, stop charging)`

