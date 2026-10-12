"""Shared native build for the live tests on Windows and POSIX."""
import os
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='session')
def live_simulator_executable(tmp_path_factory):
    override = os.getenv('SMART_EV_TEST_EXE')
    if override:
        executable = Path(override).expanduser().resolve()
        if not executable.is_file():
            raise FileNotFoundError(f'SMART_EV_TEST_EXE does not exist: {executable}')
        return executable
    directory = tmp_path_factory.mktemp('live-simulator')
    executable = directory / ('smart_ev.exe' if os.name == 'nt' else 'smart_ev')
    includes = [arg for path in sorted((ROOT / 'src').iterdir()) if path.is_dir() for arg in ('-I', str(path))]
    sources = sorted(str(path) for path in (ROOT / 'src').rglob('*.c'))
    subprocess.run(['gcc', '-std=c17', '-Wall', '-Wextra', *includes, *sources, '-o', str(executable)], cwd=ROOT, check=True)
    return executable
