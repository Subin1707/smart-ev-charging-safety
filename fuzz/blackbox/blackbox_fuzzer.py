import argparse
import random
import subprocess
import time
from pathlib import Path

from mutation_strategy import SEEDS, mutate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="reports/fuzzing/fuzz_protocol.exe")
    parser.add_argument("--cases", type=int, default=5000)
    parser.add_argument("--report", default="reports/fuzzing/fuzz_protocol_fixed.txt")
    parser.add_argument("--label", default="fixed")
    args = parser.parse_args()

    rng = random.Random(20260907)
    target = Path(args.target)
    normal = 0
    rejected = 0
    crashes = 0
    timeouts = 0
    safety_violations = 0
    started_at = time.perf_counter()

    for _ in range(args.cases):
        data = mutate(rng.choice(SEEDS), rng)
        try:
            result = subprocess.run(
                [str(target)], input=data, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=1, check=False,
            )
            if result.returncode != 0:
                crashes += 1
            else:
                normal += 1
                if b"parsed=0" in result.stdout:
                    rejected += 1
                if b"safety_violation=1" in result.stdout:
                    safety_violations += 1
        except subprocess.TimeoutExpired:
            timeouts += 1

    passed = (
        crashes == 0
        and timeouts == 0
        and safety_violations == 0
    )

    report = "\n".join([
        "============================================================",
        "                  BLACK-BOX PROTOCOL FUZZING",
        "============================================================",
        f"Target            : {args.label}",
        f"Seed corpus       : {len(SEEDS)}",
        f"Generated inputs  : {args.cases}",
        f"Normal executions : {normal}",
        f"Rejected inputs   : {rejected}",
        f"Crashes           : {crashes}",
        f"Timeouts          : {timeouts}",
        f"Safety violations: {safety_violations}",
        f"Execution time (s): {time.perf_counter() - started_at:.3f}",
        "",
        f"RESULT             : {'PASS' if passed else 'FAIL'}",
        "============================================================",
    ]) + "\n"
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report, end="")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
