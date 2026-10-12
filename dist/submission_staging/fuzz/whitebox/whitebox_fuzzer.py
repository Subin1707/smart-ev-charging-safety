"""Compatibility entry point for the shared, measured charging-guard experiment."""
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[2]
if __name__ == '__main__':
    raise SystemExit(subprocess.call([sys.executable, str(ROOT / 'scripts/compare_fuzzing.py')], cwd=ROOT))
