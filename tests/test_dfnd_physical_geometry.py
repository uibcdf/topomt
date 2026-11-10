"""Independent analytic controls for the bounded physical hull decomposition."""

import numpy as np
import pytest

from topomt.dfnd.core.physical_boundary import decompose_face, segment_clearance

TRIANGLE = np.array([[0.0, 0.0, 0.0], [4.0, 0.0, 0.0], [0.0, 4.0, 0.0]])


def test_one_disk_can_split_a_face_without_any_carrier_edge_gluing():
    # A disk intersects the two coordinate sides, but neither the origin nor
    # the opposite side. The strict complement has two connected regions.
    result = decompose_face(TRIANGLE, np.array([[1.0, 1.0, 0.0]]), np.array([1.2]))
    assert result['status'] == 'resolved'
    assert len(result['regions']) == 2
    assert result['inventory_complete']
    for region in result['regions']:
        assert region['cells']
        assert region['witness_clearance'] > 0


def test_interior_disk_hole_does_not_split_the_free_face():
    result = decompose_face(TRIANGLE, np.array([[1.0, 1.0, 0.0]]), np.array([0.2]))
    assert result['status'] == 'resolved'
    assert len(result['regions']) == 1


def test_all_atom_intruder_can_cover_a_face_without_a_vertex_ball():
    result = decompose_face(TRIANGLE, np.array([[1.0, 1.0, 0.1]]), np.array([5.0]))
    assert result['status'] == 'resolved'
    assert result['regions'] == []


@pytest.mark.parametrize('mode', ['budget', 'degenerate', 'tangent'])
def test_unsupported_decisions_are_unresolved_instead_of_computed_empty(mode):
    triangle = TRIANGLE.copy()
    centers = np.array([[1.0, 1.0, 0.0]])
    radii = np.array([1.2])
    options = {}
    if mode == 'budget':
        options['max_events'] = 1
    elif mode == 'degenerate':
        triangle[2] = triangle[1]
    else:
        radii[:] = 1.0  # touches two triangle sides exactly
    result = decompose_face(triangle, centers, radii, **options)
    assert result['status'] == 'unresolved'
    assert result['regions'] is None
    assert result['reason']


def test_continuous_segment_uses_all_atoms_and_not_only_endpoints():
    centers = np.array([[0.0, 0.0, 0.0], [10.0, 10.0, 0.0]])
    radii = np.array([0.5, 1.0])
    assert (
        segment_clearance(
            np.array([-1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0]), centers, radii
        )
        < 0
    )
    assert segment_clearance(
        np.array([-1.0, 1.0, 0.0]), np.array([1.0, 1.0, 0.0]), centers, radii
    ) == pytest.approx(0.5)


def test_physical_work_policy_is_explicit_and_validated():
    from topomt.dfnd.config import DFNDQuery

    query = DFNDQuery(physical_boundary=False, boundary_max_events=7)
    assert query.boundary_max_events == 7
    assert query.boundary_tolerance == pytest.approx(1e-7)
    for option in (
        {'boundary_max_events': 0},
        {'boundary_max_faces': True},
        {'boundary_tolerance': 0.0},
        {'physical_boundary': 'yes'},
    ):
        with pytest.raises(ValueError):
            DFNDQuery(**option)


def test_computed_zero_requires_a_complete_positive_margin_cover():
    triangle = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, np.sqrt(3.0) / 2, 0.0]]
    )
    result = decompose_face(triangle, triangle, np.full(3, 0.7))
    assert result['status'] == 'resolved' and not result['regions']
    assert result.get('complete_cover') or result.get('covered_by_ball')
    for leaf in result.get('complete_cover', []):
        vertices = np.asarray(leaf['triangle'])
        center = triangle[leaf['ball_local_index']]
        assert np.max(np.linalg.norm(vertices - center, axis=1)) < 0.7 - 1e-7


@pytest.mark.parametrize('offset', [-1e-9, 0.0, 1e-9])
def test_near_three_ball_closure_is_not_rounded_into_a_count(offset):
    triangle = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, np.sqrt(3.0) / 2, 0.0]]
    )
    result = decompose_face(triangle, triangle, np.full(3, 1.0 / np.sqrt(3.0) + offset))
    assert result['status'] == 'unresolved'
    assert result['regions'] is None


def test_segment_carrier_cover_rejects_a_gap_between_free_endpoints():
    from topomt.dfnd.core.physical_boundary import _carrier_cover

    tetrahedron = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    )
    support = np.array([tetrahedron, tetrahedron + [3.0, 0.0, 0.0]])
    assert (
        _carrier_cover(np.array([0.1, 0.1, 0.1]), np.array([3.1, 0.1, 0.1]), support)
        is None
    )
