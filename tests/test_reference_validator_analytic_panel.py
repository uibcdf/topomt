"""The expanded analytic panel preserves original proofs, precision and scope."""

import hashlib
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

from devtools.reference_validator.model import decode_scalar
from devtools.reference_validator.volume_request import VolumeRequest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'devguide/evidence/reference_validator_analytic_panel_v1'
PREFIX = 'devguide/evidence/reference_validator_analytic_panel_v1/'


def scientific(value):
    return {
        k: v
        for k, v in value.items()
        if k not in {'verifier_files_sha256', 'python_version'}
    }


def test_full_panel_preserves_all_original_and_control_mathematical_fields():
    manifest = json.loads((BASE / 'capsule_manifest.json').read_text())
    archive = BASE / 'receiving.zip'
    assert (
        hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256']
    )
    plan = json.loads((BASE / 'plan.json').read_text())
    assert len(plan['jobs']) == 92 and len(plan['reads']) == 44
    assert len({r['name'] for r in plan['jobs'] if r['category'] == 'original'}) == 19
    assert len({r['name'] for r in plan['jobs'] if r['category'] == 'controls'}) == 25
    with zipfile.ZipFile(archive) as saved:
        assert len(saved.namelist()) == len(set(saved.namelist()))
        assert set(saved.namelist()) == set(manifest['members'])
        for name, digest in manifest['members'].items():
            assert not name.startswith('/') and '..' not in Path(name).parts
            assert hashlib.sha256(saved.read(name)).hexdigest() == digest
        assert len(plan['source_files']) == 51
        assert all(manifest['members'][n] == h for n, h in plan['source_files'].items())
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
            assert cert == json.loads(saved.read(spec['inputs']['certificate']['path']))
            assert scientific(result) == scientific(reference)
            assert result['precision_status'] == 'resolved'
            request = VolumeRequest.from_record(cert['request'])
            assert request.satisfied(
                decode_scalar(result['volume_lower']),
                decode_scalar(result['volume_upper']),
            )
            assert all(
                request.satisfied(decode_scalar(r['lower']), decode_scalar(r['upper']))
                for r in result['regions']
            )
        for row in plan['reads']:
            folder = str(Path(row['protocol']).parent / 'receiving')
            checked = json.loads(saved.read(folder + '/verification.json'))
            spec = json.loads(saved.read(row['protocol']))
            for job in spec['configurations']:
                result = json.loads(
                    saved.read(
                        str(
                            Path(job['protocol']).parent / 'receiving/verification.json'
                        )
                    )
                )
                assert scientific(checked) == scientific(result)


def test_full_panel_retains_bounded_resources_and_single_observation_limits():
    index = json.loads((BASE / 'receiving_index.json').read_text())
    assert index['original_profiles'] == 19 and index['analytic_controls'] == 25
    assert index['shared_saved_reads'] == 44
    assert index['source_generation_reexecuted'] is False
    assert index['general_scaling_claim'] is False
    assert index['default_mode'] == 'serial'
    plan = json.loads((BASE / 'plan.json').read_text())
    for row in plan['jobs'] + plan['reads']:
        folder = (ROOT / row['protocol']).parent
        record = json.loads((folder / 'execution.json').read_text())
        assert record['exit_code'] == 0 and record['stop_reason'] is None
        assert len(record['cpu_affinity']) == (
            2 if row.get('mode') == 'parallel2' else 1
        )
        assert record['address_space_bytes'] == 2 * 1024**3
        assert record['cpu_soft_seconds'] == 300
        assert all(s['host']['safe'] for s in record['samples'])
    repeated = [r for r in plan['jobs'] if r['repeat'] > 0]
    assert len(repeated) == 4
    assert {r['name'] for r in repeated} == {'original/regular_tetrahedron/profile_1'}


def test_extracted_panel_has_a_fresh_producer_free_serial_reader(tmp_path):
    with zipfile.ZipFile(BASE / 'receiving.zip') as saved:
        saved.extractall(tmp_path)
    code = """
import os,resource,runpy,sys
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
resource.setrlimit(resource.RLIMIT_CPU,(15,15))
sys.argv=['drivers/worker.py','read',
    'devguide/evidence/reference_validator_analytic_panel_v1/original/regular_tetrahedron/profile_1/saved_read/protocol.json',
    'fresh_read']
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
