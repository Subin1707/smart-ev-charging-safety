"""Golden production C -> monitor -> event -> API telemetry chain."""
import json
from pathlib import Path
from conftest import post, wait_until

def test_golden_ev03_overheat(simulator):
    def ev(state):
        return next(v for v in state['vehicles'] if v['id'] == 'EV03')

    post('/api/start')
    before = wait_until(lambda s: s['simulation']['status'] == 'RUNNING' and s['tick'] >= 1
                        and ev(s)['state'] == 'CHARGING' and ev(s)['allocatedPower'] > 0)
    assert ev(before)['assignedPort'] == 3
    assert ev(before)['authenticated'] is True
    codes = [e['code'] for e in before['events'] if e['vehicleId'] == 'EV03']
    assert codes.index('VEHICLE_CONNECTED') < codes.index('AUTH_SUCCESS') < codes.index('CHARGING_STARTED')
    response = post('/api/fault', json={'vehicleId': 'EV03', 'faultType': 'OVERHEAT'})
    assert response['accepted']
    after = wait_until(lambda s: ev(s)['state'] == 'FAULT' and any(
        e['code'] == 'OVERHEAT_TRIP' and e['vehicleId'] == 'EV03' for e in s['events']))
    assert ev(after)['allocatedPower'] == 0
    assert ev(after)['temperature'] >= 60
    assert any(e['code'] == 'OVERHEAT_TRIP' and e['vehicleId'] == 'EV03' and e['severity'] == 'CRITICAL' for e in after['events'])
    assert after['station']['totalPower'] <= after['station']['maxPower']
    output = Path(__file__).resolve().parents[2] / 'evidence' / '06_e2e'
    output.mkdir(parents=True, exist_ok=True)
    for name, state in [('golden_before', before), ('golden_after', after)]:
        (output / (name + '.json')).write_text(json.dumps(state, indent=2), encoding='utf-8')
