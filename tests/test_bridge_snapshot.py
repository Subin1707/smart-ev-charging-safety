from pathlib import Path

import pytest
from fastapi import HTTPException

from bridge import main


def test_snapshot_recovers_from_temporary_windows_lock(tmp_path, monkeypatch):
    snapshot = tmp_path / "state.json"
    snapshot.write_text('{"tick": 7}', encoding="utf-8")
    monkeypatch.setattr(main, "SNAPSHOT_PATH", snapshot)
    original_open = Path.open
    attempts = 0

    def temporarily_locked(path, *args, **kwargs):
        nonlocal attempts
        attempts += 1
        if attempts <= 2:
            raise PermissionError("snapshot is being replaced")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", temporarily_locked)
    state = main.read_snapshot()
    assert state["tick"] == 7
    assert state["telemetryAgeMs"] >= 0


def test_missing_snapshot_returns_service_unavailable(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "SNAPSHOT_PATH", tmp_path / "missing.json")
    with pytest.raises(HTTPException) as error:
        main.read_snapshot()
    assert error.value.status_code == 503
