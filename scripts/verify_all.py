"""Reproducible verification: fresh logs, exact exit codes, no cached PASS."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence'
BIN = ROOT / 'bin' / 'verification'
SOURCES = sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'src').rglob('*.c') if p.name != 'main.c')
INCLUDES = [arg for p in sorted((ROOT / 'src').iterdir()) if p.is_dir() for arg in ('-I', str(p))]
ENV = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')

def run(name, command, expected=0, marker=None, timeout=180, env=None):
    path = EVIDENCE / (name + '.txt')
    path.parent.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    try:
        result = subprocess.run([str(x) for x in command], cwd=ROOT, env=env or ENV,
                                capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
        output = result.stdout + result.stderr
        exit_ok = result.returncode > 0 if expected == 'findings' else result.returncode == expected
        ok = exit_ok and (marker is None or marker in output)
        status = 'PASS' if ok else 'FAIL'
        code = result.returncode
    except (OSError, subprocess.TimeoutExpired) as exc:
        output, status, code = str(exc), 'UNAVAILABLE', None
    path.write_text(json.dumps({'command': [str(x) for x in command], 'exitCode': code,
        'status': status, 'seconds': time.perf_counter()-start}, ensure_ascii=False) + '\n' + output, encoding='utf-8')
    if status != 'PASS':
        print(f'  {name}: {status} ({path.relative_to(ROOT)})', flush=True)
    return status, output

def compile_c(name, sources, compiler='gcc', flags=()):
    exe = BIN / (name + ('.exe' if os.name == 'nt' else ''))
    status, _ = run('00_build/' + name, [compiler, '-std=c17', '-Wall', '-Wextra', *INCLUDES,
                     *flags, *sources, '-o', exe])
    if status != 'PASS':
        raise RuntimeError(f'Compilation failed: {name}')
    return exe

def build():
    compile_c('smart_ev', [*SOURCES, 'src/main.c'])
    return 'PASS'

def tests():
    statuses = []
    for group in ('unit', 'integration', 'e2e'):
        for source in sorted((ROOT / 'tests' / group).glob('*.c')):
            exe = compile_c(source.stem, [*SOURCES, str(source)])
            statuses.append(run('04_tests/' + source.stem, [exe])[0])
    return aggregate(statuses)

def model():
    exe = compile_c('kripke', ['formal/kripke/kripke_sac.c'])
    return aggregate([run('01_model/properties', [exe], marker='ALL PROPERTIES HOLD')[0],
        run('01_model/export', [sys.executable, 'scripts/export_model.py'])[0]])

def static():
    statuses = []
    for kind, suffix in [('vulnerable', 'before'), ('fixed', 'after')]:
        status, output = run('02_static/pattern_' + suffix,
            [sys.executable, 'static_analysis/scripts/pattern_scanner.py', 'static_analysis/' + kind],
            expected='findings' if kind == 'vulnerable' else 0,
            marker='Total vulnerabilities found:' if kind == 'vulnerable' else 'Total vulnerabilities found: 0')
        statuses.append(status)
        status, output = run('02_static/cppcheck_' + suffix,
            ['cppcheck', '--enable=warning,performance,portability', '--error-exitcode=2',
             '--template={file}:{line}: {severity}: {message}', 'static_analysis/' + kind],
             expected=2 if kind == 'vulnerable' else 0)
        statuses.append(status)
    statuses.append(run('02_static/cppcheck_src', ['cppcheck', '--enable=warning,performance,portability',
        '--error-exitcode=2', '--suppress=missingIncludeSystem', *INCLUDES, 'src'])[0])
    return aggregate(statuses)

def memory():
    compiler = shutil.which('clang') or shutil.which('gcc')
    if not compiler:
        return 'UNAVAILABLE'
    env = dict(ENV, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1:exitcode=1', UBSAN_OPTIONS='halt_on_error=1:exitcode=1')
    if os.name == 'nt' and 'clang' in compiler:
        resource = subprocess.check_output([compiler, '-print-resource-dir'], text=True).strip()
        env['PATH'] = str(Path(resource) / 'lib' / 'windows') + os.pathsep + env.get('PATH', '')
    statuses = []
    for sanitizer, before, after, marker in [
        ('address', 'loi_id_xe', 'sua_id_xe', 'AddressSanitizer: stack-buffer-overflow'),
        ('undefined', 'loi_tinh_nang_luong', 'sua_tinh_nang_luong', 'runtime error:')]:
        for kind, source, suffix in [('vulnerable', before, 'before'), ('fixed', after, 'after')]:
            try:
                exe = compile_c(sanitizer + '_' + suffix, ['static_analysis/' + kind + '/' + source + '.c'],
                    compiler, ['-g', '-O0', '-fsanitize=' + sanitizer])
            except RuntimeError:
                statuses.append('UNAVAILABLE')
                continue
            status, output = run('02_static/' + sanitizer + '_' + suffix, [exe],
                expected=1 if kind == 'vulnerable' else 0,
                marker=marker if kind == 'vulnerable' else None, env=env)
            if kind == 'fixed' and ('runtime error:' in output or 'ERROR: AddressSanitizer' in output):
                status = 'FAIL'
            statuses.append(status)
    try:
        exe = compile_c('production_memory', [*SOURCES, 'tests/integration/test_reassigned_port.c'],
                        compiler, ['-g', '-O0', '-fsanitize=address,undefined'])
        statuses.append(run('02_static/production_memory', [exe], env=env)[0])
    except RuntimeError:
        statuses.append('UNAVAILABLE')
    return aggregate(statuses)

def smt():
    return run('03_formal/smt_results', [sys.executable, 'verification/run_smt.py'],
               marker='FINAL RESULT: NUMERIC SAFETY PROPERTIES VERIFIED')[0]

def bmc():
    cbmc = shutil.which('cbmc')
    local = ROOT / 'tools/cbmc/extracted/cbmc/bin/cbmc.exe'
    if not cbmc and local.exists():
        cbmc = str(local)
    if not cbmc:
        return 'UNAVAILABLE'
    statuses, summary = [], ['BMC: isolated C models; not a proof of the entire application.']
    for prop in ('sr02_auth', 'sr03_overheat', 'sr04_full', 'sr05_emergency', 'sr07_exclusivity', 'sr10_power_limit'):
        for kind in ('vulnerable', 'fixed'):
            stem = prop + '_' + kind
            preprocessed = BIN / (stem + '.i')
            status, _ = run('03_formal/' + stem + '_preprocess', ['gcc', '-E', '-P', 'formal/bmc/' + stem + '.c', '-o', preprocessed])
            if status == 'PASS':
                status, _ = run('03_formal/' + stem, [cbmc, '--gcc', preprocessed, '--trace', '--unwind', '12', '--unwinding-assertions'],
                    expected=10 if kind == 'vulnerable' else 0,
                    marker='VERIFICATION FAILED' if kind == 'vulnerable' else 'VERIFICATION SUCCESSFUL')
            statuses.append(status)
            summary.append(f'{prop} {kind}: {status}' + (' (expected counterexample)' if kind == 'vulnerable' else ''))
    (EVIDENCE / '03_formal/bmc_results.txt').write_text('\n'.join(summary)+'\n', encoding='utf-8')
    return aggregate(statuses)

def fuzz():
    return run('05_fuzzing/comparison', [sys.executable, 'scripts/compare_fuzzing.py'], timeout=600)[0]

def e2e():
    return run('06_e2e/results', [sys.executable, '-m', 'pytest', 'tests/e2e', '-q'], timeout=600)[0]

def frontend():
    npm = shutil.which('npm.cmd' if os.name == 'nt' else 'npm') or 'npm'
    return run('06_e2e/dashboard_build', [npm, '--prefix', 'web', 'run', 'build'])[0]

def browser():
    return run('06_e2e/browser_results', [sys.executable, 'scripts/verify_browser.py'])[0]

def postgres():
    status, _ = run('06_e2e/postgresql_preflight', ['docker', 'info', '--format', '{{.ServerVersion}}'], timeout=10)
    if status != 'PASS':
        return 'UNAVAILABLE'
    golden = EVIDENCE / '06_e2e/browser_golden.json'
    if not golden.exists():
        return 'UNAVAILABLE'
    start = datetime.fromisoformat(json.loads(golden.read_text(encoding='utf-8'))['startedAt']).isoformat()
    status, _ = run('06_e2e/postgresql', ['docker', 'exec', 'smart_ev_database', 'psql',
        '-v', 'ON_ERROR_STOP=1', '-U', 'smart_ev_user', '-d', 'smart_ev', '-At', '-c',
        "SELECT vehicle_code,event_type,severity FROM su_kien_an_toan WHERE vehicle_code='EV03' AND event_type='OVERHEAT' AND severity='CRITICAL' AND created_at >= '" + start + "'::timestamptz ORDER BY id DESC LIMIT 1;"],
        marker='EV03|OVERHEAT|CRITICAL')
    if status == 'PASS':
        data = json.loads(golden.read_text(encoding='utf-8'))
        data['postgresql'] = 'PASS'
        data['postgresqlEvidence'] = 'evidence/06_e2e/postgresql.txt'
        golden.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    return status

def aggregate(statuses):
    return 'FAIL' if 'FAIL' in statuses else 'UNAVAILABLE' if not statuses or 'UNAVAILABLE' in statuses else 'PASS'

STAGES = {'build': build, 'model': model, 'static-analysis': static, 'sanitizer-test': memory,
          'smt-test': smt, 'bmc-test': bmc, 'test': tests, 'fuzz-test': fuzz, 'e2e-test': e2e, 'dashboard': frontend,
          'browser-test': browser, 'postgres-test': postgres}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=STAGES)
    args = parser.parse_args()
    BIN.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)
    results = {}
    for name, action in STAGES.items():
        if args.stage and name != args.stage:
            continue
        print('=== ' + name + ' ===', flush=True)
        try:
            results[name] = action()
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            results[name] = 'UNAVAILABLE'
            print(str(exc), flush=True)
        print(name + ': ' + results[name], flush=True)
    report = {'generatedAt': datetime.now(timezone.utc).isoformat(), 'stages': results,
              'status': aggregate(list(results.values())),
              'scope': 'Results apply to the documented model bounds and executed inputs. Browser and PostgreSQL have separate evidence; this is not an unbounded proof of the whole C program.'}
    name = 'summary' if not args.stage else 'summary_' + args.stage
    (EVIDENCE / (name + '.json')).write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    if not args.stage:
        subprocess.run([sys.executable, 'scripts/generate_verification_summary.py'], cwd=ROOT, env=ENV, check=True)
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
