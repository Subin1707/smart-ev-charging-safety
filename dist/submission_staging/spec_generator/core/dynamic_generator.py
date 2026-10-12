"""Generate boundary-value pytest cases from requirement IR."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def boundary_values(expression: dict[str, Any], fractional: bool = False) -> list[tuple[int | float, bool]]:
    """Return values immediately below, at, and above a numeric boundary."""
    value = expression["value"]
    if isinstance(value, str):
        return [("OPEN", False), (value, True), ("UNKNOWN", False)]
    step = 0.1 if fractional or isinstance(value, float) else 1
    operator = expression["operator"]
    if operator == "<=" :
        return [(value - step, True), (value, True), (value + step, False)]
    if operator == "<":
        return [(value - step, True), (value, False), (value + step, False)]
    if operator == ">=":
        return [(value - step, False), (value, True), (value + step, True)]
    if operator == ">":
        return [(value - step, False), (value, False), (value + step, True)]
    if operator == "==":
        return [(value - step, False), (value, True), (value + step, False)]
    if operator == "between" and isinstance(value, list) and len(value) == 2:
        lower, upper = value
        return [
            (lower - step, False), (lower, True), (lower + step, True),
            (upper - step, True), (upper, True), (upper + step, False),
        ]
    raise ValueError(f"Unsupported boundary operator: {operator}")


def range_boundary_values(expressions: list[dict[str, Any]]) -> list[tuple[int | float, bool]]:
    """Return boundary cases for a two-sided inclusive numeric range."""
    lower, upper = expressions
    step = 0.1
    return [
        (lower["value"] - step, False),
        (lower["value"], True),
        (lower["value"] + step, True),
        (upper["value"] - step, True),
        (upper["value"], True),
        (upper["value"] + step, False),
    ]


def _logic_leaves(node: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(node, list):
        return [leaf for item in node for leaf in _logic_leaves(item)]
    if "logic" not in node:
        return [node]
    if node["logic"] == "NOT":
        return _logic_leaves(node["condition"])
    return [leaf for item in node["conditions"] for leaf in _logic_leaves(item)]


def _python_expression(node: dict[str, Any] | list[dict[str, Any]]) -> str:
    if isinstance(node, list):
        node = node[0] if len(node) == 1 else {"logic": "AND", "conditions": node}
    if "logic" not in node:
        value = repr(node["value"])
        return f"{node['variable']} {node['operator']} {value}"
    if node["logic"] == "NOT":
        return f"not ({_python_expression(node['condition'])})"
    operator = " and " if node["logic"] == "AND" else " or "
    return "(" + operator.join(_python_expression(child) for child in node["conditions"]) + ")"


def _truth_values(expression: dict[str, Any]) -> tuple[Any, Any]:
    value = expression["value"]
    if expression.get("value_type") == "boolean":
        return False, True
    if expression.get("value_type") == "enum":
        return "__OTHER__", value
    if expression["operator"] in (">", ">="):
        return (value, value + 0.1) if expression["operator"] == ">" else (value - 0.1, value)
    return (value, value + 0.1) if expression["operator"] == "<" else (value + 0.1, value)


def generate_boundary_test(ir: dict[str, Any]) -> str:
    """Return a pytest module for the first expected numeric expression."""
    if ir.get("verifiable") is False:
        raise ValueError("Cannot generate dynamic code for an unverifiable requirement")
    test_id = re.sub(r"[^a-zA-Z0-9_]", "_", str(ir.get("requirement_id", "requirement")))
    if ir.get("property_type") == "sequence":
        states = ir["states"]
        expected = repr(states)
        invalid = repr([states[0], states[-1]]) if len(states) > 2 else repr([states[-1], states[0]])
        return f'''def follows_sequence(history):
    expected = {expected}
    position = 0
    for state in history:
        if position < len(expected) and state == expected[position]:
            position += 1
    return position == len(expected)


def test_{test_id}_sequence():
    assert follows_sequence({expected})
    assert follows_sequence({repr(states[:-1] + [states[-1], states[-1]])})
    assert not follows_sequence({invalid})
'''
    if ir.get("property_type") == "ordering":
        before = repr(ir["before"])
        after = repr(ir["after"])
        return f'''def ordering_holds(before, after):
    return not after or before


def test_{test_id}_ordering():
    assert ordering_holds(False, False)
    assert ordering_holds(True, False)
    assert ordering_holds(True, True)
    assert not ordering_holds(False, True)
'''
    if ir.get("property_type") == "transition":
        source = repr(ir["from"])
        target = repr(ir["to"])
        return f'''def valid_transition(source, target):
    return source == {source} and target == {target}


def test_{test_id}_transition():
    assert valid_transition({source}, {target})
    assert not valid_transition({target}, {source})
'''
    expected_items = ir["expected"] if isinstance(ir.get("expected"), list) else _logic_leaves(ir["expected"])
    expression = expected_items[0]
    variable = re.sub(r"[^a-zA-Z0-9_]", "_", str(expression["variable"]))
    test_id = re.sub(r"[^a-zA-Z0-9_]", "_", str(ir.get("requirement_id", "requirement")))
    if ir.get("property_type") == "conditional":
        trigger = ir["trigger"]
        expected_node = ir["expected"]
        trigger_leaves = _logic_leaves(trigger)
        variables = [str(leaf["variable"]) for leaf in trigger_leaves]
        if len(trigger_leaves) == 1:
            leaf = trigger_leaves[0]
            boundary_cases = boundary_values(leaf, fractional=True)
            rendered = ",\n".join(f"        ({value!r}, {result!r})" for value, result in boundary_cases)
            arguments = variables[0]
            expected_expr = _python_expression(expected_node)
            expected_leaves = _logic_leaves(expected_node)
            expected_arguments = [str(item["variable"]) for item in expected_leaves]
            wrong_values = []
            for item in expected_leaves:
                value = item["value"]
                wrong_values.append(not value if isinstance(value, bool) else "__VIOLATION__" if isinstance(value, str) else value + 1)
            violation_call = ", ".join([repr(leaf["value"]) for leaf in expected_leaves])
            wrong_call = ", ".join(repr(value) for value in wrong_values)
            return f'''def trigger_holds({arguments}):
    return {_python_expression(trigger)}


def property_check({arguments}, {', '.join(str(leaf['variable']) for leaf in _logic_leaves(expected_node))}):
    return not trigger_holds({arguments}) or {expected_expr}


def test_{test_id}_boundary():
    cases = [
{rendered}
    ]
    for value, expected in cases:
        assert trigger_holds(value) is expected
    assert property_check({boundary_cases[-1][0]!r}, {wrong_call}) is False
'''
        true_values = [_truth_values(leaf)[1] for leaf in trigger_leaves]
        false_values = [_truth_values(leaf)[0] for leaf in trigger_leaves]
        assignments = []
        for mask in range(2 ** len(trigger_leaves)):
            values = [true_values[index] if mask & (1 << index) else false_values[index] for index in range(len(trigger_leaves))]
            assignments.append((values, bool(eval(_python_expression(trigger), {}, dict(zip(variables, values))))))
        rendered = ",\n".join(
            f"        ({values[0]!r}, {result!r})" if len(values) == 1
            else f"        ({tuple(values)!r}, {result!r})"
            for values, result in assignments
        )
        arguments = ", ".join(variables)
        expected_expr = _python_expression(expected_node)
        return f'''def trigger_holds({arguments}):
    return {_python_expression(trigger)}


def property_check({arguments}, {', '.join(str(leaf['variable']) for leaf in _logic_leaves(expected_node))}):
    return not trigger_holds({arguments}) or {expected_expr}


def test_{test_id}_truth_table_and_boundaries():
    cases = [
{rendered}
    ]
    for values, expected in cases:
        arguments = values if isinstance(values, tuple) else (values,)
        assert trigger_holds(*arguments) is expected
'''
    if isinstance(ir["expected"], dict) and "logic" in ir["expected"]:
        import itertools
        leaves = _logic_leaves(ir["expected"])
        names = list(dict.fromkeys(leaf["variable"] for leaf in leaves))
        samples = {name: [] for name in names}
        for leaf in leaves:
            samples[leaf["variable"]].extend(value for value, _ in boundary_values(leaf))
        expression_text = _python_expression(ir["expected"])
        cases = [(values, eval(expression_text, {"__builtins__": {}}, dict(zip(names, values)))) for values in itertools.product(*(samples[name] for name in names))]
        return f"def check_requirement({', '.join(names)}):\n    return {expression_text}\n\ndef test_{test_id}_boundaries():\n    for values, expected in {cases!r}:\n        assert check_requirement(*values) == expected\n"
    cases = range_boundary_values(ir["expected"]) if ir.get("property_type") == "range" else boundary_values(expression)
    rendered_cases = ",\n".join(f"        ({value!r}, {expected!r})" for value, expected in cases)
    if ir.get("property_type") == "range":
        check = f"return {variable} >= {ir['expected'][0]['value']!r} and {variable} <= {ir['expected'][1]['value']!r}"
    else:
        check = f"return {variable} {expression['operator']} {expression['value']!r}"
    return f'''def check_requirement({variable}):
    {check}


def test_{test_id}_boundary():
    cases = [
{rendered_cases}
    ]

    for value, expected in cases:
        assert check_requirement(value) == expected
'''


def write_dynamic_artifact(ir: dict[str, Any], output_dir: str | Path = "generated/dynamic") -> Path:
    """Write a boundary-value pytest module and return its path."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    safe_id = re.sub(r"[^a-zA-Z0-9]+", "_", str(ir.get("requirement_id", "requirement"))).strip("_")
    path = destination / f"test_{safe_id}.py"
    path.write_text(generate_boundary_test(ir), encoding="utf-8")
    return path


def generate_fuzz_harness(ir: dict[str, Any]) -> str:
    """Return a libFuzzer harness for numeric invariant/conditional IR."""
    if ir.get("verifiable") is False or not ir.get("expected"):
        raise ValueError("Cannot generate fuzz code for an unverifiable requirement")
    expressions = (_logic_leaves(ir["trigger"]) if ir.get("trigger") else []) + _logic_leaves(ir["expected"])
    variables = list(dict.fromkeys(str(expression["variable"]) for expression in expressions))
    declarations = "\n".join(f"    float {variable};" for variable in variables)
    copies = "\n".join(
        f"    memcpy(&{variable}, data + {index} * sizeof(float), sizeof(float));"
        for index, variable in enumerate(variables)
    )

    def condition(expression: dict[str, Any]) -> str:
        value = expression["value"]
        if isinstance(value, bool):
            rendered = "1.0f" if value else "0.0f"
        elif isinstance(value, str):
            rendered = value
        else:
            rendered = f"{value:.6g}f" if isinstance(value, float) else f"{value}.0f"
        return f"{expression['variable']} {expression['operator']} {rendered}"

    def logic(node):
        if isinstance(node, list):
            return "(" + " && ".join(logic(item) for item in node) + ")"
        if "logic" not in node:
            return condition(node)
        if node["logic"] == "NOT":
            return f"!({logic(node['condition'])})"
        return "(" + (" && " if node["logic"] == "AND" else " || ").join(logic(item) for item in node["conditions"]) + ")"
    assertion = f"if (!({logic(ir['expected'])})) __builtin_trap();"
    body = f"    if ({logic(ir['trigger'])}) {{\n        {assertion}\n    }}" if ir.get("trigger") else f"    {assertion}"
    constants = sorted({str(expression["value"]) for expression in expressions if isinstance(expression["value"], str)})
    definitions = "\n".join(f"#define {constant} 1.0f" for constant in constants)
    return f'''{definitions}
#include <stddef.h>
#include <stdint.h>
#include <string.h>

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{{
    if (size < {len(variables)} * sizeof(float)) return 0;
{declarations}
{copies}
{body}
    return 0;
}}
'''


def write_fuzz_artifact(ir: dict[str, Any], output_dir: str | Path = "generated/dynamic") -> Path:
    """Write a libFuzzer harness and return its path."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    safe_id = re.sub(r"[^a-zA-Z0-9]+", "_", str(ir.get("requirement_id", "requirement"))).strip("_")
    path = destination / f"fuzz_{safe_id}.c"
    path.write_text(generate_fuzz_harness(ir), encoding="utf-8")
    return path
