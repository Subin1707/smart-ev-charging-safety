from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "reports" / "verification" / "smt"
CASES = [
    ("smt_soc", "verification/smt/kiem_chung_gioi_han_soc.py"),
    ("smt_temperature", "verification/smt/kiem_chung_nhiet_do.py"),
    ("smt_power_allocation", "verification/smt/kiem_chung_phan_phoi_cong_suat.py"),
    ("smt_energy", "verification/smt/kiem_chung_tinh_nang_luong.py"),
    ("smt_soc_priority", "verification/smt/kiem_chung_uu_tien_soc.py"),
]

REPORT_DIR.mkdir(parents=True, exist_ok=True)
summary = [
    "============================================================",
    "                 SMT / Z3 SUMMARY",
    "============================================================",
    "",
]
all_passed = True

for name, relative_script in CASES:
    script = ROOT / relative_script
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    output = result.stdout + result.stderr
    (REPORT_DIR / f"{name}.txt").write_text(output, encoding="utf-8")
    if name == "smt_soc_priority":
        passed = result.returncode == 0 and "[UNSAT] No counterexample; Low-SOC priority preserved" in output
        summary_label = "Fixed: UNSAT (no counterexample); PASS"
    else:
        vulnerable_ok = "[VULNERABLE] SAT" in output
        fixed_ok = "[FIXED] UNSAT" in output
        passed = result.returncode == 0 and vulnerable_ok and fixed_ok
        summary_label = "Vulnerable: SAT (counterexample found); Fixed: UNSAT (no counterexample); PASS"
    all_passed = all_passed and passed
    print(output, end="")
    summary.append(f"{name}: {summary_label if passed else 'FAIL'}")
    summary.append(f"Evidence: {name}.txt")
    summary.append("")

summary.append("============================================================")
summary.append(
    "FINAL RESULT: NUMERIC SAFETY PROPERTIES VERIFIED"
    if all_passed
    else "FINAL RESULT: SMT VERIFICATION INCOMPLETE"
)
summary.append("============================================================")
(REPORT_DIR / "smt_summary.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")
print("\n".join(summary))
sys.exit(0 if all_passed else 1)
