"""Four-worker observations preserve exact science and the prior expansion gate."""

import hashlib
import json
import os
import statistics
import subprocess
import sys
import zipfile
from pathlib import Path

from devtools.reference_validator.model import decode_scalar
from devtools.reference_validator.volume_request import VolumeRequest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'devguide/evidence/reference_validator_four_worker_v1'


def test_preregistered_expansion_gate_is_recomputed_from_actual_repetitions():
    plan = json.loads((BASE / 'plan.json').read_text())
    decision = json.loads((BASE / 'expansion_decision.json').read_text())
    assert decision['frozen_criterion'] == plan['conditional_expansion']
    times = decision['bounded_elapsed_seconds']
    assert all(len(v) == 3 for v in times.values())
    gain = 1 - statistics.median(times['parallel4']) / statistics.median(
        times['parallel2']
    )
    assert gain == decision['elapsed_reduction_4_vs_2']
    assert (
        gain >= plan['conditional_expansion']['median_elapsed_reduction_4_vs_2_minimum']
    )
    assert max(times['parallel4']) < min(times['parallel2'])
    assert decision['actual_worker_counts_at_largest_pools'] == [4, 4, 4]
    assert decision['sampled_task_worker_niceness_range'] == [10, 10]
    assert decision['execute_conditional_multiregion'] is True
    for name, digest in decision['input_receipts_sha256'].items():
        with zipfile.ZipFile(BASE / 'receiving.zip') as saved:
            assert hashlib.sha256(saved.read(name)).hexdigest() == digest


def test_capsule_keeps_all_mathematical_results_and_precision_requests():
    manifest = json.loads((BASE / 'capsule_manifest.json').read_text())
    archive = BASE / 'receiving.zip'
    assert (
        hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256']
    )
    plan = json.loads((BASE / 'plan.json').read_text())
    assert len(plan['jobs']) == 52 and len(plan['reads']) == 28
    with zipfile.ZipFile(archive) as saved:
        assert set(saved.namelist()) == set(manifest['members'])
        assert len(saved.namelist()) == len(set(saved.namelist()))
        for n, h in manifest['members'].items():
            assert not n.startswith('/') and '..' not in Path(n).parts
            assert hashlib.sha256(saved.read(n)).hexdigest() == h
        assert all(manifest['members'][n] == h for n, h in plan['source_files'].items())

        def strip(value):
            return {
                k: x
                for k, x in value.items()
                if k not in {'verifier_files_sha256', 'python_version'}
            }

        for row in plan['jobs']:
            spec = json.loads(saved.read(row['protocol']))
            assert (
                hashlib.sha256(saved.read(row['protocol'])).hexdigest() == row['sha256']
            )
            for obj in spec['inputs'].values():
                assert (
                    hashlib.sha256(saved.read(obj['path'])).hexdigest() == obj['sha256']
                )
            folder = str(Path(row['protocol']).parent / 'receiving')
            result = json.loads(saved.read(folder + '/verification.json'))
            reference = json.loads(saved.read(spec['inputs']['reference']['path']))
            cert = json.loads(saved.read(folder + '/certificate.json'))
            assert strip(result) == strip(reference)
            assert cert == json.loads(saved.read(spec['inputs']['certificate']['path']))
            request = VolumeRequest.from_record(cert['request'])
            assert result['precision_status'] == 'resolved'
            assert request.satisfied(
                decode_scalar(result['volume_lower']),
                decode_scalar(result['volume_upper']),
            )
            assert all(
                request.satisfied(decode_scalar(r['lower']), decode_scalar(r['upper']))
                for r in result['regions']
            )
        for row in plan['reads']:
            spec = json.loads(saved.read(row['protocol']))
            checked = json.loads(
                saved.read(
                    str(Path(row['protocol']).parent / 'receiving/verification.json')
                )
            )
            for job in spec['configurations']:
                result = json.loads(
                    saved.read(
                        str(
                            Path(job['protocol']).parent / 'receiving/verification.json'
                        )
                    )
                )
                assert strip(checked) == strip(result)


def test_bounded_resources_real_workers_and_lower_priority_are_retained():
    plan = json.loads((BASE / 'plan.json').read_text())
    index = json.loads((BASE / 'receiving_index.json').read_text())
    assert index['scientific_commands'] == 80 and index['default_mode'] == 'serial'
    assert (
        index['general_scaling_claim'] is False
        and index['zero_impact_guarantee'] is False
    )
    for row in plan['execution_order']:
        spec = json.loads((ROOT / row['protocol']).read_text())
        e = json.loads(((ROOT / row['protocol']).parent / 'execution.json').read_text())
        assert e['exit_code'] == 0 and e['stop_reason'] is None
        assert len(e['cpu_affinity']) == spec['cpus'] <= 4
        assert e['address_space_bytes'] == 2 * 1024**3 and e['cpu_soft_seconds'] == 300
        assert all(s['host']['safe'] for s in e['samples'])
    large = [
        r
        for r in index['entries']
        if r['phase'] in {'pilot_large', 'conditional_multiregion'}
        and r.get('mode') == 'parallel4'
    ]
    assert len(large) == 6
    assert all(r['largest_observed_task_worker_inventory'] == 4 for r in large)
    assert all(r['sampled_task_worker_niceness_range'] == [10, 10] for r in large)
    assert all(r['niceness'] >= 10 for r in index['entries'])


def test_fresh_extracted_four_worker_capsule_has_an_independent_serial_reader(tmp_path):
    with zipfile.ZipFile(BASE / 'receiving.zip') as saved:
        saved.extractall(tmp_path)
    code = """
import os,resource,runpy,sys
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
resource.setrlimit(resource.RLIMIT_CPU,(15,15))
sys.argv=['drivers/worker.py','read',
 'devguide/evidence/reference_validator_four_worker_v1/pilot_small/original/regular_tetrahedron/profile_1/saved_read/protocol.json','fresh_read']
runpy.run_path('drivers/worker.py',run_name='__main__')
"""
    p = subprocess.run(
        [sys.executable, '-S', '-c', code],
        cwd=tmp_path,
        env={**os.environ, 'PYTHONPATH': str(tmp_path)},
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert p.returncode == 0, p.stdout + p.stderr
    result = json.loads((tmp_path / 'fresh_read/verification.json').read_text())
    assert result['n_components'] == 1 and result['precision_status'] == 'resolved'
