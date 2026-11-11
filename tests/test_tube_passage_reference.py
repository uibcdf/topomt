"""Independent straight-tube path/bound references precede native receiving."""

import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / 'docs/content/benchlab/synthetic/cylinder_tube'
DATA = CASE / 'artifacts/cylinder_tube_v1'


def test_all_atom_path_clearance_checks_segments_between_safe_stations():
    from devtools.verify_tube_passage import polyline_clearance

    centers = np.array([[0.0, 0.0, 0.0]])
    radii = np.array([0.2])
    points = np.array([[-1.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    assert polyline_clearance(
        points, centers, radii, length_unit='angstroms'
    ) == pytest.approx(-0.2)
    assert polyline_clearance(
        points / 10, centers / 10, radii / 10, length_unit='nm'
    ) == pytest.approx(-0.2)


def test_frozen_axis_threshold_is_not_a_global_transport_claim():
    from devtools.verify_tube_passage import model_reference

    result = model_reference(DATA / 'input.json', DATA / 'protocol.json')
    assert result['axis_clearance_angstroms'] == pytest.approx(1.3952137863301655)
    assert result['axis_clearance_is_global_bottleneck'] is False
    assert result['finite_hull_cover_distance_bound_angstroms'] == pytest.approx(
        4.083579632239034
    )
    assert result['exclusion'][str(2.5)]['strictly_covered']
    assert not result['exclusion'][str(1.4)]['strictly_covered']


def test_reference_rejects_changed_input_identity(tmp_path):
    from devtools.verify_tube_passage import model_reference

    path = tmp_path / 'input.json'
    fixture = json.loads((DATA / 'input.json').read_text())
    fixture['coordinates']['values'][0][0] += 0.01
    path.write_text(json.dumps(fixture))
    with pytest.raises(ValueError, match='identity'):
        model_reference(path, DATA / 'protocol.json')


def test_path_clearance_preserves_rigid_motion_and_source_permutation():
    from devtools.verify_tube_passage import polyline_clearance

    points = np.array([[0.0, 0.0, -3.0], [0.2, 0.0, 0.0], [0.0, 0.0, 3.0]])
    centers = np.array([[1.5, 0.0, 0.0], [-2.0, 0.0, 1.0]])
    radii = np.array([0.3, 0.4])
    expected = polyline_clearance(points, centers, radii, length_unit='angstroms')
    rotation = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    offset = np.array([4.0, -7.0, 2.0])
    actual = polyline_clearance(
        points @ rotation + offset,
        (centers @ rotation + offset)[::-1],
        radii[::-1],
        length_unit='angstroms',
    )
    assert actual == pytest.approx(expected)


@pytest.mark.parametrize('damage', ['shape', 'nonfinite', 'negative_radius'])
def test_invalid_path_geometry_is_rejected(damage):
    from devtools.verify_tube_passage import polyline_clearance

    points = np.array([[0.0, 0.0, -1.0], [0.0, 0.0, 1.0]])
    centers = np.array([[1.0, 0.0, 0.0]])
    radii = np.array([0.2])
    if damage == 'shape':
        points = points[:, :2]
    elif damage == 'nonfinite':
        centers[0, 0] = np.nan
    else:
        radii[0] = -1.0
    with pytest.raises(ValueError):
        polyline_clearance(points, centers, radii, length_unit='angstroms')


def test_bounded_discovery_returns_a_checked_witness_and_refuses_work_overrun():
    from devtools.verify_tube_passage import _discover_path

    centers = np.array([[1.5, 0.0, 0.0]])
    radii = np.array([0.2])
    controls = {
        'z_stations_angstroms': [-2.0, 0.0, 2.0],
        'xy_values_angstroms': [0.0],
        'mandatory_origin': True,
        'maximum_points': 3,
        'maximum_edge_tests': 2,
        'max_lateral_step_angstroms': 0.35,
    }
    actual = _discover_path(centers, radii, controls)
    assert actual['minimum_clearance_angstroms'] == pytest.approx(1.3)
    assert actual['points_angstroms'] == [
        [0.0, 0.0, -2.0],
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 2.0],
    ]
    controls['maximum_edge_tests'] = 1
    with pytest.raises(ValueError, match='budget'):
        _discover_path(centers, radii, controls)


def test_an_occupied_origin_does_not_exclude_a_bent_end_to_end_witness():
    from devtools.verify_tube_passage import _discover_path

    controls = {
        'z_stations_angstroms': [-2.0, 0.0, 2.0],
        'xy_values_angstroms': [-1.0, 0.0, 1.0],
        'mandatory_origin': True,
        'maximum_points': 20,
        'maximum_edge_tests': 100,
        'max_lateral_step_angstroms': 1.5,
    }
    centers = np.array([[0.0, 0.0, 0.0]])
    radii = np.array([0.2])
    origin = _discover_path(centers, radii, controls)
    assert origin['minimum_clearance_angstroms'] == pytest.approx(-0.2)
    controls['mandatory_origin'] = False
    bent = _discover_path(centers, radii, controls)
    assert bent['minimum_clearance_angstroms'] > 0.9
    assert [0.0, 0.0, 0.0] not in bent['points_angstroms']


def test_retained_witnesses_separate_origin_access_from_end_to_end_passage():
    from devtools.verify_tube_passage import verify_reference

    old = json.loads((DATA / 'reference_certificate.json').read_text())
    new = json.loads((DATA / 'reference_v2_certificate.json').read_text())
    first = verify_reference(DATA / 'input.json', DATA / 'protocol.json', old)
    later = verify_reference(
        DATA / 'input.json', DATA / 'passage_v2_protocol.json', new
    )
    assert first['controls'][1]['end_to_end_path'] == 'not_established'
    assert later['controls'][1]['fixed_axis'] == 'blocked'
    assert later['controls'][1]['end_to_end_path'] == 'certified'
    assert later['controls'][1]['path_margin_angstroms'] > 0.04
    assert later['controls'][2]['finite_hull'] == 'strictly_covered'
    assert first['input_sha256'] == later['input_sha256']


@pytest.mark.parametrize('damage', ['unit', 'point', 'claimed_clearance', 'context'])
def test_retained_path_cannot_accept_changed_units_support_or_claimed_clearance(damage):
    from devtools.verify_tube_passage import verify_reference

    candidate = json.loads((DATA / 'reference_v2_certificate.json').read_text())
    if damage == 'unit':
        candidate['path_candidate']['length_unit'] = 'nm'
    elif damage == 'point':
        candidate['path_candidate']['points_angstroms'][1][0] = 4.0
    elif damage == 'claimed_clearance':
        candidate['path_candidate']['minimum_clearance_angstroms'] += 0.1
    else:
        candidate['protocol_sha256'] = '0' * 64
    with pytest.raises(ValueError):
        verify_reference(
            DATA / 'input.json', DATA / 'passage_v2_protocol.json', candidate
        )
