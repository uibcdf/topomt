"""Actual finite-worker receiving keeps source proofs and operational evidence."""

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'devguide/evidence/reference_validator_parallel_resume_v1'


def test_parallel_receiving_capsule_binds_all_original_proofs_and_partial_work():
    manifest = json.loads((BASE / 'capsule_manifest.json').read_text())
    archive = BASE / 'receiving.zip'
    assert (
        hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256']
    )
    index = json.loads((BASE / 'receiving_index.json').read_text())
    assert len(index['jobs']) == 6
    assert {r['case'] for r in index['jobs']} == {
        'regular_tetrahedron',
        'closed_shell',
        'dumbbell',
    }
    assert {r['workers'] for r in index['jobs']} == {1, 2}
    with zipfile.ZipFile(archive) as saved:
        assert len(set(saved.namelist())) == len(saved.namelist())
        assert set(saved.namelist()) == set(manifest['members'])
        for name, digest in manifest['members'].items():
            assert not name.startswith('/') and '..' not in Path(name).parts
            assert hashlib.sha256(saved.read(name)).hexdigest() == digest
        source = json.loads((BASE / 'source.json').read_text())
        assert len(source) == 49
        assert all(
            manifest['members'][name] == digest for name, digest in source.items()
        )
        for row in index['jobs']:
            protocol = json.loads((ROOT / row['protocol']).read_text())
            expected = ROOT / protocol['expected_certificate']
            assert (
                hashlib.sha256(expected.read_bytes()).hexdigest()
                == protocol['expected_certificate_sha256']
            )
            prefix = row['receiving_prefix']
            assert (
                json.loads(saved.read('models/' + row['case'] + '.json'))
                == protocol['model']
            )
            cert = json.loads(saved.read(prefix + '/complete_certificate.json'))
            assert cert == json.loads(expected.read_text())
            result = json.loads(saved.read(prefix + '/fresh_verification.json'))
            assert result['verification_status'] == 'accepted'
            assert result['topology_complete'] is True
            assert (
                result['n_components']
                == {'regular_tetrahedron': 1, 'closed_shell': 1, 'dumbbell': 3}[
                    row['case']
                ]
            )
            partial = json.loads(
                saved.read(prefix + '/partial_cancelled/progress.json')
            )
            assert len(partial['cells']) == 2
            assert partial['stop_reason'] == 'cancelled'
            assert partial['model_sha256'] == cert['model_sha256']
            complete = json.loads(saved.read(prefix + '/complete_cells/progress.json'))
            assert complete['stop_reason'] == 'cells_complete'
            assert [r['source_index'] for r in complete['cells']] == list(
                range(len(protocol['model']['atoms']))
            )
            assert [r['cell'] for r in complete['cells']] == cert['cells']


def test_all_receiving_phases_respect_limits_and_preserve_failed_attempt():
    index = json.loads((BASE / 'receiving_index.json').read_text())
    for job in index['jobs']:
        for name in ['partial', 'resume', 'verify']:
            folder = (ROOT / job['protocol']).parent
            execution = json.loads((folder / (name + '_execution.json')).read_text())
            assert execution['exit_code'] == 0 and execution['stop_reason'] is None
            assert len(execution['cpu_affinity']) == job['workers']
            assert execution['address_space_bytes'] == 2 * 1024**3
            assert all(s['host']['safe'] for s in execution['samples'])
    attempt = json.loads(
        (BASE / 'closed_shell/workers_1/resume_execution.json').read_text()
    )
    assert attempt['exit_code'] != 0
    assert (
        'BrokenProcessPool'
        in (BASE / 'closed_shell/workers_1/resume_execution.log').read_text()
    )


def test_extracted_partial_and_final_readers_need_no_producer_or_site_packages(
    tmp_path,
):
    import os
    import subprocess
    import sys

    prefix = 'regular_tetrahedron/workers_2/receiving/'
    selected = {
        'models/regular_tetrahedron.json',
        prefix + 'partial_cancelled/progress.json',
        prefix + 'complete_certificate.json',
    }
    with zipfile.ZipFile(BASE / 'receiving.zip') as saved:
        for name in saved.namelist():
            if name.startswith('devtools/') or name in selected:
                saved.extract(name, tmp_path)
    code = """
import importlib.abc,json,pathlib,sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        names=('topomt','numpy','scipy','molsysmt',
            'devtools.reference_validator.parallel',
            'devtools.reference_validator.parallel_runs',
            'devtools.reference_validator.power_cells')
        if any(fullname==n or fullname.startswith(n+'.') for n in names):
            raise ImportError('Producer/scientific import: '+fullname)
sys.meta_path.insert(0,Block())
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify import verify
from devtools.reference_validator.verify.parallel_progress import check_progress
import devtools.reference_validator.verify.parallel_progress as reader
assert pathlib.Path(reader.__file__).resolve().is_relative_to(pathlib.Path.cwd())
read=lambda name:json.loads(pathlib.Path(name).read_text())
model=Model.from_record(read('models/regular_tetrahedron.json'))
prefix='regular_tetrahedron/workers_2/receiving/'
partial=check_progress(model,read(prefix+'partial_cancelled/progress.json'))
assert partial['n_components'] is None and not partial['topology_complete']
assert len(partial['completed_source_indices'])==2
complete=verify(model,read(prefix+'complete_certificate.json'))
assert complete['topology_complete'] and complete['n_components']==1
"""
    result = subprocess.run(
        [sys.executable, '-S', '-c', code],
        cwd=tmp_path,
        env={**os.environ, 'PYTHONPATH': str(tmp_path)},
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
