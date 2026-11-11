"""A complete wall/end partition supports independent tube patch counting."""

import copy
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = (
    ROOT
    / 'docs/content/benchlab/synthetic/straight_tube_narrow_dense/artifacts/straight_tube_narrow_dense_v1'
)


def test_tube_hull_partition_is_complete_and_disjoint():
    from devtools.verify_tube_boundary import boundary_model

    model = boundary_model(DATA / 'input.json', DATA / 'boundary_1.2A_v2_protocol.json')
    assert set(model['wall_face_indices']).isdisjoint(model['end_face_indices'])
    assert sorted(model['wall_face_indices'] + model['end_face_indices']) == list(
        range(len(model['hull_faces']))
    )
    assert model['wall_face_indices'] and model['end_face_indices']
    for index in model['end_face_indices']:
        face = model['hull_faces'][index]
        assert all(atom < 9 for atom in face) or all(atom >= 72 for atom in face)


@pytest.mark.parametrize('probe', ['1.2', '1.4'])
def test_retained_boundary_reference_replays_without_a_solver(probe, monkeypatch):
    import scipy.optimize

    from devtools.verify_tube_boundary import verify_boundary

    def forbidden(*args, **kwargs):
        raise AssertionError('Replay must verify witnesses, not discover them')

    monkeypatch.setattr(scipy.optimize, 'minimize', forbidden)
    protocol = DATA / f'boundary_{probe}A_v2_protocol.json'
    certificate = json.loads(
        (DATA / f'boundary_{probe}A_v2_certificate.json').read_text()
    )
    verified = verify_boundary(DATA / 'input.json', protocol, certificate)
    assert verified['opening_component_count'] == 2
    assert sorted(verified['component_end_labels']) == ['negative_z', 'positive_z']


@pytest.mark.parametrize('damage', ['missing_wall_leaf', 'missing_end', 'seam', 'unit'])
def test_boundary_reference_rejects_incomplete_or_changed_evidence(damage):
    from devtools.verify_tube_boundary import verify_boundary

    certificate = copy.deepcopy(
        json.loads((DATA / 'boundary_1.2A_v2_certificate.json').read_text())
    )
    if damage == 'missing_wall_leaf':
        certificate['wall_cover'].pop()
    elif damage == 'missing_end':
        certificate['end_faces'].pop()
    elif damage == 'seam':
        certificate['seams'].pop()
    else:
        certificate['length_unit'] = 'nm'
    with pytest.raises(ValueError):
        verify_boundary(
            DATA / 'input.json', DATA / 'boundary_1.2A_v2_protocol.json', certificate
        )
