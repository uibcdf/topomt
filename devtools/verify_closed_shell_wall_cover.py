"""Independently verify the versioned convex-ball cover of the fixed shell wall.

Run from the repository root with ``python devtools/verify_closed_shell_wall_cover.py``.
This reference tool never imports DFND or executes a detector. It verifies a
certificate on the frozen input; it is not a general molecular pocket method.
"""

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pyunitwizard as puw
from pyunitwizard import QuantityRecord
from scipy.spatial import ConvexHull


def _values(record: dict, field: str, unit: str) -> np.ndarray:
    quantity = QuantityRecord.from_dict(record).to_quantity(field=field, unit=unit)
    return np.asarray(puw.get_value(quantity, to_unit=unit))


def _quantity(value: Any, field: str) -> dict:
    return QuantityRecord.from_quantity(
        puw.quantity(value, 'angstroms'), field=field
    ).to_dict()


def _check_partition(paths: list[list[int]]) -> None:
    tree: dict = {}
    for path in paths:
        node = tree
        for child in path:
            if None in node:
                raise ValueError('Overlapping subdivision leaves')
            node = node.setdefault(child, {})
        if node:
            raise ValueError('Duplicate or overlapping subdivision leaves')
        node[None] = True

    def complete(node: dict) -> None:
        if None in node:
            return
        if set(node) != {0, 1, 2, 3}:
            raise ValueError('Incomplete hull-face partition')
        for child in node.values():
            complete(child)

    complete(tree)


def verify_triangle_cover(
    coordinates: np.ndarray,
    radii: np.ndarray,
    faces: np.ndarray,
    leaves: list[dict[str, Any]],
    probe_radius: float,
    tolerance: float,
    *,
    length_unit: str,
    maximum_depth: int,
    maximum_nodes: int,
) -> dict[str, Any]:
    """Verify complete convex-ball coverage of the supplied triangles.

    Parameters
    ----------
    coordinates, radii : numpy.ndarray
        Atomic centers and nonnegative radii, in ``length_unit``.
    faces : numpy.ndarray
        Local atom-index triples of the supplied triangles.
    leaves : list of dict
        Original face, ordered subdivision path and covering-atom witnesses.
    probe_radius, tolerance : float
        Nonnegative probe and positive safety margin, in ``length_unit``.
    length_unit : str
        Required explicit common input length unit.
    maximum_depth, maximum_nodes : int
        Bounds on subdivision depth and total verified tree nodes.

    Returns
    -------
    dict
        Counts, vertex distances and coverage margins with explicit units.
        The caller establishes the boundary represented by these triangles;
        coverage of a subset alone does not establish enclosure.

    Raises
    ------
    ValueError
        If geometry, bounds, covering inequalities or partitions are invalid.

    Examples
    --------
    Both certificate checkers in this directory use this reference operation.
    """
    scale = float(puw.get_value(puw.quantity(1.0, length_unit), to_unit='angstroms'))
    coords = np.asarray(coordinates, dtype=float) * scale
    radii = np.asarray(radii, dtype=float) * scale
    probe = float(probe_radius) * scale
    tolerance = float(tolerance) * scale
    faces = np.asarray(faces)
    if coords.ndim != 2 or coords.shape[1] != 3 or radii.shape != (len(coords),):
        raise ValueError('Invalid cover geometry shape')
    if (
        not np.isfinite(coords).all()
        or not np.isfinite(radii).all()
        or (radii < 0).any()
    ):
        raise ValueError('Invalid atomic cover geometry')
    if (
        not np.isfinite(probe)
        or probe < 0
        or not np.isfinite(tolerance)
        or tolerance <= 0
    ):
        raise ValueError('Invalid probe or safety tolerance')
    if (
        faces.ndim != 2
        or faces.shape[1] != 3
        or faces.dtype.kind not in 'iu'
        or (faces < 0).any()
        or (faces >= len(coords)).any()
    ):
        raise ValueError('Invalid cover triangle indices')
    partitions: list[list[list[int]]] = [[] for _ in faces]
    distances = []
    margins = []
    if len(leaves) > maximum_nodes:
        raise ValueError('Certificate exceeds the declared node budget')
    for leaf in leaves:
        face_index = leaf['hull_face_index']
        path = leaf['subdivision_path']
        atom = leaf['covering_atom_index']
        if not isinstance(face_index, int) or not 0 <= face_index < len(faces):
            raise ValueError('Invalid hull-face index')
        if not isinstance(atom, int) or not 0 <= atom < len(coords):
            raise ValueError('Invalid covering atom')
        if len(path) > maximum_depth or any(
            type(i) is not int or i not in range(4) for i in path
        ):
            raise ValueError('Invalid subdivision path')
        triangle = coords[faces[face_index]]
        for child in path:
            a, b, c = triangle
            ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
            triangle = np.asarray(
                ((a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca))[child]
            )
        maximum_distance = float(np.linalg.norm(triangle - coords[atom], axis=1).max())
        margin = float(radii[atom] + probe - maximum_distance)
        if margin <= tolerance:
            raise ValueError('A leaf is not covered with the declared safety margin')
        partitions[face_index].append(path)
        distances.append(maximum_distance)
        margins.append(margin)
    for paths in partitions:
        _check_partition(paths)
    if not margins:
        raise ValueError('An empty cover proves no supplied boundary')
    if (4 * len(leaves) - len(faces)) // 3 > maximum_nodes:
        raise ValueError('Complete cover exceeds the declared node budget')
    return {
        'leaf_count': len(leaves),
        'maximum_depth': max(len(leaf['subdivision_path']) for leaf in leaves),
        'maximum_vertex_distances': _quantity(distances, 'maximum_vertex_distances'),
        'minimum_coverage_margin': _quantity(min(margins), 'minimum_coverage_margin'),
    }


def verify_certificate(
    input_file: Path, protocol_file: Path, certificate: dict[str, Any]
) -> dict[str, Any]:
    """Check input identity, every covering inequality and complete partitions.

    Parameters
    ----------
    input_file, protocol_file : pathlib.Path
        Frozen quantity-aware input and declared covering protocol.
    certificate : dict
        Original hull faces and ordered midpoint-subdivision leaf witnesses.

    Returns
    -------
    dict
        Verified counts, explicit length quantities and the origin-enclosure
        conclusion. The conclusion makes no exact global cavity-count claim.

    Raises
    ------
    ValueError
        If identity, geometry, coverage or partition checks fail.

    Examples
    --------
    See the executable invocation at the end of this module. The case overview
    documents the convexity proof and the versioned certificate layout.
    """
    input_bytes = input_file.read_bytes()
    protocol_bytes = protocol_file.read_bytes()
    fixture = json.loads(input_bytes)
    protocol = json.loads(protocol_bytes)
    if certificate['input_sha256'] != hashlib.sha256(input_bytes).hexdigest():
        raise ValueError('Input identity does not match the wall certificate')
    if protocol['input_sha256'] != certificate['input_sha256']:
        raise ValueError('Protocol input identity does not match')
    if certificate['protocol_sha256'] != hashlib.sha256(protocol_bytes).hexdigest():
        raise ValueError('Protocol identity does not match the wall certificate')
    coords = _values(fixture['coordinates'], 'coordinates', 'angstroms')
    radii = _values(fixture['atom_radii'], 'atom_radii', 'angstroms')
    origin = _values(protocol['origin'], 'origin', 'angstroms')
    probe = float(_values(protocol['probe_radius'], 'probe_radius', 'angstroms'))
    tolerance = float(
        _values(protocol['length_absolute'], 'length_absolute', 'angstroms')
    )
    hull = ConvexHull(coords)
    faces = np.asarray(certificate['hull_faces'], dtype=int)
    expected = {tuple(sorted(face)) for face in hull.simplices}
    if (
        len(faces) != len(expected)
        or {tuple(sorted(face)) for face in faces} != expected
    ):
        raise ValueError('Certificate does not cover the actual hull faces')
    leaves = certificate['leaves']
    coverage = verify_triangle_cover(
        coords,
        radii,
        faces,
        leaves,
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
        certificate['maximum_vertex_distances'], 'maximum_vertex_distances', 'angstroms'
    )
    if recorded.shape != (len(leaves),) or not np.allclose(
        recorded, distances, rtol=0, atol=1e-12
    ):
        raise ValueError('Recorded vertex-distance witnesses differ')
    signed = hull.equations[:, :3] @ origin + hull.equations[:, 3]
    origin_margin = float(
        (np.linalg.norm(coords - origin, axis=1) - radii).min() - probe
    )
    if not np.all(signed < -tolerance) or origin_margin <= tolerance:
        raise ValueError('Origin is not strictly interior and free')
    return {
        'verification': 'passed',
        'conclusion': 'origin_free_and_enclosed',
        'hull_face_count': len(faces),
        'leaf_count': len(leaves),
        'maximum_depth': coverage['maximum_depth'],
        'minimum_coverage_margin': coverage['minimum_coverage_margin'],
        'origin_free_margin': _quantity(origin_margin, 'origin_free_margin'),
    }


if __name__ == '__main__':
    case = (
        Path(__file__).resolve().parents[1]
        / 'docs/content/benchlab/synthetic/closed_shell'
    )
    directory = case / 'artifacts/wall_certificate_v1'
    result = verify_certificate(
        case / 'artifacts/closed_shell_v1/input.json',
        directory / 'protocol.json',
        json.loads((directory / 'certificate.json').read_text()),
    )
    print(json.dumps(result, indent=2, allow_nan=False))
