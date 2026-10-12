#!/usr/bin/env python3
"""Explain SpecVerificationLab formal results with short counterexamples.

This is a presentation/evidence layer only. It does not perform model checking
and does not change PASS/FAIL results. For each teacher-reported FAIL property,
it finds the shortest reachable path to a state containing the violation label.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = ROOT / "teacher_specs" / "smart_ev_formal_verification.json"
DEFAULT_RESULT = ROOT / "evidence" / "formal_verification" / "teacher_app_result.json"
DEFAULT_OUTPUT = ROOT / "reports" / "verification" / "formal_explained_result.md"
DEFAULT_COUNTEREXAMPLE_DIR = ROOT / "reports" / "verification" / "counterexamples"


AG_NEGATION_RE = re.compile(r"^AG\(!([A-Za-z0-9_:-]+)\)$")
UNARY_PROPERTY_RE = re.compile(r"^(AG|EF|AF|EG|AX|EX)\((!?[A-Za-z0-9_:-]+)\)$")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def property_to_label(prop: str) -> str | None:
    match = AG_NEGATION_RE.match(prop.strip())
    if match:
        return match.group(1)
    match = UNARY_PROPERTY_RE.match(prop.strip())
    if not match:
        return None
    atom = match.group(2)
    return atom[1:] if atom.startswith("!") else atom


def build_adjacency(transitions: list[list[str]]) -> dict[str, list[str]]:
    adjacency: dict[str, list[str]] = {}
    for transition in transitions:
        if len(transition) != 2:
            continue
        src, dst = transition
        adjacency.setdefault(src, []).append(dst)
    return adjacency


def shortest_path_to_label(
    initial_states: list[str],
    transitions: list[list[str]],
    labeling: dict[str, list[str]],
    violation_label: str,
) -> list[str] | None:
    adjacency = build_adjacency(transitions)
    queue = deque()
    parent: dict[str, str | None] = {}

    for state in initial_states:
        queue.append(state)
        parent[state] = None

    target: str | None = None
    while queue:
        state = queue.popleft()
        if violation_label in labeling.get(state, []):
            target = state
            break
        for nxt in adjacency.get(state, []):
            if nxt not in parent:
                parent[nxt] = state
                queue.append(nxt)

    if target is None:
        return None

    path = []
    current: str | None = target
    while current is not None:
        path.append(current)
        current = parent[current]
    return list(reversed(path))


def dot_graph(requirement_id: str, violation_label: str, path: list[str]) -> str:
    lines = [
        "digraph counterexample {",
        '  rankdir="LR";',
        f'  label="{requirement_id} - {violation_label}";',
        '  labelloc="t";',
    ]
    for idx, state in enumerate(path):
        attrs = ['shape="box"']
        if idx == 0:
            attrs.append('style="filled"')
            attrs.append('fillcolor="lightblue"')
        if idx == len(path) - 1:
            attrs.append('style="filled"')
            attrs.append('fillcolor="mistyrose"')
        lines.append(f'  "{state}" [{", ".join(attrs)}];')
    for src, dst in zip(path, path[1:]):
        lines.append(f'  "{src}" -> "{dst}";')
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def normalize_result_status(status: str | None) -> str:
    value = (status or "").upper()
    if value in {"PASS", "DUNG", "ĐÚNG"}:
        return "PASS"
    if value in {"FAIL", "SAI", "VI PHAM", "VI_PHAM", "VIOLATION"}:
        return "FAIL"
    return value or "UNKNOWN"


def explain(spec_path: Path, result_path: Path, output_path: Path, counterexample_dir: Path) -> int:
    spec = read_json(spec_path)
    result = read_json(result_path)
    state_machine = spec.get("state_machine") or {}
    initial = state_machine.get("initial") or []
    transitions = state_machine.get("transitions") or []
    labeling = state_machine.get("labeling") or {}

    lines = [
        "# Formal Verification Result Explainer",
        "",
        f"Spec: `{rel(spec_path)}`",
        f"Raw result: `{rel(result_path)}`",
        "",
        "This report explains teacher-app formal results without changing them.",
        "",
    ]

    fail_count = 0
    pass_count = 0
    unknown_count = 0
    counterexample_dir.mkdir(parents=True, exist_ok=True)

    for item in result.get("properties", []):
        requirement_id = item.get("requirement_id", "UNKNOWN_REQUIREMENT")
        prop = item.get("property", "")
        violation_label = item.get("violation_label") or item.get("atomic_label") or property_to_label(prop) or "UNKNOWN_LABEL"
        status = normalize_result_status(item.get("status") or item.get("reported_result"))

        if status == "PASS":
            pass_count += 1
            lines.extend(
                [
                    f"[PASS] {requirement_id}",
                    "",
                    "Property:",
                    f"`{prop}`",
                    "",
                    "Meaning:",
                    item.get("meaning", "Teacher app reported the property as satisfied."),
                    "",
                ]
            )
            continue

        if status != "FAIL":
            unknown_count += 1
            lines.extend(
                [
                    f"[UNKNOWN] {requirement_id}",
                    "",
                    f"`{prop}`",
                    "",
                    "Result status is not PASS or FAIL in the raw teacher-app result.",
                    "",
                ]
            )
            continue

        fail_count += 1
        path = shortest_path_to_label(initial, transitions, labeling, violation_label)
        graph_path = counterexample_dir / f"{requirement_id.lower().replace('-', '_')}.dot"

        lines.extend(
            [
                f"[FAIL] {requirement_id}",
                "",
                "Property:",
                f"`{prop}`",
                "",
                "Violation:",
                f"`{violation_label}`",
                "",
                "Counterexample:",
            ]
        )

        if path:
            lines.extend(["", "```text"])
            lines.append("\n->\n".join(path))
            lines.extend(["```", ""])
            write_text(graph_path, dot_graph(requirement_id, violation_label, path))
            lines.append(f"Counterexample graph: `{rel(graph_path)}`")
        else:
            lines.extend(["", "No reachable violation state was found in the provided model."])

        lines.extend(
            [
                "",
                "Reason:",
                item.get("reason")
                or ("A reachable state satisfies the violation predicate."
                if path
                else "The raw result reports FAIL, but no path to the reported label was found in the provided model."),
                "",
            ]
        )

    lines.extend(
        [
            "## Summary",
            "",
            f"- PASS: {pass_count}",
            f"- FAIL: {fail_count}",
            f"- UNKNOWN: {unknown_count}",
            "",
        ]
    )
    write_text(output_path, "\n".join(lines))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Explain SpecVerificationLab formal results.")
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--counterexamples", type=Path, default=DEFAULT_COUNTEREXAMPLE_DIR)
    args = parser.parse_args()

    rc = explain(
        args.spec.resolve(),
        args.result.resolve(),
        args.output.resolve(),
        args.counterexamples.resolve(),
    )
    print(f"Formal Result Explainer")
    print(f"Spec: {rel(args.spec.resolve())}")
    print(f"Result: {rel(args.result.resolve())}")
    print(f"Output: {rel(args.output.resolve())}")
    print(f"Counterexamples: {rel(args.counterexamples.resolve())}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
