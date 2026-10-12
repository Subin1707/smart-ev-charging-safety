# Teacher Code Generation Capability - Phase 7.5-A

Purpose: reverse-engineer the code-generation schema actually exposed by `SpecVerificationLab.exe` from the extracted app documentation and sample specifications before building a Smart EV code-generation adapter.

Sources inspected:

- `teacher_app/extracted_static/dataset/specs/FORMAT.md`
- `teacher_app/extracted_static/dataset/specs_excel/FORMAT_EXCEL.md`
- `teacher_app/extracted_static/dataset/specs/session_manager_spec.json`
- `teacher_app/extracted_static/dataset/specs/session_manager_fixed_spec.json`
- `teacher_app/extracted_static/dataset/specs/resource_pool_spec.json`
- `teacher_app/extracted_static/dataset/specs/iot_gateway_spec.json`
- `teacher_app/extracted_static/dataset/specs/auth_rate_limit_spec.json`
- `teacher_app/extracted_static/dataset/specs/file_upload_auth_spec.json`
- `teacher_app/extracted_static/dataset/specs/elevator_control_spec.json`

## Supported Language

| Language | Status | Evidence |
|---|---|---|
| C | DOCUMENTED + OBSERVED | `FORMAT.md` documents C `FunctionSpec`; extracted JSON samples use `language: "c"`. |
| Python | DOCUMENTED + OBSERVED | `FORMAT.md` documents Python `FunctionSpec`; extracted JSON samples use `language: "python"`. |

## Supported Code-Generation Sections

| Section | Role | Status |
|---|---|---|
| `functions[]` | Drives Ch2 code generation for C/Python functions. | DOCUMENTED + OBSERVED |
| `arithmetic_checks[]` | Drives Ch3 SMT/overflow checks, not ordinary C code generation. | DOCUMENTED + OBSERVED |
| `state_machine` | Drives Ch1 Kripke/CTL, not C function generation. | DOCUMENTED + OBSERVED |
| `requirements[]` | Documentation/traceability; does not itself generate C without `functions[]`. | DOCUMENTED |
| `test_cases[]` | Optional documentation/test metadata in some samples; no evidence it generates C. | OBSERVED OPTIONAL |

## FunctionSpec Schema

Minimal JSON shape documented in `FORMAT.md`:

```json
{
  "name": "function_name",
  "language": "c",
  "kind": "buffer_copy",
  "params": ["input"],
  "buffer_size": 16,
  "bug": null,
  "magic_values": [1234, 5678]
}
```

## Required Fields

| Field | Required When | Notes |
|---|---|---|
| `name` | all `functions[]` entries | Function identifier to generate. |
| `language` | all `functions[]` entries | Observed values: `c`, `python`. |
| `kind` | all `functions[]` entries | Selects generator template. |
| `params` | all observed entries | For C `alloc_release`, samples use `[]`. |

## Optional / Kind-Specific Fields

| Field | Used By | Notes |
|---|---|---|
| `buffer_size` | C `buffer_copy`, C `alloc_release` | Defaults are mentioned in Excel docs, but JSON samples provide it explicitly. |
| `bug` | C `buffer_copy`, C `alloc_release` | `null` means safe variant where supported. |
| `magic_values` | Python `magic_value` | Two values, used as target branch constants. |

## Supported Kinds

| Language | Kind | Documentation Status | JSON Sample Evidence | Generated Construct |
|---|---|---|---|---|
| C | `buffer_copy` | DOCUMENTED | OBSERVED | Fixed-size local char buffer; unsafe `strcpy()` if `bug: "buffer-overflow"`, safe `strncpy()` if `bug: null`. |
| C | `alloc_release` | DOCUMENTED | OBSERVED | `malloc()`/`free()` pattern; bug variants include leak, double-free, use-after-free, or safe `null`. |
| C | `arithmetic` | DOCUMENTED | NOT OBSERVED IN JSON SAMPLES | Simple arithmetic C function; mentioned in `FORMAT.md` and Excel docs, but absent from extracted JSON samples inspected. Treat as documented but lower-confidence until tested in app. |
| Python | `divide` | DOCUMENTED | OBSERVED | Python integer division function for black-box fuzzing. |
| Python | `magic_value` | DOCUMENTED | OBSERVED | Python branch on secret values for concolic/white-box fuzzing. |

## Supported Bug Values

| Kind | Supported `bug` values | Evidence |
|---|---|---|
| `buffer_copy` | `buffer-overflow`, `null` | `session_manager_spec.json`, `session_manager_fixed_spec.json`, `FORMAT.md`. |
| `alloc_release` | `memory-leak`, `double-free`, `use-after-free`, `null` | `iot_gateway_spec.json`, `resource_pool_spec.json`, `elevator_control_spec.json`, `FORMAT.md`. |

## Generated Constructs

Documented/observed generated constructs are template-driven:

- C string-copy wrapper around a fixed-size buffer.
- C allocation/release wrapper around `malloc()`/`free()`.
- C arithmetic wrapper, documented but not observed in JSON samples.
- Python integer division function.
- Python magic-value branch function.

## Unsupported / Not Proven

No inspected source proves support for:

- Generating arbitrary Smart EV production-like C logic directly from `state_machine`.
- Generating C `struct` models for vehicles, ports, batteries, or charging stations.
- Generating C functions with custom boolean formulas such as `charging_allowed = connected && authenticated && ...`.
- Linking `requirements[]` to generated C unless a matching `functions[]` entry exists.
- Treating teacher-generated C as equivalent to existing production C.

## Consequence For Smart EV

The Smart EV code-generation adapter must not pretend that teacher-generated C is production C.

Correct interpretation:

1. Production C: the real Smart EV implementation under `src/`.
2. Teacher-generated C: a Ch2 artifact generated by `SpecVerificationLab.exe` from `functions[]`.
3. Verification harnesses: C harnesses under `verification/harness/` used to validate production C.

The Ch2 goal is therefore:

```text
Smart EV specification -> app teacher code-generation schema -> non-placeholder generated artifact -> compile/traceability/semantic inspection
```

not:

```text
Teacher-generated C == production implementation
```

## Risk For Smart EV Adapter

Smart EV semantics are mostly boolean/numeric safety predicates, not string-copy or memory-management requirements. The documented Ch2 schema is template-based and memory/fuzz oriented. Therefore:

- Using `buffer_copy` or `alloc_release` for every Smart EV requirement would be misleading.
- A C `arithmetic` function may be the only documented C kind close to numeric Smart EV checks, but it is not observed in extracted JSON samples and must be app-tested before relying on it.
- If the teacher app cannot generate boolean safety-gate C directly, the adapter should report that limitation instead of fabricating IoT/session-manager style functions.

## Phase 7.5-A Gate

```yaml
Schema source inspected: YES
functions[] schema identified: YES
Supported languages identified: YES
Supported kinds identified: YES
Unsupported constructs identified: YES
Do not use fake IoT/session functions: YES
Status: PASS
```
