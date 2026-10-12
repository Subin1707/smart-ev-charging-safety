# GD9.1 — Teacher E2E Pipeline Capability

Generated: 2026-09-28T16:33:52.798323+00:00

## E2E Pipeline (Reconstructed from FORMAT.md)

```
Spec (JSON/Excel)
   |
   +-- state_machine + safety_properties
   |      -> Ch1: Kripke + CTL model checker
   |      -> CWE-833 (deadlock), CTL violations
   |
   +-- functions[language='c', kind='buffer_copy'/'alloc_release']
   |      -> Ch2: static memory analyzer (heuristic)
   |      -> CWE-121/401/415/416
   |
   +-- functions[language='c', kind='arithmetic']
   |      -> Ch3: AST extraction -> Z3 arithmetic check
   |
   +-- arithmetic_checks[condition='x >= 0 and x <= N']
   |      -> Ch3: DIRECT Z3 SAT/UNSAT check (range/comparison supported)
   |      -> CWE-190 (overflow via overflow_expr)
   |
   +-- functions[language='python', kind='divide'/'magic_value']
          -> Ch4: black-box / concolic fuzzer
          -> CWE-369
```

## Key Finding: functions[] is NOT mandatory

> Each chapter runs independently. If `functions=[]`, Ch2/Ch3/Ch4 are skipped.
> `arithmetic_checks[]` is a **direct Z3 path** independent of `functions[]`.
> This means: numeric Smart EV requirements (SOC range, TEMP threshold) can be
> fed to Z3 via `arithmetic_checks[].condition` WITHOUT needing functions[].

## CodeGen Kinds (functions[])

| Kind | Language | Description | CWE |
|---|---|---|---|
| `buffer_copy` | `c` | Generates strcpy (with bug) or strncpy (safe) into fixed buf | CWE-121 (Stack-based Buffer Overflow) |
| `alloc_release` | `c` | Generates malloc/free pair with optional memory bug. | CWE-401/415/416 |
| `arithmetic` | `c` | Generates int fn(int a, int b) { return a + b; } | None (used for AST extraction only) |
| `divide` | `python` | Generates def fn(a, b): return a // b — black-box fuzz targe | CWE-369 (Divide by Zero) if fuzzer finds b=0 |
| `magic_value` | `python` | Generates Python function with nested if checking two magic  | CWE-327 / hard-coded magic value detection |

## arithmetic_checks[] — Direct Z3 SAT Checker

- Supports comparison operators in `condition`: YES
- Supports range expressions: YES  (e.g. `soc >= 0 and soc <= 100`)
- Supports overflow check: YES  (`overflow_expr` field)

## Static Checker

- Input: Generated C from functions[] only
- Accepts external .c files: **NO**
- Rules: strcpy -> buffer-overflow (CWE-121), malloc without free -> memory-leak (CWE-401) ...

## Smart EV Requirement Compatibility

| REQ | Support | Adapter Path |
|---|---|---|
| REQ-AUTH-01 | **ADAPTER_POSSIBLE** | Kripke model (Ch1) with violation labeling — already done in V2 |
| REQ-AUTH-02 | **ADAPTER_POSSIBLE** | Kripke model (Ch1) |
| REQ-SOC-01 | **DIRECTLY_SUPPORTED** | arithmetic_checks[] with condition='soc >= 0 and soc <= 100' |
| REQ-SOC-02 | **ADAPTER_POSSIBLE** | arithmetic_checks[] condition='soc >= 100' OR Kripke Ch1 model |
| REQ-TEMP-01 | **DIRECTLY_SUPPORTED** | arithmetic_checks[] with int_vars=['temperature','limit'], condition=' |
| REQ-PORT-01 | **ADAPTER_POSSIBLE** | Kripke model (Ch1) — already done |
| REQ-PORT-02 | **ADAPTER_POSSIBLE** | mutual_exclusion field OR Kripke violation label |
| REQ-PORT-03 | **ADAPTER_POSSIBLE** | Kripke model Ch1 OR arithmetic_checks condition |
| REQ-CHG-01 | **ADAPTER_POSSIBLE** | Kripke model Ch1 — charging state only reachable from valid preconditi |
| REQ-CHG-02 | **ADAPTER_POSSIBLE** | Kripke model — validity gate as composite label |
| REQ-EMG-01 | **ADAPTER_POSSIBLE** | Kripke model Ch1 — already done in V2 |

**Total       : 11**
**Directly supported : 2** (REQ-SOC-01, REQ-TEMP-01)
**Adapter possible   : 9**
**Unsupported        : 0**

## Next Action

**GD9.2 Path:**

```
arithmetic_checks[] path (Z3 direct):
  REQ-SOC-01: condition='soc >= 0 and soc <= 100'
  REQ-TEMP-01: condition='temperature >= 60 and temperature > limit'
  -> Feed real threshold values from src/core/hang_so.h (SOC_MAX=100, NHIET_DO_TOI_DA=60)

Kripke path (Ch1) already done for all 11 REQ in V2.

Ch2/Ch4 (memory/fuzz): Not applicable to Smart EV safety requirements.
```
