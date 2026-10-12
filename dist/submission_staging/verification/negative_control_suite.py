#!/usr/bin/env python3
"""Generate Phase 7 negative-control specs and selectivity report."""

from __future__ import annotations

import copy
import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NORMAL_SPEC_PATH = ROOT / "teacher_specs" / "smart_ev_formal_verification.json"
PROPERTY_SUITE_PATH = ROOT / "reports" / "verification" / "formal_property_suite_v2.json"
OUTPUT_DIR = ROOT / "teacher_specs" / "negative_controls"
OUTPUT_JSON = ROOT / "reports" / "verification" / "negative_control_selectivity.json"
OUTPUT_MD = ROOT / "reports" / "verification" / "negative_control_selectivity.md"


DOMAIN_CONTROLS = [
    {
        "domain": "AUTH",
        "file": "auth_negative.json",
        "requirement_id": "REQ-AUTH-01",
        "violation_label": "req_auth_01_violation",
        "property": "AG(!req_auth_01_violation)",
    },
    {
        "domain": "SOC",
        "file": "soc_negative.json",
        "requirement_id": "REQ-SOC-01",
        "violation_label": "req_soc_01_violation",
        "property": "AG(!req_soc_01_violation)",
    },
    {
        "domain": "TEMP",
        "file": "temp_negative.json",
        "requirement_id": "REQ-TEMP-01",
        "violation_label": "req_temp_01_violation",
        "property": "AG(!req_temp_01_violation)",
    },
    {
        "domain": "PORT",
        "file": "port_negative.json",
        "requirement_id": "REQ-PORT-03",
        "violation_label": "req_port_03_violation",
        "property": "AG(!req_port_03_violation)",
    },
    {
        "domain": "CHARGING",
        "file": "charging_negative.json",
        "requirement_id": "REQ-CHG-01",
        "violation_label": "req_chg_01_violation",
        "property": "AG(!req_chg_01_violation)",
    },
    {
        "domain": "EMERGENCY",
        "file": "emergency_negative.json",
        "requirement_id": "REQ-EMG-01",
        "violation_label": "req_emg_01_violation",
        "property": "AG(!req_emg_01_violation)",
    },
]


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def reachable_states(initial: list[str], transitions: list[list[str]]) -> set[str]:
    outgoing: dict[str, list[str]] = {}
    for src, dst in transitions:
        outgoing.setdefault(src, []).append(dst)
    seen = set(initial)
    queue = deque(initial)
    while queue:
        current = queue.popleft()
        for nxt in outgoing.get(current, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def safety_violation_labels(spec: dict[str, Any]) -> set[str]:
    labels = set()
    for prop in spec.get("safety_properties", []):
        if prop.startswith("AG(!") and prop.endswith(")"):
            labels.add(prop.removeprefix("AG(!").removesuffix(")"))
    return labels


def inject_negative_model(normal: dict[str, Any], control: dict[str, str]) -> dict[str, Any]:
    model = copy.deepcopy(normal)
    sm = model["state_machine"]
    initial = sm["initial"][0]
    injected_state = f"injected_{control['domain'].lower()}_{control['violation_label']}"
    sm["states"].append(injected_state)
    sm["labeling"][injected_state] = sorted(
        {
            "smart_ev",
            "negative_control",
            control["domain"].lower(),
            control["requirement_id"].lower().replace("-", "_"),
            control["violation_label"],
        }
    )
    sm["transitions"].append([initial, injected_state])
    sm["transitions"].append([injected_state, injected_state])
    model["name"] = f"smart_ev_{control['domain'].lower()}_negative_control"
    model["description"] = (
        f"Negative control for {control['domain']}: injects exactly one reachable "
        f"{control['violation_label']} state. Expected only {control['domain']} to violate."
    )
    return model


def expected_matrix() -> list[dict[str, Any]]:
    domains = [item["domain"] for item in DOMAIN_CONTROLS]
    rows = [
        {
            "model": "NORMAL",
            "expected": {domain: "DUNG" for domain in domains},
            "target_domain": None,
        }
    ]
    for control in DOMAIN_CONTROLS:
        expected = {domain: "DUNG" for domain in domains}
        expected[control["domain"]] = "VI PHAM"
        rows.append(
            {
                "model": control["file"],
                "expected": expected,
                "target_domain": control["domain"],
            }
        )
    return rows


def validate_negative_model(model: dict[str, Any], control: dict[str, str], all_violation_labels: set[str]) -> dict[str, Any]:
    sm = model["state_machine"]
    reachable = reachable_states(sm["initial"], sm["transitions"])
    reachable_labels = {
        label
        for state in reachable
        for label in sm["labeling"].get(state, [])
        if label in all_violation_labels
    }
    injected_states = [
        state
        for state in reachable
        if control["violation_label"] in sm["labeling"].get(state, [])
    ]
    errors = []
    if control["violation_label"] not in reachable_labels:
        errors.append("target violation label is not reachable")
    unexpected = sorted(reachable_labels - {control["violation_label"]})
    if unexpected:
        errors.append(f"unexpected reachable violation labels: {', '.join(unexpected)}")
    return {
        "reachable_violation_labels": sorted(reachable_labels),
        "unexpected_reachable_violation_labels": unexpected,
        "injected_states_reachable": sorted(injected_states),
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }


def build_report() -> dict[str, Any]:
    normal = read_json(NORMAL_SPEC_PATH)
    property_suite = read_json(PROPERTY_SUITE_PATH) if PROPERTY_SUITE_PATH.exists() else {}
    all_violation_labels = safety_violation_labels(normal)
    normal_reachable = reachable_states(
        normal["state_machine"]["initial"],
        normal["state_machine"]["transitions"],
    )
    normal_reachable_violation_labels = sorted(
        {
            label
            for state in normal_reachable
            for label in normal["state_machine"]["labeling"].get(state, [])
            if label in all_violation_labels
        }
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    controls = []
    for control in DOMAIN_CONTROLS:
        model = inject_negative_model(normal, control)
        output_path = OUTPUT_DIR / control["file"]
        write_json(output_path, model)
        validation = validate_negative_model(model, control, all_violation_labels)
        controls.append(
            {
                **control,
                "output": rel(output_path),
                "injected_state": f"injected_{control['domain'].lower()}_{control['violation_label']}",
                "validation": validation,
            }
        )

    errors = []
    if normal_reachable_violation_labels:
        errors.append("normal model has reachable violation labels")
    failed_controls = [item["domain"] for item in controls if item["validation"]["status"] != "PASS"]
    if failed_controls:
        errors.append(f"negative controls failed validation: {', '.join(failed_controls)}")
    if len(controls) != 6:
        errors.append("expected 6 negative controls")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Phase 7 checker selectivity negative controls: each model injects exactly one reachable domain violation.",
        "inputs": [rel(NORMAL_SPEC_PATH), rel(PROPERTY_SUITE_PATH)] if property_suite else [rel(NORMAL_SPEC_PATH)],
        "normal_model": {
            "spec": rel(NORMAL_SPEC_PATH),
            "expected": {item["domain"]: "DUNG" for item in DOMAIN_CONTROLS},
            "reachable_violation_labels": normal_reachable_violation_labels,
        },
        "negative_controls": controls,
        "expected_selectivity_matrix": expected_matrix(),
        "summary": {
            "negative_controls": len(controls),
            "domains": [item["domain"] for item in controls],
            "normal_reachable_violation_labels": len(normal_reachable_violation_labels),
            "failed_controls": failed_controls,
            "status": "PASS" if not errors else "FAIL",
        },
        "validation": {
            "errors": errors,
            "status": "PASS" if not errors else "FAIL",
        },
    }


def render_md(report: dict[str, Any]) -> str:
    domains = [item["domain"] for item in DOMAIN_CONTROLS]
    lines = [
        "# Negative Control Selectivity - Phase 7",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "Each negative-control spec injects exactly one reachable violation label. The expected result is selective: only the injected domain should report `VI PHAM`; all other domains should remain `DUNG`.",
        "",
        "## Generated Files",
        "",
        "| Domain | File | Injected label | Expected failing property | Validation |",
        "|---|---|---|---|---|",
    ]
    for item in report["negative_controls"]:
        lines.append(
            f"| {item['domain']} | `{item['output']}` | `{item['violation_label']}` | "
            f"`{item['property']}` | `{item['validation']['status']}` |"
        )

    lines.extend(
        [
            "",
            "## Expected Selectivity Matrix",
            "",
            "| Model | " + " | ".join(domains) + " |",
            "|---" + "|---" * len(domains) + "|",
        ]
    )
    for row in report["expected_selectivity_matrix"]:
        lines.append(
            f"| `{row['model']}` | "
            + " | ".join(row["expected"][domain] for domain in domains)
            + " |"
        )

    lines.extend(
        [
            "",
            "## Validation",
            "",
            "```yaml",
            f"Negative controls: {report['summary']['negative_controls']}/6",
            f"Normal reachable violation labels: {report['summary']['normal_reachable_violation_labels']}",
            f"Failed controls: {len(report['summary']['failed_controls'])}",
            f"Status: {report['summary']['status']}",
            "```",
            "",
            "## Phase 7 Gate",
            "",
            "```yaml",
            "AUTH negative: one injected violation",
            "SOC negative: one injected violation",
            "TEMP negative: one injected violation",
            "PORT negative: one injected violation",
            "CHARGING negative: one injected violation",
            "EMERGENCY negative: one injected violation",
            f"Status: {report['validation']['status']}",
            "```",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    write_json(OUTPUT_JSON, report)
    write_text(OUTPUT_MD, render_md(report))
    print("Negative Control Selectivity")
    print(f"Status: {report['summary']['status']}")
    print(f"Negative controls: {report['summary']['negative_controls']}/6")
    print(f"Output JSON: {rel(OUTPUT_JSON)}")
    print(f"Output MD: {rel(OUTPUT_MD)}")
    return 0 if report["summary"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
