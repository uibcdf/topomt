"""Check the fixed shell's hull-opening certificate without DFND or optimization.

Convex intersection witnesses determine the nerve through dimension two.
Together with a complete cover of the remaining hull, planar complement
duality counts strict-clearance boundary patches. This reference tool does
not redefine the native external-link or public Mouth semantics.
"""

import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import pyunitwizard as puw
from pyunitwizard import QuantityRecord
from scipy.spatial import ConvexHull

if __package__:
    from .verify_closed_shell_wall_cover import verify_triangle_cover
else:
    from verify_closed_shell_wall_cover import verify_triangle_cover


def _values(record: dict, field: str, unit: str) -> np.ndarray:
    quantity = QuantityRecord.from_dict(record).to_quantity(field=field, unit=unit)
    return np.asarray(puw.get_value(quantity, to_unit=unit))


def _length(value: Any, field: str) -> dict:
    return QuantityRecord.from_quantity(
        puw.quantity(value, 'angstroms'), field=field
    ).to_dict()


def _weights(record: dict, field: str, size: int) -> np.ndarray:
    result = _values(record, field, 'dimensionless')
    if (
        result.shape != (size,)
        or not np.isfinite(result).all()
        or (result < 0).any()
        or result.sum() <= 0
    ):
        raise ValueError(f'Invalid {field}')
    return result / result.sum()


def first_betti(
    vertices: list[int],
    edges: list[tuple[int, int]],
    triangles: list[tuple[int, int, int]],
) -> dict[str, int]:
    """Compute H1 rank of a finite nerve from its complete two-skeleton over F2.

    Parameters
    ----------
    vertices, edges, triangles : list
        Unique vertex IDs, edge pairs and triangle triples of the two-skeleton.

    Returns
    -------
    dict
        Simplex counts, graph components, exact boundary-two rank and beta_1.
        Higher simplices cannot change H1. Interpreting this as planar holes
        additionally requires the verified convex-nerve hypotheses.

    Raises
    ------
    ValueError
        If simplices are duplicated or their required faces are absent.

    Examples
    --------
    A three-edge cycle has beta_1=1; adding its triangle makes beta_1=0.
    """
    vertex_set = set(vertices)
    edge_set = {tuple(sorted(edge)) for edge in edges}
    triangle_set = {tuple(sorted(triangle)) for triangle in triangles}
    if (
        len(vertex_set) != len(vertices)
        or len(edge_set) != len(edges)
        or len(triangle_set) != len(triangles)
    ):
        raise ValueError('Duplicate nerve simplex')
    if any(len(set(edge)) != 2 or not set(edge) <= vertex_set for edge in edge_set):
        raise ValueError('Invalid nerve edge')
    if any(
        len(set(triangle)) != 3
        or not all(edge in edge_set for edge in combinations(triangle, 2))
        for triangle in triangle_set
    ):
        raise ValueError('A triangle is missing a required edge')
    parents = {vertex: vertex for vertex in vertices}

    def root(vertex: int) -> int:
        while parents[vertex] != vertex:
            vertex = parents[vertex]
        return vertex

    for a, b in edge_set:
        parents[root(a)] = root(b)
    components = len({root(vertex) for vertex in vertices})
    edge_index = {edge: index for index, edge in enumerate(sorted(edge_set))}
    basis: dict[int, int] = {}
    for triangle in sorted(triangle_set):
        column = sum(1 << edge_index[edge] for edge in combinations(triangle, 2))
        while column:
            pivot = column.bit_length() - 1
            if pivot in basis:
                column ^= basis[pivot]
            else:
                basis[pivot] = column
                break
    return {
        'vertices': len(vertices),
        'edges': len(edges),
        'triangles': len(triangles),
        'components': components,
        'rank_boundary_2': len(basis),
        'beta_1': len(edges) - len(vertices) + components - len(basis),
    }


def verify_convex_intersections(
    coords: np.ndarray,
    parent_ids: list[int],
    triangle: np.ndarray,
    expanded_radius: float,
    tolerance: float,
    records: list[dict],
    budget: int,
    *,
    length_unit: str,
) -> dict[str, Any]:
    """Verify a complete two-skeleton of equal-ball intersections on a triangle.

    Parameters
    ----------
    coords, triangle : numpy.ndarray
        Atomic centers and three triangle vertices in ``length_unit``.
    parent_ids : list[int]
        Unique source IDs corresponding to rows of ``coords``.
    expanded_radius, tolerance : float
        Common closed-ball radius and positive decision margin in ``length_unit``.
    records : list[dict]
        Complete singleton, active-pair and clique-triple decisions. Positive
        decisions carry barycentric witnesses; negative ones carry convex dual
        weights and a unit separating direction, all dimensionless records.
    budget : int
        Maximum accepted number of records.
    length_unit : str
        Explicit length unit for every bare geometric argument.

    Returns
    -------
    dict
        Nerve ranks and a quantity-aware minimum decision margin in angstroms.

    Raises
    ------
    ValueError
        If geometry, a witness or the complete inventory cannot be verified.

    Examples
    --------
    Both BenchLab hull-boundary checkers use this routine with explicit units.
    """
    coords = np.asarray(
        puw.get_value(puw.quantity(coords, length_unit), to_unit='angstroms')
    )
    triangle = np.asarray(
        puw.get_value(puw.quantity(triangle, length_unit), to_unit='angstroms')
    )
    expanded_radius = float(
        puw.get_value(puw.quantity(expanded_radius, length_unit), to_unit='angstroms')
    )
    tolerance = float(
        puw.get_value(puw.quantity(tolerance, length_unit), to_unit='angstroms')
    )
    if (
        coords.shape != (len(parent_ids), 3)
        or not parent_ids
        or len(set(parent_ids)) != len(parent_ids)
        or triangle.shape != (3, 3)
        or not np.isfinite(coords).all()
        or not np.isfinite(triangle).all()
        or not np.isfinite(expanded_radius)
        or not np.isfinite(tolerance)
        or expanded_radius <= 0
        or tolerance <= 0
        or np.linalg.norm(
            np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
        )
        == 0
    ):
        raise ValueError('Invalid convex-intersection geometry or tolerance')
    if len(records) > budget:
        raise ValueError('Intersection certificate exceeds its budget')
    source_map = {atom: index for index, atom in enumerate(parent_ids)}
    decisions: dict[tuple[int, ...], bool] = {}
    margins = []
    for record in records:
        subset = tuple(record['atom_indices'])
        if (
            not 1 <= len(subset) <= 3
            or tuple(sorted(set(subset))) != subset
            or not set(subset) <= source_map.keys()
        ):
            raise ValueError('Invalid intersection atom subset')
        if subset in decisions or type(record['nonempty']) is not bool:
            raise ValueError('Duplicate or invalid intersection decision')
        centers = coords[[source_map[atom] for atom in subset]]
        if record['nonempty']:
            weights = _weights(record['barycentric_weights'], 'barycentric_weights', 3)
            point = weights @ triangle
            margin = float(
                expanded_radius - np.linalg.norm(centers - point, axis=1).max()
            )
            if margin <= tolerance:
                raise ValueError('Invalid positive intersection witness')
        else:
            weights = _weights(record['dual_weights'], 'dual_weights', len(subset))
            direction = _values(record['direction'], 'direction', 'dimensionless')
            if (
                direction.shape != (3,)
                or not np.isfinite(direction).all()
                or abs(np.linalg.norm(direction) - 1) > 1e-10
            ):
                raise ValueError('Invalid separating direction')
            direction = direction / np.linalg.norm(direction)
            center = weights @ centers
            variance = float(weights @ np.sum((centers - center) ** 2, axis=1))
            separation = max(0.0, float(((triangle - center) @ direction).min()))
            # For every point in T, the weighted squared distance is at least
            # variance + separation**2. It cannot satisfy all expanded balls.
            margin = float(np.sqrt(variance + separation**2) - expanded_radius)
            if margin <= tolerance:
                raise ValueError('Invalid negative intersection lower bound')
        margins.append(margin)
        decisions[subset] = record['nonempty']
    required: set[tuple[int, ...]] = {(atom,) for atom in parent_ids}
    if not required <= decisions.keys():
        raise ValueError('Incomplete vertex intersection inventory')
    vertices = sorted(atom for atom in parent_ids if decisions[(atom,)])
    pairs = set(combinations(vertices, 2))
    required |= pairs
    if not pairs <= decisions.keys():
        raise ValueError('Incomplete edge intersection inventory')
    edges = sorted(edge for edge in pairs if decisions[edge])
    edge_set = set(edges)
    triples = {
        triple
        for triple in combinations(vertices, 3)
        if all(edge in edge_set for edge in combinations(triple, 2))
    }
    required |= triples
    if set(decisions) != required:
        raise ValueError('Incomplete or extraneous triangle intersection inventory')
    triangles = sorted(triple for triple in triples if decisions[triple])
    return {
        'nerve': first_betti(vertices, edges, triangles),
        'minimum_intersection_decision_margin': _length(
            min(margins), 'minimum_intersection_decision_margin'
        ),
    }


def verify_certificate(
    input_file: Path, protocol_file: Path, certificate: dict[str, Any]
) -> dict[str, Any]:
    """Verify the fixed-input strict-clearance opening count on its convex hull.

    Parameters
    ----------
    input_file, protocol_file : pathlib.Path
        Frozen quantity-aware atomic input and declared reference protocol.
    certificate : dict
        Complete wall cover and positive/negative convex-intersection witnesses.

    Returns
    -------
    dict
        Boundary-patch count, verified nerve, origin connection and explicit
        length margins. The count uses the declared hull and strict clearance.

    Raises
    ------
    ValueError
        If a witness, completeness condition, identity or scope hypothesis fails.

    Examples
    --------
    From the repository root: ``python devtools/verify_opening_connectivity.py``.
    """
    raw_input = input_file.read_bytes()
    raw_protocol = protocol_file.read_bytes()
    fixture, protocol = json.loads(raw_input), json.loads(raw_protocol)
    if (
        hashlib.sha256(raw_input).hexdigest() != certificate['input_sha256']
        or protocol['input_sha256'] != certificate['input_sha256']
    ):
        raise ValueError('Input identity differs from the certificate')
    if hashlib.sha256(raw_protocol).hexdigest() != certificate['protocol_sha256']:
        raise ValueError('Protocol identity differs from the certificate')
    coords = _values(fixture['coordinates'], 'coordinates', 'angstroms')
    radii = _values(fixture['atom_radii'], 'atom_radii', 'angstroms')
    probe = float(_values(protocol['probe_radius'], 'probe_radius', 'angstroms'))
    tolerance = float(
        _values(protocol['length_absolute'], 'length_absolute', 'angstroms')
    )
    parent_ids = fixture['derivation']['parent_atom_indices']
    parent_map = {atom: index for index, atom in enumerate(parent_ids)}
    selected = tuple(sorted(protocol['face_parent_atom_indices']))
    local_face = [parent_map[atom] for atom in selected]
    triangle = coords[local_face]
    if not np.all(radii == radii[0]):
        raise ValueError('This certificate requires equal atomic radii')
    hull = ConvexHull(coords)
    all_faces = {tuple(sorted(map(int, face))) for face in hull.simplices}
    if tuple(sorted(local_face)) not in all_faces:
        raise ValueError('Selected triangle is not a hull face')
    cover = certificate['wall_cover']
    covered_faces = np.asarray(cover['hull_faces'], dtype=int)
    if len(covered_faces) != len(all_faces) - 1 or {
        tuple(sorted(map(int, face))) for face in covered_faces
    } != all_faces - {tuple(sorted(local_face))}:
        raise ValueError('Wall certificate does not cover exactly the other hull faces')
    coverage = verify_triangle_cover(
        coords,
        radii,
        covered_faces,
        cover['leaves'],
        probe,
        tolerance,
        length_unit='angstroms',
        maximum_depth=protocol['maximum_depth'],
        maximum_nodes=protocol['maximum_visited_nodes'],
    )
    distances = _values(
        coverage['maximum_vertex_distances'], 'maximum_vertex_distances', 'angstroms'
    )
    recorded = _values(
        cover['maximum_vertex_distances'], 'maximum_vertex_distances', 'angstroms'
    )
    if recorded.shape != distances.shape or not np.allclose(
        recorded, distances, atol=1e-12, rtol=0
    ):
        raise ValueError('Wall vertex-distance witnesses differ')
    intersections = verify_convex_intersections(
        coords,
        parent_ids,
        triangle,
        float(radii[0] + probe),
        tolerance,
        certificate['intersections'],
        protocol['maximum_intersection_records'],
        length_unit='angstroms',
    )
    nerve = intersections['nerve']
    origin = _values(protocol['origin'], 'origin', 'angstroms')
    axis = _values(protocol['axis'], 'axis', 'dimensionless')
    if axis.shape != (3,) or abs(np.linalg.norm(axis) - 1) > 1e-12:
        raise ValueError('Invalid origin ray direction')
    if not np.all(hull.equations[:, :3] @ origin + hull.equations[:, 3] < -tolerance):
        raise ValueError('Origin is not strictly inside the hull')
    delta = coords - origin
    projected = np.maximum(delta @ axis, 0)
    ray_clearance = float(
        (np.linalg.norm(delta - projected[:, None] * axis, axis=1) - radii).min()
    )
    normal = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
    denominator = float(normal @ axis)
    if abs(denominator) < 1e-12:
        raise ValueError('Origin ray is parallel to the selected face')
    distance = float(normal @ (triangle[0] - origin) / denominator)
    crossing = origin + distance * axis
    basis = np.stack([triangle[1] - triangle[0], triangle[2] - triangle[0]], axis=1)
    barycentric = np.linalg.lstsq(basis, crossing - triangle[0], rcond=None)[0]
    weights = np.array([1 - barycentric.sum(), *barycentric])
    if (
        distance <= tolerance
        or weights.min() <= protocol['barycentric_absolute']
        or ray_clearance - probe <= tolerance
        or nerve['beta_1'] < 1
    ):
        raise ValueError('Origin ray does not certify a free interior crossing')
    return {
        'verification': 'passed',
        'face_parent_atom_indices': list(selected),
        'covered_hull_face_count': len(covered_faces),
        'cover_leaf_count': coverage['leaf_count'],
        'nerve': nerve,
        'opening_component_count': nerve['beta_1'],
        'origin_connected_to_opening': True,
        'minimum_coverage_margin': coverage['minimum_coverage_margin'],
        'minimum_intersection_decision_margin': intersections[
            'minimum_intersection_decision_margin'
        ],
        'ray_minimum_clearance': _length(ray_clearance, 'ray_minimum_clearance'),
        'ray_crossing': _length(crossing, 'ray_crossing'),
        'scope': 'Strict-clearance probe-center components on this convex-hull boundary; not an intrinsic biological mouth count or a general graph-path proof.',
    }


if __name__ == '__main__':
    case = (
        Path(__file__).resolve().parents[1]
        / 'docs/content/benchlab/synthetic/shell_with_opening'
    )
    data = case / 'artifacts/opening_connectivity_v1'
    result = verify_certificate(
        case / 'artifacts/shell_with_opening_v1/input.json',
        data / 'protocol.json',
        json.loads((data / 'certificate.json').read_text()),
    )
    print(json.dumps(result, indent=2, allow_nan=False))
