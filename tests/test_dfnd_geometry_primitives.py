import math

import numpy as np
import pytest

from topomt.dfnd.core.clearance import (
    face_gate_radius,
    face_gate_radius_batch,
    face_three_atom_clearance_candidate_2d,
    tetrahedron_residence_radius,
    tetrahedron_residence_radius_batch,
)
from topomt.dfnd.core.permeability import check_face_permeability
from topomt.dfnd.core.solvent_volume import (
    tetrahedron_solvent_volume_estimate,
    tetrahedron_volume,
)


def _inside_tetrahedron(point, vertices, tol=1e-7):
    vertices = np.asarray(vertices, dtype=float)
    matrix = np.column_stack(
        [vertices[0] - vertices[3], vertices[1] - vertices[3], vertices[2] - vertices[3]]
    )
    bary = np.linalg.solve(matrix, np.asarray(point, dtype=float) - vertices[3])
    return bool(np.all(bary >= -tol) and bary.sum() <= 1.0 + tol)


def test_tetrahedron_residence_radius_regular_tetrahedron_equal_radii():
    coords = np.array(
        [
            [1.874, 1.874, 1.874],
            [1.874, -1.874, -1.874],
            [-1.874, 1.874, -1.874],
            [-1.874, -1.874, 1.874],
        ],
        dtype=float,
    )
    radii = np.full(4, 1.7, dtype=float)

    result = tetrahedron_residence_radius(coords, radii)
    radius, center = result.radius, result.center

    side = np.linalg.norm(coords[0] - coords[1])
    expected = side * math.sqrt(3.0 / 8.0) - 1.7
    assert radius == pytest.approx(expected, abs=1e-6)
    assert center == pytest.approx(np.zeros(3), abs=1e-6)


def test_tetrahedron_residence_radius_is_the_clearance_at_an_interior_center():
    # The habitable optimum need NOT be tangent to all four atoms; for this cell
    # it is tangent to three. The robust invariant is that the reported radius
    # equals the actual clearance at the returned center, the center is inside
    # the tetrahedron, and the sphere overlaps no atom.
    coords = np.array(
        [
            [0.0, 0.0, 0.0],
            [5.0, 0.0, 0.0],
            [0.5, 4.5, 0.0],
            [0.5, 0.3, 4.8],
        ],
        dtype=float,
    )
    radii = np.array([1.5, 1.7, 1.2, 1.9], dtype=float)

    result = tetrahedron_residence_radius(coords, radii)
    radius, center = result.radius, result.center

    assert radius > 0.0
    assert _inside_tetrahedron(center, coords)
    clearances = np.linalg.norm(coords - center, axis=1) - radii
    assert clearances.min() == pytest.approx(radius, abs=1e-6)   # radius == clearance
    assert clearances.min() >= -1e-9                              # overlaps no atom


def test_face_gate_equilateral_equal_radii():
    side = 5.3
    height = side * math.sqrt(3.0) / 2.0
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [side, 0.0, 0.0],
            [side / 2.0, height, 0.0],
        ],
        dtype=float,
    )
    radii = np.full(3, 1.7, dtype=float)

    gate = check_face_permeability(points[0], points[1], points[2], radii[0], radii[1], radii[2])

    expected = side / math.sqrt(3.0) - 1.7
    assert gate == pytest.approx(expected, abs=1e-6)


def test_face_gate_is_invariant_to_rigid_transform():
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [4.8, 0.0, 0.0],
            [0.6, 4.3, 0.0],
        ],
        dtype=float,
    )
    radii = np.array([1.4, 1.8, 1.5], dtype=float)
    rotation = np.array(
        [
            [0.0, -1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    shifted = points @ rotation.T + np.array([3.0, -2.0, 5.0])

    gate_a = check_face_permeability(points[0], points[1], points[2], radii[0], radii[1], radii[2])
    gate_b = check_face_permeability(shifted[0], shifted[1], shifted[2], radii[0], radii[1], radii[2])

    assert gate_a > 0.0
    assert gate_b == pytest.approx(gate_a, abs=1e-6)


def test_face_gate_can_be_limited_by_two_atoms_at_boundary():
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [5.0, 0.0, 0.0],
            [2.5, 2.5, 0.0],
        ],
        dtype=float,
    )
    radii = np.array([1.5, 1.5, 1.5], dtype=float)

    gate = check_face_permeability(points[0], points[1], points[2], radii[0], radii[1], radii[2])

    assert gate == pytest.approx(1.0, abs=1e-6)


def test_tetrahedron_residence_radius_is_invariant_to_atom_order():
    coords = np.array(
        [
            [0.0, 0.0, 0.0],
            [5.0, 0.0, 0.0],
            [0.5, 4.5, 0.0],
            [0.5, 0.3, 4.8],
        ],
        dtype=float,
    )
    radii = np.array([1.5, 1.7, 1.2, 1.9], dtype=float)

    ref_result = tetrahedron_residence_radius(coords, radii)
    ref_radius, ref_center = ref_result.radius, ref_result.center
    order = [2, 0, 3, 1]
    ordered = np.asarray(order, dtype=int)
    result = tetrahedron_residence_radius(coords[ordered], radii[ordered])
    radius, center = result.radius, result.center

    assert radius == pytest.approx(ref_radius, abs=1e-6)
    assert center == pytest.approx(ref_center, abs=1e-6)


def test_face_gate_is_invariant_to_atom_order():
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [4.8, 0.0, 0.0],
            [0.6, 4.3, 0.0],
        ],
        dtype=float,
    )
    radii = np.array([1.4, 1.8, 1.5], dtype=float)

    ref_gate = check_face_permeability(points[0], points[1], points[2], radii[0], radii[1], radii[2])
    gate = check_face_permeability(points[2], points[0], points[1], radii[2], radii[0], radii[1])

    assert gate == pytest.approx(ref_gate, abs=1e-6)


# --- Face three-atom clearance candidate direct coverage. ---

def test_face_three_atom_clearance_candidate_inner_soddy_three_tangent_circles():
    # Three mutually tangent unit circles: the inner tangent probe is the inner
    # Soddy circle, radius 1/(3 + 2*sqrt(3)), centered at the triangle centroid.
    radius = 1.0
    c1 = np.array([0.0, 0.0])
    c2 = np.array([2.0, 0.0])
    c3 = np.array([1.0, math.sqrt(3.0)])

    solution = face_three_atom_clearance_candidate_2d(c1, radius, c2, radius, c3, radius)

    assert solution is not None
    r_sol, center = solution
    assert r_sol == pytest.approx(1.0 / (3.0 + 2.0 * math.sqrt(3.0)), abs=1e-6)
    assert center == pytest.approx([1.0, math.sqrt(3.0) / 3.0], abs=1e-6)


def test_face_three_atom_clearance_candidate_returns_none_for_collinear_centers():
    assert (
        face_three_atom_clearance_candidate_2d(
            np.array([0.0, 0.0]), 1.0,
            np.array([2.0, 0.0]), 1.0,
            np.array([4.0, 0.0]), 1.0,
        )
        is None
    )


# --- Tetrahedron residence radius reliability: active-set solver. ---
#
# History: residence_radius used to take max(roots) without checking the
# center was inside the cell, so it returned the EXTERIOR tangent sphere (e.g.
# R_insphere = 29.76 with a longest edge of only 5.95). The solver now enumerates
# interior (4-tangent), face (3-tangent) and edge (2-tangent) candidates and
# keeps the largest clearance whose center is inside the tetrahedron. These
# tests lock that behavior with the former failure case plus property tests
# built on two independent strategies: Monte-Carlo sampling and tangency
# reverse-engineering.

_FORMER_EXTERIOR_ROOT_COORDS = np.array(
    [
        [2.2, 1.2, 2.01],
        [0.48, 4.84, 1.08],
        [3.36, 1.5, 4.37],
        [3.31, 0.66, 4.23],
    ],
    dtype=float,
)
_FORMER_EXTERIOR_ROOT_RADII = np.array([1.78, 1.77, 1.67, 1.54], dtype=float)


def _solve_3d(coords, radii):
    result = tetrahedron_residence_radius(coords, radii)
    return result.radius, result.center


def test_tetrahedron_residence_radius_former_exterior_root_is_now_bounded_and_inside():
    coords = _FORMER_EXTERIOR_ROOT_COORDS
    radii = _FORMER_EXTERIOR_ROOT_RADII
    radius, center = _solve_3d(coords, radii)

    max_edge = max(
        float(np.linalg.norm(coords[a] - coords[b]))
        for a in range(4) for b in range(a + 1, 4)
    )
    assert radius > 0.0
    assert _inside_tetrahedron(center, coords)
    assert radius <= max_edge  # an inscribed sphere cannot exceed the cell size


def _random_tetrahedron(rng):
    return rng.normal(size=(4, 3)) * 3.0, rng.uniform(1.0, 2.0, size=4)


def _monte_carlo_max_clearance(coords, radii, rng, n=50000):
    weights = rng.dirichlet(np.ones(4), size=n)        # uniform inside the tetra
    points = weights @ coords
    clearances = np.linalg.norm(points[:, None, :] - coords[None, :, :], axis=2) - radii
    return float(clearances.min(axis=1).max())


def test_tetrahedron_residence_radius_matches_monte_carlo_reference():
    # Strategy 1: random centers strictly inside the cell give a lower bound on
    # the true residence radius; the active-set solver must be at least as good.
    rng = np.random.default_rng(20240520)
    checked = 0
    for _ in range(100):
        coords, radii = _random_tetrahedron(rng)
        radius, _center = _solve_3d(coords, radii)
        if radius <= 0.0:
            continue
        checked += 1
        assert radius >= _monte_carlo_max_clearance(coords, radii, rng) - 1e-2
    assert checked >= 20


def test_tetrahedron_residence_radius_result_is_a_valid_inscribed_sphere():
    # Strategy 2: reverse-engineer the result. The reported radius must equal the
    # clearance at the returned center (so the sphere touches its nearest atoms
    # and overlaps none), and the center must be inside the cell.
    rng = np.random.default_rng(11)
    checked = 0
    for _ in range(100):
        coords, radii = _random_tetrahedron(rng)
        radius, center = _solve_3d(coords, radii)
        if radius <= 0.0:
            continue
        checked += 1
        assert _inside_tetrahedron(center, coords)
        clearances = np.linalg.norm(coords - center, axis=1) - radii
        assert clearances.min() == pytest.approx(radius, abs=1e-6)
    assert checked >= 20


# --- Residence active-set toys (residence_radius_audit.md): assert which
#     stratum produced the optimum, so the right label is reached for the right
#     reason. R_residence is NOT assumed to equal the four-atom Apollonius. ---

def test_residence_interior4_compact_tetrahedron():
    # Compact regular tetrahedron: the 4-atom Apollonius center is inside and is
    # the maximum, so R_residence == R_apollonius4 and it is valid.
    s = 1.874
    coords = np.array([[s, s, s], [s, -s, -s], [-s, s, -s], [-s, -s, s]], dtype=float)
    radii = np.full(4, 1.7, dtype=float)

    result = tetrahedron_residence_radius(coords, radii)

    assert result.kind == 'interior4'
    assert result.apollonius4_valid is True
    assert result.radius == pytest.approx(result.r_apollonius4, abs=1e-6)
    assert _inside_tetrahedron(result.center, coords)


def test_residence_face_limited_three_atom_optimum():
    # The optimum lies on a face (tangent to three atoms); the four-atom
    # Apollonius candidate is not the residence radius here.
    coords = np.array(
        [[0.0, 0.0, 0.0], [5.0, 0.0, 0.0], [0.5, 4.5, 0.0], [0.5, 0.3, 4.8]],
        dtype=float,
    )
    radii = np.array([1.5, 1.7, 1.2, 1.9], dtype=float)

    result = tetrahedron_residence_radius(coords, radii)

    assert result.kind == 'face3'
    assert result.apollonius4_valid is False
    assert result.radius > 0.0
    assert _inside_tetrahedron(result.center, coords)


def test_residence_edge_limited_sliver():
    # A needle/sliver tetrahedron: the best admissible point is on an edge,
    # tangent to two atoms.
    coords = np.array(
        [[0.0, 0.0, 0.0], [12.0, 0.0, 0.0], [3.0, 1.2, 0.3], [3.5, 0.8, -0.4]],
        dtype=float,
    )
    radii = np.full(4, 1.6, dtype=float)

    result = tetrahedron_residence_radius(coords, radii)

    assert result.kind == 'edge2'
    assert result.radius > 0.0
    assert _inside_tetrahedron(result.center, coords)


def test_residence_apollonius4_invalid_is_not_used():
    # Former exterior-root failure case: the four-atom Apollonius radius is huge
    # (29.76) with a center outside the cell, so it must NOT be the residence
    # radius. Residence comes from a valid in-cell stratum and stays bounded.
    coords = _FORMER_EXTERIOR_ROOT_COORDS
    radii = _FORMER_EXTERIOR_ROOT_RADII

    result = tetrahedron_residence_radius(coords, radii)

    max_edge = max(
        float(np.linalg.norm(coords[a] - coords[b]))
        for a in range(4) for b in range(a + 1, 4)
    )
    assert result.apollonius4_valid is False
    assert result.r_apollonius4 > max_edge          # the raw 4-atom candidate is the exterior sphere
    assert 0.0 < result.radius <= max_edge          # residence stays physical
    assert _inside_tetrahedron(result.center, coords)


def _monte_carlo_face_gate(coords, radii, rng, n=60000):
    # Uniform sampling inside the triangular face gives a lower bound on the
    # largest empty circle clipped to the face (the gate).
    weights = rng.dirichlet(np.ones(3), size=n)
    points = weights @ coords
    clearances = np.linalg.norm(points[:, None, :] - coords[None, :, :], axis=2) - radii
    return float(clearances.min(axis=1).max())


def test_face_gate_radius_matches_monte_carlo_reference():
    # Strategy 1 for the gate: the largest empty circle clipped to the face is an
    # active-set optimum (3-atom interior or 2-atom edge). Monte-Carlo sampling
    # inside the triangle is a lower bound; the (exact) gate must be at least as
    # good, proving the candidate enumeration is complete for the 2D problem.
    rng = np.random.default_rng(424242)
    checked = 0
    for _ in range(120):
        coords = rng.normal(size=(3, 3)) * 3.0
        radii = rng.uniform(1.0, 2.0, size=3)
        result = face_gate_radius(
            coords[0], coords[1], coords[2], radii[0], radii[1], radii[2]
        )
        if result.radius <= 0.0:
            continue
        checked += 1
        assert result.radius >= _monte_carlo_face_gate(coords, radii, rng) - 1.5e-2
    assert checked >= 20


def test_residence_batch_matches_scalar_reference():
    # The vectorized batch solver must bit-match the scalar active-set solver
    # (the trusted, MC-validated reference). This freezes the brute-force
    # vectorized version so a future redundancy-free solver can be diff-tested
    # against it.
    rng = np.random.default_rng(2024)
    coords = rng.normal(size=(400, 4, 3)) * 3.0
    radii = rng.uniform(1.0, 2.0, size=(400, 4))

    radius_batch, _centers, _kinds, _r4, _valid = tetrahedron_residence_radius_batch(coords, radii)
    radius_scalar = np.array(
        [tetrahedron_residence_radius(coords[i], radii[i]).radius for i in range(coords.shape[0])]
    )

    assert np.max(np.abs(radius_batch - radius_scalar)) < 1e-9


def test_tetrahedron_solvent_volume_estimate_is_full_for_zero_radii():
    vertices = np.array(
        [
            [0.0, 0.0, 0.0],
            [4.0, 0.0, 0.0],
            [0.0, 4.0, 0.0],
            [0.0, 0.0, 4.0],
        ],
        dtype=float,
    )
    radii = np.zeros(4, dtype=float)

    result = tetrahedron_solvent_volume_estimate(vertices, radii, resolution=5)

    assert result.volume == pytest.approx(tetrahedron_volume(vertices), abs=1e-12)
    assert result.empty_fraction == pytest.approx(1.0, abs=1e-12)
    assert result.occupied_fraction == pytest.approx(0.0, abs=1e-12)
    assert result.n_samples > 0


def test_tetrahedron_solvent_volume_estimate_decreases_with_atom_radii():
    vertices = np.array(
        [
            [0.0, 0.0, 0.0],
            [4.0, 0.0, 0.0],
            [0.0, 4.0, 0.0],
            [0.0, 0.0, 4.0],
        ],
        dtype=float,
    )
    small_radii = np.full(4, 0.1, dtype=float)
    large_radii = np.full(4, 2.5, dtype=float)

    small = tetrahedron_solvent_volume_estimate(vertices, small_radii, resolution=7)
    large = tetrahedron_solvent_volume_estimate(vertices, large_radii, resolution=7)

    assert 0.0 <= large.volume <= small.volume <= tetrahedron_volume(vertices)
    assert large.occupied_fraction > small.occupied_fraction


def test_face_gate_radius_batch_matches_scalar_reference():
    # The vectorized face gate must bit-match the scalar face_gate_radius (the
    # MC-validated reference). Freezes the brute vectorized gate for a future
    # redundancy-free (unique-face) version to be diff-tested against.
    rng = np.random.default_rng(99)
    coords = rng.normal(size=(400, 3, 3)) * 3.0
    radii = rng.uniform(1.0, 2.0, size=(400, 3))

    radius_batch, _centers, _kinds = face_gate_radius_batch(coords, radii)
    radius_scalar = np.array(
        [
            face_gate_radius(
                coords[i, 0], coords[i, 1], coords[i, 2], radii[i, 0], radii[i, 1], radii[i, 2]
            ).radius
            for i in range(coords.shape[0])
        ]
    )

    assert np.max(np.abs(radius_batch - radius_scalar)) < 1e-9
