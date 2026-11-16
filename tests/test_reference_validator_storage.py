"""Every committed JSON bundle fits the same bounded reader envelope."""

import hashlib
import json
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from devtools.reference_validator import storage
from devtools.reference_validator.model import Box, Model, point


def _payload(value):
    return (
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n'
    ).encode()


def _model():
    return Model.from_spheres(
        [(0, 0, 0)], [1], 0, domain=Box(point((-2, -2, -2)), point((2, 2, 2)))
    )


@pytest.fixture(params=['raw', 'power', 'parallel', 'partition', 'region', 'edge'])
def route(request):
    """Build real valid records; this fixture does not launch any workers."""
    model = _model()
    if request.param == 'raw':
        record = {'text': 'µ球' * 32, 'integer': 3}
        return (
            lambda p: storage.write_progress_bundle(p, record, schema='test/1'),
            lambda p: storage.read_progress_bundle(p, schema='test/1'),
            {'progress.json': record},
            record,
        )
    if request.param == 'power':
        from devtools.reference_validator.power_runs import (
            load_power_bundle,
            save_power_bundle,
            start_power_run,
        )

        record = start_power_run(model, cell_budget=1)
        return (
            lambda p: save_power_bundle(p, model, record),
            lambda p: load_power_bundle(p, model),
            {'progress.json': record},
            record,
        )
    if request.param == 'parallel':
        from devtools.reference_validator.parallel_runs import (
            ParallelPowerSession,
            load_parallel_power_bundle,
        )

        session = ParallelPowerSession(model)
        return (
            session.save,
            lambda p: load_parallel_power_bundle(p, model),
            {'progress.json': session.snapshot},
            session.snapshot,
        )
    if request.param == 'partition':
        from devtools.reference_validator.runs import start_run

        cp, run = start_run(model, split_budget=0)
        return (
            lambda p: storage.save_bundle(p, model, cp, run),
            lambda p: storage.load_bundle(p, model),
            {'checkpoint.json': cp, 'run.json': run},
            (cp, run),
        )
    from devtools.reference_validator.power_cells import topology_certificate
    from devtools.reference_validator.volume_request import VolumeRequest

    topology = topology_certificate(model)
    volume_request = VolumeRequest(Fraction(1, 100), Fraction(1, 100))
    if request.param == 'region':
        from devtools.reference_validator.region_volume import (
            load_region_bundle,
            region_volume_certificate,
            save_region_bundle,
        )

        cert = region_volume_certificate(model, topology, volume_request, max_leaves=1)
        return (
            lambda p: save_region_bundle(p, model, cert),
            lambda p: load_region_bundle(p, model),
            {'model.json': model.to_record(), 'certificate.json': cert},
            cert,
        )
    from devtools.reference_validator.edge_tasks import EdgeVerificationSession
    from devtools.reference_validator.edge_volume import edge_volume_proposal

    session = EdgeVerificationSession(
        model, edge_volume_proposal(model, topology, volume_request)
    )
    session.advance(piece_budget=1)
    return (
        session.save,
        lambda p: EdgeVerificationSession.from_bundle(model, p).snapshot,
        {'progress.json': session.snapshot},
        session.snapshot,
    )


def test_exact_encoded_byte_limit_round_trips_with_the_real_scientific_reader(
    route, tmp_path, monkeypatch
):
    write, read, files, expected = route
    largest = max(len(_payload(v)) for v in files.values())
    # Smaller test envelopes exercise every real route without huge geometry.
    monkeypatch.setattr(storage, '_MAX_RECORD_BYTES', largest, raising=False)
    folder = tmp_path / 'exact'
    write(folder)
    assert read(folder) == expected
    assert max((folder / n).stat().st_size for n in files) == largest
    for name, value in files.items():
        assert (folder / name).read_bytes() == _payload(value)


def test_one_byte_excess_leaves_no_new_directory_and_preserves_last_checkpoint(
    route, tmp_path, monkeypatch
):
    write, read, files, expected = route
    previous = tmp_path / 'last_valid'
    write(previous)
    hashes = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in previous.iterdir()
    }
    largest = max(len(_payload(v)) for v in files.values())
    monkeypatch.setattr(storage, '_MAX_RECORD_BYTES', largest - 1, raising=False)
    rejected = tmp_path / 'oversized'
    with pytest.raises(ValueError, match='limit|envelope|size'):
        write(rejected)
    assert not rejected.exists()
    monkeypatch.setattr(storage, '_MAX_RECORD_BYTES', 16 * 1024**2)
    assert read(previous) == expected
    assert hashes == {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in previous.iterdir()
    }


def test_real_parallel_writer_cannot_publish_a_record_its_reader_rejects(tmp_path):
    from devtools.reference_validator.parallel_runs import _write_bundle

    value = {'padding': 'x' * (16 * 1024**2)}
    folder = tmp_path / 'unreadable'
    with pytest.raises(ValueError, match='limit|envelope|size'):
        _write_bundle(folder, value)
    assert not folder.exists()


def test_real_limit_includes_json_escapes_formatting_and_final_newline(tmp_path):
    value = {'padding': ''}
    overhead = len(_payload(value))
    # The non-ASCII character occupies six bytes in the escaped JSON payload.
    value['padding'] = 'µ' + 'x' * (16 * 1024**2 - overhead - 6)
    folder = tmp_path / 'exact'
    storage.write_progress_bundle(folder, value, schema='test/1')
    assert (folder / 'progress.json').stat().st_size == 16 * 1024**2
    assert storage.read_progress_bundle(folder, schema='test/1') == value
    value['padding'] += 'x'
    with pytest.raises(ValueError):
        storage.write_progress_bundle(tmp_path / 'one_more', value, schema='test/1')
    assert not (tmp_path / 'one_more').exists()


def test_oversized_commit_manifest_cannot_publish_an_unreadable_bundle(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(storage, '_MAX_RECORD_BYTES', 512, raising=False)
    with pytest.raises(ValueError):
        storage.write_progress_bundle(tmp_path / 'bad', {}, schema='x' * 513)
    assert not (tmp_path / 'bad').exists()


def test_fresh_independent_reader_accepts_each_written_bundle_without_producers(
    route, request, tmp_path
):
    write, _, _, _ = route
    folder = tmp_path / 'saved'
    write(folder)
    (tmp_path / 'model.json').write_bytes(_payload(_model().to_record()))
    script = """
import importlib.abc,json,sys
from pathlib import Path
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        names=('topomt','numpy','scipy','molsysmt','pyunitwizard','ackredit',
            'devtools.reference_validator.producer',
            'devtools.reference_validator.runs',
            'devtools.reference_validator.power_cells',
            'devtools.reference_validator.power_runs',
            'devtools.reference_validator.parallel_runs',
            'devtools.reference_validator.edge_volume',
            'devtools.reference_validator.edge_tasks',
            'devtools.reference_validator.region_volume',
            'devtools.reference_validator.parallel')
        if any(fullname==n or fullname.startswith(n+'.') for n in names):
            raise ImportError('Producer/scientific import: '+fullname)
sys.meta_path.insert(0,Block())
from devtools.reference_validator import storage
from devtools.reference_validator.model import Model
model=Model.from_record(storage.read_record(Path('model.json')))
folder=Path('saved');kind=sys.argv[1]
if kind=='partition':
    cp,run=storage.load_bundle(folder,model)
    assert cp['performed_splits']==0
elif kind=='region':
    from devtools.reference_validator.verify.region_volume import check_region_volume
    proof=storage.read_record(folder/'certificate.json')
    assert check_region_volume(model,proof)['topology_complete']
else:
    schema={'raw':'test/1','power':'topomt.reference-validator.power-bundle/1',
        'parallel':'topomt.reference-validator.parallel-power-bundle/1',
        'edge':'topomt.reference-validator.edge-work-bundle/1'}[kind]
    proof=storage.read_progress_bundle(folder,schema=schema)
    if kind=='raw':assert proof['integer']==3
    else:
        name={'power':'power_progress','parallel':'parallel_progress',
            'edge':'edge_progress'}[kind]
        mod=__import__('devtools.reference_validator.verify.'+name,fromlist=['check_progress'])
        mod.check_progress(model,proof)
print(kind+' independently checked')
"""
    # The complete scientific storage readers, not a JSON-only echo, run fresh.
    name = request.node.callspec.params['route']
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, '-S', '-c', script, name],
        cwd=tmp_path,
        env={**os.environ, 'PYTHONPATH': str(root)},
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stdout + result.stderr
