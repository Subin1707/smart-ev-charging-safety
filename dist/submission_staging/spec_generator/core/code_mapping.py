"""Explicit, human-reviewed mapping from specification variables to C code."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_MAPPING_PATH = Path(__file__).resolve().parents[1] / "input" / "code_mapping.json"


class CodeMappingError(ValueError):
    """Raised when a code mapping is malformed or points to a missing source."""


def load_production_mapping(path: str | Path = DEFAULT_MAPPING_PATH) -> dict[str, Any]:
    """Load the full production mapping schema, including actions and enums."""
    mapping_path = Path(path)
    payload = json.loads(mapping_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CodeMappingError("Production mapping must be a JSON object")
    if "variables" not in payload:
        payload = {"variables": payload, "actions": {}, "enums": {}}
    for name, entry in payload.get("variables", {}).items():
        if not isinstance(entry, dict) or not entry.get("source"):
            raise CodeMappingError(f"Mapping for {name!r} requires source")
        access = entry.get("access")
        if access:
            if access.get("type") not in {"function", "global", "field", "expression"}:
                raise CodeMappingError(f"Unsupported access type for {name!r}")
            if access["type"] in {"function", "global"} and not access.get("symbol"):
                raise CodeMappingError(f"Mapping for {name!r} requires access.symbol")
            if access["type"] == "field" and not access.get("object") or access.get("type") == "field" and not access.get("field"):
                raise CodeMappingError(f"Mapping for {name!r} requires access.object and access.field")
    return payload


def load_code_mapping(path: str | Path = DEFAULT_MAPPING_PATH) -> dict[str, dict[str, str]]:
    """Load explicit mappings; no source-code guessing is performed."""
    mapping_path = Path(path)
    payload = load_production_mapping(mapping_path).get("variables", {})
    if not isinstance(payload, dict):
        raise CodeMappingError("Code mapping must be a JSON object")
    for variable, entry in payload.items():
        if not isinstance(entry, dict) or not entry.get("source"):
            raise CodeMappingError(f"Mapping for {variable!r} requires source")
        access = entry.get("access", {})
        if not entry.get("symbol") and not access.get("symbol") and access.get("type") not in {"field", "expression"}:
            raise CodeMappingError(f"Mapping for {variable!r} requires symbol or field access")
    return payload


def _ir_variables(ir: dict[str, Any]) -> set[str]:
    variables: set[str] = set()
    def visit(node: Any) -> None:
        if isinstance(node, list):
            for item in node:
                visit(item)
        elif isinstance(node, dict):
            if "variable" in node:
                variables.add(str(node["variable"]))
            for key in ("trigger", "expected", "condition", "conditions", "preconditions"):
                if key in node:
                    visit(node[key])
    visit(ir)
    return variables


def validate_mapping(
    ir: dict[str, Any], mapping: dict[str, Any], project_root: str | Path | None = None
) -> dict[str, Any]:
    """Validate that every IR variable has a usable production mapping."""
    variables = mapping.get("variables", mapping)
    required = _ir_variables(ir)
    mapped = sorted(variable for variable in required if variable in variables)
    missing = sorted(required - set(mapped))
    invalid = []
    root = Path(project_root) if project_root else Path(__file__).resolve().parents[2]
    for variable in mapped:
        entry = variables[variable]
        if not entry.get("source") or not (root / entry["source"]).is_file():
            invalid.append(variable)
    if invalid:
        status = "INVALID_MAPPING"
    elif not mapped:
        status = "NOT_MAPPED"
    elif missing:
        status = "PARTIALLY_MAPPED"
    else:
        status = "MAPPED"
    return {"status": status, "mapped": mapped, "missing": missing, "invalid": sorted(invalid)}


def validate_code_mapping(
    mapping: dict[str, dict[str, str]], project_root: str | Path | None = None
) -> dict[str, dict[str, Any]]:
    """Report mapping completeness and source existence without auto-correcting it."""
    root = Path(project_root) if project_root else Path(__file__).resolve().parents[2]
    result: dict[str, dict[str, Any]] = {}
    for variable, entry in mapping.items():
        source_path = root / entry["source"]
        access = entry.get("access", {})
        symbol = access.get("symbol") or (
            f"{access.get('object')}.{access.get('field')}" if access.get("type") == "field" else entry.get("symbol")
        )
        result[variable] = {
            "source": entry["source"],
            "symbol": symbol,
            "source_exists": source_path.is_file(),
            "status": "CONFIRMED" if source_path.is_file() else "MISSING_SOURCE",
        }
    return result


def mapping_for_variables(
    variables: set[str], mapping: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """Return mappings for variables used by an IR, preserving missing entries."""
    return {variable: mapping[variable] for variable in variables if variable in mapping}
