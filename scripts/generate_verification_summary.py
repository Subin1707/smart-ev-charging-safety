from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
OUTPUT = REPORTS / "dashboard" / "summary.json"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def tool_status(paths: list[Path], pass_pattern: str) -> tuple[str, str | None]:
    existing = [path for path in paths if path.exists()]
    if not existing:
        return "UNKNOWN", None
    content = "\n".join(read_text(path) for path in existing)
    if re.search(pass_pattern, content, re.IGNORECASE):
        return "PASS", str(existing[0].relative_to(ROOT)).replace("\\", "/")
    return "UNKNOWN", str(existing[0].relative_to(ROOT)).replace("\\", "/")


def json_tool(path: Path) -> dict:
    if not path.exists():
        return {"status": "UNKNOWN", "report": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "UNKNOWN", "report": str(path.relative_to(ROOT)).replace("\\", "/")}
    data["report"] = str(path.relative_to(ROOT)).replace("\\", "/")
    return data


def build_summary() -> dict:
    fresh = ROOT / 'evidence' / 'summary.json'
    if fresh.exists():
        run = json_tool(fresh)
        mapping = {'staticAnalysis': 'static-analysis', 'memorySafety': 'sanitizer-test',
                   'cbmc': 'bmc-test', 'smtZ3': 'smt-test', 'fuzzing': 'fuzz-test', 'e2e': 'e2e-test',
                   'goldenBrowser': 'browser-test', 'postgresql': 'postgres-test'}
        stages = run.get('stages', {})
        age = int(max(0, time.time() - fresh.stat().st_mtime))
        tools = {key: {'status': stages.get(stage, 'UNKNOWN'), 'report': 'evidence/summary.json'}
                 for key, stage in mapping.items()}
        paths = {'staticAnalysis': '02_static/cppcheck_src.txt', 'memorySafety': '02_static/production_memory.txt',
                 'cbmc': '03_formal/bmc_results.txt', 'smtZ3': '03_formal/smt_results.txt',
                 'fuzzing': '05_fuzzing/comparison.json', 'e2e': '06_e2e/results.txt',
                 'goldenBrowser': '06_e2e/browser_results.txt', 'postgresql': '06_e2e/postgresql.txt'}
        for key, path in paths.items():
            if (ROOT / 'evidence' / path).exists():
                tools[key]['report'] = 'evidence/' + path
        if 'FAIL' in stages.values():
            overall = 'FAIL'
        elif run.get('status') != 'PASS' or any(v['status'] != 'PASS' for v in tools.values()):
            overall = 'UNKNOWN'
        else:
            overall = 'STALE' if age > 86400 else 'PASS'
        requirements = [
            ('SR01', 'Connect before authentication', ['test']),
            ('SR02', 'Authenticate before charging', ['test', 'bmc-test']),
            ('SR03', 'Overheat cuts charging power', ['test', 'smt-test', 'bmc-test', 'e2e-test']),
            ('SR04', 'Full battery receives zero power', ['test', 'bmc-test', 'e2e-test']),
            ('SR05', 'Emergency stop removes power', ['test', 'bmc-test', 'e2e-test']),
            ('SR06', 'Faulted vehicle cannot start directly', ['test']),
            ('SR07', 'One vehicle per port', ['test', 'bmc-test']),
            ('SR08', 'One port per vehicle', ['test']),
            ('SR09', 'SOC bounds validation', ['test', 'smt-test']),
            ('SR10', 'Station power limit', ['test', 'smt-test', 'bmc-test', 'e2e-test']),
            ('SR11', 'Low SOC priority under limited supply', ['test', 'smt-test']),
        ]
        properties = [{'id': ident, 'name': name,
                       'status': 'PASS' if all(stages.get(s) == 'PASS' for s in checks) else 'UNKNOWN',
                       'verifiedBy': checks} for ident, name, checks in requirements]
        return {'generatedAt': run.get('generatedAt'), 'evidenceAgeSeconds': age,
                'stale': age > 86400, 'staleAfterSeconds': 86400, 'overallStatus': overall,
                'tools': tools, 'safetyProperties': properties, 'scope': run.get('scope')}
    formal_path = REPORTS / "verification" / "formal_verification_summary.txt"
    smt_path = REPORTS / "smt" / "smt_results.txt"
    formal = read_text(formal_path)
    smt = read_text(smt_path)

    cbmc_passed = len(re.findall(r"Fixed\s*:\s*PASS", formal, re.IGNORECASE))
    smt_passed = len(re.findall(r"\[FIXED\] UNSAT|\[UNSAT\]", smt, re.IGNORECASE))
    cbmc_status = "PASS" if cbmc_passed == 6 and not re.search(r'Fixed\s*:\s*FAIL', formal, re.I) else "UNKNOWN"
    smt_status = "PASS" if smt_passed == 5 and '[FIXED] SAT' not in smt else "UNKNOWN"

    static = json_tool(REPORTS / "static-analysis" / "report.json")
    memory = json_tool(REPORTS / "memory-safety" / "report.json")
    fuzz = json_tool(REPORTS / "fuzzing" / "report.json")
    e2e_path = REPORTS / "e2e" / "report.json"
    e2e_status = "UNKNOWN"
    e2e_report = None
    e2e = {}
    if e2e_path.exists():
        e2e_report = str(e2e_path.relative_to(ROOT)).replace("\\", "/")
        e2e = json.loads(e2e_path.read_text(encoding="utf-8"))
        e2e_status = "PASS" if e2e.get('status') == 'PASS' and e2e.get('total', 0) > 0 and e2e.get("failed", 1) == 0 else "FAIL"

    tools = {
        "staticAnalysis": static,
        "memorySafety": memory,
        "cbmc": {
            "status": cbmc_status,
            "properties": cbmc_passed,
            "passed": cbmc_passed,
            "report": str(formal_path.relative_to(ROOT)).replace("\\", "/"),
        },
        "smtZ3": {
            "status": smt_status,
            "properties": smt_passed,
            "passed": smt_passed,
            "report": str(smt_path.relative_to(ROOT)).replace("\\", "/"),
        },
        "fuzzing": fuzz,
        "e2e": {
            "status": e2e_status,
            "total": e2e.get("total"),
            "passed": e2e.get("passed"),
            "failed": e2e.get("failed"),
            "report": e2e_report,
        },
    }

    safety_properties = [
        {"id": "SOC_BOUNDS", "name": "SOC must remain within [0,100]", "status": smt_status, "verifiedBy": ["SMT"]},
        {"id": "POWER_LIMIT", "name": "Station total power <= 100 kW", "status": smt_status, "verifiedBy": ["SMT", "E2E"]},
        {"id": "FAULT_ZERO_POWER", "name": "Faulted vehicle receives zero power", "status": cbmc_status, "verifiedBy": ["CBMC", "E2E"]},
        {"id": "AUTH_BEFORE_CHARGING", "name": "Authentication required before charging", "status": cbmc_status, "verifiedBy": ["CBMC", "E2E"]},
        {"id": "CONNECTED_BEFORE_CHARGING", "name": "Vehicle must be connected before charging", "status": cbmc_status, "verifiedBy": ["CBMC", "E2E"]},
        {"id": "EMERGENCY_ZERO_POWER", "name": "Emergency stop forces station power to zero", "status": cbmc_status, "verifiedBy": ["CBMC", "E2E"]},
        {"id": "FULL_ZERO_POWER", "name": "Full battery receives zero charging power", "status": cbmc_status, "verifiedBy": ["CBMC", "E2E"]},
    ]
    statuses = [tool["status"] for tool in tools.values()]
    evidence_paths = [Path(tool["report"]) for tool in tools.values() if tool.get("report")]
    ages = [max(0, time.time() - (ROOT / path).stat().st_mtime) for path in evidence_paths if (ROOT / path).exists()]
    evidence_age = int(max(ages, default=0))
    stale = evidence_age > 86400
    if "FAIL" in statuses:
        overall = "FAIL"
    elif any(status == "UNKNOWN" for status in statuses):
        overall = "UNKNOWN"
    elif stale:
        overall = "STALE"
    else:
        overall = "PASS"
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "evidenceAgeSeconds": evidence_age,
        "stale": stale,
        "staleAfterSeconds": 86400,
        "overallStatus": overall,
        "tools": tools,
        "safetyProperties": safety_properties,
    }


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build_summary(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
