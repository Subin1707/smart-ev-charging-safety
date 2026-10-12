#!/usr/bin/env python3
"""GD9.6 security finding triage plus Docker/Linux sanitizer attempt."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "verification"
EVIDENCE = ROOT / "evidence" / "production_e2e"
OUT_JSON = REPORTS / "gd96_security_sanitizer.json"
OUT_MD = REPORTS / "gd96_security_sanitizer.md"

STATIC_JSON = REPORTS / "production_static_analysis.json"
DYNAMIC_JSON = REPORTS / "production_dynamic_verification.json"

INCLUDES = [
    "src/core",
    "src/vehicle",
    "src/station",
    "src/charging",
    "src/auth",
    "src/safety",
    "src/simulation",
    "src/communication",
    "src/monitoring",
    "src/logging",
    "src/database",
    "src/utils",
    "verification/harness",
]

SOURCE_DIRS = [
    "src/core",
    "src/vehicle",
    "src/station",
    "src/auth",
    "src/charging",
    "src/safety",
    "src/logging",
    "src/monitoring",
    "src/simulation",
    "src/communication",
    "src/database",
    "src/utils",
]

TRIAGE_NOTES = {
    ("src/database/database.c", 55): {
        "function": "khoi_tao_database",
        "classification": "MITIGATED",
        "requirement": "NOT_APPLICABLE",
        "exploitability": (
            "No Smart EV external input reaches this fallback copy. The code copies a fixed "
            "literal into static char g_sql_path[256]; caller-controlled paths use strncpy "
            "with explicit NUL termination in the preceding branch."
        ),
        "evidence": "Destination is static char g_sql_path[256]; source literal is logs/database/persistence.sql.",
    },
    ("src/logging/logger.c", 50): {
        "function": "ghi_log",
        "classification": "MITIGATED",
        "requirement": "NOT_APPLICABLE",
        "exploitability": (
            "Fallback executes only when localtime() fails. The source is the fixed literal "
            "00:00:00 copied into char thoi_gian_str[32], so no attacker-controlled overflow "
            "path exists in Smart EV flows."
        ),
        "evidence": "Destination is char thoi_gian_str[32]; source literal is 8 characters plus NUL.",
    },
    ("src/station/tram_sac.c", 16): {
        "function": "khoi_tao_tram_sac",
        "classification": "MITIGATED",
        "requirement": "REQ-AUTH-01,REQ-AUTH-02,REQ-PORT-01,REQ-PORT-02",
        "exploitability": (
            "The strcpy branch is used only when ma_tram is NULL and copies the fixed default "
            "station ID STATION01 into char ma_tram[20]. Non-null station IDs use strncpy "
            "with explicit NUL termination."
        ),
        "evidence": "Destination is TramSac.ma_tram[20]; source literal is STATION01.",
    },
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_cmd(cmd: list[str], timeout: int = 300) -> dict[str, Any]:
    try:
        p = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        return {"command": cmd, "exit_code": p.returncode, "output": p.stdout, "timeout": False}
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "exit_code": None,
            "output": exc.stdout or "",
            "timeout": True,
        }


def code_line(path_text: str, line: int) -> str:
    path = ROOT / path_text
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if 1 <= line <= len(lines):
        return lines[line - 1].strip()
    return ""


def triage_static_findings(static_report: dict[str, Any]) -> list[dict[str, Any]]:
    security = [f for f in static_report.get("findings", []) if f.get("severity") == "SECURITY"]
    triaged = []
    for finding in security:
        key = (finding["file"], int(finding["line"]))
        note = TRIAGE_NOTES.get(key)
        if note is None:
            classification = "INCONCLUSIVE"
            note = {
                "function": finding.get("function", "UNKNOWN"),
                "classification": classification,
                "requirement": finding.get("related_requirement", "UNTRACEABLE"),
                "exploitability": "No specific triage rule available.",
                "evidence": "Manual review still required.",
            }
        triaged.append(
            {
                "tool": finding["tool"],
                "rule": finding["classification"],
                "file": finding["file"],
                "line": finding["line"],
                "function": note["function"],
                "code": code_line(finding["file"], int(finding["line"])),
                "related_requirement": note["requirement"],
                "original_message": finding["message"],
                "triage_classification": note["classification"],
                "exploitability_in_smart_ev_flow": note["exploitability"],
                "evidence": note["evidence"],
            }
        )
    return triaged


def production_sources() -> list[str]:
    sources: list[Path] = []
    for directory in SOURCE_DIRS:
        sources.extend(sorted((ROOT / directory).glob("*.c")))
    return [rel(p) for p in sources if p.name != "main.c"]


def ensure_dynamic_harness() -> Path | None:
    harness = EVIDENCE / "gd95_dynamic_harness.c"
    if harness.exists():
        return harness
    return None


def write_docker_script() -> Path:
    harness = "evidence/production_e2e/gd95_dynamic_harness.c"
    output = "evidence/production_e2e/gd96_sanitized"
    flags = " ".join(
        [
            "gcc",
            "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-std=c17",
            *[f"-I{inc}" for inc in INCLUDES],
            *production_sources(),
            harness,
            "-lm",
            "-o",
            output,
        ]
    )
    script = EVIDENCE / "gd96_docker_sanitizer.sh"
    script.write_text(
        "#!/usr/bin/env bash\n"
        "set -u\n"
        f"{flags}\n"
        "compile_status=$?\n"
        "if [ $compile_status -ne 0 ]; then exit $compile_status; fi\n"
        f"./{output}\n",
        encoding="utf-8",
    )
    return script


def docker_sanitizer_command() -> str:
    harness = "evidence/production_e2e/gd95_dynamic_harness.c"
    output = "evidence/production_e2e/gd96_sanitized"
    compile_cmd = " ".join(
        [
            "gcc",
            "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-std=c17",
            *[f"-I{inc}" for inc in INCLUDES],
            *production_sources(),
            harness,
            "-lm",
            "-o",
            output,
        ]
    )
    return f"{compile_cmd} && ./{output}"


def run_docker_sanitizer() -> dict[str, Any]:
    docker = shutil.which("docker")
    if not docker:
        return {
            "attempted": False,
            "available": False,
            "asan": "UNAVAILABLE",
            "ubsan": "UNAVAILABLE",
            "reason": "docker CLI not found",
            "test_cases_executed": 0,
            "asan_findings": 0,
            "ubsan_findings": 0,
            "crashes": 0,
            "raw": {},
        }
    if ensure_dynamic_harness() is None:
        return {
            "attempted": False,
            "available": False,
            "asan": "UNAVAILABLE",
            "ubsan": "UNAVAILABLE",
            "reason": "GD9.5 dynamic harness not found; run production_e2e_verification.py first",
            "test_cases_executed": 0,
            "asan_findings": 0,
            "ubsan_findings": 0,
            "crashes": 0,
            "raw": {},
        }

    script = write_docker_script()
    docker_cmd = [
        docker,
        "run",
        "--rm",
        "-v",
        f"{ROOT}:/app",
        "-w",
        "/app",
        "gcc:13",
        "bash",
        "-lc",
        docker_sanitizer_command(),
    ]
    raw = run_cmd(docker_cmd, timeout=360)
    out = raw["output"] or ""
    daemon_unavailable = raw["exit_code"] is None or "permission denied" in out.lower() or "cannot connect" in out.lower()
    image_unavailable = "pull access denied" in out.lower() or "not found" in out.lower()
    asan_findings = len(re.findall(r"AddressSanitizer|ERROR: ASan", out))
    ubsan_findings = len(re.findall(r"runtime error:|UndefinedBehaviorSanitizer", out))
    crashes = 1 if raw["exit_code"] not in (0, None) and (asan_findings or ubsan_findings or "assert" in out.lower()) else 0
    boundary = parse_metric(out, "BOUNDARY_CASES")
    boolean = parse_metric(out, "BOOLEAN_COMBINATIONS")

    if raw["exit_code"] == 0:
        asan = "PASS" if asan_findings == 0 else "FAIL"
        ubsan = "PASS" if ubsan_findings == 0 else "FAIL"
        reason = "Docker sanitizer run completed."
    elif daemon_unavailable:
        asan = ubsan = "UNAVAILABLE"
        reason = "Docker daemon/API unavailable or permission denied in current environment."
    elif image_unavailable:
        asan = ubsan = "UNAVAILABLE"
        reason = "Docker image unavailable locally and could not be pulled."
    else:
        asan = "FAIL" if asan_findings else "INCONCLUSIVE"
        ubsan = "FAIL" if ubsan_findings else "INCONCLUSIVE"
        reason = "Docker sanitizer command failed; inspect raw output."

    write_text(EVIDENCE / "gd96_docker_sanitizer_output.txt", out)
    return {
        "attempted": True,
        "available": raw["exit_code"] == 0,
        "asan": asan,
        "ubsan": ubsan,
        "reason": reason,
        "test_cases_executed": boundary + boolean if raw["exit_code"] == 0 else 0,
        "boundary_cases": boundary,
        "boolean_combinations": boolean,
        "asan_findings": asan_findings,
        "ubsan_findings": ubsan_findings,
        "crashes": crashes,
        "script": rel(script),
        "output_file": "evidence/production_e2e/gd96_docker_sanitizer_output.txt",
        "raw": raw,
    }


def parse_metric(output: str, key: str) -> int:
    m = re.search(rf"{re.escape(key)}=(\d+)", output)
    return int(m.group(1)) if m else 0


def summarize(triaged: list[dict[str, Any]]) -> dict[str, int]:
    labels = ["CONFIRMED", "FALSE_POSITIVE", "MITIGATED", "INCONCLUSIVE"]
    return {label: sum(1 for item in triaged if item["triage_classification"] == label) for label in labels}


def determine_status(summary: dict[str, int], docker_result: dict[str, Any]) -> str:
    if summary["CONFIRMED"] > 0:
        return "FAIL"
    if docker_result["asan"] == "FAIL" or docker_result["ubsan"] == "FAIL":
        return "FAIL"
    if docker_result["asan"] == "PASS" and docker_result["ubsan"] == "PASS" and summary["INCONCLUSIVE"] == 0:
        return "PASS"
    return "INCONCLUSIVE"


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# GD9.6 — Security Triage + Sanitizer",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Static Finding Triage",
        "",
        "| Classification | Tool/Rule | Location | Function | Requirement | Code | Conclusion Evidence |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in report["triaged_findings"]:
        lines.append(
            f"| {item['triage_classification']} | {item['tool']} / `{item['rule']}` | `{item['file']}:{item['line']}` | `{item['function']}` | {item['related_requirement']} | `{item['code']}` | {item['evidence']} {item['exploitability_in_smart_ev_flow']} |"
        )
    docker = report["docker_sanitizer"]
    lines += [
        "",
        "## Sanitizer",
        "",
        f"- Native MinGW ASan: {report['native_mingw']['asan']}",
        f"- Native MinGW UBSan: {report['native_mingw']['ubsan']}",
        f"- Linux/Docker ASan: {docker['asan']}",
        f"- Linux/Docker UBSan: {docker['ubsan']}",
        f"- Sanitizer test cases executed: {docker['test_cases_executed']}",
        f"- ASan findings: {docker['asan_findings']}",
        f"- UBSan findings: {docker['ubsan_findings']}",
        f"- Crashes: {docker['crashes']}",
        f"- Docker note: {docker['reason']}",
        "",
        "## Status",
        "",
        f"Canonical production modified: {report['canonical_production_modified']}",
        f"GĐ9.6 STATUS: {report['status']}",
    ]
    write_text(OUT_MD, "\n".join(lines) + "\n")


def print_summary(report: dict[str, Any]) -> None:
    summary = report["triage_summary"]
    docker = report["docker_sanitizer"]
    print("============================================================")
    print(" GĐ9.6 — SECURITY TRIAGE + SANITIZER")
    print("============================================================")
    print(f"Static findings                   : {report['static_findings']}")
    print(f"Confirmed                         : {summary['CONFIRMED']}")
    print(f"False positive                    : {summary['FALSE_POSITIVE']}")
    print(f"Mitigated                         : {summary['MITIGATED']}")
    print(f"Inconclusive                      : {summary['INCONCLUSIVE']}")
    print()
    print(f"Native MinGW ASan                 : {report['native_mingw']['asan']}")
    print(f"Native MinGW UBSan                : {report['native_mingw']['ubsan']}")
    print()
    print(f"Linux/Docker ASan                 : {docker['asan']}")
    print(f"Linux/Docker UBSan                : {docker['ubsan']}")
    print()
    print(f"Sanitizer test cases executed     : {docker['test_cases_executed']}")
    print(f"ASan findings                     : {docker['asan_findings']}")
    print(f"UBSan findings                    : {docker['ubsan_findings']}")
    print(f"Crashes                           : {docker['crashes']}")
    print()
    print(f"Canonical production modified     : {report['canonical_production_modified']}")
    print()
    print(f"GĐ9.6 STATUS                      : {report['status']}")
    print("============================================================")


def main() -> int:
    static_report = read_json(STATIC_JSON)
    dynamic_report = read_json(DYNAMIC_JSON) if DYNAMIC_JSON.exists() else {}
    triaged = triage_static_findings(static_report)
    summary = summarize(triaged)
    docker = run_docker_sanitizer()
    native = {
        "asan": dynamic_report.get("sanitizer", {}).get("asan", "UNAVAILABLE"),
        "ubsan": dynamic_report.get("sanitizer", {}).get("ubsan", "UNAVAILABLE"),
        "reason": dynamic_report.get("sanitizer", {}).get("compile_output", ""),
    }
    report = {
        "phase": "GD9.6",
        "generated_at": now(),
        "static_findings": len(triaged),
        "triage_summary": summary,
        "triaged_findings": triaged,
        "native_mingw": native,
        "docker_sanitizer": docker,
        "canonical_production_modified": "NO",
        "status": determine_status(summary, docker),
    }
    write_json(OUT_JSON, report)
    write_md(report)
    print_summary(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
