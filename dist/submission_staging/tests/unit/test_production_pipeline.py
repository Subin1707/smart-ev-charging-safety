"""Regression checks for production contracts and evidence isolation."""
import copy
import json
from pathlib import Path

import pytest

from spec_generator.core.analyzer import analyze_requirement, build_ir
from spec_generator.core.code_mapping import load_production_mapping, validate_mapping
from spec_generator.core.production_harness_generator import generate_production_harness
from spec_generator.core.spec_reader import read_requirements
from spec_generator.core.static_generator import generate_z3
from spec_generator.core.traceability_generator import build_traceability, save_traceability_csv
from spec_generator import pipeline

ROOT = Path(__file__).resolve().parents[2]


def demo_irs():
    return [build_ir(analyze_requirement(r)) for r in read_requirements(ROOT / 'spec_generator/input/production_demo.txt')]


def test_power_limits_are_two_distinct_variables():
    ir = demo_irs()[0]
    assert ir['expected']['logic'] == 'AND'
    assert [x['variable'] for x in ir['expected']['conditions']] == ['total_power', 'port_power']
    assert [x['value'] for x in ir['expected']['conditions']] == [100, 22]


def test_nested_mapping_cannot_ignore_unmapped_variable():
    ir = demo_irs()[1]
    mapping = load_production_mapping()
    del mapping['variables']['charging']
    assert validate_mapping(ir, mapping)['missing'] == ['charging']
    source, status = generate_production_harness(ir, mapping)
    assert source is None and status['status'] == 'PARTIALLY_MAPPED'


def test_access_only_mapping_never_generates_uninitialized_harness():
    mapping = load_production_mapping()
    mapping['harnesses'] = {}
    source, status = generate_production_harness(demo_irs()[0], mapping)
    assert source is None
    assert status['status'] == 'PARTIALLY_MAPPED'


def test_missing_enum_mapping_fails_closed():
    mapping = load_production_mapping()
    mapping['enums'] = {}
    source, status = generate_production_harness(demo_irs()[1], mapping)
    assert source is None
    assert status['status'] == 'INVALID_MAPPING'


def test_trigger_is_saved_before_monitor_and_all_ports_are_checked():
    mapping = load_production_mapping()
    overheat, _ = generate_production_harness(demo_irs()[1], mapping)
    assert overheat.index('const bool trigger_before') < overheat.index('(void)giam_sat_xe_va_cong') < overheat.index('if (trigger_before)')
    assert 'cong->trang_thai == CONG_LOI' in overheat
    power, _ = generate_production_harness(demo_irs()[0], mapping)
    assert 'port_index < SO_CONG_SAC' in power
    assert 'tram->cong[port_index].cong_suat_kw <= 22.0f' in power


@pytest.mark.parametrize('index', [0, 1, 2])
def test_production_harness_links_and_executes_real_sources(index, tmp_path, monkeypatch):
    ir = demo_irs()[index]
    source, status = generate_production_harness(ir, load_production_mapping())
    path = tmp_path / f"{ir['requirement_id']}.c"
    path.write_text(source)
    monkeypatch.setattr(pipeline, 'resolve_tool', lambda _: None)
    result = pipeline.verify_production(path, status)
    assert [t['status'] for t in result['tools']] == ['PASS', 'PASS', 'UNAVAILABLE'], result
    assert f"PRODUCTION_CASES={status['native_cases']}" in result['tools'][1]['stdout']


def test_z3_can_find_violation_of_either_soc_bound(tmp_path):
    import subprocess
    import sys
    path = tmp_path / 'soc_z3.py'
    path.write_text(generate_z3(demo_irs()[2]))
    result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout.strip() == 'sat'


def test_pipeline_preserves_per_requirement_per_tool_results(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, 'ROOT', tmp_path)
    mapping_path = ROOT / 'spec_generator/input/code_mapping.json'
    monkeypatch.setattr(pipeline, 'verify_artifacts', lambda _: {'tools': [{'tool':'pytest','status':'PASS'}]})
    statuses = iter(['PASS', 'FAIL', 'UNAVAILABLE'])
    def verify(path, mapping):
        return {'tools': [{'tool':'gcc','status':'PASS'}, {'tool':'cbmc','status':next(statuses)}]}
    monkeypatch.setattr(pipeline, 'verify_production', verify)
    result = pipeline.run_pipeline(ROOT / 'spec_generator/input/production_demo.txt', mapping_path)
    rows = json.loads((tmp_path / 'evidence/generation/manifest.json').read_text())
    assert [r['result'] for r in rows] == ['PASS', 'FAIL', 'INCONCLUSIVE']
    assert all(r['mapping']['status'] == 'MAPPED' for r in rows)
    assert result['summary']['coverage']['production_mapping'] == 1
    assert rows[2]['verification_tools'][-2:] == [{'name':'gcc','status':'PASS','level':'production'}, {'name':'cbmc','status':'UNAVAILABLE','level':'production'}]
    assert all(r['production_sources'] and r['generated_artifacts'] for r in rows)
    assert all('production' in r['artifacts'] and 'cbmc' in r['artifacts'] for r in rows)


def test_artifact_selection_does_not_mix_prefix_ids():
    assert pipeline._belongs(Path('SR10_cbmc.c'), 'SR10')
    assert not pipeline._belongs(Path('SR10_cbmc.c'), 'SR1')


def test_csv_preserves_tool_status(tmp_path):
    records = build_traceability([{'requirement_id':'SR10','verification_tools':[{'name':'gcc','status':'PASS'}, {'name':'cbmc','status':'UNAVAILABLE'}]}])
    path = tmp_path / 'traceability.csv'
    save_traceability_csv(records, path)
    assert 'gcc=PASS' in path.read_text(encoding='utf-8-sig')
    assert 'cbmc=UNAVAILABLE' in path.read_text(encoding='utf-8-sig')
