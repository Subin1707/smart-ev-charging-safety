"""Exercise dashboard commands against an isolated production C simulator and bridge."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import requests

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_live(tmp_path, live_simulator_executable):
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

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        web_port = sock.getsockname()[1]
    web_env = dict(env, VITE_BRIDGE_BASE_URL=base, VITE_SIMULATION_MODE="backend")
    web = subprocess.Popen(["node", "web/node_modules/vite/bin/vite.js", "web", "--host", "127.0.0.1", "--port", str(web_port), "--strictPort"], cwd=ROOT, env=web_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        simulator.stdin.write("2\n")
        simulator.stdin.flush()
        wait(lambda s: s["tick"] == 0)
        from playwright.sync_api import sync_playwright, expect
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{web_port}")
            page.wait_for_function("document.querySelectorAll('.charging-port').length === 5")
            # Use visible controls; C should see arrivals in order, then increase SOC.
            page.locator('.speed-group button').last.click()
            page.get_by_role('button', name='START', exact=True).click()
            def ev(snapshot, identifier):
                return next(v for v in snapshot['vehicles'] if v['id'] == identifier)
            before = wait(lambda s: ev(s, 'EV01')['state'] == 'CHARGING')
            assert ev(before, 'EV02')['state'] == 'WAITING'
            wait(lambda s: ev(s, 'EV02')['state'] == 'CHARGING')
            wait(lambda s: ev(s, 'EV01')['soc'] > ev(before, 'EV01')['soc'])
            soc = page.locator('.port-1 .soc-row')
            expect(soc).to_be_visible()
            assert soc.evaluate("el => { const a=el.getBoundingClientRect(); const b=el.closest('.charging-port').getBoundingClientRect(); return a.top>=b.top && a.bottom<=b.bottom; }")
            page.locator('#target-vehicle').select_option('EV01')
            page.locator('#fault-type').select_option('OVERHEAT')
            page.locator('section').filter(has=page.locator('#fault-type')).locator('button').click()
            wait(lambda s: ev(s, 'EV01')['state'] == 'FAULT' and ev(s, 'EV01')['allocatedPower'] == 0)
            # Every menu scenario must be consumed and trigger, including after pause.
            for scenario in ['NORMAL', 'OVERHEAT', 'CRITICAL_TEMPERATURE', 'THERMAL_RUNAWAY', 'FIRE_RISK', 'AUTH_FAILURE', 'UNEXPECTED_DISCONNECT', 'POWER_OVERLOAD', 'EMERGENCY_STOP', 'MIXED']:
                page.locator('#scenario-select').select_option(scenario)
                page.locator('#scenario-vehicle').select_option('EV02')
                page.locator('section').filter(has=page.locator('#scenario-select')).locator('button').click()
                wait(lambda s: s['scenario']['name'] == scenario and s['scenario']['status'] == 'TRIGGERED')
            page.get_by_role('button', name='RESET', exact=True).click()
            wait(lambda s: s['tick'] == 0)
            page.get_by_role('button', name='START', exact=True).click()
            wait(lambda s: ev(s, 'EV01')['state'] == 'CHARGING')
            assert not errors, errors
            output = ROOT / 'reports' / 'dashboard'
            output.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(output / 'controls_arrivals_soc.png'), full_page=True)
            browser.close()
    finally:
        for process in (web, simulator, bridge):
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
