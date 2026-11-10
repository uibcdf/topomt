"""Independent convex-nerve boundary reference, with no production DFND imports.

Each face uses clipped expanded balls plus three compact exterior halfplanes.
Their complete two-skeleton counts free face interiors without assuming that
triangle edges are covered. Bare numeric records have a fixed angstrom schema.
"""

from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

from devtools.verify_opening_connectivity import first_betti


class ReferenceUnresolved(ValueError):
    """A bounded reference could not establish a complete justified decision."""


class _Budget:
    def __init__(self, decisions=20_000, solvers=2000):
        self.decisions = decisions
        self.solvers = solvers
        self.used_decisions = 0
        self.used_solvers = 0

    def decision(self):
        if self.used_decisions >= self.decisions:
            raise ReferenceUnresolved('Reference decision budget exhausted')
        self.used_decisions += 1

    def solver(self):
        if self.used_solvers >= self.solvers:
            raise ReferenceUnresolved('Reference solver budget exhausted')
        self.used_solvers += 1


def _project(point, domain):
    """Closest point in a point/segment/triangle, with convex weights."""
    size = len(domain)
    if size == 1:
        return domain[0], np.ones(1)
    candidates = []
    for a, b in combinations(range(size), 2):
        direction = domain[b] - domain[a]
        t = float(
            np.clip((point - domain[a]) @ direction / (direction @ direction), 0.0, 1.0)
        )
        weights = np.zeros(size)
        weights[a] = 1.0 - t
        weights[b] = t
        candidates.append((weights @ domain, weights))
    if size == 3:
        directions = domain[1:] - domain[0]
        tail = np.linalg.solve(
            directions @ directions.T, directions @ (point - domain[0])
        )
        weights = np.array([1.0 - tail.sum(), *tail])
        if np.min(weights) >= 0.0:
            candidates.append((weights @ domain, weights))
    return min(candidates, key=lambda row: np.linalg.norm(row[0] - point))


def _domain(triangle, subset):
    excluded = {-vertex - 1 for vertex in subset if vertex < 0}
    keep = [index for index in range(3) if index not in excluded]
    return triangle[keep], keep


def _decision(triangle, centers, radius, subset, margin, budget):
    budget.decision()
    atoms = [index for index in subset if index >= 0]
    record = {'sets': list(subset)}
    if not atoms:
        record.update(
            intersects=len(subset) < 3, symbolic='compact_exterior_halfplanes'
        )
        return record
    domain, keep = _domain(triangle, subset)
    selected = centers[atoms]

    def evaluate(weights):
        weights = np.maximum(0.0, weights)
        weights /= weights.sum()
        center = weights @ selected
        point, barycentric = _project(center, domain)
        primal_margin = float(radius - np.max(np.linalg.norm(selected - point, axis=1)))
        direction = point - center
        norm = np.linalg.norm(direction)
        direction = direction / norm if norm > 1e-14 else np.array([1.0, 0.0, 0.0])
        variance = float(weights @ np.sum((selected - center) ** 2, axis=1))
        separation = max(0.0, float(np.min((domain - center) @ direction)))
        lower = float(np.sqrt(variance + separation**2))
        return weights, barycentric, direction, primal_margin, lower - radius

    weights = np.full(len(atoms), 1.0 / len(atoms))
    witnesses = [evaluate(weights)]
    if max(witnesses[0][-2:]) <= margin and len(atoms) > 1:
        from scipy.optimize import minimize

        def dual_objective(w):
            center = w @ selected
            point, _ = _project(center, domain)
            variance = w @ np.sum((selected - center) ** 2, axis=1)
            return -(variance + np.sum((center - point) ** 2))

        def dual_jacobian(w):
            point, _ = _project(w @ selected, domain)
            return -(np.sum(selected**2, axis=1) - 2 * selected @ point)

        budget.solver()
        result = minimize(
            dual_objective,
            weights,
            jac=dual_jacobian,
            method='SLSQP',
            bounds=[(0.0, 1.0)] * len(atoms),
            constraints={
                'type': 'eq',
                'fun': lambda w: w.sum() - 1.0,
                'jac': lambda w: np.ones_like(w),
            },
            options={'maxiter': 100, 'ftol': 1e-12},
        )
        witnesses.append(evaluate(result.x))
    positive = max(witnesses, key=lambda row: row[-2])
    negative = max(witnesses, key=lambda row: row[-1])
    if positive[-2] > margin:
        barycentric = np.zeros(3)
        barycentric[keep] = positive[1]
        record.update(intersects=True, barycentric_weights=barycentric.tolist())
    elif negative[-1] > margin:
        record.update(
            intersects=False,
            dual_weights=negative[0].tolist(),
            direction=negative[2].tolist(),
        )
    else:
        raise ReferenceUnresolved(
            f'Convex intersection {subset} has no verified margin'
        )
    return record


def _validate_record(triangle, centers, radius, margin, record):
    subset = tuple(record['sets'])
    if (
        not 1 <= len(subset) <= 3
        or tuple(sorted(set(subset))) != subset
        or not all(-3 <= index < len(centers) for index in subset)
        or not all(type(index) is int for index in subset)
        or type(record['intersects']) is not bool
    ):
        raise ValueError('Invalid intersection inventory record')
    atoms = [index for index in subset if index >= 0]
    if not atoms:
        if record.get('symbolic') != 'compact_exterior_halfplanes' or record[
            'intersects'
        ] != (len(subset) < 3):
            raise ValueError('Invalid exterior-halfplane intersection')
        return subset, None
    domain, keep = _domain(triangle, subset)
    selected = centers[atoms]
    if record['intersects']:
        weights = np.asarray(record['barycentric_weights'], dtype=float)
        if (
            weights.shape != (3,)
            or not np.isfinite(weights).all()
            or np.min(weights) < 0
            or abs(weights.sum() - 1.0) > 1e-12
            or any(weights[index] != 0.0 for index in range(3) if index not in keep)
        ):
            raise ValueError('Invalid positive convex witness')
        point = weights @ triangle
        checked_margin = float(
            radius - np.max(np.linalg.norm(selected - point, axis=1))
        )
    else:
        weights = np.asarray(record['dual_weights'], dtype=float)
        direction = np.asarray(record['direction'], dtype=float)
        if (
            weights.shape != (len(atoms),)
            or not np.isfinite(weights).all()
            or np.min(weights) < 0
            or abs(weights.sum() - 1.0) > 1e-12
            or direction.shape != (3,)
            or not np.isfinite(direction).all()
            or abs(np.linalg.norm(direction) - 1.0) > 1e-12
        ):
            raise ValueError('Invalid negative convex witness')
        center = weights @ selected
        variance = float(weights @ np.sum((selected - center) ** 2, axis=1))
        separation = max(0.0, float(np.min((domain - center) @ direction)))
        checked_margin = float(np.sqrt(variance + separation**2) - radius)
    if checked_margin <= margin:
        raise ValueError('Intersection witness lacks the declared decision margin')
    return subset, checked_margin


def _geometry(triangle, centers, radius, tolerance):
    triangle = np.asarray(triangle, dtype=float)
    centers = np.asarray(centers, dtype=float)
    if (
        triangle.shape != (3, 3)
        or centers.ndim != 2
        or centers.shape[1] != 3
        or not np.isfinite(triangle).all()
        or not np.isfinite(centers).all()
        or not np.isfinite(radius)
        or not np.isfinite(tolerance)
        or min(radius, tolerance) <= 0
        or np.linalg.norm(
            np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
        )
        <= tolerance**2
    ):
        raise ValueError('Invalid fixed-angstrom convex-reference geometry')
    return triangle, centers


def build_face_certificate(
    triangle: np.ndarray,
    centers: np.ndarray,
    expanded_radius: float,
    *,
    tolerance: float = 1e-6,
    budget: Any = None,
) -> dict[str, Any]:
    """Discover a complete two-skeleton certificate independently of DFND.

    Parameters
    ----------
    triangle, centers : numpy.ndarray
        Carrier triangle and all atomic centers, in angstroms.
    expanded_radius, tolerance : float
        Common expanded radius and positive decision margin, in angstroms.
    budget : object, optional
        Shared bounded reference work counter for a multi-face capture.

    Returns
    -------
    dict
        Complete intersection decisions with directly verifiable witnesses.

    Raises
    ------
    ValueError
        Geometry is invalid or a bounded decision lacks a verified margin.
    """
    triangle, centers = _geometry(triangle, centers, expanded_radius, tolerance)
    if budget is None:
        budget = _Budget()
    records = []
    decisions = {}

    def record(subset):
        row = _decision(triangle, centers, expanded_radius, subset, tolerance, budget)
        _validate_record(triangle, centers, expanded_radius, tolerance, row)
        records.append(row)
        decisions[subset] = row['intersects']

    for index in range(-3, len(centers)):
        record((index,))
    active = [index for index in range(-3, len(centers)) if decisions[index,]]
    for pair in combinations(active, 2):
        record(pair)
    for triple in combinations(active, 3):
        if all(decisions[pair] for pair in combinations(triple, 2)):
            record(triple)
    return {
        'schema': 'topomt.convex-face-reference.angstrom/1',
        'length_unit': 'angstrom',
        'decisions': records,
    }


def verify_face_certificate(
    triangle: np.ndarray,
    centers: np.ndarray,
    expanded_radius: float,
    certificate: dict[str, Any],
    *,
    tolerance: float = 1e-6,
    max_decisions: int = 20_000,
) -> dict[str, Any]:
    """Check complete convex evidence and count free triangle interiors.

    Parameters
    ----------
    triangle, centers : numpy.ndarray
        Carrier and all atomic centers, in angstroms.
    expanded_radius, tolerance : float
        Common expanded radius and required decision margin, in angstroms.
    certificate : dict
        Complete fixed-unit intersection records, including exterior pieces.
    max_decisions : int
        Hard receiving limit; incomplete inventories cannot establish a count.

    Returns
    -------
    dict
        First Betti rank of the augmented convex cover, equal to the number of
        free face-interior components under the documented compact-cover proof.

    Raises
    ------
    ValueError
        A unit, inventory, geometric decision or witness is invalid/incomplete.
    """
    triangle, centers = _geometry(triangle, centers, expanded_radius, tolerance)
    if (
        certificate.get('schema') != 'topomt.convex-face-reference.angstrom/1'
        or certificate.get('length_unit') != 'angstrom'
    ):
        raise ValueError('Unrecognized convex-reference schema or units')
    records = certificate['decisions']
    if len(records) > max_decisions:
        raise ValueError('Reference inventory exceeds budget')
    decisions = {}
    margins = []
    for record in records:
        subset, margin = _validate_record(
            triangle, centers, expanded_radius, tolerance, record
        )
        if subset in decisions:
            raise ValueError('Duplicate intersection decision')
        decisions[subset] = record['intersects']
        if margin is not None:
            margins.append(margin)
    required: set[tuple[int, ...]] = {(index,) for index in range(-3, len(centers))}
    if not required <= decisions.keys():
        raise ValueError('Incomplete singleton inventory')
    vertices = [index for index in range(-3, len(centers)) if decisions[index,]]
    pairs = set(combinations(vertices, 2))
    required |= pairs
    if not pairs <= decisions.keys():
        raise ValueError('Incomplete pair inventory')
    edges = sorted(pair for pair in pairs if decisions[pair])
    edge_set = set(edges)
    triples = {
        triple
        for triple in combinations(vertices, 3)
        if all(pair in edge_set for pair in combinations(triple, 2))
    }
    required |= triples
    if set(decisions) != required:
        raise ValueError('Incomplete or extraneous two-skeleton inventory')
    triangles = sorted(triple for triple in triples if decisions[triple])
    result = first_betti(vertices, edges, triangles)
    return {
        'free_components': result['beta_1'],
        'complete_two_skeleton': True,
        'nerve': result,
        'minimum_decision_margin_angstroms': min(margins) if margins else None,
        'decision_count': len(records),
    }


def _edge_intervals(start, end, centers, radius, tolerance):
    """Independently inventory quadratic ball-entry events on an entire edge."""
    direction = end - start
    length = np.linalg.norm(direction)
    aa = float(direction @ direction)
    events = [0.0, 1.0]
    for center in centers:
        delta = start - center
        bb = float(2 * direction @ delta)
        cc = float(delta @ delta - radius**2)
        foot = -bb / (2 * aa)
        distance = np.linalg.norm(start + foot * direction - center)
        if 0.0 <= foot <= 1.0 and abs(distance - radius) <= tolerance:
            raise ReferenceUnresolved('Reference edge is marginally tangent')
        discriminant = bb * bb - 4 * aa * cc
        if discriminant > 0:
            for t in (
                (-bb - np.sqrt(discriminant)) / (2 * aa),
                (-bb + np.sqrt(discriminant)) / (2 * aa),
            ):
                if 0.0 < t < 1.0:
                    events.append(float(t))
    critical = []
    roundoff = 512 * np.finfo(float).eps
    for value in sorted(events):
        if critical and value - critical[-1] <= roundoff:
            continue
        if critical and (value - critical[-1]) * length <= tolerance:
            raise ReferenceUnresolved('Reference edge event ordering is marginal')
        critical.append(value)
    intervals = []
    for lo, hi in zip(critical[:-1], critical[1:], strict=True):
        point = start + ((lo + hi) / 2) * direction
        margin = float(np.min(np.linalg.norm(centers - point, axis=1)) - radius)
        if abs(margin) <= tolerance:
            raise ReferenceUnresolved('Reference edge sign is marginal')
        if margin > 0:
            intervals.append([lo, hi])
    return intervals


def _model(input_file, protocol_file):
    import hashlib
    import json

    from scipy.spatial import ConvexHull

    from devtools.verify_closed_shell_wall_cover import _values

    input_bytes = input_file.read_bytes()
    protocol_bytes = protocol_file.read_bytes()
    fixture = json.loads(input_bytes)
    protocol = json.loads(protocol_bytes)
    if protocol.get('schema') != 'topomt.benchlab.small-probe-boundary-protocol/1':
        raise ValueError('Unrecognized small-probe reference protocol')
    if protocol['budgets']['optimizer_iterations_per_call'] != 100:
        raise ValueError('Unsupported reference optimizer iteration policy')
    digest = hashlib.sha256(input_bytes).hexdigest()
    if protocol['case'] != fixture['case_id'] or protocol['input_sha256'] != digest:
        raise ValueError('Small-probe reference input identity differs')
    if protocol['length_unit'] != 'angstrom':
        raise ValueError('Unrecognized reference units')
    centers = _values(fixture['coordinates'], 'coordinates', 'angstroms')
    radii = _values(fixture['atom_radii'], 'atom_radii', 'angstroms')
    if not np.all(radii == radii[0]):
        raise ValueError('This bounded reference requires equal atomic radii')
    radius = float(radii[0] + protocol['probe_angstroms'])
    tolerance = protocol['decision_margin_angstroms']
    hull = ConvexHull(centers)
    faces = sorted(tuple(sorted(map(int, face))) for face in hull.simplices)
    if len(set(faces)) != len(faces):
        raise ValueError('Duplicate hull face')
    edges = {tuple(sorted(edge)) for face in faces for edge in combinations(face, 2)}
    return (
        centers,
        radius,
        tolerance,
        faces,
        sorted(edges),
        protocol,
        digest,
        hashlib.sha256(protocol_bytes).hexdigest(),
    )


def build_certificate(input_file: Path, protocol_file: Path) -> dict[str, Any]:
    """Discover the frozen equal-radius shell certificate without running DFND.

    Parameters
    ----------
    input_file, protocol_file : Path
        Frozen quantity-aware input and predeclared bounded reference protocol.

    Returns
    -------
    dict
        Complete convex-intersection and seam evidence in fixed angstrom units.

    Raises
    ------
    ValueError
        Identity, geometry, units or bounded witness discovery is unsupported.
    """
    centers, radius, tolerance, faces, edges, protocol, input_hash, protocol_hash = (
        _model(input_file, protocol_file)
    )
    limits = protocol['budgets']
    budget = _Budget(limits['intersection_decisions'], limits['solver_calls'])
    records = []
    for face in faces:
        certificate = build_face_certificate(
            centers[list(face)], centers, radius, tolerance=tolerance, budget=budget
        )
        records.append(
            {'atom_indices': list(face), 'convex_intersections': certificate}
        )
    seams = [
        {
            'atom_indices': list(edge),
            'free_t_intervals': _edge_intervals(
                centers[edge[0]], centers[edge[1]], centers, radius, tolerance
            ),
        }
        for edge in edges
    ]
    return {
        'schema': 'topomt.benchlab.small-probe-boundary.angstrom/1',
        'input_sha256': input_hash,
        'protocol_sha256': protocol_hash,
        'length_unit': 'angstrom',
        'faces': records,
        'seams': seams,
        'work': {
            'intersection_decisions': budget.used_decisions,
            'solver_calls': budget.used_solvers,
        },
    }


def verify_certificate(
    input_file: Path, protocol_file: Path, certificate: dict[str, Any]
) -> dict[str, Any]:
    """Verify all convex witnesses, face counts and seams before a global count.

    No optimizer is imported or called by this receiving route. A face with
    more than one free component is unsupported by its bounded seam mapping.

    Parameters
    ----------
    input_file, protocol_file : Path
        Frozen input and exact protocol associated with the certificate.
    certificate : dict
        Complete fixed-unit hull, convex-intersection and edge evidence.

    Returns
    -------
    dict
        Independently checked face/component counts and their source supports.

    Raises
    ------
    ValueError
        Identity, units, witnesses, inventory or bounded scope cannot be verified.
    """
    centers, radius, tolerance, faces, edges, protocol, input_hash, protocol_hash = (
        _model(input_file, protocol_file)
    )
    if (
        certificate.get('schema') != 'topomt.benchlab.small-probe-boundary.angstrom/1'
        or certificate.get('length_unit') != 'angstrom'
        or certificate['input_sha256'] != input_hash
        or certificate['protocol_sha256'] != protocol_hash
    ):
        raise ValueError('Unrecognized certificate or changed input/protocol identity')
    face_records = certificate['faces']
    if [tuple(row['atom_indices']) for row in face_records] != faces:
        raise ValueError('Incomplete or reordered hull face inventory')
    counts = []
    verified = []
    decisions = 0
    for face, row in zip(faces, face_records, strict=True):
        result = verify_face_certificate(
            centers[list(face)],
            centers,
            radius,
            row['convex_intersections'],
            tolerance=tolerance,
            max_decisions=protocol['budgets']['intersection_decisions'],
        )
        decisions += result['decision_count']
        if decisions > protocol['budgets']['intersection_decisions']:
            raise ValueError('Global reference decision budget exceeded')
        if result['free_components'] not in (0, 1):
            raise ReferenceUnresolved(
                'Multiple face components need independent seam localization'
            )
        counts.append(result['free_components'])
        verified.append(result)
    if [tuple(row['atom_indices']) for row in certificate['seams']] != edges:
        raise ValueError('Incomplete or reordered seam inventory')
    parents = {index: index for index, count in enumerate(counts) if count}

    def root(index):
        while parents[index] != index:
            index = parents[index]
        return index

    seam_count = 0
    for edge, row in zip(edges, certificate['seams'], strict=True):
        expected = _edge_intervals(
            centers[edge[0]], centers[edge[1]], centers, radius, tolerance
        )
        supplied = row['free_t_intervals']
        if len(expected) != len(supplied) or (
            expected and not np.allclose(expected, supplied, rtol=0.0, atol=1e-12)
        ):
            raise ValueError('Incorrect free seam intervals')
        incident = [index for index, face in enumerate(faces) if set(edge) <= set(face)]
        if len(incident) != 2:
            raise ValueError('Nonmanifold reference hull')
        if expected:
            if not all(counts[index] == 1 for index in incident):
                raise ValueError('Free seam disagrees with independent face count')
            parents[root(incident[0])] = root(incident[1])
            seam_count += 1
    # Each hull vertex is covered by its own expanded ball, so no omitted
    # vertex-only connection can join components of this face/seam graph.
    if radius <= tolerance:
        raise ValueError('Hull-vertex exclusion is not separated')
    groups: dict[int, list[int]] = {}
    for index in parents:
        groups.setdefault(root(index), []).append(index)
    return {
        'schema': 'topomt.benchlab.small-probe-boundary-verification/1',
        'input_sha256': input_hash,
        'protocol_sha256': protocol_hash,
        'hull_face_count': len(faces),
        'hull_edge_count': len(edges),
        'free_face_count': sum(counts),
        'free_seam_count': seam_count,
        'opening_component_count': len(groups),
        'components_faces_source_atom_indices': [
            [list(faces[index]) for index in group] for group in groups.values()
        ],
        'face_verification': verified,
        'scope': 'Independent fixed equal-radius hull count; free aperture area and transport bottlenecks not established',
    }
