"""Independent all-atom certificates for the frozen dumbbell study.

A polygonal surface and its complete neck section are covered by actual
expanded atomic balls. Complete simplex subdivision trees make coverage
replayable without a native graph, an optimizer or sampled-point inference.
"""

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pyunitwizard as puw
from scipy.spatial import ConvexHull

from devtools.verify_closed_shell_wall_cover import _values
from devtools.verify_tube_passage import polyline_clearance


class ReferenceIncomplete(ValueError):
    """A bounded reference construction did not establish the requested cover."""


def _geometry(vertices, cells, centers, radii, probe, length_unit):
    scale = float(puw.get_value(puw.quantity(1.0, length_unit), to_unit='angstroms'))
    vertices = np.asarray(vertices, dtype=float) * scale
    centers = np.asarray(centers, dtype=float) * scale
    radii = np.asarray(radii, dtype=float) * scale
    cells = np.asarray(cells)
    probe = float(probe) * scale
    if (
        vertices.ndim != 2
        or vertices.shape[1] != 3
        or centers.ndim != 2
        or centers.shape[1] != 3
        or len(centers) == 0
        or radii.shape != (len(centers),)
        or np.any(radii < 0)
        or cells.ndim != 2
        or cells.shape[1] not in (3, 4)
        or len(cells) == 0
        or cells.dtype.kind not in 'iu'
        or np.any(cells < 0)
        or np.any(cells >= len(vertices))
        or not np.isfinite(probe)
        or probe < 0
        or not all(np.isfinite(x).all() for x in (vertices, centers, radii))
    ):
        raise ValueError('Invalid explicit-unit simplex/atomic-ball geometry')
    return vertices, cells, centers, radii, probe


def _children(simplex, edge):
    i, j = edge
    midpoint = (simplex[i] + simplex[j]) / 2
    first, second = simplex.copy(), simplex.copy()
    first[i] = midpoint
    second[j] = midpoint
    return first, second


def _limits(maximum_depth, maximum_nodes, margin):
    if (
        type(maximum_depth) is not int
        or not 0 <= maximum_depth <= 32
        or type(maximum_nodes) is not int
        or not 1 <= maximum_nodes <= 1000000
        or not np.isfinite(margin)
        or margin <= 0
    ):
        raise ValueError('Invalid bounded cover limits or angstrom safety margin')


def build_simplex_cover(
    vertices: np.ndarray,
    cells: np.ndarray,
    centers: np.ndarray,
    radii: np.ndarray,
    probe: float,
    *,
    length_unit: str,
    maximum_depth: int,
    maximum_nodes: int,
    margin_angstroms: float = 1e-6,
) -> dict[str, Any]:
    """Construct a sufficient ball cover of complete triangles or tetrahedra.

    Parameters
    ----------
    vertices, cells : numpy.ndarray
        Separate reference vertices and integer triples/quadruples defining
        the entire finite simplicial set to cover.
    centers, radii : numpy.ndarray
        Actual obstacle centers and nonnegative radii; reference vertices are
        never inserted into this obstacle set.
    probe : float
        Nonnegative probe radius in the explicitly declared source length unit.
    length_unit : str
        Common input length unit, converted explicitly to angstroms.
    maximum_depth, maximum_nodes : int
        Maximum binary subdivision depth and visited nodes across all cells.
    margin_angstroms : float, default=1e-6
        Required positive covering margin, explicitly in angstroms.

    Returns
    -------
    dict
        One complete binary subdivision tree per simplex. Every leaf retains
        a real covering atom and every branch its edge and both children.

    Raises
    ------
    ValueError
        Geometry or resource policy is invalid.
    ReferenceIncomplete
        Coverage is unavailable within the declared geometry/margin/budget.
    """
    vertices, cells, centers, radii, probe = _geometry(
        vertices, cells, centers, radii, probe, length_unit
    )
    _limits(maximum_depth, maximum_nodes, margin_angstroms)
    work = 0

    def cover(simplex, depth):
        nonlocal work
        work += 1
        if work > maximum_nodes:
            raise ReferenceIncomplete('Complete cover exceeds visited-node budget')
        distances = np.linalg.norm(simplex[:, None] - centers[None], axis=2)
        margins = radii + probe - distances.max(axis=0)
        atom = int(np.argmax(margins))
        if margins[atom] > margin_angstroms:
            return {'covering_atom_index': atom}
        if np.any(np.min(distances - radii - probe, axis=1) >= -margin_angstroms):
            raise ReferenceIncomplete(
                'Reference simplex has an uncovered vertex or insufficient margin'
            )
        if depth >= maximum_depth:
            raise ReferenceIncomplete('Complete cover exceeds subdivision-depth budget')
        lengths = np.sum((simplex[:, None] - simplex[None]) ** 2, axis=2)
        i, j = map(int, np.unravel_index(np.argmax(lengths), lengths.shape))
        edge = sorted((i, j))
        first, second = _children(simplex, edge)
        return {
            'edge': edge,
            'children': [cover(first, depth + 1), cover(second, depth + 1)],
        }

    return {
        'schema': 'topomt.benchlab.simplex-ball-cover/1',
        'roots': [cover(vertices[cell], 0) for cell in cells],
        'visited_nodes': work,
    }


def verify_simplex_cover(
    vertices: np.ndarray,
    cells: np.ndarray,
    centers: np.ndarray,
    radii: np.ndarray,
    probe: float,
    certificate: dict[str, Any],
    *,
    length_unit: str,
    maximum_depth: int,
    maximum_nodes: int,
    margin_angstroms: float = 1e-6,
) -> dict[str, Any]:
    """Replay every partition and covering inequality without search.

    Parameters
    ----------
    vertices, cells, centers, radii, probe : numpy.ndarray or float
        Same separate reference/atomic geometry as ``build_simplex_cover``.
    certificate : dict
        Original complete binary subdivision trees, with explicit split edges.
    length_unit : str
        Common explicit input length unit.
    maximum_depth, maximum_nodes : int
        Bounds charged across the complete certificate.
    margin_angstroms : float, default=1e-6
        Required positive coverage margin in angstroms.

    Returns
    -------
    dict
        Verified work and leaf counts and a dimensional minimum margin.

    Raises
    ------
    ValueError
        Any geometry, witness, partition, margin or work condition fails.
    """
    vertices, cells, centers, radii, probe = _geometry(
        vertices, cells, centers, radii, probe, length_unit
    )
    _limits(maximum_depth, maximum_nodes, margin_angstroms)
    if certificate.get('schema') != 'topomt.benchlab.simplex-ball-cover/1' or len(
        certificate.get('roots', [])
    ) != len(cells):
        raise ValueError('Missing or invalid complete simplex roots')
    work, leaves, least = 0, 0, float('inf')

    def visit(node, simplex, depth):
        nonlocal work, leaves, least
        work += 1
        if work > maximum_nodes or depth > maximum_depth or not isinstance(node, dict):
            raise ValueError('Certificate exceeds bounded partition policy')
        if set(node) == {'covering_atom_index'}:
            atom = node['covering_atom_index']
            if type(atom) is not int or not 0 <= atom < len(centers):
                raise ValueError('Invalid real covering atom index')
            margin = float(
                radii[atom]
                + probe
                - np.linalg.norm(simplex - centers[atom], axis=1).max()
            )
            if margin <= margin_angstroms:
                raise ValueError('Simplex is not covered with the required margin')
            least = min(least, margin)
            leaves += 1
            return
        if set(node) != {'edge', 'children'}:
            raise ValueError('Incomplete or overlapping cover partition')
        edge = node['edge']
        if (
            not isinstance(edge, list)
            or len(edge) != 2
            or any(type(i) is not int or not 0 <= i < len(simplex) for i in edge)
            or edge[0] >= edge[1]
            or not isinstance(node['children'], list)
            or len(node['children']) != 2
        ):
            raise ValueError('Incomplete binary subdivision or invalid split edge')
        for child, piece in zip(node['children'], _children(simplex, edge)):
            visit(child, piece, depth + 1)

    for tree, cell in zip(certificate['roots'], cells):
        visit(tree, vertices[cell], 0)
    if work != certificate.get('visited_nodes'):
        raise ValueError('Declared certificate work differs from complete replay')
    return {
        'visited_nodes': work,
        'leaf_count': leaves,
        'minimum_coverage_margin': puw.quantity(least, 'angstroms'),
    }


def _model(input_file, protocol_file):
    payload, policy = input_file.read_bytes(), protocol_file.read_bytes()
    fixture, protocol = json.loads(payload), json.loads(policy)
    if (
        protocol['schema'] != 'topomt.benchlab.dumbbell-protocol/1'
        or fixture['case_id'] != protocol['case']
        or protocol['case'] != 'dumbbell'
        or protocol['input_sha256'] != hashlib.sha256(payload).hexdigest()
        or protocol['length_unit'] != 'angstroms'
        or [c['probe_angstroms'] for c in protocol['selected_controls']]
        != [1.4, 2.2, 6.0]
        or protocol['barrier']['wall_probe_angstroms'] != 1.4
        or protocol['barrier']['separator_probe_angstroms'] != 2.2
        or protocol['axis_reference']['probe_angstroms'] != 1.4
    ):
        raise ValueError('Dumbbell input/protocol identity or units differ')
    centers = _values(fixture['coordinates'], 'coordinates', 'angstroms')
    radii = _values(fixture['atom_radii'], 'atom_radii', 'angstroms')
    anchors = _values(protocol['anchors'], 'anchors', 'angstroms')
    if (
        centers.shape != (94, 3)
        or radii.shape != (94,)
        or anchors.shape != (2, 3)
        or not np.all(radii == 1.88)
        or fixture['source_atom_indices'] != list(range(94))
    ):
        raise ValueError('Frozen dumbbell model or source support differs')
    return centers, radii, anchors, protocol, hashlib.sha256(policy).hexdigest()


def _barrier(protocol):
    p = protocol['barrier']
    radius, half = (
        p['nominal_lobe_radius_angstroms'],
        p['nominal_separation_angstroms'] / 2,
    )
    n, intervals = p['angular_columns'], p['polar_intervals_per_lobe']
    if (
        type(n) is not int
        or not 3 <= n <= 128
        or type(intervals) is not int
        or not 2 <= intervals <= 64
        or not 0 < half < radius
        or p['separator_plane_x_angstroms'] != 0
    ):
        raise ValueError('Unsupported simple polygonal dumbbell barrier')
    angles = np.linspace(np.pi, np.arccos(half / radius), intervals + 1)
    xs, rs = -half + radius * np.cos(angles), radius * np.sin(angles)
    xs[-1], rs[0] = 0.0, 0.0
    profile = np.column_stack([np.r_[xs, -xs[-2::-1]], np.r_[rs, rs[-2::-1]]])
    if not np.all(np.diff(profile[:, 0]) > 0) or np.any(profile[1:-1, 1] <= 0):
        raise ValueError('Barrier is not a simple closed chain of positive frusta')
    theta = np.arange(n) * 2 * np.pi / n
    vertices = [[profile[0, 0], 0.0, 0.0]]
    for x, r in profile[1:-1]:
        vertices.extend(
            np.column_stack(
                [np.full(n, x), r * np.cos(theta), r * np.sin(theta)]
            ).tolist()
        )
    vertices.append([profile[-1, 0], 0.0, 0.0])
    faces = [[0, 1 + j, 1 + (j + 1) % n] for j in range(n)]
    for ring in range(len(profile) - 3):
        a, b = 1 + ring * n, 1 + (ring + 1) * n
        for j in range(n):
            k = (j + 1) % n
            faces.extend([[a + j, b + j, b + k], [a + j, b + k, a + k]])
    last = 1 + (len(profile) - 3) * n
    faces.extend([[last + j, len(vertices) - 1, last + (j + 1) % n] for j in range(n)])
    counts = Counter(
        tuple(sorted((f[j], f[(j + 1) % 3]))) for f in faces for j in range(3)
    )
    if set(counts.values()) != {2}:
        raise ValueError('Barrier boundary has incomplete mesh seams')
    seam = np.asarray(vertices)[1 + (intervals - 1) * n : 1 + intervals * n]
    if not np.all(seam[:, 0] == 0):
        raise ValueError('Separator differs from the complete neck section')
    section_vertices = np.vstack([[0.0, 0.0, 0.0], seam])
    section_faces = np.asarray([[0, 1 + j, 1 + (j + 1) % n] for j in range(n)])
    return (
        np.asarray(vertices),
        np.asarray(faces),
        section_vertices,
        section_faces,
        profile,
    )


def _hull(centers):
    hull = ConvexHull(centers)
    faces = np.asarray(sorted(tuple(sorted(map(int, face))) for face in hull.simplices))
    vertices = np.vstack([centers, centers.mean(axis=0)])
    return vertices, np.column_stack([np.full(len(faces), len(centers)), faces]), hull


def build_reference(input_file: Path, protocol_file: Path) -> dict[str, Any]:
    """Construct independent wall, separator and finite-hull certificates.

    Parameters
    ----------
    input_file, protocol_file : Path
        Frozen ball input and preceding explicit reference protocol.

    Returns
    -------
    dict
        Original geometry-independent-of-DFND subdivision witnesses. References
        concern named anchors; no exact global cavity-count claim is supplied.

    Raises
    ------
    ValueError
        Input or reference geometry is invalid.
    ReferenceIncomplete
        Any sufficient cover cannot be established within its frozen limits.
    """
    centers, radii, _, p, digest = _model(input_file, protocol_file)
    outer_v, outer_f, neck_v, neck_f, _ = _barrier(p)
    hull_v, hull_c, _ = _hull(centers)
    limits = p['reference_limits']
    arguments = {
        'length_unit': 'angstroms',
        'maximum_depth': limits['maximum_depth'],
        'maximum_nodes': limits['maximum_visited_nodes'],
        'margin_angstroms': limits['length_margin_angstroms'],
    }
    stages = [
        ('wall', outer_v, outer_f, p['barrier']['wall_probe_angstroms']),
        ('separator', neck_v, neck_f, p['barrier']['separator_probe_angstroms']),
        ('finite_hull', hull_v, hull_c, 6.0),
    ]
    return {
        'schema': 'topomt.benchlab.dumbbell-certificate/1',
        'input_sha256': p['input_sha256'],
        'protocol_sha256': digest,
        'stages': {
            name: build_simplex_cover(v, cells, centers, radii, probe, **arguments)
            for name, v, cells, probe in stages
        },
    }


def verify_reference(
    input_file: Path, protocol_file: Path, certificate: dict[str, Any]
) -> dict[str, Any]:
    """Replay covers and derive only justified anchor/set conclusions.

    Parameters
    ----------
    input_file, protocol_file : Path
        Frozen ball input and declared reference policy.
    certificate : dict
        Complete independent wall, separator and native finite-hull covers.

    Returns
    -------
    dict
        Explicit dimensional clearances, enclosure/separation and exclusion
        conclusions, with global component count and optimum left unestablished.

    Raises
    ------
    ValueError
        Any identity, continuous-path, geometry, cover or enclosure check fails.
    """
    centers, radii, anchors, p, digest = _model(input_file, protocol_file)
    if (
        certificate.get('schema') != 'topomt.benchlab.dumbbell-certificate/1'
        or certificate.get('input_sha256') != p['input_sha256']
        or certificate.get('protocol_sha256') != digest
        or set(certificate.get('stages', {})) != {'wall', 'separator', 'finite_hull'}
    ):
        raise ValueError('Certificate identity or complete stage inventory differs')
    outer_v, outer_f, neck_v, neck_f, profile = _barrier(p)
    hull_v, hull_c, hull = _hull(centers)
    limits = p['reference_limits']
    arguments = {
        'length_unit': 'angstroms',
        'maximum_depth': limits['maximum_depth'],
        'maximum_nodes': limits['maximum_visited_nodes'],
        'margin_angstroms': limits['length_margin_angstroms'],
    }
    cover_rows = {}
    for name, vertices, cells, probe in [
        ('wall', outer_v, outer_f, 1.4),
        ('separator', neck_v, neck_f, 2.2),
        ('finite_hull', hull_v, hull_c, 6.0),
    ]:
        cover_rows[name] = verify_simplex_cover(
            vertices,
            cells,
            centers,
            radii,
            probe,
            certificate['stages'][name],
            **arguments,
        )
    margin = limits['length_margin_angstroms']
    anchor_clearances = np.min(
        np.linalg.norm(anchors[:, None] - centers[None], axis=2) - radii, axis=1
    )
    stations = np.asarray(p['axis_reference']['stations_angstroms'])
    if (
        stations.shape != (3, 3)
        or not np.array_equal(stations[[0, -1]], anchors)
        or not np.all(stations[:, 1:] == 0)
        or not np.all(np.diff(stations[:, 0]) > 0)
        or np.any(anchors[:, 0] <= profile[0, 0])
        or np.any(anchors[:, 0] >= profile[-1, 0])
        or anchors[0, 0] >= 0
        or anchors[1, 0] <= 0
        or not np.all(anchors[:, 1:] == 0)
        or np.any(
            hull.equations[:, :3] @ anchors.T + hull.equations[:, 3, None] >= -margin
        )
        or np.min(anchor_clearances) <= 2.2 + margin
    ):
        raise ValueError(
            'Named anchors are not free in both lobes and inside the finite hull/barrier'
        )
    path_clearance = polyline_clearance(
        stations, centers, radii, length_unit='angstroms'
    )
    if path_clearance <= 1.4 + margin:
        raise ValueError(
            'The complete designated axis is not a free connecting witness'
        )
    return {
        'schema': 'topomt.benchlab.dumbbell-verification/1',
        'input_sha256': p['input_sha256'],
        'protocol_sha256': digest,
        'anchor_connection_1.4A': 'certified',
        'anchor_enclosure_1.4A': 'certified',
        'anchor_separation_2.2A': 'certified',
        'finite_hull_exclusion_6A': 'certified',
        'anchor_clearances': puw.quantity(anchor_clearances, 'angstroms'),
        'connecting_axis_minimum_clearance': puw.quantity(path_clearance, 'angstroms'),
        'barrier_vertices': len(outer_v),
        'barrier_faces': len(outer_f),
        'separator_triangles': len(neck_f),
        'finite_hull_tetrahedra': len(hull_c),
        'covers': cover_rows,
        'exact_global_free_component_count': 'not_established',
        'barrier_equals_native_hull': False,
        'optimal_bottleneck': 'not_established',
        'scope': 'One enclosed connected region containing both anchors at 1.4 A; at least two distinct enclosed regions at 2.2 A; no free center anywhere in the finite native hull at 6 A. Other regions/volumes and physical aperture area are not counted.',
    }
