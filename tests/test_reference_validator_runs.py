"""Resumable proofs retain the physical model and all earlier established facts."""

import copy
import hashlib
import json
import subprocess
import sys
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from devtools.reference_validator.contracts import Configuration, kernel_identity
from devtools.reference_validator.model import (
    Atom,
    Box,
    Model,
    point,
    record_digest,
    scalar,
)
from devtools.reference_validator.runs import resume_run, start_run
from devtools.reference_validator.storage import load_bundle, save_bundle
from devtools.reference_validator.verify import verify
from devtools.reference_validator.verify.records import (
    make_run_record,
    verify_checkpoint,
    verify_run,
    verify_transition,
)


def model():
    return Model(
        (Atom(2, point((0, 0, 0)), scalar(1)),),
        scalar(0),
        Box(point((-2, -2, -2)), point((2, 2, 2))),
        'a' * 64,
    )


def test_chunked_run_equals_uninterrupted_run_and_bounds_never_worsen():
    original = model()
    config = Configuration(max_depth=3, max_leaves=512)
    whole, whole_run = start_run(original, configuration=config, split_budget=4095)
    cp, run = start_run(original, configuration=config, split_budget=0)
    assert verify_run(original, run, cp)['stop_reason'] == 'step_budget'
    before = Fraction(64)
    lower_before = Fraction()
    for _ in range(100):
        if verify_checkpoint(original, cp)['stop_reason'] != 'step_budget':
            break
        old = cp
        snapshot = copy.deepcopy(old)
        cp, run = resume_run(original, old, split_budget=3)
        assert old == snapshot
        result = verify_transition(original, old, cp, run)
        assert result['lineage_status'] == 'resolved'
        assert cp['run_sha256'] == old['run_sha256'] == whole['run_sha256']
        assert cp['parent_sha256'] == record_digest(old)
        assert result['topology_complete'] is False
        lower = Fraction(*map(int, result['volume_lower']))
        upper = Fraction(*map(int, result['volume_upper']))
        assert lower_before <= lower <= upper <= before
        lower_before, before = lower, upper
    else:
        pytest.fail('Finite bounded run did not stop')
    assert cp['certificate'] == whole['certificate']
    assert run['verification']['stop_reason'] == 'depth_limit'
    assert whole_run['verification']['stop_reason'] == 'depth_limit'


def test_empty_full_and_leaf_ceiling_are_distinct_from_step_budget():
    base = model()
    free = replace(base, atoms=())
    blocked = replace(base, atoms=(Atom(2, point((0, 0, 0)), scalar(4)),))
    for source, count in ((free, 1), (blocked, 0)):
        cp, run = start_run(source, split_budget=0)
        result = verify_run(source, run, cp)
        assert result['stop_reason'] == 'no_unknown_cells'
        assert result['n_components'] == count
    cp, run = start_run(base, configuration=Configuration(max_depth=4, max_leaves=1))
    result = verify_run(base, run, cp)
    assert result['stop_reason'] == 'leaf_limit'
    assert result['n_components'] is None


@pytest.mark.parametrize('changed', ['probe', 'domain', 'atom'])
def test_resume_refuses_changed_physical_inputs(changed):
    source = model()
    cp, _ = start_run(source, split_budget=1)
    if changed == 'probe':
        other = replace(source, probe=Fraction(1, 10))
    elif changed == 'domain':
        other = replace(source, domain=Box(point((-3, -2, -2)), point((2, 2, 2))))
    else:
        other = replace(source, atoms=())
    with pytest.raises(ValueError):
        resume_run(other, cp)


@pytest.mark.parametrize(
    'changed',
    [
        'frontier',
        'leaves',
        'kernel',
        'configuration',
        'counters',
        'parent',
        'schema',
        'extra',
    ],
)
def test_resume_rejects_missing_work_or_altered_identity(changed):
    source = model()
    cp, _ = start_run(source, split_budget=1)
    bad = copy.deepcopy(cp)
    if changed == 'frontier':
        bad['frontier'].pop()
    elif changed == 'leaves':
        bad['certificate']['leaves'].pop()
    elif changed == 'kernel':
        bad['kernel']['files']['producer.py'] = '0' * 64
    elif changed == 'configuration':
        bad['configuration']['max_depth'] += 1
    elif changed == 'counters':
        bad['total_splits'] += 1
    elif changed == 'parent':
        bad['parent_sha256'] = 'invalid'
    elif changed == 'schema':
        bad['schema'] = 'unknown'
    else:
        bad['topology_complete'] = True
    with pytest.raises(ValueError):
        resume_run(source, bad)


def test_run_summary_and_lineage_do_not_override_the_proof():
    source = model()
    cp, _ = start_run(source, split_budget=1)
    later, run = resume_run(source, cp, split_budget=1)
    bad = copy.deepcopy(run)
    bad['verification']['n_components'] = 0
    with pytest.raises(ValueError):
        verify_run(source, bad, later)
    bad_cp = copy.deepcopy(later)
    bad_cp['parent_sha256'] = '0' * 64
    with pytest.raises(ValueError):
        verify_transition(source, cp, bad_cp, run)


def test_saved_bundles_reject_partial_and_corrupted_writes(tmp_path):
    source = model()
    cp, run = start_run(source, split_budget=1)
    output = tmp_path / 'step'
    save_bundle(output, source, cp, run)
    restored_cp, restored_run = load_bundle(output, source)
    assert restored_cp == cp and restored_run == run
    with pytest.raises(FileExistsError):
        save_bundle(output, source, cp, run)
    (output / 'checkpoint.json').write_text('{}')
    with pytest.raises(ValueError):
        load_bundle(output, source)
    incomplete = tmp_path / 'partial'
    incomplete.mkdir()
    (incomplete / 'checkpoint.json').write_text(json.dumps(cp))
    with pytest.raises(ValueError):
        load_bundle(incomplete, source)


def test_run_verifier_never_imports_search_code(tmp_path):
    source = model()
    cp, run = start_run(source, split_budget=1)
    data = tmp_path / 'input.json'
    data.write_text(json.dumps([source.to_record(), cp, run]))
    script = """
import json, sys
from pathlib import Path
sys.modules['topomt'] = None
sys.modules['devtools.reference_validator.producer'] = None
sys.modules['devtools.reference_validator.runs'] = None
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify.records import verify_run
m, cp, run = json.loads(Path(sys.argv[1]).read_text())
print(json.dumps(verify_run(Model.from_record(m), run, cp)))
"""
    result = subprocess.run(
        [sys.executable, '-c', script, str(data)],
        text=True,
        capture_output=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['topology_complete'] is False


def test_cli_start_resume_and_saved_verification(tmp_path):
    source = model()
    path = tmp_path / 'model.json'
    path.write_text(json.dumps(source.to_record()))
    command = [sys.executable, '-m', 'devtools.reference_validator']
    first, second = tmp_path / 'first', tmp_path / 'second'
    run = subprocess.run(
        command
        + ['start', str(path), str(first), '--max-depth', '2', '--split-budget', '1'],
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stderr
    run = subprocess.run(
        command + ['resume', str(path), str(first), str(second), '--split-budget', '3'],
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)['lineage_status'] == 'resolved'
    run = subprocess.run(
        command + ['verify-run', str(path), str(second)], capture_output=True, text=True
    )
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)['lineage_status'] == 'not_checked'
    assert json.loads(run.stdout)['topology_complete'] is False


def test_transition_rejects_forgetting_an_already_proved_cell():
    source = model()
    old, _ = start_run(source, split_budget=2)
    child, _ = resume_run(source, old, split_budget=0)
    leaf = next(v for v in child['certificate']['leaves'] if v['state'] == 'free')
    leaf['state'] = 'unknown'
    child['frontier'] = sorted(child['frontier'] + [leaf['path']])
    # The weakened enclosure is a valid stand-alone proof, but not a valid
    # continuation preserving all facts already established by the parent.
    run = make_run_record(source, child)
    verify_run(source, run, child)
    with pytest.raises(ValueError, match='previously proved'):
        verify_transition(source, old, child, run)


@pytest.mark.parametrize('budget', [-1, True, 4096])
def test_invalid_per_step_budgets_are_rejected(budget):
    with pytest.raises(ValueError):
        start_run(model(), split_budget=budget)


def test_resume_pilot_writes_a_replayable_tetrahedron_chain(tmp_path):
    protocol = (
        Path(__file__).resolve().parents[1]
        / 'devguide/evidence/reference_validator_resume_v1/protocol.json'
    )
    script = """
import os, resource, sys
from pathlib import Path
os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
from devtools.reference_validator.capture_resume import capture
capture(Path(sys.argv[1]), Path(sys.argv[2]))
"""
    result = subprocess.run(
        [sys.executable, '-c', script, str(protocol), str(tmp_path / 'pilot')],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    receipt = json.loads((tmp_path / 'pilot/receipt.json').read_text())
    assert len(receipt['steps']) == 9
    assert receipt['same_as_continuous'] is True
    assert receipt['steps'][0]['stop_reason'] == 'step_budget'
    assert receipt['steps'][-1]['n_components'] == 0
    assert receipt['steps'][-1]['stop_reason'] == 'no_unknown_cells'


def test_retained_resume_chain_preserves_history_and_mathematical_proofs():
    root = Path(__file__).resolve().parents[1]
    base = root / 'devguide/evidence/reference_validator_resume_v1'
    spec = json.loads((base / 'protocol.json').read_text())
    source = Model.from_record(json.loads((root / spec['model']).read_text()))
    saved = base / 'receiving'
    receipt = json.loads((saved / 'receipt.json').read_text())
    assert (
        hashlib.sha256((base / 'protocol.json').read_bytes()).hexdigest()
        == receipt['protocol_sha256']
    )
    for name, expected in receipt['files'].items():
        assert hashlib.sha256((saved / name).read_bytes()).hexdigest() == expected
    previous = None
    for row in receipt['steps']:
        directory = saved / row['directory']
        cp = json.loads((directory / 'checkpoint.json').read_text())
        run = json.loads((directory / 'run.json').read_text())
        assert record_digest(cp) == row['checkpoint_sha256']
        assert record_digest(run) == row['run_record_sha256']
        checked = verify(source, cp['certificate'])
        assert checked['n_components'] == row['n_components']
        assert checked['volume_lower'] == row['volume_lower']
        assert checked['volume_upper'] == row['volume_upper']
        if previous is not None:
            assert cp['parent_sha256'] == record_digest(previous)
        if cp['kernel'] == kernel_identity():
            load_bundle(directory, source)
            if previous is not None:
                verify_transition(source, previous, cp, run)
        else:
            # New source/runtime may check old mathematical proofs, but may
            # not silently resume executable work under a different kernel.
            with pytest.raises(ValueError, match='kernel/runtime'):
                verify_checkpoint(source, cp)
        previous = cp
