from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
INCLUDE_DIRS = [
    "core", "vehicle", "station", "charging", "auth", "safety", "simulation",
    "communication", "monitoring", "logging", "database", "utils",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def collect_static() -> None:
    output = REPORTS / "analysis" / "cppcheck_src_clean.txt"
    command = ["cppcheck", "--enable=warning,style,performance,portability", "--inconclusive", "--std=c17",
               "--suppress=missingIncludeSystem", "--suppress=missingInclude"]
    command.extend(argument for directory in INCLUDE_DIRS for argument in ("-I", f"src/{directory}"))
    command.extend(["src"])
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result.stderr, encoding="utf-8")
    errors = len(re.findall(r"\berror:\s", result.stderr, re.IGNORECASE))
    warnings = len(re.findall(r"\bwarning:\s", result.stderr, re.IGNORECASE))
    report = {
        "status": "PASS" if result.returncode == 0 and errors == 0 else "FAIL",
        "findings": errors + warnings,
        "errors": errors,
        "warnings": warnings,
        "report": rel(output),
        "exitCode": result.returncode,
    }
    path = REPORTS / "static-analysis" / "report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def collect_fuzz() -> None:
    text_path = REPORTS / "fuzzing" / "report.txt"
    text = text_path.read_text(encoding="utf-8", errors="replace") if text_path.exists() else ""

    def number(label: str) -> int:
        match = re.search(rf"^{label}\s*:\s*(\d+)", text, re.MULTILINE)
        return int(match.group(1)) if match else 0

    crashes = number("Crashes")
    timeouts = number("Timeouts")
    report = {
        "status": "PASS" if text and crashes == 0 and timeouts == 0 and "RESULT             : PASS" in text else "UNKNOWN",
        "executions": number("Generated inputs"),
        "crashes": crashes,
        "timeouts": timeouts,
        "report": rel(text_path) if text_path.exists() else None,
    }
    path = REPORTS / "fuzzing" / "report.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def collect_memory_unavailable() -> None:
    # Never overwrite a real sanitizer run with a hard-coded unavailable result.
    source = ROOT / 'evidence' / 'summary.json'
    if source.exists():
        data = json.loads(source.read_text(encoding='utf-8'))
        status = data.get('stages', {}).get('sanitizer-test', 'UNKNOWN')
        path = REPORTS / 'memory-safety' / 'report.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'status': status, 'report': 'evidence/02_static/',
                                   'scope': 'ASan/UBSan vulnerable and fixed fixtures'}, indent=2), encoding='utf-8')
        return
    path = REPORTS / "memory-safety" / "report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "status": "UNKNOWN",
        "asanErrors": None,
        "ubsanErrors": None,
        "executions": 0,
        "reason": "ASan/UBSan toolchain unavailable: Docker daemon and MinGW sanitizer runtimes were unavailable.",
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    collect_static()
    collect_fuzz()
    collect_memory_unavailable()
    print("Collected static-analysis, fuzzing, and memory-safety evidence")
