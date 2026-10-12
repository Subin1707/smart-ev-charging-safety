"""Exercise dashboard commands against an isolated production C simulator and bridge."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import requests

ROOT = Path(__file__).resolve().parents[1]


def test_live_controls(tmp_path, live_simulator_executable):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    for folder in ("logs/control", "logs/telemetry", "logs/simulation", "reports"):
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, SMART_EV_POSTGRES="0",
               SMART_EV_SNAPSHOT_PATH=str(tmp_path / "logs/telemetry/latest_state.json"),
               SMART_EV_COMMAND_PATH=str(tmp_path / "logs/control/command.json"))
    exe = live_simulator_executable
    simulator = subprocess.Popen([str(exe)], cwd=tmp_path, env=env,
                                 stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, text=True)
    bridge = subprocess.Popen([sys.executable, "-m", "uvicorn", "bridge.main:app",
                               "--port", str(port)], cwd=ROOT, env=env,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def state():
        response = requests.get(base + "/api/state", timeout=2)
        response.raise_for_status()
        return response.json()

    def wait(predicate, timeout=8):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                current = state()
                if predicate(current):
                    return current
            except requests.RequestException:
                pass
            time.sleep(.05)
        raise AssertionError("Timed out waiting for control result")

    def post(path, **kwargs):
        response = requests.post(base + path, timeout=5, **kwargs)
        response.raise_for_status()
        return response.json()

    try:
        simulator.stdin.write("2\n")
        simulator.stdin.flush()
        wait(lambda s: s["tick"] == 0)
        post("/api/tick")
        wait(lambda s: s["tick"] == 1)
        time.sleep(.3)
        assert state()["tick"] == 1
        post("/api/speed", json={"speed": 5})
        post("/api/start")
        wait(lambda s: s["tick"] >= 12, timeout=5)
        post("/api/pause")
        paused = wait(lambda s: s["simulation"]["status"] == "PAUSED")["tick"]
        time.sleep(.4)
        assert state()["tick"] == paused
        post("/api/tick")
        wait(lambda s: s["tick"] == paused + 1)
        post("/api/reset")
        wait(lambda s: s["tick"] == 0 and s["simulation"]["status"] == "PAUSED")
        post("/api/speed", json={"speed": .5})
        post("/api/start")
        wait(lambda s: s["simulation"]["status"] == "RUNNING")
        time.sleep(.7)
        assert state()["tick"] == 0
        wait(lambda s: s["tick"] == 1, timeout=3)
        for speed in (1, 2):
            assert post("/api/speed", json={"speed": speed})["accepted"]
        assert requests.post(base + "/api/speed", json={"speed": 0}, timeout=5).status_code == 422
        simulator.terminate()
        simulator.wait(timeout=5)
        time.sleep(3.2)
        assert requests.post(base + "/api/start", timeout=5).status_code == 503
    finally:
        for process in (simulator, bridge):
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
