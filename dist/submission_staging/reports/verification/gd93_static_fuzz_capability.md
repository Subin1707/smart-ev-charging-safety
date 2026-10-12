# GD9.3 — Static + Fuzz E2E Analysis

Generated: 2026-09-28T17:12:30.387560+00:00

## Ch2 Static Checker (core.memory_analyzer)

- **Main function:** `check_c_source(c_source: str) -> List[Finding]`
- **Input:** Python string of generated C source
- **External .c supported:** NO
- **Evidence:** check_c_source() takes a plain str parameter. There is no file path input, no API to inject external .c files. Also confirmed: analyze_file(path) exists but is an internal utility that reads from a lo...

**Heuristics confirmed from co_consts:**
  - dangerous-function: strcpy/strcat/strncpy/strncat detection -> HIGH (buffer-overflow CWE-121)
  - format-string: printf/fprintf/sprintf/snprintf/syslog with variable as format arg
  - double-free: pointer freed twice in same function
  - use-after-free: pointer accessed after free()
  - memory-leak: malloc/calloc/realloc with no corresponding free() in function

**Semantic adapter:** token handling -> buffer_copy with buffer_size=DO_DAI_TOKEN(32)
**Fake mapping:** False

## Ch4 Dynamic Fuzzer (core.dynamic_fuzzer)

- **Functions:** blackbox_fuzz, concolic_fuzz, mutation_fuzz
- **Input:** Python callable + arg_types=['int'|'str']
- **External C supported:** NO
- **Supported kinds:** ['divide', 'magic_value']

**Semantic adapter:** charging rate calculation -> divide(energy_kwh, time_hours)
**Fake mapping:** False

## E2E Routes

| Channel | External Production C | Semantic Adapter | CWE Expected |
|---|---|---|---|
| Ch2 Static | NO | YES (buffer_copy for token) | None (safe code) |
| Ch4 Fuzz   | NO | YES (divide for charge rate) | CWE-369 (div-by-zero) |
