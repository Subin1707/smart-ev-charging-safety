# Specification input generator

Stage 1 converts a `.xlsx`, `.csv`, or `.txt` file into
`spec_generator/output/requirements_raw.json`.

Every non-empty row must provide these headers (case-insensitive):

```text
ID | Type | Priority | Content
```

Example:

```text
REQ-01 | safety | HIGH | Total power must not exceed 100 kW.
REQ-02 | safety | HIGH | SOC must remain between 0 and 100%.
```

Run from the repository root:

```powershell
python -m spec_generator.generate_requirements path\to\requirements.txt
```

The parser only normalizes the supplied fields. It does not require users to
provide implementation constants such as `POWER_LIMIT` or `OVERHEAT`.

## Stage 2: analysis and IR

Use `spec_generator.core.spec_reader.read_requirements` to read normalized
requirements, then `spec_generator.core.analyzer.analyze_requirements` to
produce the common intermediate representation (IR). Verifiable invariants
and conditionals contain variables, operators, values, units, triggers, and
expected results. Requirements without measurable acceptance criteria are
returned with `verifiable: false` and are never converted into invented
assertions.

## Code mapping

`spec_generator/input/code_mapping.json` is an explicit, reviewed mapping
from IR variables to production symbols. The loader validates that each entry
has `source` and `symbol`, and can report whether the source file exists. It
does not infer mappings from source code.

Static artifacts are standalone models by default. Passing the mapping to
`write_static_artifacts` adds the reviewed production symbol and source path as
metadata, producing a mapping-aware harness scaffold. A true production
harness still requires an agreed C entry point and object initialization; the
generator does not pretend that a field mapping alone proves that integration.

## Stage 5: verification pipeline

Run the build and available checks from the repository root:

```powershell
python -m spec_generator.pipeline spec_generator/input/requirements_example.txt
```

The pipeline writes evidence to
`evidence/generation/verification.json`. It performs C syntax compilation,
Cppcheck, CBMC when installed, Python/Z3 execution, and generated pytest
boundary tests. Missing tools are reported as `UNAVAILABLE`; a Z3
`SAT_COUNTEREXAMPLE` or failed compile makes the command fail. This prevents a
standalone model from being reported as a production proof before its harness
has production initialization and entry-point contracts.

The same pipeline writes traceability artifacts:

- `evidence/generation/requirements_raw.json`
- `evidence/generation/requirements_ir.json`
- `evidence/generation/manifest.json`
- `evidence/summary.json`
- `evidence/generation/counterexamples/` for failed Z3 checks

The generic demonstration input is
`spec_generator/input/generic_example.txt`. It covers pressure and a symbolic
valve state, proving the analyzer is not limited to Smart EV variable names.