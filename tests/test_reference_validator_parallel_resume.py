"""Parallel source work retains checked cells without inventing global topology."""

from copy import deepcopy
from fractions import Fraction as F

import pytest

from devtools.reference_validator.model import Box, Model, point
from devtools.reference_validator.power_cells import propose_cell, topology_certificate


def model():
    return Model.from_spheres(
        [(-1, 0, 0), (1, 0, 0), (0, 1, 0)],
        [F(1, 4)] * 3,
        0,
        domain=Box(point((-2, -2, -2)), point((2, 2, 2))),
    )


class FakePool:
    """Return actual geometric proposals in reverse completion order."""

    fail = False
    calls = []

    def __init__(self, model, proof, checked, policy):
        self.model = model

    def iter_map(self, tasks):
        atoms = sorted(self.model.atoms, key=lambda a: a.source_id) or [None]
        for _, index, _ in reversed(tasks):
            self.calls.append(index)
            yield index, propose_cell(self.model, atoms[index])
            if self.fail:
                raise RuntimeError('Injected child failure after completed work')

    def close(self):
        pass

    def receipt(self):
        return {'worker_records': [], 'worker_count': 2}


@pytest.fixture
def fake_pool(monkeypatch):
    from devtools.reference_validator import parallel_runs

    FakePool.fail = False
    FakePool.calls = []
    monkeypatch.setattr(parallel_runs, '_Pool', FakePool)
    return FakePool


def test_out_of_order_cells_save_and_resume_to_identical_serial_proof(
    tmp_path, fake_pool
):
    from devtools.reference_validator.parallel import LocalPolicy
    from devtools.reference_validator.parallel_runs import (
        ParallelPowerSession,
        load_parallel_power_bundle,
    )
    from devtools.reference_validator.verify.parallel_progress import check_progress

    m = model()
    s = ParallelPowerSession(m)
    state = s.advance(
        cell_budget=2, policy=LocalPolicy(workers=2), checkpoint_root=tmp_path
    )
    assert fake_pool.calls == [1, 0]
    assert [r['source_index'] for r in state['cells']] == [0, 1]
    checked = check_progress(m, state)
    assert checked['n_components'] is None and checked['topology_complete'] is False
    with pytest.raises(ValueError, match='incomplete'):
        s.finish()
    # The first durable result is a non-prefix inventory, not a false prefix.
    first = load_parallel_power_bundle(tmp_path / 'cells_0001', m)
    assert [r['source_index'] for r in first['cells']] == [1]
    loaded = load_parallel_power_bundle(tmp_path / 'cells_0002', m)
    resumed = ParallelPowerSession(m, progress=loaded)
    resumed.advance(cell_budget=3, policy=LocalPolicy(workers=1))
    assert fake_pool.calls == [1, 0, 2]
    assert resumed.finish() == topology_certificate(m)


def test_failure_preserves_nonprefix_work_and_retry_does_not_repeat_it(
    tmp_path, fake_pool
):
    from devtools.reference_validator.parallel import LocalPolicy
    from devtools.reference_validator.parallel_runs import ParallelPowerSession

    s = ParallelPowerSession(model())
    fake_pool.fail = True
    with pytest.raises(RuntimeError, match='Injected'):
        s.advance(
            cell_budget=2, policy=LocalPolicy(workers=2), checkpoint_root=tmp_path
        )
    assert [r['source_index'] for r in s.snapshot['cells']] == [1]
    assert s.snapshot['stop_reason'] == 'worker_failure'
    fake_pool.fail = False
    resumed = ParallelPowerSession(model(), progress=s.snapshot)
    resumed.advance(cell_budget=3, policy=LocalPolicy(workers=2))
    assert fake_pool.calls.count(1) == 1
    assert resumed.finish() == topology_certificate(model())


def test_cooperative_stop_keeps_completed_batch_and_bounded_pending_work(fake_pool):
    from devtools.reference_validator.parallel import LocalPolicy
    from devtools.reference_validator.parallel_runs import ParallelPowerSession

    s = ParallelPowerSession(model())
    state = s.advance(
        cell_budget=3,
        policy=LocalPolicy(workers=2),
        stop=lambda: bool(fake_pool.calls),
    )
    assert len(state['cells']) == 2
    assert state['stop_reason'] == 'cancelled'
    detached = s.snapshot
    detached['cells'].clear()
    assert len(s.snapshot['cells']) == 2


def test_changed_model_kernel_tasks_duplicate_cells_and_bad_geometry_are_rejected(
    fake_pool,
):
    from devtools.reference_validator.parallel_runs import ParallelPowerSession
    from devtools.reference_validator.verify.parallel_progress import check_progress

    m = model()
    s = ParallelPowerSession(m)
    state = s.advance(cell_budget=2)
    changes = [
        lambda d: d.update(model_sha256='0' * 64),
        lambda d: d['kernel'].update(algorithm='foreign'),
        lambda d: d['cells'][0].update(task_sha256='0' * 64),
        lambda d: d['cells'].append(deepcopy(d['cells'][0])),
        lambda d: d['cells'][0]['cell']['vertices'].clear(),
        lambda d: d['cells'][0].update(source_index=True),
        lambda d: d.update(stop_reason='cells_complete'),
    ]
    for change in changes:
        bad = deepcopy(state)
        change(bad)
        with pytest.raises(ValueError):
            check_progress(m, bad)


def test_manifest_last_storage_rejects_torn_rehashed_and_overwritten_work(
    tmp_path, fake_pool
):
    import hashlib
    import json

    from devtools.reference_validator.parallel_runs import (
        ParallelPowerSession,
        load_parallel_power_bundle,
    )

    m = model()
    s = ParallelPowerSession(m)
    s.advance(cell_budget=1)
    folder = tmp_path / 'saved'
    s.save(folder)
    with pytest.raises(FileExistsError):
        s.save(folder)
    manifest = json.loads((folder / 'MANIFEST.json').read_text())
    payload = folder / 'progress.json'
    bad = json.loads(payload.read_text())
    bad['cells'][0]['cell']['vertices'].clear()
    payload.write_text(json.dumps(bad))
    manifest['progress_sha256'] = hashlib.sha256(payload.read_bytes()).hexdigest()
    (folder / 'MANIFEST.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        load_parallel_power_bundle(folder, m)
    (folder / 'MANIFEST.json').unlink()
    with pytest.raises(ValueError, match='Incomplete'):
        load_parallel_power_bundle(folder, m)


def _spawn(tmp_path, body):
    import os
    import subprocess
    import sys
    import textwrap
    from pathlib import Path

    script = tmp_path / 'runner.py'
    script.write_text(
        'def run():\n'
        + textwrap.indent(
            """import os, resource
os.sched_setaffinity(0, set(sorted(os.sched_getaffinity(0))[:2]))
resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
"""
            + body,
            '    ',
        )
        + "\nif __name__ == '__main__':\n    run()\n"
    )
    env = {
        **os.environ,
        'PYTHONPATH': str(Path(__file__).resolve().parents[1]),
        'OMP_NUM_THREADS': '1',
        'OPENBLAS_NUM_THREADS': '1',
    }
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=35,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_spawned_child_failure_retains_other_work_and_rejects_duplicate_ids(tmp_path):
    _spawn(
        tmp_path,
        """from fractions import Fraction as F
from devtools.reference_validator.model import Model, Box, point
from devtools.reference_validator.parallel import LocalPolicy, _Pool
from devtools.reference_validator.verify.power_cells import checked_cells
from devtools.reference_validator.power_contracts import PowerLimits
m=Model.from_spheres([(-1,0,0),(1,0,0)],[F(1,4)]*2,0,
    domain=Box(point((-2,-2,-2)),point((2,2,2))))
p=_Pool(m,None,None,LocalPolicy(workers=2))
accepted=[]
try:
    try:
        for i,row in p.iter_map([('cell_proposal',0,None),('bad',1,None)]):
            checked_cells(m,[row],limits=PowerLimits(),complete=False,offset=i)
            accepted.append(i)
    except ValueError as exc:
        assert 'Unknown' in str(exc)
    else: raise AssertionError('Child failure disappeared')
    assert accepted==[0]
    try: list(p.iter_map([('cell',0,None),('cell',0,None)]))
    except ValueError: pass
    else: raise AssertionError('Duplicate tasks accepted')
finally: p.close()
assert p.receipt()['worker_records']
""",
    )


def test_real_spawn_checkpoint_fresh_resume_and_serial_proof_agree(tmp_path):
    _spawn(
        tmp_path,
        """from fractions import Fraction as F
from pathlib import Path
from devtools.reference_validator.model import Model, Box, point
from devtools.reference_validator.parallel import LocalPolicy
from devtools.reference_validator.parallel_runs import (
    ParallelPowerSession, load_parallel_power_bundle)
from devtools.reference_validator.power_cells import topology_certificate
m=Model.from_spheres([(-1,0,0),(1,0,0),(0,1,0)],[F(1,4)]*3,0,
    domain=Box(point((-2,-2,-2)),point((2,2,2))))
s=ParallelPowerSession(m)
s.advance(cell_budget=2,policy=LocalPolicy(workers=2),checkpoint_root=Path('checkpoints'))
state=load_parallel_power_bundle(Path('checkpoints/cells_0002'),m)
resumed=ParallelPowerSession(m,progress=state)
resumed.advance(cell_budget=3,policy=LocalPolicy(workers=1))
assert resumed.finish()==topology_certificate(m)
assert all(r['address_space_bytes']<=256*1024**2 for r in s.execution['worker_records'])
""",
    )


def test_nested_pools_are_rejected_before_launching_workers(monkeypatch):
    import multiprocessing

    from devtools.reference_validator.parallel import LocalPolicy, _Pool

    monkeypatch.setattr(multiprocessing.current_process(), 'name', 'SpawnProcess-1')
    with pytest.raises(ValueError, match='Nested'):
        _Pool(model(), None, None, LocalPolicy())


@pytest.mark.parametrize('centers', [[], [(0, 0, 0)], [(0, 0, 0), (0, 0, 0)]])
def test_empty_singleton_and_coincident_sources_keep_complete_coverage(
    centers, fake_pool
):
    from devtools.reference_validator.parallel_runs import ParallelPowerSession

    m = Model.from_spheres(
        centers,
        [F(1, 4)] * len(centers),
        0,
        domain=Box(point((-1, -1, -1)), point((1, 1, 1))),
    )
    session = ParallelPowerSession(m)
    state = session.advance(cell_budget=128)
    assert len(state['cells']) == max(1, len(centers))
    assert state['stop_reason'] == 'cells_complete'
    assert session.finish() == topology_certificate(m)


def test_saved_partial_checker_needs_no_producer_or_scientific_imports(
    tmp_path, fake_pool
):
    import json
    import os
    import subprocess
    import sys
    from pathlib import Path

    from devtools.reference_validator.parallel_runs import ParallelPowerSession

    m = model()
    state = ParallelPowerSession(m).advance(cell_budget=2)
    (tmp_path / 'model.json').write_text(json.dumps(m.to_record()))
    (tmp_path / 'state.json').write_text(json.dumps(state))
    code = """
import importlib.abc,json,pathlib,sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        blocked=('topomt','numpy','scipy','molsysmt',
            'devtools.reference_validator.parallel',
            'devtools.reference_validator.parallel_runs',
            'devtools.reference_validator.power_cells')
        if any(fullname==n or fullname.startswith(n+'.') for n in blocked):
            raise ImportError('Producer/scientific import: '+fullname)
sys.meta_path.insert(0,Block())
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify.parallel_progress import check_progress
model=Model.from_record(json.loads(pathlib.Path('model.json').read_text()))
result=check_progress(model,json.loads(pathlib.Path('state.json').read_text()))
assert result['completed_source_indices']==[0,1]
assert result['n_components'] is None and result['topology_complete'] is False
"""
    env = {**os.environ, 'PYTHONPATH': str(Path(__file__).resolve().parents[1])}
    result = subprocess.run(
        [sys.executable, '-S', '-c', code],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stdout + result.stderr
