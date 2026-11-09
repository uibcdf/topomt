"""Independently verify strict-clearance patches on the fixed tetrahedron hull.

No DFND, detector or optimizer is used. Shared edges are blocked; the convex
intersection nerve on each face counts bounded complementary patches. Explicit
all-atom rays connect the four patches to the same free centroid.
"""

import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import pyunitwizard as puw
from pyunitwizard import QuantityRecord

if __package__:
    from .verify_opening_connectivity import verify_convex_intersections
else:
    from verify_opening_connectivity import verify_convex_intersections


def _values(record: dict, field: str) -> np.ndarray:
    quantity = QuantityRecord.from_dict(record).to_quantity(
        field=field, unit='angstroms'
    )
    return np.asarray(puw.get_value(quantity, to_unit='angstroms'), dtype=float)


def _length(value: Any, field: str) -> dict:
    return QuantityRecord.from_quantity(
        puw.quantity(value, 'angstroms'), field=field
    ).to_dict()


def verify_certificate(
    input_file: Path, protocol_file: Path, certificate: dict[str, Any]
) -> dict[str, Any]:
    """Verify the fixed tetrahedron's three independently justified regimes.

    Parameters
    ----------
    input_file, protocol_file : pathlib.Path
        Quantity-aware atomic input and frozen scope, probes, budgets and mapping.
    certificate : dict
        Input/protocol hashes, complete six-edge inventory and all four faces'
        positive/negative intersection witnesses, expressed in source atom IDs.

    Returns
    -------
    dict
        Boundary-patch counts, per-face nerves, ray-clearance evidence and sealed
        and excluded controls, with explicit quantity-aware length margins.

    Raises
    ------
    ValueError
        If identities, geometry, inventories, witnesses or strict margins fail.

    Examples
    --------
    From the repository root: ``python devtools/verify_tetrahedron_boundary.py``.
    """
    raw_input, raw_protocol = input_file.read_bytes(), protocol_file.read_bytes()
    fixture, protocol = json.loads(raw_input), json.loads(raw_protocol)
    if (
        hashlib.sha256(raw_input).hexdigest() != certificate['input_sha256']
        or protocol['input_sha256'] != certificate['input_sha256']
        or hashlib.sha256(raw_protocol).hexdigest() != certificate['protocol_sha256']
    ):
        raise ValueError('Input or protocol identity differs')
    coords = _values(fixture['coordinates'], 'coordinates')
    radii = _values(fixture['atom_radii'], 'atom_radii')
    probes = _values(protocol['probe_radii'], 'probe_radii')
    tolerance = float(_values(protocol['length_absolute'], 'length_absolute'))
    edge = float(_values(fixture['edge'], 'edge'))
    ids = protocol['atom_indices']
    if (
        coords.shape != (4, 3)
        or radii.shape != (4,)
        or not np.isfinite(coords).all()
        or not np.isfinite(radii).all()
        or not np.all(radii == radii[0])
        or radii[0] <= 0
        # Equivalent quantity records can differ by conversion roundoff.
        or not 0 < tolerance <= 1e-6 * (1 + 1e-12)
        or probes.shape != (3,)
        or not np.allclose(probes, [1.2, 1.4, 1.7], atol=1e-14, rtol=0)
        or len(ids) != 4
        or set(ids) != set(range(4))
        or not 1 <= protocol['maximum_intersection_records_per_face'] <= 8
    ):
        raise ValueError('Unsupported geometry, probes, tolerance or mapping')
    source_map = {atom: index for index, atom in enumerate(ids)}
    all_edges = set(combinations(range(4), 2))
    edge_lengths = np.array(
        [
            np.linalg.norm(coords[source_map[a]] - coords[source_map[b]])
            for a, b in sorted(all_edges)
        ]
    )
    if not np.isfinite(edge) or not np.allclose(edge_lengths, edge, atol=1e-12, rtol=0):
        raise ValueError('Input is not the declared regular tetrahedron')
    blocked_edges = [tuple(pair) for pair in certificate['blocked_edges']]
    if len(blocked_edges) != 6 or set(blocked_edges) != all_edges:
        raise ValueError('Incomplete or duplicate blocked edge inventory')
    expanded = float(radii[0] + probes[0])
    edge_margin = float((expanded - edge_lengths / 2).min())
    if edge_margin <= tolerance:
        raise ValueError('A shared edge is not strictly blocked')
    faces = certificate['faces']
    face_ids = [tuple(face['atom_indices']) for face in faces]
    if len(faces) != 4 or set(face_ids) != set(combinations(range(4), 3)):
        raise ValueError('Incomplete or duplicate face inventory')
    origin = coords.mean(axis=0)
    origin_clearance = float((np.linalg.norm(coords - origin, axis=1) - radii).min())
    cover_radii, results = [], []
    for face in sorted(faces, key=lambda item: item['atom_indices']):
        triangle = coords[[source_map[atom] for atom in face['atom_indices']]]
        intersections = verify_convex_intersections(
            coords,
            ids,
            triangle,
            expanded,
            tolerance,
            face['intersections'],
            protocol['maximum_intersection_records_per_face'],
            length_unit='angstroms',
        )
        # The blocked triangle boundary makes every free component bounded.
        # The closed-convex nerve theorem and planar duality identify its count.
        if intersections['nerve']['beta_1'] != 1:
            raise ValueError('Face does not have exactly one free patch')
        center = triangle.mean(axis=0)
        axis = center - origin
        axis /= np.linalg.norm(axis)
        delta = coords - origin
        projected = np.maximum(delta @ axis, 0)
        clearance = float(
            (np.linalg.norm(delta - projected[:, None] * axis, axis=1) - radii).min()
        )
        if clearance - probes[0] <= tolerance:
            raise ValueError('Centroid ray does not reach the free patch')
        cover_radii.append(float(np.linalg.norm(triangle - center, axis=1).max()))
        results.append(
            {
                'atom_indices': face['atom_indices'],
                **intersections,
                'ray_minimum_clearance': _length(clearance, 'ray_minimum_clearance'),
                'ray_crossing': _length(center, 'ray_crossing'),
            }
        )
    sealed_margin = float(radii[0] + probes[1] - max(cover_radii))
    excluded_margin = float(
        radii[0] + probes[2] - np.linalg.norm(coords - origin, axis=1).max()
    )
    if min(sealed_margin, excluded_margin, origin_clearance - probes[1]) <= tolerance:
        raise ValueError('Sealed or excluded control is not certified')
    return {
        'verification': 'passed',
        'opening_component_count': sum(face['nerve']['beta_1'] for face in results),
        'blocked_edge_count': len(blocked_edges),
        'origin_connected_patch_count': len(results),
        'origin': _length(origin, 'origin'),
        'origin_clearance': _length(origin_clearance, 'origin_clearance'),
        'minimum_edge_coverage_margin': _length(
            edge_margin, 'minimum_edge_coverage_margin'
        ),
        'faces': results,
        'sealed_control': {
            'probe_radius': _length(float(probes[1]), 'probe_radius'),
            'opening_component_count': 0,
            'origin_is_free': True,
            'minimum_face_coverage_margin': _length(
                sealed_margin, 'minimum_face_coverage_margin'
            ),
        },
        'excluded_control': {
            'probe_radius': _length(float(probes[2]), 'probe_radius'),
            'has_free_finite_hull_point': False,
            'minimum_enclosing_ball_margin': _length(
                excluded_margin, 'minimum_enclosing_ball_margin'
            ),
        },
    }


if __name__ == '__main__':
    case = Path('docs/content/benchlab/synthetic/regular_tetrahedron')
    data = case / 'artifacts/boundary_connectivity_v1'
    print(
        json.dumps(
            verify_certificate(
                case / 'artifacts/regular_tetrahedron_v1/input.json',
                data / 'protocol.json',
                json.loads((data / 'certificate.json').read_text()),
            ),
            indent=2,
        )
    )
