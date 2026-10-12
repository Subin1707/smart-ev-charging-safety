"""Public reader API for normalized requirements.

The format-specific implementation remains in :mod:`parser`; this module
defines the Stage 2 reader contract used by analyzers and later generators.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .parser import load_requirements


def read_requirements(path: str | Path) -> list[dict[str, Any]]:
    """Read XLSX, CSV, or TXT requirements as normalized dictionaries."""
    return load_requirements(path)


def read_requirements_json(path: str | Path) -> list[dict[str, Any]]:
    """Read a previously generated ``requirements_raw.json`` document."""
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("requirements"), list):
        return payload["requirements"]
    if isinstance(payload, list):
        return payload
    raise ValueError("requirements_raw.json must contain a requirements list")
