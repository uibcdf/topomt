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
    partitions: list[list[list[int]]] = [[] for _ in faces]
    distances = []
    margins = []
    leaves = certificate['leaves']
    if len(leaves) > protocol['maximum_visited_nodes']:
        raise ValueError('Certificate exceeds the declared node budget')
    for leaf in leaves:
        face_index = leaf['hull_face_index']
        path = leaf['subdivision_path']
        atom = leaf['covering_atom_index']
        if not isinstance(face_index, int) or not 0 <= face_index < len(faces):
            raise ValueError('Invalid hull-face index')
        if not isinstance(atom, int) or not 0 <= atom < len(coords):
            raise ValueError('Invalid covering atom')
        if len(path) > protocol['maximum_depth'] or any(
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
        'maximum_depth': max(map(len, (leaf['subdivision_path'] for leaf in leaves))),
        'minimum_coverage_margin': _quantity(min(margins), 'minimum_coverage_margin'),
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
