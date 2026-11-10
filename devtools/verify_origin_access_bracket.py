"""Independent, bounded access/closure brackets on a fixed atomic-center hull."""

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.spatial import ConvexHull

from devtools.verify_closed_shell_wall_cover import _values, verify_triangle_cover
from devtools.verify_small_probe_boundary import _project
from devtools.verify_small_probe_regions import _algebraic_candidates, _outward_normal


def path_clearance(
    origin: np.ndarray,
    point: np.ndarray,
    direction: np.ndarray,
    centers: np.ndarray,
    radii: np.ndarray,
) -> float:
    """Return the minimum bare-ball clearance of a segment and infinite ray.

    All arrays share an explicit caller-declared length unit. ``direction`` must
    be a unit vector. This positive witness supplies no optimality claim.
    """
    direction = np.asarray(direction, dtype=float)
    if direction.shape != (3,) or not np.isclose(np.linalg.norm(direction), 1.0):
        raise ValueError('A unit ray direction is required')
    delta = point - origin
    denominator = float(delta @ delta)
    if denominator <= 0:
        raise ValueError('The origin segment must have positive length')
    along = np.clip((centers - origin) @ delta / denominator, 0.0, 1.0)
    segment = np.linalg.norm(origin + along[:, None] * delta - centers, axis=1)
    along = np.maximum(0.0, (centers - point) @ direction)
    ray = np.linalg.norm(point + along[:, None] * direction - centers, axis=1)
    return float(np.min(np.minimum(segment, ray) - radii))


def build_cover(
    centers: np.ndarray,
    radii: np.ndarray,
    faces: np.ndarray,
    probe: float,
    tolerance: float,
    maximum_depth: int,
    maximum_nodes: int,
) -> tuple[list[dict[str, Any]], int]:
    """Discover complete midpoint leaves covered by individual expanded balls.

    Parameters use one common explicit caller-declared length unit. Every
    accepted triangle is covered because a convex ball covers its three
    vertices. Failure at a depth/work budget raises ``ValueError``; a partial
    list is never returned as a complete cover. The independent shared verifier
    must check the resulting leaves and all face partitions before acceptance.
    """
    leaves: list[dict[str, Any]] = []
    work = 0
    for index, face in enumerate(faces):
        pending: list[tuple[np.ndarray, list[int]]] = [(centers[face], [])]
        while pending:
            if work >= maximum_nodes:
                raise ValueError('Cover work budget exhausted')
            triangle, path = pending.pop()
            work += 1
            distances = np.linalg.norm(
                triangle[:, None, :] - centers[None, :, :], axis=2
            ).max(axis=0)
            margins = radii + probe - distances
            atom = int(np.argmax(margins))
            if margins[atom] > tolerance:
                leaves.append(
                    {
                        'hull_face_index': index,
                        'subdivision_path': path,
                        'covering_atom_index': atom,
                    }
                )
                continue
            if len(path) >= maximum_depth:
                raise ValueError('Cover depth budget exhausted')
            a, b, c = triangle
            ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
            children = ((a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca))
            pending.extend(
                (np.array(child), [*path, i])
                for i, child in reversed(list(enumerate(children)))
            )
    return leaves, work


def _model(input_file, protocol_file):
    input_bytes = input_file.read_bytes()
    protocol_bytes = protocol_file.read_bytes()
    fixture = json.loads(input_bytes)
    protocol = json.loads(protocol_bytes)
    digest = hashlib.sha256(input_bytes).hexdigest()
    if (
        protocol['schema']
        not in {
            'topomt.benchlab.origin-access-bracket-protocol/1',
            'topomt.benchlab.origin-access-bracket-protocol/2',
        }
        or protocol['input_sha256'] != digest
        or protocol['case'] != fixture['case_id']
        or protocol['length_unit'] != 'angstroms'
    ):
        raise ValueError('Origin bracket input/protocol identity differs')
    centers = _values(fixture['coordinates'], 'coordinates', 'angstroms')
    radii = _values(fixture['atom_radii'], 'atom_radii', 'angstroms')
    if not np.all(radii == radii[0]):
        raise ValueError('This bounded discovery requires equal ball radii')
    hull = ConvexHull(centers)
    faces = np.array(sorted(tuple(sorted(map(int, face))) for face in hull.simplices))
    origin = np.asarray(protocol['origin'], dtype=float)
    tolerance = protocol['safety_margin']
    if (
        origin.shape != (3,)
        or not np.isfinite(origin).all()
        or tolerance <= 0
        or not np.isfinite(tolerance)
    ):
        raise ValueError('Invalid original origin or tolerance')
    for face in faces:
        triangle = centers[face]
        if (origin - triangle[0]) @ _outward_normal(triangle, centers) >= -tolerance:
            raise ValueError('Origin must be strictly inside the complete hull')
    return (
        centers,
        radii,
        faces,
        origin,
        protocol,
        digest,
        hashlib.sha256(protocol_bytes).hexdigest(),
    )


def _discovery_faces(input_file, protocol_file, protocol, centers, radii, faces):
    if protocol['schema'].endswith('/1'):
        return list(range(len(faces)))
    from devtools.verify_opening_connectivity import verify_certificate

    reference = protocol['covered_wall_reference']
    files = {
        name: protocol_file.parent / record['path']
        for name, record in reference.items()
    }
    for name, file in files.items():
        if hashlib.sha256(file.read_bytes()).hexdigest() != reference[name]['sha256']:
            raise ValueError('Preverified wall reference identity differs')
    prior = json.loads(files['protocol'].read_text())
    prior_probe = float(_values(prior['probe_radius'], 'probe_radius', 'angstroms'))
    if prior_probe > protocol['known_access_probe']:
        raise ValueError('A larger-probe cover cannot prune smaller-probe faces')
    certificate = json.loads(files['certificate'].read_text())
    verify_certificate(input_file, files['protocol'], certificate)
    covered = {tuple(sorted(face)) for face in certificate['wall_cover']['hull_faces']}
    return [i for i, face in enumerate(faces) if tuple(face) not in covered]


def build_access_bracket(input_file: Path, protocol_file: Path) -> dict[str, Any]:
    """Discover a positive path and complete boundary cover within frozen budgets.

    Parameters
    ----------
    input_file, protocol_file : Path
        Unchanged quantity-aware case input and predeclared v1 bracket protocol.

    Returns
    -------
    dict
        Full source-face/path/cover witnesses with explicit angstrom units.

    Raises
    ------
    ValueError
        Input identity differs or no bracket meets the bounded accepted ladder.
    """
    centers, radii, faces, origin, protocol, digest, protocol_digest = _model(
        input_file, protocol_file
    )
    tolerance = protocol['safety_margin']
    best = None
    best_clearance = protocol['known_access_probe']
    tests = 0
    selected = _discovery_faces(
        input_file, protocol_file, protocol, centers, radii, faces
    )
    for index in selected:
        face = faces[index]
        triangle = centers[face]
        active = [
            i
            for i, center in enumerate(centers)
            if np.linalg.norm(center - _project(center, triangle)[0])
            <= radii[i] + protocol['known_covered_probe'] + tolerance
        ]
        convex = {'decisions': [{'sets': [i], 'intersects': True} for i in active]}
        candidates = [np.full(3, 1 / 3)]
        candidates.extend(
            _algebraic_candidates(triangle, centers, 0.0, convex, tolerance)
        )
        normal = _outward_normal(triangle, centers)
        for weights in candidates:
            tests += 1
            if tests > protocol['maximum_path_candidates']:
                raise ValueError('Origin path candidate budget exhausted')
            point = weights @ triangle
            clearance = path_clearance(origin, point, normal, centers, radii)
            if clearance > best_clearance:
                best_clearance = clearance
                best = {
                    'face_index': index,
                    'barycentric_weights': weights.tolist(),
                    'ray_direction': normal.tolist(),
                }
    if best is None:
        raise ValueError('No improved positive origin path within this budget')
    lower = best_clearance - protocol['lower_safety_offset']
    trials: list[dict[str, Any]] = []
    for width in protocol['width_attempts']:
        upper = lower + width
        if upper > protocol['upper_limit']:
            continue
        # Failed attempts may consume the complete declared per-attempt ceiling.
        spent = sum(row['charged_node_budget'] for row in trials)
        remaining = protocol['maximum_cover_nodes_total'] - spent
        budget = min(protocol['maximum_cover_nodes_per_attempt'], remaining)
        if budget < len(faces):
            break
        try:
            leaves, work = build_cover(
                centers,
                radii,
                faces,
                upper,
                tolerance,
                protocol['maximum_cover_depth'],
                budget,
            )
        except ValueError as error:
            trials.append(
                {
                    'width': width,
                    'status': 'unresolved',
                    'reason': str(error),
                    'charged_node_budget': budget,
                }
            )
            continue
        trials.append(
            {
                'width': width,
                'status': 'covered',
                'nodes': work,
                'charged_node_budget': work,
            }
        )
        candidate = {
            'schema': 'topomt.benchlab.origin-access-bracket/1',
            'input_sha256': digest,
            'protocol_sha256': protocol_digest,
            'length_unit': 'angstroms',
            'hull_faces': faces.tolist(),
            'lower_probe': lower,
            'upper_probe': upper,
            'origin_path': best,
            'cover_leaves': leaves,
            'discovery': {'path_tests': tests, 'cover_trials': trials},
        }
        verify_access_bracket(input_file, protocol_file, candidate)
        return candidate
    raise ValueError('No complete cover within the declared bracket ladder/budgets')


def verify_access_bracket(
    input_file: Path, protocol_file: Path, certificate: dict[str, Any]
) -> dict[str, Any]:
    """Replay a complete independent bracket without any witness discovery.

    Parameters
    ----------
    input_file, protocol_file : Path
        Frozen input and v1 protocol.
    certificate : dict
        Complete hull, positive origin path and upper-probe cover evidence.

    Returns
    -------
    dict
        Verified interval, path/cover margins, units and achieved width target.

    Raises
    ------
    ValueError
        Identity, geometry, margins, completeness or budget contracts fail.
    """
    centers, radii, faces, origin, protocol, digest, protocol_digest = _model(
        input_file, protocol_file
    )
    if (
        certificate['schema'] != 'topomt.benchlab.origin-access-bracket/1'
        or certificate['input_sha256'] != digest
        or certificate['protocol_sha256'] != protocol_digest
        or certificate['length_unit'] != 'angstroms'
        or certificate['hull_faces'] != faces.tolist()
    ):
        raise ValueError('Bracket certificate identity or complete hull differs')
    lower, upper = certificate['lower_probe'], certificate['upper_probe']
    width = upper - lower
    tolerance = protocol['safety_margin']
    if (
        not np.isfinite([lower, upper]).all()
        or not protocol['known_access_probe']
        <= lower
        < upper
        <= protocol['upper_limit']
        or not any(abs(width - w) < 1e-12 for w in protocol['width_attempts'])
    ):
        raise ValueError('Invalid or undeclared bracket endpoints')
    path = certificate['origin_path']
    index = path['face_index']
    if type(index) is not int or not 0 <= index < len(faces):
        raise ValueError('Invalid origin-path face')
    weights = np.asarray(path['barycentric_weights'], dtype=float)
    if (
        weights.shape != (3,)
        or not np.isfinite(weights).all()
        or np.min(weights) < 0.0
        or abs(weights.sum() - 1) > 1e-12
    ):
        raise ValueError('Invalid path barycentric weights')
    triangle = centers[faces[index]]
    normal = _outward_normal(triangle, centers)
    direction = np.asarray(path['ray_direction'], dtype=float)
    if direction.shape != (3,) or not np.allclose(
        direction, normal, rtol=0.0, atol=1e-12
    ):
        raise ValueError('Origin continuation must be the outward normal ray')
    clearance = path_clearance(origin, weights @ triangle, normal, centers, radii)
    if clearance - lower <= tolerance:
        raise ValueError('Complete lower-probe origin path lacks positive clearance')
    if np.min(np.linalg.norm(centers - origin, axis=1) - radii - upper) <= tolerance:
        raise ValueError('Upper-probe origin is not free')
    cover = verify_triangle_cover(
        centers,
        radii,
        faces,
        certificate['cover_leaves'],
        upper,
        tolerance,
        length_unit='angstroms',
        maximum_depth=protocol['maximum_cover_depth'],
        maximum_nodes=protocol['maximum_cover_nodes_per_attempt'],
    )
    discovery = certificate['discovery']
    if (
        discovery['path_tests'] > protocol['maximum_path_candidates']
        or sum(row['charged_node_budget'] for row in discovery['cover_trials'])
        > protocol['maximum_cover_nodes_total']
    ):
        raise ValueError('Reference discovery exceeds the frozen work budget')
    return {
        'length_unit': 'angstroms',
        'origin_access_lower_probe': lower,
        'origin_enclosed_upper_probe': upper,
        'bracket_width': width,
        'desired_width_met': width <= protocol['desired_width'] + 1e-12,
        'lower_path_margin': clearance - lower,
        'upper_cover': cover,
        'scope': 'Original origin access on this fixed ball/hull model; not an exact maximum bottleneck or global cavity count',
    }
