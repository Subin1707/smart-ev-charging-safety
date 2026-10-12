"""Convert normalized requirement text into verifiable analysis and IR."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

UNVERIFIABLE_REASON = "Không có tiêu chí chấp nhận có thể đo lường."

MEMORY_PATTERNS = {
    "buffer_overflow": (
        "buffer overflow", "out of bounds", "out-of-bounds", "write beyond",
        "ghi vuot", "tran bo dem", "vuot qua kich thuoc vung dem",
    ),
    "use_after_free": (
        "use after free", "use-after-free", "access memory after", "truy cap vung nho sau khi",
        "su dung sau khi giai phong",
    ),
    "double_free": (
        "double free", "double-free", "freed more than once", "giai phong nhieu hon mot lan",
        "giai phong hai lan",
    ),
    "memory_leak": (
        "memory leak", "memory must be released", "memory must be freed", "ro ri bo nho",
        "phai duoc giai phong",
    ),
    "integer_overflow": (
        "integer overflow", "integer calculations", "arithmetic overflow", "signed overflow", "tran so nguyen", "tran so",
    ),
}

_VARIABLES = (
    (r"(?:tong\s+cong\s+suat|total\s+(?:station\s+)?power)", "total_power"),
    (r"(?:nhiet\s*do|temperature)", "temperature"),
    (r"(?:cong\s+suat|power)", "power"),
    (r"\bSOC\b|state\s+of\s+charge", "soc"),
    (r"pressure|ap\s*suat", "pressure"),
    (r"voltage|dien\s*ap", "voltage"),
    (r"valve|van", "valve"),
    (r"system[_\s]?state|trang\s*thai\s*he\s*thong", "system_state"),
    (r"\bstate\b|trang\s*thai", "state"),
    (r"\bcharging\b|dang\s*sac", "charging"),
)
_NUMBER = r"[-+]?\d+(?:[.,]\d+)?"
_UNIT = r"(?:kW|kwh|kPa|km/h|°C|ºC|C|%|A|V)"
_COMPARISON = (
    (r"(?:khong\s+duoc\s+vuot\s+qua|must\s+not\s+exceed|less\s+than\s+or\s+equal\s+to|<=)", "<="),
    (r"(?:khong\s+duoc\s+thap\s+hon|must\s+be\s+at\s+least|greater\s+than\s+or\s+equal\s+to|>=)", ">="),
    (r"(?:nho\s+hon|must\s+be\s+less\s+than|less\s+than|<)", "<"),
    (r"(?:lon\s+hon|must\s+be\s+greater\s+than|greater\s+than|>)", ">"),
    (r"(?:not\s+equal|must\s+not\s+be|must\s+not\s+equal|khong\s+bang|khong\s+duoc\s+la|!=)", "!="),
    (r"(?:phai\s+(?:o\s+trang\s+thai\s+)?bang|bang|must\s+be|must\s+equal|equal(?:s)?(?:\s+to)?|==|=)", "=="),
)


def _fold(text: str) -> str:
    """Make Vietnamese keywords matchable without changing returned content."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(character for character in decomposed if unicodedata.category(character) != "Mn").replace("đ", "d")


def _variable(text: str) -> str | None:
    folded = _fold(text)
    explicit = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*_[A-Za-z0-9_]*)\s*(?:<=|>=|==|!=|<|>)", text)
    if explicit:
        return explicit.group(1).lower()
    for pattern, name in _VARIABLES:
        if re.search(pattern, folded, re.IGNORECASE):
            return name
    candidates = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text)
    ignored = {"if", "when", "khi", "neu", "then", "thi", "must", "be", "equal", "equals", "not", "the", "phai", "bang", "la"}
    ignored.update({"true", "false", "c", "kw", "kpa", "km", "h", "v"})
    for candidate in candidates:
        if candidate.lower() not in ignored:
            return candidate.lower()
    return None


def _operator(text: str) -> str | None:
    folded = _fold(text)
    for pattern, operator in _COMPARISON:
        if re.search(pattern, folded, re.IGNORECASE):
            return operator
    return None


def _value_unit(text: str) -> tuple[int | float, str | None] | None:
    match = re.search(rf"({_NUMBER})\s*({_UNIT})?", text, re.IGNORECASE)
    if not match:
        return None
    raw_value = match.group(1).replace(",", ".")
    value: int | float = float(raw_value) if "." in raw_value else int(raw_value)
    unit = match.group(2)
    if unit:
        unit = {"ºC": "C", "°C": "C", "c": "C"}.get(unit, unit)
    return value, unit


def detect_value_type(value: Any) -> tuple[str, Any]:
    """Normalize a literal into a number, boolean, or case-normalized enum."""
    text = str(value).strip()
    if text.lower() == "true":
        return "boolean", True
    if text.lower() == "false":
        return "boolean", False
    try:
        number = float(text)
        return "number", int(number) if number.is_integer() else number
    except ValueError:
        return "enum", text.upper()


def _range(text: str) -> tuple[str, int | float, int | float, str | None] | None:
    """Extract a variable and two numeric bounds from common range wording."""
    folded = _fold(text)
    has_range_wording = bool(re.search(
        r"\b(?:between|from|in\s+range|trong\s+khoang|tu|den)\b|<=.*<=",
        folded,
    ))
    if not has_range_wording:
        return None
    numbers = re.findall(_NUMBER, folded)
    if len(numbers) < 2:
        return None
    if re.search(r"<=.*<=", folded):
        variable = _variable(text)
    else:
        variable = _variable(text)
        if not variable:
            prefix = re.split(r"\b(?:between|from|in\s+range|trong\s+khoang|tu|từ)\b", folded, maxsplit=1)[0]
            words = re.findall(r"[a-z][a-z0-9_]*", prefix)
            variable = words[-1] if words else None
    if not variable:
        return None
    number_matches = list(re.finditer(_NUMBER, text))
    unit_match = re.search(rf"(?<![A-Za-z])({_UNIT})(?![A-Za-z])", text[number_matches[1].end():], re.IGNORECASE)
    unit = unit_match.group(1) if unit_match else None
    if unit:
        unit = {"ºC": "C", "°C": "C", "c": "C"}.get(unit, unit)
    values = [float(value.replace(",", ".")) for value in numbers[:2]]
    bounds: list[int | float] = [int(value) if value.is_integer() else value for value in values]
    return variable, bounds[0], bounds[1], unit


def _expression(text: str) -> dict[str, Any] | None:
    variable = _variable(text)
    operator = _operator(text)
    parsed_value = _value_unit(text)
    if not variable or not operator:
        return None
    if not parsed_value:
        symbolic = re.search(r"\b(?:true|false)\b|\b[A-Z][A-Z0-9_]*\b", text)
        if not symbolic:
            return None
        value_type, normalized = detect_value_type(symbolic.group(0))
        return {"variable": variable, "operator": operator, "value": normalized, "value_type": value_type, "unit": None}
    value, unit = parsed_value
    return {"variable": variable, "operator": operator, "value": value, "value_type": "number", "unit": unit}


def _split_logic(text: str, operator: str) -> list[str]:
    patterns = {
        "AND": r"\s+(?:AND|and|VÀ|và|&&)\s+",
        "OR": r"\s+(?:OR|or|HOẶC|hoặc|\|\|)\s+",
    }
    return re.split(patterns[operator], text)


def parse_logic_expression(text: str) -> dict[str, Any] | dict[str, Any] | None:
    """Parse logic with AND precedence over OR and return an IR logic node."""
    or_parts = _split_logic(text, "OR")
    if len(or_parts) > 1:
        return {"logic": "OR", "conditions": [parse_logic_expression(part.strip()) for part in or_parts]}
    and_parts = _split_logic(text, "AND")
    if len(and_parts) > 1:
        return {"logic": "AND", "conditions": [parse_logic_expression(part.strip()) for part in and_parts]}
    return _expression(text.strip())


def _clean_state(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_ ]", "", value).strip().upper().replace(" ", "_")


def parse_arrow_sequence(text: str) -> dict[str, Any] | None:
    """Parse an ordered state sequence without assigning strict-transition semantics."""
    if "->" not in text:
        return None
    states = [_clean_state(part) for part in text.split("->") if _clean_state(part)]
    if len(states) < 2:
        return None
    return {
        "property_type": "sequence",
        "states": states,
        "semantics": "ordered",
    }


def _ordering(text: str) -> tuple[str, str] | None:
    folded = _fold(text)
    match = re.search(
        r"^(.+?)\s+(?:must\s+(?:occur|happen|be\s+completed)|must|phai\s+(?:xay\s+ra|duoc\s+thuc\s+hien))\s+before\s+(.+?)(?:\.|$)"
        r"|^(.+?)\s+before\s+(.+?)(?:\.|$)"
        r"|^(.+?)\s+truoc\s+khi\s+(.+?)(?:\.|$)",
        folded,
        re.IGNORECASE,
    )
    if not match:
        return None
    before_text = match.group(1) or match.group(3)
    after_text = match.group(2) or match.group(4) or match.group(6)
    before_text = match.group(1) or match.group(3) or match.group(5)
    ignored = r"(?:authentication|charging|starts?|succeeds?|user|account|system|verification|activation|xay\s+ra|duoc\s+thuc\s+hien)"
    before_text = re.sub(r"\b(?:must|occur|happen|be|completed|phai|xay|ra|duoc|thuc|hien)\b", " ", before_text)
    after_text = re.sub(r"\b(?:must|occur|happen|be|completed|phai|xay|ra|duoc|thuc|hien|starts?|succeeds?)\b", " ", after_text)
    before = _clean_state(before_text)
    after = _clean_state(after_text)
    if before and after:
        return before, after
    return None


def _transition(text: str) -> tuple[str, str] | None:
    match = re.search(r"(?:transition|change|move)\s+from\s+([A-Za-z_ ]+?)\s+to\s+([A-Za-z_ ]+?)(?:\.|$)", text, re.IGNORECASE)
    if not match:
        match = re.search(r"chuyen\s+(?:trang\s+thai\s+)?tu\s+(.+?)\s+sang\s+(.+?)(?:\.|$)", _fold(text), re.IGNORECASE)
    if not match:
        return None
    return _clean_state(match.group(1)), _clean_state(match.group(2))


def _memory_issue(text: str) -> str | None:
    folded = _fold(text)
    if "buffer" in folded and "overflow" in folded:
        return "buffer_overflow"
    for issue, patterns in MEMORY_PATTERNS.items():
        if any(pattern in folded for pattern in patterns):
            return issue
    return None


def _memory_target(text: str) -> dict[str, str] | None:
    function = re.search(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)\b", text, re.IGNORECASE)
    if function:
        return {"type": "function", "name": function.group(1)}
    buffer_match = re.search(r"\bbuffer\s+([A-Za-z_][A-Za-z0-9_]*)\b", text, re.IGNORECASE)
    if buffer_match:
        return {"type": "variable", "name": buffer_match.group(1)}
    return None


def _memory_analysis(requirement_id: Any, content: str) -> dict[str, Any] | None:
    issue = _memory_issue(content)
    if not issue:
        return None
    if issue == "integer_overflow":
        return {
            "id": requirement_id, "property_type": "arithmetic_safety",
            "issue": issue, "expression": None, "content": content,
        }
    return {
        "id": requirement_id, "property_type": "memory_safety",
        "memory_issue": issue, "target": _memory_target(content), "content": content,
    }


def analyze_requirement(requirement: dict[str, Any]) -> dict[str, Any]:
    """Analyze one normalized requirement without inventing missing criteria."""
    content = str(requirement.get("content", "")).strip()
    memory = _memory_analysis(requirement.get("id"), content)
    if memory:
        return memory
    sequence = parse_arrow_sequence(content)
    if sequence:
        return {"id": requirement.get("id"), **sequence, "content": content}
    transition = _transition(content)
    if transition and not re.search(r"\b(?:if|when|khi|neu)\b", _fold(content)):
        return {
            "id": requirement.get("id"), "property_type": "transition",
            "from": transition[0], "to": transition[1], "content": content,
        }
    ordering = _ordering(content)
    if ordering:
        return {
            "id": requirement.get("id"), "property_type": "ordering",
            "before": ordering[0], "after": ordering[1], "content": content,
        }
    parsed_range = _range(content) if not re.search(r"(?:<=|>=|==|!=|<|>).+\b(?:AND|OR)\b.+(?:<=|>=|==|!=|<|>)", content, re.IGNORECASE) else None
    if parsed_range:
        variable, lower, upper, unit = parsed_range
        return {
            "id": requirement.get("id"),
            "property_type": "range",
            "lower": {"variable": variable, "operator": ">=", "value": lower, "value_type": "number", "unit": unit},
            "upper": {"variable": variable, "operator": "<=", "value": upper, "value_type": "number", "unit": unit},
            "content": content,
        }
    conditional = re.split(r"\s*(?:,|;|\bthen\b|thi\s+thi)\s*", content, maxsplit=1, flags=re.IGNORECASE)
    if len(conditional) == 2 and re.search(r"\b(?:if|when|khi|neu)\b", _fold(conditional[0])):
        condition_text = re.sub(r"^\s*(?:if|when|khi|neu)\s+", "", conditional[0], flags=re.IGNORECASE)
        transition_target = _transition(conditional[1])
        if transition_target:
            return {
                "id": requirement.get("id"), "property_type": "transition",
                "from": transition_target[0], "to": transition_target[1],
                "condition": parse_logic_expression(condition_text), "content": content,
            }
        condition = parse_logic_expression(condition_text)
        expected_text = re.sub(r"^\s*(?:then|thì|thi)\s+", "", conditional[1], flags=re.IGNORECASE)
        expected = parse_logic_expression(expected_text)
        if condition and expected:
            return {
                "id": requirement.get("id"),
                "property_type": "conditional",
                "condition": condition,
                "expected": expected,
                "content": content,
            }

    expression = parse_logic_expression(content)
    if expression and "logic" in expression:
        return {"id": requirement.get("id"), "property_type": "invariant", "expression": expression, "content": content}
    if expression:
        return {
            "id": requirement.get("id"),
            "property_type": "state" if expression.get("value_type") != "number" else "invariant",
            "expression": expression,
            "content": content,
        }
    return {
        "id": requirement.get("id"),
        "property_type": "unknown",
        "verifiable": False,
        "reason": UNVERIFIABLE_REASON,
        "content": content,
    }


def build_ir(analysis: dict[str, Any]) -> dict[str, Any]:
    """Build the common intermediate representation from an analysis result."""
    if analysis.get("verifiable") is False:
        return {
            "requirement_id": analysis.get("id"),
            "verifiable": False,
            "reason": analysis.get("reason", UNVERIFIABLE_REASON),
        }
    if analysis.get("property_type") == "sequence":
        states = analysis["states"]
        return {
            "requirement_id": analysis.get("id"), "verifiable": True,
            "property_type": "sequence", "states": states,
            "transitions": [{"from": source, "to": target} for source, target in zip(states, states[1:])],
            "semantics": analysis.get("semantics", "ordered"),
        }
    if analysis.get("property_type") == "memory_safety":
        return {
            "requirement_id": analysis.get("id"), "verifiable": True,
            "property_type": "memory_safety",
            "memory_issue": analysis["memory_issue"],
            "target": analysis.get("target"),
        }
    if analysis.get("property_type") == "arithmetic_safety":
        return {
            "requirement_id": analysis.get("id"), "verifiable": True,
            "property_type": "arithmetic_safety",
            "issue": analysis["issue"],
            "expression": analysis.get("expression"),
        }
    if analysis.get("property_type") == "ordering":
        return {
            "requirement_id": analysis.get("id"), "verifiable": True,
            "property_type": "ordering", "preconditions": [],
            "before": analysis["before"], "after": analysis["after"],
        }
    if analysis.get("property_type") == "transition":
        result = {
            "requirement_id": analysis.get("id"), "verifiable": True,
            "property_type": "transition", "from": analysis["from"], "to": analysis["to"],
        }
        if analysis.get("condition"):
            result["condition"] = analysis["condition"]
        return result
    if analysis.get("property_type") == "conditional":
        trigger = analysis["condition"]
        expected = analysis["expected"]
        return {
            "requirement_id": analysis.get("id"),
            "verifiable": True,
            "property_type": "conditional",
            "preconditions": [],
            "trigger": trigger,
            "expected": expected if isinstance(expected, dict) and "logic" in expected else [expected],
        }
    if analysis.get("property_type") == "memory_safety":
        return {
            "requirement_id": analysis.get("id"),
            "verifiable": True,
            "property_type": "memory_safety",
            "preconditions": [],
            "trigger": None,
            "expected": [],
        }
    if analysis.get("property_type") == "range":
        return {
            "requirement_id": analysis.get("id"),
            "verifiable": True,
            "property_type": "range",
            "preconditions": [],
            "trigger": None,
            "expected": [analysis["lower"], analysis["upper"]],
        }
    if analysis.get("property_type") == "state":
        return {
            "requirement_id": analysis.get("id"),
            "verifiable": True,
            "property_type": "state",
            "preconditions": [],
            "trigger": None,
            "expected": analysis["expression"] if "logic" in analysis["expression"] else [analysis["expression"]],
        }
    return {
        "requirement_id": analysis.get("id"),
        "verifiable": True,
        "property_type": "invariant",
        "preconditions": [],
        "trigger": None,
        "expected": analysis["expression"] if "logic" in analysis["expression"] else [analysis["expression"]],
    }


def analyze_requirements(requirements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Analyze requirements and return IR records for downstream generators."""
    return [build_ir(analyze_requirement(requirement)) for requirement in requirements]
