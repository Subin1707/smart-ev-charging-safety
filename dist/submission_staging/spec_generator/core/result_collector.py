"""Normalize tool results into requirement-level verification outcomes."""

from __future__ import annotations

from typing import Any


def _tool_classification(result: dict[str, Any], verification_level: str) -> tuple[str | None, str | None]:
    status = result.get("status")
    output = f"{result.get('stdout', '')}\n{result.get('stderr', '')}".lower()
    if status == "PASS":
        return None, None
    if status == "UNAVAILABLE":
        return "TOOL_FAILURE", f"{str(result.get('tool', 'tool')).upper()}_UNAVAILABLE"
    if status == "TIMEOUT":
        return "TIMEOUT", f"{str(result.get('tool', 'tool')).upper()}_TIMEOUT"
    if status in {"BUILD_ERROR", "EXECUTION_ERROR"}:
        return "BUILD_FAILURE" if status == "BUILD_ERROR" else "HARNESS_FAILURE", status
    if status == "NOT_APPLICABLE":
        return "UNSUPPORTED", "TOOL_NOT_APPLICABLE"
    if status == "FAIL":
        if verification_level == "standalone_model":
            return "MODEL_LIMITATION", "STANDALONE_MODEL_COUNTEREXAMPLE"
        if "pointer" in output or "syntax error" in output or "dead object" in output:
            return "MODEL_LIMITATION", "PRODUCTION_MODEL_LIMITATION"
        return "PROPERTY_VIOLATION", "ASSERTION_FAILED"
    return "TOOL_FAILURE", f"{str(status or 'UNKNOWN').upper()}_STATUS"


def collect_results(
    requirement_id: str,
    ir: dict[str, Any],
    strategy: dict[str, list[str]],
    tool_results: list[dict[str, Any]],
    mapping: dict[str, Any] | None = None,
    verification_level: str = "standalone_model",
) -> dict[str, Any]:
    classified_tools = []
    for result in tool_results:
        classified = dict(result)
        failure_class, reason = _tool_classification(classified, verification_level)
        if failure_class:
            classified["failure_class"] = failure_class
            classified["reason"] = reason
        classified_tools.append(classified)
    if ir.get("verifiable") is False:
        overall = "NOT_VERIFIABLE"
    elif mapping and mapping.get("status") in {"NOT_MAPPED", "PARTIALLY_MAPPED", "INVALID_MAPPING"}:
        overall = "NOT_MAPPED"
    else:
        statuses = [result.get("status") for result in classified_tools]
        if any(status in {"FAIL", "BUILD_ERROR", "EXECUTION_ERROR"} for status in statuses):
            overall = "FAIL"
        elif any(status in {"UNAVAILABLE", "TIMEOUT", "NOT_APPLICABLE"} for status in statuses):
            overall = "INCONCLUSIVE"
        elif statuses and all(status == "PASS" for status in statuses):
            overall = "PASS"
        else:
            overall = "INCONCLUSIVE"
    counterexamples = [
        result.get("counterexample") or result.get("stderr")
        for result in classified_tools
        if result.get("status") == "FAIL" and (result.get("counterexample") or result.get("stderr"))
    ]
    failures = [result for result in classified_tools if result.get("failure_class")]
    failure_class = next((result["failure_class"] for result in failures if result["failure_class"] == "PROPERTY_VIOLATION"), None)
    failure_class = failure_class or (failures[0]["failure_class"] if failures else None)
    reason = next((result.get("reason") for result in failures if result.get("reason")), None)
    return {
        "requirement_id": requirement_id,
        "verification_level": verification_level,
        "strategy": strategy,
        "tools": classified_tools,
        "mapping": mapping,
        "overall_result": overall,
        "counterexamples": counterexamples,
        "failure_class": failure_class,
        "reason": reason,
    }