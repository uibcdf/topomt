"""Frozen analytic-task receiving preserves every original request and interval."""

import hashlib
import json
import zipfile
from pathlib import Path

from devtools.reference_validator.model import decode_scalar
from devtools.reference_validator.volume_request import VolumeRequest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'devguide/evidence/reference_validator_parallel_edge_v1'


def scientific(result):
    return {
        k: v
        for k, v in result.items()
        if k not in {'verifier_files_sha256', 'python_version'}
    }


def test_frozen_task_capsule_preserves_all_original_mathematical_results():
    manifest = json.loads((BASE / 'capsule_manifest.json').read_text())
    archive = BASE / 'receiving.zip'
    assert (
        hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256']
    )
    index = json.loads((BASE / 'receiving_index.json').read_text())
    assert len(index['originals']) == 6 and len(index['controls']) == 50
    assert len({r['name'] for r in index['controls']}) == 25
    with zipfile.ZipFile(archive) as saved:
        assert len(saved.namelist()) == len(set(saved.namelist()))
        assert set(saved.namelist()) == set(manifest['members'])
        for name, digest in manifest['members'].items():
            assert not name.startswith('/') and '..' not in Path(name).parts
            assert hashlib.sha256(saved.read(name)).hexdigest() == digest
        source = json.loads((BASE / 'source.json').read_text())
        assert len(source) == 51
        assert all(manifest['members'][n] == h for n, h in source.items())
        for row in index['originals'] + index['controls']:
            p = ROOT / row['protocol']
            assert hashlib.sha256(p.read_bytes()).hexdigest() == row['protocol_sha256']
            spec = json.loads(p.read_text())
            for obj in spec['inputs'].values():
                assert (
                    hashlib.sha256((ROOT / obj['path']).read_bytes()).hexdigest()
                    == obj['sha256']
                )
            prefix = row['receiving_prefix']
            result = json.loads(saved.read(prefix + '/session_verification.json'))
            checked = json.loads(saved.read(prefix + '/serial_verification.json'))
            reference = json.loads(
                (ROOT / spec['inputs']['reference']['path']).read_text()
            )
            cert = json.loads(
                (ROOT / spec['inputs']['certificate']['path']).read_text()
            )
            assert scientific(result) == scientific(checked) == scientific(reference)
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


def test_original_recovery_phases_are_bounded_and_partial_work_has_no_total():
    index = json.loads((BASE / 'receiving_index.json').read_text())
    with zipfile.ZipFile(BASE / 'receiving.zip') as saved:
        for row in index['originals']:
            folder = (ROOT / row['protocol']).parent
            for phase in ['partial', 'resume', 'read']:
                execution = json.loads(
                    (folder / (phase + '_execution.json')).read_text()
                )
                assert execution['exit_code'] == 0 and execution['stop_reason'] is None
                assert len(execution['cpu_affinity']) == (
                    1 if row['configuration'] == 'serial' else 2
                )
                assert execution['address_space_bytes'] == 2 * 1024**3
                assert all(s['host']['safe'] for s in execution['samples'])
            partial = json.loads(
                saved.read(row['receiving_prefix'] + '/partial/progress.json')
            )
            assert len(partial['items']) == 2
            assert 'volume_lower' not in partial and 'precision_status' not in partial
            assert row['all_mathematical_fields_equal_original_and_serial']


def test_extracted_parallel_checker_and_saved_reader_run_without_producers(tmp_path):
    import os
    import signal
    import subprocess
    import sys

    prefix = 'original/regular_tetrahedron/parallel2/receiving/'
    selected = {
        'inputs/original/regular_tetrahedron/model.json',
        'inputs/original/regular_tetrahedron/certificate.json',
        prefix + 'partial/progress.json',
        prefix + 'partial/MANIFEST.json',
    }
    with zipfile.ZipFile(BASE / 'receiving.zip') as saved:
        for name in saved.namelist():
            if name.startswith('devtools/') or name in selected:
                saved.extract(name, tmp_path)
    script = tmp_path / 'replay.py'
    script.write_text("""import importlib.abc,json,os,pathlib,resource,sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        names=('topomt','numpy','scipy','molsysmt','pyunitwizard','ackredit',
            'devtools.reference_validator.power_cells',
            'devtools.reference_validator.edge_volume',
            'devtools.reference_validator.parallel_runs',
            'devtools.reference_validator.boundary_volume',
            'devtools.reference_validator.region_volume',
            'devtools.reference_validator.producer')
        if any(fullname==n or fullname.startswith(n+'.') for n in names):
            raise ImportError('Producer/scientific import: '+fullname)
sys.meta_path.insert(0,Block())
def main():
    os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:2]))
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    resource.setrlimit(resource.RLIMIT_CPU,(30,30))
    from devtools.reference_validator.model import Model
    from devtools.reference_validator.edge_tasks import EdgeVerificationSession
    from devtools.reference_validator.parallel import LocalPolicy
    from devtools.reference_validator.verify import verify
    from devtools.reference_validator.verify.edge_progress import check_progress
    read=lambda name:json.loads(pathlib.Path(name).read_text())
    model=Model.from_record(read('inputs/original/regular_tetrahedron/model.json'))
    cert=read('inputs/original/regular_tetrahedron/certificate.json')
    partial=pathlib.Path('original/regular_tetrahedron/parallel2/receiving/partial')
    assert check_progress(model,read(partial/'progress.json'))['completed_pieces']==2
    session=EdgeVerificationSession.from_bundle(model,partial)
    session.advance(piece_budget=4096,policy=LocalPolicy(workers=2))
    result=session.finish();serial=verify(model,cert)
    strip=lambda v:{k:x for k,x in v.items() if k!='verifier_files_sha256'}
    assert strip(result)==strip(serial) and result['precision_status']=='resolved'
if __name__=='__main__':main()
""")
    process = subprocess.Popen(
        [sys.executable, '-S', str(script)],
        cwd=tmp_path,
        env={**os.environ, 'PYTHONPATH': str(tmp_path)},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    try:
        output = process.communicate(timeout=35)[0]
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
        raise
    assert process.returncode == 0, output
