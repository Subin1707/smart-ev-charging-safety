"""Build and verify standalone models and explicit production contracts separately."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from spec_generator.core.analyzer import analyze_requirements
from spec_generator.core.dynamic_generator import write_dynamic_artifact, write_fuzz_artifact
from spec_generator.core.production_harness_generator import write_production_harness
from spec_generator.core.spec_reader import read_requirements
from spec_generator.core.static_generator import write_static_artifacts
from spec_generator.core.strategy_selector import select_strategy
from spec_generator.core.parser import write_requirements_raw
from spec_generator.core.executor import run_cbmc, run_cppcheck, run_gcc_syntax, run_pytest, run_z3, run_command, resolve_tool
from spec_generator.core.result_collector import collect_results
from spec_generator.core.traceability_generator import build_traceability, build_summary, generate_markdown_report, save_summary, save_traceability_csv, save_traceability_json

ROOT = Path(__file__).resolve().parent.parent


def _safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")


def build_artifacts(irs: list[dict[str, Any]], mapping_path: Path | None = None) -> tuple[list[Path], dict[str, Any]]:
    artifacts: list[Path] = []
    production_results: dict[str, Any] = {}
    for ir in irs:
        if ir.get("verifiable") is False:
            continue
        if ir.get("property_type") not in ("memory_safety", "arithmetic_safety"):
            artifacts.extend(write_static_artifacts(ir, ROOT / "generated/static", mapping_path))
            artifacts.append(write_dynamic_artifact(ir, ROOT / "generated/dynamic"))
            if "Fuzz" in select_strategy(ir)["dynamic"]:
                artifacts.append(write_fuzz_artifact(ir, ROOT / "generated/dynamic"))
        if mapping_path:
            path, status = write_production_harness(ir, mapping_path, ROOT / "generated/production")
            production_results[str(ir["requirement_id"])] = {"mapping": status, "artifact": str(path) if path else None}
            if path:
                artifacts.append(path)
    return artifacts, production_results


def verify_artifacts(artifacts: list[Path]) -> dict[str, Any]:
    """Verify one requirement's standalone files, with one main per CBMC run."""
    c_files = [p for p in artifacts if p.suffix == ".c"]
    py_files = [p for p in artifacts if p.suffix == ".py"]
    results = []
    if c_files:
        results.extend([run_gcc_syntax(c_files, ROOT), run_cppcheck(c_files, ROOT)])
    if py_files:
        result = run_command([sys.executable, "-m", "py_compile", *map(str, py_files)], ROOT)
        results.append({**result, "tool": "py_compile"})
    for path in artifacts:
        if path.name.endswith("_cbmc.c"):
            results.append({**run_cbmc([path], ROOT), "artifact": str(path)})
        elif path.name.endswith("_z3.py"):
            results.append({**run_z3(path, ROOT), "artifact": str(path)})
    dynamic = [p for p in py_files if not p.name.endswith("_z3.py")]
    if dynamic:
        results.append(run_pytest(dynamic, ROOT))
    return {"tools": results}


def verify_production(path: Path, mapping: dict[str, Any]) -> dict[str, Any]:
    """Link the real C translation units, execute samples, then check CBMC domains."""
    includes = [arg for directory in mapping["include_dirs"] for arg in ("-I", str(ROOT / directory))]
    sources = [str(ROOT / source) for source in mapping["sources"]]
    binary_dir = ROOT / "bin/production"
    binary_dir.mkdir(parents=True, exist_ok=True)
    binary = binary_dir / (path.stem + (".exe" if os.name == "nt" else ""))
    # Discard unreachable UI/database/demo functions; reachable production functions
    # must still resolve at link time. No production behavior is stubbed.
    compiled = run_command(["gcc", "-std=c17", "-Wall", "-Wextra", "-ffunction-sections", "-fdata-sections", *includes, str(path), *[str(ROOT / source) for source in mapping.get("link_sources", mapping["sources"])], "-Wl,--gc-sections", "-o", str(binary)], ROOT, 60)
    compiled["tool"] = "gcc"
    if compiled["status"] == "FAIL":
        compiled["status"] = "BUILD_ERROR"
    native = run_command([str(binary)], ROOT) if compiled["status"] == "PASS" else {"status": "NOT_APPLICABLE", "reason": "Production build did not pass"}
    native["tool"] = "native"
    cbmc = resolve_tool("cbmc")
    formal = run_cbmc([path, *sources], ROOT, 60, [ROOT / d for d in mapping["include_dirs"]], unwind=16) if cbmc else {"status": "UNAVAILABLE"}
    formal["tool"] = "cbmc"
    return {"tools": [compiled, native, formal], "scope": mapping["scope"], "native_cases": mapping["native_cases"]}


def _belongs(path: Path, safe_id: str) -> bool:
    return path.name in {f"{safe_id}_cbmc.c", f"{safe_id}_z3.py", f"test_{safe_id}.py", f"fuzz_{safe_id}.c", f"{safe_id}_production_cbmc.c"}


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def run_pipeline(input_path: Path, mapping_path: Path | None = None) -> dict[str, Any]:
    requirements = read_requirements(input_path)
    irs = analyze_requirements(requirements)
    identifiers = [_safe_id(str(ir["requirement_id"])) for ir in irs]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Requirement IDs must be unique after filename normalization")
    artifacts, production_results = build_artifacts(irs, mapping_path)
    evidence_root = ROOT / "evidence"
    generation_root = evidence_root / "generation"
    generation_root.mkdir(parents=True, exist_ok=True)
    write_requirements_raw(requirements, generation_root / "requirements_raw.json")
    (generation_root / "requirements_ir.json").write_text(json.dumps(irs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = []
    for requirement, ir in zip(requirements, irs):
        requirement_id = str(ir["requirement_id"])
        safe_id = _safe_id(requirement_id)
        selected = [p for p in artifacts if _belongs(p, safe_id)]
        production = production_results.get(requirement_id, {})
        mapping = production.get("mapping", {"status": "NOT_MAPPED", "reason": "No production mapping supplied"})
        standalone_paths = [p for p in selected if p.parent.name != "production"]
        standalone = verify_artifacts(standalone_paths)
        production_execution = verify_production(Path(production["artifact"]), mapping) if production.get("artifact") else {"tools": []}
        standalone_result = collect_results(requirement_id, ir, select_strategy(ir), standalone["tools"])
        production_result = collect_results(requirement_id, ir, select_strategy(ir), production_execution["tools"], mapping, "production_integrated")
        # Standalone models are independent abstractions, not implementations of C.
        chosen = production_result if mapping_path else standalone_result
        tool_records = [{"name": item["tool"], "status": item["status"], "level": level} for level, execution in (("standalone", standalone_result), ("production", production_result)) for item in execution["tools"]]
        copied = {}
        for path in selected:
            if path.parent.name == "production":
                folder, key = "production", "production"
            elif path.name.startswith("fuzz_"):
                folder, key = "dynamic/fuzz", "fuzz"
            elif path.suffix == ".c":
                folder, key = "static/cbmc", "cbmc"
            elif path.name.endswith("_z3.py"):
                folder, key = "static/z3", "z3"
            else:
                folder, key = "dynamic/boundary", "boundary"
            destination = evidence_root / folder / path.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
            copied[key] = _relative(destination)
        execution = {
            "standalone": {
                "tools": standalone_result["tools"],
                "result": standalone_result["overall_result"],
                "failure_class": standalone_result.get("failure_class"),
                "reason": standalone_result.get("reason"),
            },
            "production": {
                "tools": production_result["tools"],
                "result": production_result["overall_result"],
                "failure_class": production_result.get("failure_class"),
                "reason": production_result.get("reason"),
            },
        }
        result_file = generation_root / f"{safe_id}_execution.json"
        result_file.write_text(json.dumps(execution, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest.append({
            "requirement_id": requirement_id, "source": {"file": requirement.get("source"), "row": requirement.get("source_row")},
            "content": requirement.get("content"), "ir": ir, "strategy": select_strategy(ir), "mapping": mapping,
            "artifacts": copied, "generated_artifacts": [_relative(p) for p in selected], "production_sources": mapping.get("sources", []),
            "verification_tools": tool_records, "verification_level": chosen["verification_level"], "execution": execution,
            "evidence": [*copied.values(), _relative(result_file)], "result": chosen["overall_result"],
            "failure_class": chosen.get("failure_class"), "reason": chosen.get("reason") or ir.get("reason") or mapping.get("reason"), "counterexample": chosen["counterexamples"] or None,
        })
    (generation_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    records = build_traceability(manifest)
    save_traceability_json(records, evidence_root / "traceability.json")
    save_traceability_csv(records, evidence_root / "traceability.csv")
    summary = build_summary(records)
    save_summary(summary, evidence_root / "summary.json")
    generate_markdown_report(records, summary, evidence_root / "report.md")
    evidence = {"input": str(input_path), "requirements": len(requirements), "verifiable": sum(ir.get("verifiable", True) for ir in irs), "artifacts": [str(p) for p in artifacts], "production_results": production_results, "summary": summary, "manifest": _relative(generation_root / "manifest.json")}
    (generation_root / "verification.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--mapping", type=Path, default=ROOT / "spec_generator/input/code_mapping.json")
    args = parser.parse_args()
    evidence = run_pipeline(args.input, args.mapping)
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    summary = evidence["summary"]
    return 0 if summary["total"] > 0 and summary["pass"] == summary["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
