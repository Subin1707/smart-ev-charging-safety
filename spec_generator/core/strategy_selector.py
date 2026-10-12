"""Select verification techniques from requirement IR."""

from __future__ import annotations

from typing import Any

MEMORY_STRATEGIES = {
    "buffer_overflow": {"static": ["cppcheck", "cbmc"], "dynamic": ["asan", "fuzz"]},
    "use_after_free": {"static": ["cppcheck"], "dynamic": ["asan", "fuzz"]},
    "double_free": {"static": ["cppcheck"], "dynamic": ["asan", "fuzz"]},
    "memory_leak": {"static": ["static-analysis"], "dynamic": ["leaksan"]},
    "integer_overflow": {"static": ["cbmc", "static-analysis"], "dynamic": ["ubsan", "boundary"]},
}
NUMERIC_STATIC_TOOLS = ["CBMC", "SMT/Z3"]


def _text(ir: dict[str, Any]) -> str:
    return str(ir.get("content", "")).lower()


def select_strategy(ir: dict[str, Any]) -> dict[str, list[str]]:
    """Return the smallest useful static and dynamic verification set."""
    if ir.get("verifiable") is False:
        return {"static": [], "dynamic": []}

    text = _text(ir)
    if ir.get("property_type") == "memory_safety":
        return MEMORY_STRATEGIES.get(ir.get("memory_issue"), {"static": ["cppcheck"], "dynamic": ["asan", "fuzz"]})
    if ir.get("memory_safety"):
        return {"static": ["Cppcheck"], "dynamic": ["ASan", "Fuzz"]}
    if ir.get("property_type") == "arithmetic_safety":
        return MEMORY_STRATEGIES["integer_overflow"]

    if ir.get("property_type") == "conditional":
        return {
            "static": NUMERIC_STATIC_TOOLS[:],
            "dynamic": ["Boundary Test", "Runtime", "Fuzz"],
        }
    return {"static": NUMERIC_STATIC_TOOLS[:], "dynamic": ["Boundary Test"]}


def select_strategies(requirements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach a strategy selection to each IR record."""
    return [
        {"requirement_id": ir.get("requirement_id"), "strategy": select_strategy(ir)}
        for ir in requirements
    ]
