"""CLI for converting raw requirement input to requirements_raw.json."""

from __future__ import annotations

import argparse
from pathlib import Path

from spec_generator.core.parser import load_requirements, write_requirements_raw

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize EV safety requirements")
    parser.add_argument("input", type=Path, help="Input .xlsx, .csv, or .txt file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=ROOT / "spec_generator" / "output" / "requirements_raw.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    requirements = load_requirements(args.input)
    output = write_requirements_raw(requirements, args.output)
    print(f"Wrote {len(requirements)} requirements to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())