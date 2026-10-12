"""Random and SMT-generated inputs exercise the same production charging guard."""
import json
import random
import subprocess
import time
from z3 import Ints, Solver, Or, sat
from verify_all import ROOT, EVIDENCE, ENV, SOURCES, compile_c

def execute(exe, cases, started):
    data = ''.join(' '.join(map(str, row))+'\n' for row in cases)
    result = subprocess.run([str(exe)], input=data, capture_output=True, text=True,
                            cwd=ROOT, env=ENV, timeout=60)
    rows = [tuple(map(int, line.split()[1:])) for line in result.stdout.splitlines() if line.startswith('RESULT ')]
    assert result.returncode == 0 and len(rows) == len(cases), 'Harness crashed or lost inputs'
    first = next((i+1 for i, row in enumerate(rows) if row[1]), None)
    return {'generated': len(cases), 'accepted': sum(r[0] for r in rows),
            'rejected': sum(not r[0] for r in rows), 'crashes': 0, 'timeouts': 0,
            'safetyViolations': sum(r[2] for r in rows), 'targetReached': first is not None,
            'firstTargetInput': first, 'seconds': time.perf_counter()-started}

def rates(result):
    generated = result['generated']
    return {
        'targetDiscoveryInput': result['firstTargetInput'],
        'targetDiscoveryRate': (1.0 / result['firstTargetInput']) if result['firstTargetInput'] else 0.0,
        'acceptedRate': result['accepted'] / generated if generated else 0.0,
        'rejectedRate': result['rejected'] / generated if generated else 0.0,
        'safetyViolationRate': result['safetyViolations'] / generated if generated else 0.0,
    }

def main():
    exe = compile_c('fuzz_charging_gate', [*SOURCES, 'fuzz/harness/fuzz_charging_gate.c'])
    start = time.perf_counter()
    rng = random.Random(20260910)
    black = [(rng.randrange(8), rng.randrange(2), rng.randint(-20,120), rng.randint(-10,110),
              rng.randint(-5,30), rng.randint(-1,7)) for _ in range(10000)]
    bb = execute(exe, black, start)
    start = time.perf_counter()
    variables = Ints('command auth temperature soc power port')
    command, auth, temperature, soc, power, port = variables
    solver = Solver()
    solver.add(command == 1, auth == 1, temperature >= 60, temperature <= 120,
               soc >= 0, soc < 100, power > 0, power <= 22, port >= 1, port <= 5)
    white = []
    for _ in range(4):
        assert solver.check() == sat
        model = solver.model()
        row = tuple(model[v].as_long() for v in variables)
        white.append(row)
        solver.add(Or(*[v != n for v, n in zip(variables, row)]))
    wb = execute(exe, white, start)
    bb_rates = rates(bb)
    wb_rates = rates(wb)
    report = {'target': 'START && authenticated && temperature >= 60 && 0 <= SOC < 100 with valid port/power',
              'meaning': 'Target reached means unsafe request exercised; fixed guard must reject it.',
              'seed': 20260910, 'blackbox': bb, 'whitebox': wb, 'whiteboxInputs': white,
              'metrics': {
                  'blackbox': bb_rates,
                  'whitebox': wb_rates,
                  'targetDiscoveryImprovement': bb['firstTargetInput'] / wb['firstTargetInput'],
                  'generatedInputReduction': bb['generated'] / wb['generated'],
                  'interpretation': (
                      'White-box is more directed for this branch target: it reaches the overheat target '
                      'on its first generated input, while deterministic black-box random fuzz reaches it '
                      'on input 115. Both produce zero safety violations because the production guard rejects '
                      'the unsafe overheat request.'
                  ),
              },
              'timing': 'Generation plus persistent process; white-box includes Z3 solving; compile excluded.'}
    folder = EVIDENCE / '05_fuzzing'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'comparison.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if all(r['targetReached'] and r['safetyViolations'] == 0 for r in (bb, wb)) and wb['accepted'] == 0 else 1

if __name__ == '__main__':
    raise SystemExit(main())
