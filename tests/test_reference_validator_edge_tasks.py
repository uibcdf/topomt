"""Parallel arithmetic keeps the canonical signed frontier and error accounting."""

import json
from copy import deepcopy
from fractions import Fraction as F

import pytest

from devtools.reference_validator.edge_volume import edge_volume_proposal
from devtools.reference_validator.model import Box, Model, decode_scalar, point
from devtools.reference_validator.power_cells import topology_certificate
from devtools.reference_validator.verify import verify
from devtools.reference_validator.volume_request import VolumeRequest


def inputs(radius=F(3, 2), bits=128):
    model = Model.from_spheres(
        [(0, 0, 0)], [radius], 0, domain=Box(point((-1, -1, -1)), point((1, 1, 1)))
    )
    cert = edge_volume_proposal(
        model,
        topology_certificate(model),
        VolumeRequest(F(8, 2**32), F(1, 2**32)),
        bits=bits,
    )
    return model, cert


def scientific(result):
    return {k: v for k, v in result.items() if k != 'verifier_files_sha256'}


def test_serial_tasks_equal_complete_reader_and_partial_work_has_no_volume():
    from devtools.reference_validator.edge_tasks import EdgeVerificationSession

    m, cert = inputs()
    session = EdgeVerificationSession(m, cert)
    state = session.advance(piece_budget=2)
    assert len(state['items']) == 2 and state['stop_reason'] == 'piece_budget'
    assert 'volume_lower' not in state and 'precision_status' not in state
    with pytest.raises(ValueError, match='incomplete'):
        session.finish()
    session.advance(piece_budget=4096)
    result = session.finish()
    assert scientific(result) == scientific(verify(m, cert))
    assert len(result['regions']) == 8 and result['precision_status'] == 'resolved'
    detached = session.snapshot
    detached['items'].clear()
    assert session.snapshot['items']


def test_manifest_storage_and_rehashed_arithmetic_are_independently_checked(tmp_path):
    import hashlib

    from devtools.reference_validator.edge_tasks import EdgeVerificationSession

    m, cert = inputs()
    session = EdgeVerificationSession(m, cert)
    session.advance(piece_budget=3)
    folder = tmp_path / 'checkpoint'
    session.save(folder)
    loaded = EdgeVerificationSession.from_bundle(m, folder)
    assert loaded.snapshot == session.snapshot
    loaded.advance(piece_budget=4096)
    assert scientific(loaded.finish()) == scientific(verify(m, cert))
    with pytest.raises(FileExistsError):
        loaded.save(folder)
    progress = json.loads((folder / 'progress.json').read_text())
    progress['items'][0]['bound']['lower'] = ['0', '1']
    progress['items'][0]['bound']['upper'] = ['0', '1']
    data = json.dumps(progress).encode()
    (folder / 'progress.json').write_bytes(data)
    manifest = json.loads((folder / 'MANIFEST.json').read_text())
    manifest['progress_sha256'] = hashlib.sha256(data).hexdigest()
    (folder / 'MANIFEST.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='bound'):
        EdgeVerificationSession.from_bundle(m, folder)
    (folder / 'MANIFEST.json').unlink()
    with pytest.raises(ValueError, match='Incomplete'):
        EdgeVerificationSession.from_bundle(m, folder)


def test_changed_frontier_task_units_duplicate_and_geometry_are_rejected():
    from devtools.reference_validator.edge_tasks import EdgeVerificationSession
    from devtools.reference_validator.verify.edge_progress import check_progress

    m, cert = inputs()
    state = EdgeVerificationSession(m, cert).advance(piece_budget=3)
    mutations = [
        lambda d: d.update(frontier_sha256='0' * 64),
        lambda d: d['items'][0].update(task_sha256='0' * 64),
        lambda d: d['items'][0]['bound'].update(unit='angstrom**3'),
        lambda d: d['items'].append(deepcopy(d['items'][0])),
        lambda d: d['certificate'].update(bits=256),
        lambda d: d.update(model_sha256='0' * 64),
        lambda d: d.update(stop_reason='pieces_complete'),
        lambda d: d['certificate']['topology_certificate']['cells'].clear(),
    ]
    for change in mutations:
        bad = deepcopy(state)
        change(bad)
        with pytest.raises(ValueError):
            check_progress(m, bad)


class ReversePool:
    fail = False
    calls = []

    def __init__(self, model, proof, checked, policy):
        pass

    def iter_map(self, tasks):
        from devtools.reference_validator.verify.edge_volume import triangle_flux

        for _, i, payload in reversed(tasks):
            self.calls.append(i)
            yield i, triangle_flux(*payload)
            if self.fail:
                raise RuntimeError('Injected arithmetic worker failure')

    def close(self):
        pass

    def receipt(self):
        return {'worker_count': 2, 'worker_records': []}


def test_out_of_order_failure_resume_counts_each_signed_piece_once(monkeypatch):
    from devtools.reference_validator import edge_tasks
    from devtools.reference_validator.parallel import LocalPolicy

    monkeypatch.setattr(edge_tasks, '_Pool', ReversePool)
    ReversePool.fail = True
    ReversePool.calls = []
    m, cert = inputs()
    session = edge_tasks.EdgeVerificationSession(m, cert)
    with pytest.raises(RuntimeError, match='Injected'):
        session.advance(piece_budget=4, policy=LocalPolicy(workers=2))
    assert [r['piece_index'] for r in session.snapshot['items']] == [1]
    ReversePool.fail = False
    resumed = edge_tasks.EdgeVerificationSession(m, cert, progress=session.snapshot)
    resumed.advance(piece_budget=4096, policy=LocalPolicy(workers=2))
    assert ReversePool.calls.count(1) == 1
    assert len(set(ReversePool.calls)) == len(ReversePool.calls)
    assert scientific(resumed.finish()) == scientific(verify(m, cert))


def test_zero_and_whole_free_shortcuts_keep_exact_literal_zero_requests():
    from devtools.reference_validator.edge_tasks import EdgeVerificationSession

    blocked, blocked_cert = inputs(F(2))
    free = Model.from_spheres([], [], 0, domain=blocked.domain)
    free_cert = edge_volume_proposal(
        free, topology_certificate(free), VolumeRequest(F(0), F(0))
    )
    for m, cert in [(blocked, blocked_cert), (free, free_cert)]:
        cert['request'] = VolumeRequest(F(0), F(0)).to_record()
        session = EdgeVerificationSession(m, cert)
        session.advance(piece_budget=1)
        assert not session.snapshot['items']
        result = session.finish()
        assert scientific(result) == scientific(verify(m, cert))
        assert result['precision_status'] == 'resolved'


def test_cancellation_missing_results_and_foreign_results_never_supply_a_total(
    monkeypatch,
):
    from devtools.reference_validator import edge_tasks
    from devtools.reference_validator.parallel import LocalPolicy

    m, cert = inputs()
    stopped = edge_tasks.EdgeVerificationSession(m, cert)
    state = stopped.advance(piece_budget=4096, stop=lambda: True)
    assert not state['items'] and state['stop_reason'] == 'cancelled'
    with pytest.raises(ValueError, match='incomplete'):
        stopped.finish()
    monkeypatch.setattr(edge_tasks, '_Pool', ReversePool)
    for output in [[], [(10000, None)], [(False, None)]]:
        monkeypatch.setattr(ReversePool, 'iter_map', lambda self, tasks: iter(output))
        session = edge_tasks.EdgeVerificationSession(m, cert)
        with pytest.raises(ValueError):
            session.advance(piece_budget=2, policy=LocalPolicy(workers=2))
        with pytest.raises(ValueError, match='incomplete'):
            session.finish()


def test_owned_arithmetic_context_rejects_pickle_pid_and_kernel_change(monkeypatch):
    import os
    import pickle

    from devtools.reference_validator import edge_tasks

    m, cert = inputs()
    s = edge_tasks.EdgeVerificationSession(m, cert)
    with pytest.raises(TypeError, match='serialized'):
        pickle.dumps(s)
    pid = os.getpid()
    with monkeypatch.context() as patch:
        patch.setattr(edge_tasks.os, 'getpid', lambda: pid + 1)
        with pytest.raises(ValueError, match='process or executable'):
            _ = s.snapshot
    with monkeypatch.context() as patch:
        patch.setattr(edge_tasks, 'kernel_identity', lambda: {'algorithm': 'foreign'})
        with pytest.raises(ValueError, match='process or executable'):
            s.finish()


def test_actual_spawned_arithmetic_matches_serial_tiny_and_asymmetric_controls(
    tmp_path,
):
    from tests.test_reference_validator_parallel_resume import _spawn

    _spawn(
        tmp_path,
        """from fractions import Fraction as F
from math import isqrt
from pathlib import Path
from devtools.reference_validator.model import Model, Box, point
from devtools.reference_validator.power_cells import topology_certificate
from devtools.reference_validator.edge_volume import edge_volume_proposal
from devtools.reference_validator.edge_tasks import EdgeVerificationSession
from devtools.reference_validator.parallel import LocalPolicy
from devtools.reference_validator.verify import verify
from devtools.reference_validator.volume_request import VolumeRequest
models=[
    Model.from_spheres([(0,0,0)],[F(3,2)],0,
        domain=Box(point((-1,-1,-1)),point((1,1,1)))),
    Model.from_spheres([(0,0,0)],[F(isqrt(3<<160),1<<80)],0,
        domain=Box(point((-1,-1,-1)),point((1,1,1)))),
    Model.from_spheres([(-8,0,0),(8,0,0)],[4,5],1,
        domain=Box(point((-20,-3,-4)),point((20,3,4)))),
]
for n,m in enumerate(models):
    cert=edge_volume_proposal(m,topology_certificate(m),VolumeRequest(F(1,2**32),F(1,2**32)),bits=512)
    s=EdgeVerificationSession(m,cert)
    s.advance(piece_budget=2,policy=LocalPolicy(workers=2))
    s.save(Path('saved_'+str(n)))
    resumed=EdgeVerificationSession.from_bundle(m,Path('saved_'+str(n)))
    resumed.advance(piece_budget=4096,policy=LocalPolicy(workers=2))
    result=resumed.finish();expected=verify(m,cert)
    assert {k:v for k,v in result.items() if k!='verifier_files_sha256'}=={k:v for k,v in expected.items() if k!='verifier_files_sha256'}
    assert result['precision_status']=='resolved'
    assert len(result['regions'])==[8,8,3][n]
""",
    )


def test_unmet_precision_and_literal_zero_positive_integrals_remain_explicit():
    from math import isqrt

    from devtools.reference_validator.edge_tasks import EdgeVerificationSession

    for radius, bits, request in [
        (F(isqrt(3 << 160), 1 << 80), 64, VolumeRequest(F(1, 2**32), F(1, 2**32))),
        (F(1, 2), 128, VolumeRequest(F(0), F(0))),
    ]:
        m, cert = inputs(radius, bits)
        cert['request'] = request.to_record()
        s = EdgeVerificationSession(m, cert)
        s.advance(piece_budget=4096)
        result = s.finish()
        assert scientific(result) == scientific(verify(m, cert))
        assert result['precision_status'] == 'unresolved'


def test_saved_signed_work_reader_does_not_import_a_pool_or_producer(tmp_path):
    import os
    import subprocess
    import sys
    from pathlib import Path

    from devtools.reference_validator.edge_tasks import EdgeVerificationSession

    m, cert = inputs()
    session = EdgeVerificationSession(m, cert)
    session.advance(piece_budget=3)
    (tmp_path / 'model.json').write_text(json.dumps(m.to_record()))
    (tmp_path / 'progress.json').write_text(json.dumps(session.snapshot))
    code = """
import importlib.abc,json,pathlib,sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        names=('topomt','numpy','scipy','molsysmt',
            'devtools.reference_validator.parallel',
            'devtools.reference_validator.parallel_runs',
            'devtools.reference_validator.edge_tasks',
            'devtools.reference_validator.edge_volume',
            'devtools.reference_validator.power_cells')
        if any(fullname==n or fullname.startswith(n+'.') for n in names):
            raise ImportError('Producer/pool/scientific import: '+fullname)
sys.meta_path.insert(0,Block())
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify.edge_progress import check_progress
read=lambda name:json.loads(pathlib.Path(name).read_text())
result=check_progress(Model.from_record(read('model.json')),read('progress.json'))
assert result['completed_pieces']==3 and not result['work_complete']
assert result['volume_enclosure_status']=='not_computed'
"""
    run = subprocess.run(
        [sys.executable, '-S', '-c', code],
        cwd=tmp_path,
        env={**os.environ, 'PYTHONPATH': str(Path(__file__).resolve().parents[1])},
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert run.returncode == 0, run.stdout + run.stderr


def test_signed_owner_contributions_and_rational_zero_radius_are_preserved():
    from devtools.reference_validator.edge_tasks import EdgeVerificationSession

    m = Model.from_spheres(
        [(0, 0, 0), (F(3, 5), 0, 0)],
        [1, F(7, 5)],
        0,
        domain=Box(point((-3, -3, -3)), point((3, 3, 3))),
    )
    cert = edge_volume_proposal(
        m, topology_certificate(m), VolumeRequest(F(216, 2**32), F(1, 2**32))
    )
    s = EdgeVerificationSession(m, cert)
    s.advance(piece_budget=4096)
    assert any(decode_scalar(r['bound']['lower']) < 0 for r in s.snapshot['items'])
    assert scientific(s.finish()) == scientific(verify(m, cert))
    zero, zero_cert = inputs(F(0))
    zero_cert['request'] = VolumeRequest(F(0), F(0)).to_record()
    z = EdgeVerificationSession(zero, zero_cert)
    z.advance(piece_budget=4096)
    result = z.finish()
    assert (
        decode_scalar(result['volume_lower'])
        == decode_scalar(result['volume_upper'])
        == 8
    )
    assert result['precision_status'] == 'resolved'


def test_direct_task_entry_rejects_unbound_certificate_headers():
    from devtools.reference_validator.edge_tasks import EdgeVerificationSession

    m, cert = inputs()
    for key, value in [
        ('kind', 'point'),
        ('schema', 'bad'),
        ('model_sha256', '0' * 64),
        ('arithmetic', 'float'),
        ('bits', True),
    ]:
        bad = deepcopy(cert)
        bad[key] = value
        with pytest.raises(ValueError):
            EdgeVerificationSession(m, bad)


def test_generic_progress_storage_rejects_oversize_before_publishing_and_bad_schema(
    tmp_path,
):
    from devtools.reference_validator.storage import (
        read_progress_bundle,
        write_progress_bundle,
    )

    destination = tmp_path / 'too_large'
    with pytest.raises(ValueError, match='16 MiB'):
        write_progress_bundle(
            destination, {'payload': 'x' * (16 * 1024**2)}, schema='fixture/1'
        )
    assert not destination.exists()
    valid = tmp_path / 'valid'
    write_progress_bundle(
        valid, {'unit': 'nm**3', 'value': ['1', '2']}, schema='fixture/1'
    )
    assert read_progress_bundle(valid, schema='fixture/1')['unit'] == 'nm**3'
    with pytest.raises(ValueError, match='schema'):
        read_progress_bundle(valid, schema='fixture/2')
