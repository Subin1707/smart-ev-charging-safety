"""Generate executable production harnesses from trusted, explicit C contracts.

Native runs enumerate sample inputs; CBMC explores the declared integer domains.
Assertions come from the IR, never from assignments of the expected outcome.
"""
from __future__ import annotations

import itertools
import re
from pathlib import Path
from typing import Any

from .code_mapping import _ir_variables, load_production_mapping, validate_mapping
from .static_generator import _as_node, _c_condition, _leaves


def _mapped_expression(expression: dict[str, Any], mapping: dict[str, Any]) -> str:
    variable = str(expression["variable"])
    access = mapping["variables"][variable]["access"]
    if access["type"] == "function":
        name = f"{access['symbol']}()"
    elif access["type"] == "global":
        name = access["symbol"]
    elif access["type"] == "expression":
        name = f"({access['expression']})"
    else:
        name = f"{access['object']}{access.get('member_operator', '.')}{access['field']}"
    mapped = dict(expression)
    if mapped.get("value_type") == "enum":
        mapped["value"] = mapping["enums"][variable][str(mapped["value"])]
    return _c_condition(mapped, name)


def _mapped_logic(node: Any, mapping: dict[str, Any]) -> str:
    node = _as_node(node)
    if "logic" not in node:
        return _mapped_expression(node, mapping)
    if node["logic"] == "NOT":
        return f"!({_mapped_logic(node['condition'], mapping)})"
    operator = " && " if node["logic"] == "AND" else " || "
    return "(" + operator.join(_mapped_logic(item, mapping) for item in node["conditions"]) + ")"


def generate_production_harness(
    ir: dict[str, Any], mapping: dict[str, Any], include_setup: bool = True
) -> tuple[str | None, dict[str, Any]]:
    """Setup is mandatory; include_setup is retained for caller compatibility."""
    validation = validate_mapping(ir, mapping)
    if validation["status"] != "MAPPED":
        return None, validation
    contract = mapping.get("harnesses", {}).get(str(ir["requirement_id"]))
    if not contract:
        return None, {**validation, "status": "PARTIALLY_MAPPED", "reason": "No explicit production setup/action contract for this requirement"}
    root = Path(__file__).resolve().parents[2]
    try:
        if not ir.get("expected"):
            raise ValueError("IR has no assertion expression")
        if not _ir_variables(ir) <= set(contract["variables"]):
            raise ValueError("Contract does not bind every IR variable")
        if not contract.get("actions") or not contract.get("setup"):
            raise ValueError("Contract requires setup and production actions")
        if not contract.get("sources") or any(not (root / s).is_file() for s in contract["sources"]):
            raise ValueError("Contract requires existing production sources")
        for node in (ir.get("trigger"), ir["expected"], ir.get("preconditions")):
            if node:
                for leaf in _leaves(_as_node(node)):
                    if leaf.get("value_type") == "enum" and str(leaf["value"]) not in mapping.get("enums", {}).get(leaf["variable"], {}):
                        raise ValueError(f"Missing enum mapping: {leaf['variable']}.{leaf['value']}")
        inputs = contract.get("inputs", [])
        for item in inputs:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", item["name"]):
                raise ValueError("Invalid input identifier")
            if not item["samples"] or not all(item["min"] <= value <= item["max"] for value in item["samples"]):
                raise ValueError("Samples must be within the input domain")
        declarations = [mapping["objects"][name]["declaration"] for name in contract["objects"]]
        actions = [mapping["actions"][name] for name in contract["actions"]]
        assertion = _mapped_logic(ir["expected"], mapping)
        trigger = _mapped_logic(ir["trigger"], mapping) if ir.get("trigger") else "true"
    except (KeyError, TypeError, ValueError) as error:
        return None, {**validation, "status": "INVALID_MAPPING", "reason": str(error)}

    headers = sorted(set(contract.get("headers", [])) | {
        mapping["variables"][name]["header"] for name in _ir_variables(ir)
    })
    lines = ['#include <assert.h>', '#include <stdbool.h>', '#include <stdio.h>']
    lines += [f'#include "{header}"' for header in headers]
    lines += [f"/* Production verification scope: {contract.get('scope', '')} */", "static unsigned triggered_cases = 0;"]
    args = ", ".join(f"int {item['name']}" for item in inputs) or "void"
    lines += [f"static void check_case({args})", "{"]
    lines += [f"    {line}" for line in declarations + contract["setup"]]
    if ir.get("preconditions"):
        lines += [f"    if (!({_mapped_logic(ir['preconditions'], mapping)})) return;"]
    lines += [f"    const bool trigger_before = {trigger};"]
    lines += [f"    {line}" for line in actions]
    lines += ["    if (trigger_before) {", "        ++triggered_cases;"]
    loop = contract.get("assertion_loop")
    if loop:
        lines += [f"        for (int {loop['index']} = 0; {loop['index']} < {loop['count']}; ++{loop['index']}) {{", f"            assert({assertion});", "        }"]
    else:
        lines += [f"        assert({assertion});"]
    lines += ["    }", "}", "#ifdef __CPROVER__", "extern int nondet_int(void);", "#endif", "int main(void)", "{", "#ifdef __CPROVER__"]
    for item in inputs:
        name = item["name"]
        lines += [f"    int {name} = nondet_int();", f"    __CPROVER_assume({name} >= {item['min']} && {name} <= {item['max']});"]
    lines += [f"    check_case({', '.join(item['name'] for item in inputs)});", "#else"]
    samples = list(itertools.product(*(item["samples"] for item in inputs)))
    for sample in samples:
        lines += [f"    check_case({', '.join(map(str, sample))});"]
    lines += ["    assert(triggered_cases > 0);", f'    printf("PRODUCTION_CASES={len(samples)} TRIGGERED=%u\\n", triggered_cases);', "#endif", "    return 0;", "}"]
    return "\n".join(lines) + "\n", {**validation, "sources": contract["sources"], "link_sources": contract.get("link_sources", contract["sources"]), "include_dirs": contract.get("include_dirs", []), "scope": contract.get("scope"), "inputs": inputs, "native_cases": len(samples)}


def write_production_harness(
    ir: dict[str, Any], mapping_path: str | Path, output_dir: str | Path = "generated/production"
) -> tuple[Path | None, dict[str, Any]]:
    source, status = generate_production_harness(ir, load_production_mapping(mapping_path))
    if source is None:
        return None, status
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    identifier = re.sub(r"[^A-Za-z0-9]+", "_", str(ir["requirement_id"])).strip("_")
    path = destination / f"{identifier}_production_cbmc.c"
    path.write_text(source, encoding="utf-8")
    return path, status
