"""Replay retained physical hull facts without promoting partial path evidence."""

import hashlib
import json
from pathlib import Path

import pytest

from devtools.reference_validator.model import HullDomain, Model
from devtools.reference_validator.verify import verify

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'devguide/evidence/reference_validator_hull_sterics_v1'
SAVED = BASE / 'receiving'


def _read(path):
    return json.loads(path.read_text())


def test_retained_hull_steric_runs_bind_frozen_inputs_resources_and_all_artifacts():
    protocol = _read(BASE / 'protocol.json')
    execution = _read(BASE / 'execution.json')
    for folder in ['receiving', 'receiving_initial']:
        directory = BASE / folder
        receipt = _read(directory / 'receipt.json')
        assert receipt['source_revision'] == '833a774e52932d7d9dad7335218f2b0933bb9dcc'
        assert (
            receipt['protocol_sha256']
            == hashlib.sha256((BASE / 'protocol.json').read_bytes()).hexdigest()
        )
        assert receipt['originals_selected'] is True
        assert len(receipt['profiles']) == 10
        assert sum(len(p['queries']) for p in receipt['profiles']) == 40
        assert (
            sum(
                q['verification_status'] == 'rejected_candidate'
                for p in receipt['profiles']
                for q in p['queries'].values()
            )
            == 5
        )
        expected = {f'{p["name"]}/model.json' for p in receipt['profiles']} | {
            f'{p["name"]}/queries/{name}.{kind}.json'
            for p in receipt['profiles']
            for name in p['queries']
            for kind in ['certificate', 'verification']
        }
        assert set(receipt['files']) == expected
        assert {
            str(p.relative_to(directory)) for p in directory.rglob('*.json')
        } == expected | {'receipt.json'}
        for name, digest in receipt['files'].items():
            assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest
        assert receipt['concurrency'] == 1
        assert len(receipt['cpu_affinity']) == 1
        assert receipt['address_space_limit_bytes'] == 2 * 1024**3
        assert receipt['cpu_limit_seconds'] == 50
    for kind in ['current', 'initial']:
        assert (
            execution[kind]['receipt_sha256']
            == hashlib.sha256(
                (BASE / execution[kind]['receipt']).read_bytes()
            ).hexdigest()
        )
    assert execution['scheduler_used'] is False
    assert (
        execution['current']['external_wall_limit_seconds']
        == protocol['resources']['wall_seconds']
        == 60
    )
    assert (
        _read(BASE / 'receiving_initial/receipt.json')['files']
        == _read(SAVED / 'receipt.json')['files']
    )
    for row in protocol['originals']:
        assert (
            hashlib.sha256((ROOT / row['input']).read_bytes()).hexdigest()
            == row['input_sha256']
        )
        assert (
            hashlib.sha256((ROOT / row['hull']).read_bytes()).hexdigest()
            == row['hull_sha256']
        )
    reference = protocol['path_reference']
    assert (
        hashlib.sha256((ROOT / reference['path']).read_bytes()).hexdigest()
        == reference['sha256']
    )


@pytest.mark.parametrize(
    'name',
    [
        'cube_permeable',
        'cube_interior_obstacle',
        'cube_complete_cover',
        'tetrahedron_domain',
        'regular_tetrahedron_probe_1_2',
        'regular_tetrahedron_probe_1_4',
        'regular_tetrahedron_probe_1_7',
        'straight_tube_narrow_dense_probe_1_2',
        'straight_tube_narrow_dense_probe_1_4',
        'straight_tube_narrow_dense_probe_2_5',
    ],
)
def test_every_saved_hull_profile_replays_its_exact_physical_facts(name):
    receipt = _read(SAVED / 'receipt.json')
    row = next(p for p in receipt['profiles'] if p['name'] == name)
    model = Model.from_record(_read(SAVED / name / 'model.json'))
    assert isinstance(model.domain, HullDomain)
    assert model.digest == row['model_sha256']
    assert len(model.atoms) == row['n_atoms']
    assert tuple(a.source_id for a in model.atoms) == tuple(range(len(model.atoms)))
    for query, old in row['queries'].items():
        cert = _read(SAVED / name / 'queries' / f'{query}.certificate.json')
        assert _read(SAVED / name / 'queries' / f'{query}.verification.json') == old
        if old['verification_status'] == 'rejected_candidate':
            with pytest.raises(ValueError, match='Path collides or leaves'):
                verify(model, cert)
            assert 'n_components' not in old
        else:
            checked = verify(model, cert)
            for key, value in old.items():
                if key not in {'python_version', 'verifier_files_sha256'}:
                    assert checked[key] == value
            if name == 'cube_complete_cover' and query == 'whole_domain':
                assert checked['topology_complete'] is True
                assert checked['n_components'] == 0
            else:
                assert checked['topology_complete'] is False
                assert checked['n_components'] is None
    if name == 'cube_interior_obstacle':
        assert len(model.atoms) == 9 and len(model.domain.vertices) == 8
    if name.startswith('straight_tube_narrow_dense'):
        assert len(model.atoms) == 81 and len(model.domain.vertices) == 25
