"""Point diagnostics must not certify an entire local DFND component."""

from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import pyunitwizard as puw

from devtools.benchlab.residence_witnesses import inspect_residence_witnesses


def authored_observation(blocked=True):
    """Supply mapping/point arithmetic, not an asserted Delaunay result."""
    coordinates = np.array(
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [6, 6, 6]],
        dtype=float,
    )
    center = np.full(3, 0.25)
    if blocked:
        coordinates[-1] = center
    raw = {
        'schema_version': 'dfnd.raw.nm.v2',
        'units': {'coordinates': 'nm', 'R_residence': 'nm', 'volume': 'nm**3'},
        'parameters': {
            'result_key': 'authored-mapping-control',
            'epsilon': 1e-7,
            'query': {'probe_radius': 0.2},
        },
        'tetrahedra': [
            {
                'tetrahedron_id': 0,
                'local_atom_indices': [0, 1, 2, 3],
                'atom_indices': [90, 4, 30, 15],
                'center': center.tolist(),
                'R_residence': float(np.linalg.norm(center) - 0.1),
                'residence_candidate_kind': 'authored_point',
                'volume_topological': 1 / 6,
            }
        ],
        'wet_components': [
            {'id': 7, 'resident_tetrahedron_ids': [0], 'tetrahedron_ids': [0]},
            {'id': 8, 'resident_tetrahedron_ids': [], 'tetrahedron_ids': []},
        ],
    }
    return SimpleNamespace(
        dfnd=SimpleNamespace(raw=raw),
        input_context=SimpleNamespace(
            coordinates=puw.quantity(coordinates, 'nm'),
            radii=puw.quantity(np.full(5, 0.1), 'nm'),
            atom_indices=np.array([90, 4, 30, 15, 8]),
        ),
    )


def test_nonlocal_atom_blocks_a_locally_clear_point_without_mutating_evidence():
    topo = authored_observation()
    before = deepcopy(topo.dfnd.raw)
    result = inspect_residence_witnesses(topo)
    row = result['witnesses'][0]
    assert row['component_id'] == 'WET-7'
    assert row['nearest_source_atom_index'] == 8
    assert row['nearest_atom_is_nonlocal']
    assert row['all_atom_clearance'] == pytest.approx(-0.1)
    assert row['local_capacity_residual'] == pytest.approx(0)
    assert row['center_in_support'] is True
    assert row['point_status'] == 'blocked'
    assert result['component_existence'] == 'not_determined_by_point_checks'
    assert result['unexamined_connector_component_ids'] == ['WET-8']
    assert topo.dfnd.raw == before


def test_clear_point_retains_only_its_point_guarantee():
    result = inspect_residence_witnesses(authored_observation(blocked=False))
    row = result['witnesses'][0]
    assert row['point_status'] == 'clear'
    assert row['all_atom_clearance'] == pytest.approx(row['local_clearance'])
    assert result['component_existence'] == 'not_determined_by_point_checks'
    assert result['paths_and_boundary'] == 'not_examined'


def test_quantity_policy_and_nonidentity_source_maps_preserve_the_diagnosis():
    topo = authored_observation()
    reference = inspect_residence_witnesses(topo)
    topo.input_context.coordinates = puw.convert(
        topo.input_context.coordinates, to_unit='pm'
    )
    topo.input_context.radii = puw.convert(topo.input_context.radii, to_unit='pm')
    result = inspect_residence_witnesses(topo)
    assert result['witnesses'] == reference['witnesses']
    assert result['length_unit'] == 'nm'
    assert result['witnesses'][0]['source_atom_indices'] == [90, 4, 30, 15]


def test_margin_outside_support_and_degenerate_support_remain_distinct():
    topo = authored_observation(blocked=False)
    topo.dfnd.raw['parameters']['query']['probe_radius'] = topo.dfnd.raw['tetrahedra'][
        0
    ]['R_residence']
    assert inspect_residence_witnesses(topo)['witnesses'][0]['point_status'] == (
        'numerically_unresolved'
    )
    topo.dfnd.raw['tetrahedra'][0]['center'] = [2.0, 2.0, 2.0]
    assert inspect_residence_witnesses(topo)['witnesses'][0]['point_status'] == (
        'outside_support'
    )
    topo.input_context.coordinates[3] = topo.input_context.coordinates[2]
    assert inspect_residence_witnesses(topo)['witnesses'][0]['point_status'] == (
        'unresolved_support'
    )


def test_empty_resident_bank_is_not_a_physical_empty_space_certificate():
    topo = authored_observation()
    topo.dfnd.raw['wet_components'][0]['resident_tetrahedron_ids'] = []
    result = inspect_residence_witnesses(topo)
    assert result['witnesses'] == []
    assert result['component_existence'] == 'not_determined_by_point_checks'


def test_mismatched_map_and_excess_work_refuse_before_point_checks():
    topo = authored_observation()
    with pytest.raises(ValueError, match='budget'):
        inspect_residence_witnesses(topo, max_pairs=4)
    topo.dfnd.raw['tetrahedra'][0]['atom_indices'][0] = 91
    with pytest.raises(ValueError, match='source map'):
        inspect_residence_witnesses(topo)


@pytest.mark.parametrize(
    'case, probe, count',
    [('straight_tube_narrow_dense', 2.5, 30), ('straight_tube_wide_sparse', 5.0, 1)],
)
def test_frozen_public_exclusion_profiles_expose_nonlocal_blocked_centers(
    case, probe, count
):
    from devtools.benchlab.ball_study import receive
    from devtools.benchlab.public_contract import describe_public_contract

    directory = (
        Path(__file__).resolve().parents[1] / 'docs/content/benchlab/synthetic' / case
    )
    topo = receive(directory, probe)
    public = describe_public_contract(topo)
    assert public['public_features']  # current local promotion is preserved
    before = list(topo)
    result = inspect_residence_witnesses(topo)
    assert len(result['witnesses']) == count
    assert list(topo) == before
    assert all(row['center_in_support'] for row in result['witnesses'])
    assert all(row['point_status'] == 'blocked' for row in result['witnesses'])
    assert all(row['nearest_atom_is_nonlocal'] for row in result['witnesses'])
    assert max(abs(row['local_capacity_residual']) for row in result['witnesses']) < (
        1e-12
    )
