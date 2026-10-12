"""Generate small CBMC C harnesses and Z3 counterexample scripts from IR."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .code_mapping import load_code_mapping, mapping_for_variables


def _identifier(value: str) -> str:
    identifier = re.sub(r"[^a-zA-Z0-9_]", "_", value)
    return identifier if identifier and not identifier[0].isdigit() else f"value_{identifier}"


def _literal(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _c_literal(value: Any) -> str:
    if isinstance(value, int):
        return f"{value}.0f"
    if isinstance(value, float):
        rendered = f"{value:.6g}"
        if "." not in rendered:
            rendered += ".0"
        return f"{rendered}f"
    return str(value)


def _is_symbolic(expression: dict[str, Any]) -> bool:
    return expression.get("value_type") in ("enum", "boolean") or isinstance(expression.get("value"), str)


def _c_condition(expression: dict[str, Any], variable: str | None = None) -> str:
    name = variable or _identifier(str(expression["variable"]))
    value = expression["value"]
    if expression.get("value_type") == "boolean":
        rendered = "true" if value else "false"
    elif expression.get("value_type") == "enum":
        rendered = _identifier(str(value))
    else:
        rendered = _c_literal(value)
    return f"{name} {expression['operator']} {rendered}"


def _mapping_comments(ir: dict[str, Any], mapping: dict[str, dict[str, str]] | None) -> str:
    if not mapping:
        return "/* Mode: standalone verification model; no production mapping supplied. */\n"
    expected = _as_node(ir.get("expected", []))
    variables = {str(expression["variable"]) for expression in _leaves(expected)}
    if ir.get("trigger"):
        variables.update(str(expression["variable"]) for expression in _leaves(ir["trigger"]))
    selected = mapping_for_variables(variables, mapping)
    lines = ["/* Mode: mapping-aware harness scaffold; production objects are not guessed. */"]
    for variable in sorted(variables):
        entry = selected.get(variable)
        if entry:
            access = entry.get("access", {})
            symbol = entry.get("symbol") or access.get("symbol") or f"{access.get('object', '')}{access.get('member_operator', '.')}{access.get('field', '')}"
            lines.append(f"/* {variable} -> {symbol} ({entry['source']}) */")
        else:
            lines.append(f"/* {variable} -> UNMAPPED; standalone nondeterministic value retained */")
    return "\n".join(lines) + "\n"


def _as_node(value: Any) -> dict[str, Any]:
    if isinstance(value, list):
        return value[0] if len(value) == 1 else {"logic": "AND", "conditions": value}
    return value


def _leaves(node: dict[str, Any]) -> list[dict[str, Any]]:
    if "logic" in node:
        if node["logic"] == "NOT":
            return _leaves(node["condition"])
        return [leaf for child in node["conditions"] for leaf in _leaves(child)]
    return [node]


def generate_c_expression(node: dict[str, Any]) -> str:
    """Render a leaf or logic node as a C boolean expression."""
    if "logic" not in node:
        return _c_condition(node)
    logic = node["logic"]
    if logic == "NOT":
        return f"!({generate_c_expression(node['condition'])})"
    operator = " && " if logic == "AND" else " || "
    return "(" + operator.join(generate_c_expression(child) for child in node["conditions"]) + ")"


def _state_declarations(states: list[str]) -> str:
    values = ",\n".join(f"    {_identifier(state)}" for state in states)
    return f"typedef enum {{\n    ENUM_UNKNOWN = 0,\n{values}\n}} GeneratedState;\n"


def generate_sequence_model(ir: dict[str, Any]) -> str:
    states = ir["states"]
    transitions = ir.get("transitions", [{"from": a, "to": b} for a, b in zip(states, states[1:])])
    checks = "\n".join(
        f"    if (from == {_identifier(item['from'])} && to == {_identifier(item['to'])}) return 1;"
        for item in transitions
    )
    return f'''#include <assert.h>

{_state_declarations(states)}
int valid_transition(GeneratedState from, GeneratedState to)
{{
{checks}
    return 0;
}}

int main(void)
{{
    GeneratedState from = ENUM_UNKNOWN;
    GeneratedState to = ENUM_UNKNOWN;
    (void)from;
    (void)to;
    return 0;
}}
'''


def generate_ordering_model(ir: dict[str, Any]) -> str:
    before = _identifier(ir["before"])
    after = _identifier(ir["after"])
    return f'''#include <assert.h>
#include <stdbool.h>

extern bool nondet_bool(void);

int main(void)
{{
    bool {before} = nondet_bool();
    bool {after} = nondet_bool();
    if ({after}) assert({before});
    return 0;
}}
'''


def generate_cbmc(ir: dict[str, Any], mapping: dict[str, dict[str, str]] | None = None) -> str:
    """Return a CBMC harness that asserts the IR property."""
    if ir.get("verifiable") is False:
        raise ValueError("Cannot generate static code for an unverifiable requirement")
    if ir.get("property_type") == "sequence":
        return generate_sequence_model(ir)
    if ir.get("property_type") == "ordering":
        return generate_ordering_model(ir)
    if ir.get("property_type") == "transition":
        states = [ir["from"], ir["to"]]
        return generate_sequence_model({"states": states, "transitions": [{"from": states[0], "to": states[1]}]})

    expected_node = _as_node(ir["expected"])
    trigger_node = ir.get("trigger")
    expected_leaves = _leaves(expected_node)
    trigger_leaves = _leaves(trigger_node) if trigger_node else []
    expressions = expected_leaves + trigger_leaves
    variables = {str(expression["variable"]) for expression in expressions}
    enum_variables = {
        str(expression["variable"])
        for expression in expressions
        if expression.get("value_type") == "enum"
    }
    boolean_variables = {
        str(expression["variable"])
        for expression in expressions
        if expression.get("value_type") == "boolean"
    }
    declarations = "\n".join(
        f"    {'GeneratedEnum' if variable in enum_variables else 'bool' if variable in boolean_variables else 'float'} {_identifier(variable)} = "
        f"{'nondet_enum()' if variable in enum_variables else 'nondet_bool()' if variable in boolean_variables else 'nondet_float()'};"
        for variable in sorted(variables)
    )
    assumptions = "\n".join(
        f"    __CPROVER_assume({_identifier(variable)} >= 0.0f);"
        for variable in sorted(variables)
        if variable not in enum_variables and variable not in boolean_variables
    )
    assertion = f"assert({generate_c_expression(expected_node)});"
    if trigger_node:
        trigger = generate_c_expression(trigger_node)
        body = f"    if ({trigger}) {{\n        {assertion}\n    }}"
    else:
        body = f"    {assertion}"
    constants = sorted({
        str(expression["value"])
        for expression in expressions
        if expression.get("value_type") == "enum"
    })
    constant_definitions = (
        "typedef enum {\n    ENUM_UNKNOWN = 0,\n"
        + ",\n".join(f"    {_identifier(constant)}" for constant in constants)
        + "\n} GeneratedEnum;\n"
        if constants else ""
    )
    includes = "#include <stdbool.h>\n" if boolean_variables else ""
    return _mapping_comments(ir, mapping) + includes + constant_definitions + ("\n" if constant_definitions else "") + f"""#include <assert.h>

extern float nondet_float(void);
""" + ("extern bool nondet_bool(void);\n" if boolean_variables else "") + ("extern GeneratedEnum nondet_enum(void);\n" if enum_variables else "") + f"""

int main(void)
{{
{declarations}

{assumptions}

{body}

    return 0;
}}
"""


def _z3_constraint(expression: dict[str, Any], negate: bool = False) -> str:
    operator = expression["operator"]
    if negate:
        operator = {"<": ">=", "<=": ">", ">": "<=", ">=": "<", "==": "!=", "!=": "=="}[operator]
    variable = _identifier(str(expression["variable"]))
    return f"{variable} {operator} {_literal(expression['value'])}"


def generate_z3(ir: dict[str, Any], mapping: dict[str, dict[str, str]] | None = None) -> str:
    """Return a Z3 script that searches for a counterexample to the IR."""
    if ir.get("verifiable") is False:
        raise ValueError("Cannot generate static code for an unverifiable requirement")
    expected = _as_node(ir["expected"])
    trigger = ir.get("trigger")
    expressions = _leaves(expected) + (_leaves(trigger) if trigger else [])
    types = {leaf["variable"]: leaf.get("value_type", "number") for leaf in expressions}
    declarations = "\n".join(f'{_identifier(v)} = {"Bool" if t == "boolean" else "Int" if t == "enum" else "Real"}("{v}")' for v, t in sorted(types.items()))
    constants = sorted({str(e["value"]) for e in expressions if e.get("value_type") == "enum"})
    definitions = "\n".join(f"{_identifier(c)} = {i}" for i, c in enumerate(constants, 1))

    def render(node):
        node = _as_node(node)
        if "logic" in node:
            if node["logic"] == "NOT":
                return f"Not({render(node['condition'])})"
            return ("And" if node["logic"] == "AND" else "Or") + "(" + ", ".join(render(c) for c in node["conditions"]) + ")"
        return _z3_constraint(node)

    constraints = [f"s.add({_identifier(v)} >= 0)" for v, t in sorted(types.items()) if t == "number"]
    if trigger:
        constraints.append(f"s.add({render(trigger)})")
    # Negate the whole conjunction: violating either range bound is a counterexample.
    constraints.append(f"s.add({ _z3_constraint(expected, negate=True) if 'logic' not in expected else 'Not(' + render(expected) + ')' })")
    comments = _mapping_comments(ir, mapping).replace("/*", "#").replace("*/", "")
    return comments + "from z3 import Bool, Int, Real, Solver, And, Or, Not\n\n" + definitions + "\n" + declarations + "\n\ns = Solver()\n" + "\n".join(constraints) + "\n\nprint(s.check())\n"



def _filename(requirement_id: Any, suffix: str) -> str:
    safe_id = re.sub(r"[^a-zA-Z0-9]+", "_", str(requirement_id)).strip("_")
    return f"{safe_id}_{suffix}"


def write_static_artifacts(
    ir: dict[str, Any],
    output_dir: str | Path = "generated/static",
    mapping_path: str | Path | None = None,
) -> list[Path]:
    """Write CBMC and Z3 artifacts and return their paths."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    requirement_id = ir.get("requirement_id", "requirement")
    mapping = load_code_mapping(mapping_path) if mapping_path else None
    cbmc_path = destination / f"{_filename(requirement_id, 'cbmc')}.c"
    z3_path = destination / f"{_filename(requirement_id, 'z3')}.py"
    cbmc_path.write_text(generate_cbmc(ir, mapping), encoding="utf-8")
    if not ir.get("expected"):
        return [cbmc_path]
    z3_path.write_text(generate_z3(ir, mapping), encoding="utf-8")
    return [cbmc_path, z3_path]
