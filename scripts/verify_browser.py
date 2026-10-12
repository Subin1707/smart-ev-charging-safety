"""Real browser + live bridge + production simulator golden scenario."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone
import requests
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/06_e2e'
API = 'http://127.0.0.1:8021'

def wait_for(predicate, timeout=20):
    end = time.monotonic()+timeout
    while time.monotonic() < end:
        try:
            result = predicate()
            if result:
                return result
        except requests.RequestException:
            pass
        time.sleep(0.1)
    raise AssertionError('Golden browser scenario timed out')

def state():
    response = requests.get(API+'/api/state', timeout=2)
    response.raise_for_status()
    return response.json()

def vehicle(snapshot):
    return next(v for v in snapshot['vehicles'] if v['id'] == 'EV03')

def post(path, **kwargs):
    response = requests.post(API+path, timeout=3, **kwargs)
    response.raise_for_status()

def main():
    started = datetime.now(timezone.utc).isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    processes, files = [], []
    env = dict(os.environ, SMART_EV_SCENARIO='GOLDEN_OVERHEAT', VITE_BRIDGE_BASE_URL=API,
               VITE_SIMULATION_MODE='backend')
    env['SMART_EV_POSTGRES'] = '0'
    try:
        probe = subprocess.run(['docker', 'exec', 'smart_ev_database', 'pg_isready', '-U', 'smart_ev_user'],
                               capture_output=True, timeout=5)
        if probe.returncode == 0:
            env['SMART_EV_POSTGRES'] = '1'
    except (OSError, subprocess.TimeoutExpired):
        pass
    try:
        for name, command in [
            ('browser_bridge', [sys.executable, '-m', 'uvicorn', 'bridge.main:app', '--host', '127.0.0.1', '--port', '8021']),
            ('browser_web', ['node', 'web/node_modules/vite/bin/vite.js', 'web', '--host', '127.0.0.1', '--port', '5178', '--strictPort'])]:
            log = (OUT/(name+'.log')).open('w', encoding='utf-8')
            files.append(log)
            processes.append(subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=log))
        wait_for(lambda: requests.get(API+'/api/health', timeout=1).ok)
        wait_for(lambda: requests.get('http://127.0.0.1:5178', timeout=1).ok)
        (ROOT/'logs/telemetry/latest_state.json').unlink(missing_ok=True)
        exe = ROOT / ('bin/smart_ev.exe' if os.name == 'nt' else 'bin/smart_ev')
        log = (OUT/'browser_simulator.log').open('w', encoding='utf-8')
        files.append(log)
        sim = subprocess.Popen([str(exe)], cwd=ROOT, env=env, stdin=subprocess.PIPE, stdout=log, stderr=log, text=True)
        processes.append(sim)
        sim.stdin.write('2\n')
        sim.stdin.flush()
        wait_for(lambda: state().get('tick') == 0)
        before = state()
        assert vehicle(before)['soc'] == 12 and vehicle(before)['temperature'] == 35
        assert vehicle(before)['state'] == 'CHARGING' and vehicle(before)['allocatedPower'] > 0
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1600, 'height': 1100})
            errors = []
            page.on('pageerror', lambda exc: errors.append(str(exc)))
            page.goto('http://127.0.0.1:5178')
            post('/api/fault', json={'vehicleId': 'EV03', 'faultType': 'OVERHEAT'})
            wait_for(lambda: any(e['code'] == 'OVERHEAT_INJECTED' and e['vehicleId'] == 'EV03' for e in state()['events']))
            post('/api/tick')
            wait_for(lambda: vehicle(state())['state'] == 'FAULT')
            after = state()
            assert vehicle(after)['allocatedPower'] == 0
            expect(page.locator('.event-code').filter(has_text='OVERHEAT_TRIP')).to_be_visible(timeout=15000)
            page.locator('.map-vehicle').filter(has=page.locator('svg[aria-label="EV03 electric vehicle"]')).press('Enter')
            expect(page.locator('.vehicle-inspector-state')).to_have_text('FAULT')
            expect(page.locator('.vehicle-inspector-alert')).to_contain_text('Charging stopped')
            page.screenshot(path=str(OUT/'golden_dashboard.png'), full_page=True)
            page.locator('.vehicle-inspector').screenshot(path=str(OUT/'golden_vehicle_inspector.png'))
            page.locator('.event-code').filter(has_text='OVERHEAT_TRIP').scroll_into_view_if_needed()
            page.locator('.event-card').screenshot(path=str(OUT/'golden_event_timeline.png'))
            assert not errors, errors
            browser.close()
        (OUT/'browser_golden.json').write_text(json.dumps({'status': 'PASS', 'startedAt': started, 'before': before, 'after': after,
            'browserErrors': errors, 'postgresql': 'NOT_VERIFIED'}, indent=2), encoding='utf-8')
        print('PASS: live EV03 -> OVERHEAT_TRIP -> FAULT, zero power -> browser inspector and screenshot')
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                try:
                    if process.stdin is not None and process.stdin.writable():
                        process.stdin.write('0\n')
                        process.stdin.flush()
                except (BrokenPipeError, ValueError, OSError):
                    pass
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
        for stream in files:
            stream.close()

if __name__ == '__main__':
    main()
