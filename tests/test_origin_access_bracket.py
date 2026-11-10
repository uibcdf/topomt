"""Origin access is bracketed by a complete path and a complete hull cover."""

import numpy as np
import pytest


def test_preverified_opening_wall_prunes_only_independently_covered_faces():
    from pathlib import Path

    from devtools.verify_origin_access_bracket import _discovery_faces, _model

    case = (
        Path(__file__).resolve().parents[1]
        / 'docs/content/benchlab/synthetic/shell_with_opening'
    )
    protocol_file = case / 'artifacts/access_bracket_v2/protocol.json'
    input_file = case / 'artifacts/shell_with_opening_v1/input.json'
    centers, radii, faces, _, protocol, *_ = _model(input_file, protocol_file)
    selected = _discovery_faces(
        input_file, protocol_file, protocol, centers, radii, faces
    )
    assert len(selected) == 1
    assert len(faces) == 128
    assert len(selected) < len(faces)


def test_subdivision_cover_requires_complete_positive_margin_partition():
    from devtools.verify_closed_shell_wall_cover import verify_triangle_cover
    from devtools.verify_origin_access_bracket import build_cover

    centers = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    radii = np.full(3, 0.7)
    faces = np.array([[0, 1, 2]])
    leaves, work = build_cover(centers, radii, faces, 0.1, 1e-6, 12, 1000)
    assert work <= 1000
    verify_triangle_cover(
        centers,
        radii,
        faces,
        leaves,
        0.1,
        1e-6,
        length_unit='angstroms',
        maximum_depth=12,
        maximum_nodes=1000,
    )
    with pytest.raises(ValueError):
        verify_triangle_cover(
            centers,
            radii,
            faces,
            leaves[:-1],
            0.1,
            1e-6,
            length_unit='angstroms',
            maximum_depth=12,
            maximum_nodes=1000,
        )


def test_cover_budget_failure_supplies_no_accepted_cover():
    from devtools.verify_origin_access_bracket import build_cover

    centers = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    with pytest.raises(ValueError, match='budget'):
        build_cover(centers, np.full(3, 0.1), np.array([[0, 1, 2]]), 0.01, 1e-6, 1, 1)


def test_path_checks_segment_interior_and_infinite_ray():
    from devtools.verify_origin_access_bracket import path_clearance

    centers = np.array([[0.0, 0.0, 0.0]])
    assert (
        path_clearance(
            np.array([-2.0, 0.0, 0.0]),
            np.array([2.0, 0.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
            centers,
            np.array([0.5]),
        )
        < 0
    )
    assert (
        path_clearance(
            np.array([-2.0, 0.0, 0.0]),
            np.array([-1.0, 0.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
            centers,
            np.array([0.5]),
        )
        < 0
    )
    assert (
        path_clearance(
            np.array([-2.0, 0.0, 0.0]),
            np.array([-1.0, 0.0, 0.0]),
            np.array([-1.0, 0.0, 0.0]),
            centers,
            np.array([0.5]),
        )
        == 0.5
    )
