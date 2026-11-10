"""Independent localization of convex-nerve face components by covered loops."""

from collections import deque
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

from devtools.verify_small_probe_boundary import (
    ReferenceUnresolved,
    verify_face_certificate,
)


def _cycles(certificate):
    decisions = {tuple(row['sets']): row for row in certificate['decisions']}
    vertices = sorted(
        key[0] for key, row in decisions.items() if len(key) == 1 and row['intersects']
    )
    edges = sorted(
        key for key, row in decisions.items() if len(key) == 2 and row['intersects']
    )
    parents = {vertex: vertex for vertex in vertices}
    tree = {vertex: [] for vertex in vertices}
    extra = []

    def root(vertex):
        while parents[vertex] != vertex:
            vertex = parents[vertex]
        return vertex

    for a, b in edges:
        if root(a) == root(b):
            extra.append((a, b))
        else:
            parents[root(a)] = root(b)
            tree[a].append(b)
            tree[b].append(a)
    cycles = []
    for a, b in extra:
        previous = {a: None}
        pending = deque([a])
        while b not in previous:
            vertex = pending.popleft()
            for neighbor in sorted(tree[vertex]):
                if neighbor not in previous:
                    previous[neighbor] = vertex
                    pending.append(neighbor)
        path = [b]
        while path[-1] != a:
            path.append(previous[path[-1]])
        cycles.append([*reversed(path), a])
    return cycles


def _weights(subset, decisions):
    row = decisions[tuple(sorted(subset))]
    if 'barycentric_weights' in row:
        return np.asarray(row['barycentric_weights'])
    keep = [index for index in range(3) if -index - 1 not in subset]
    weights = np.zeros(3)
    weights[keep] = 1.0 / len(keep)
    return weights


def _polygons(triangle, certificate, cycles):
    decisions = {tuple(row['sets']): row for row in certificate['decisions']}
    polygons = []
    for cycle in cycles:
        points = [_weights((cycle[0],), decisions) @ triangle]
        for a, b in zip(cycle[:-1], cycle[1:], strict=True):
            points.extend(
                [
                    _weights((a, b), decisions) @ triangle,
                    _weights((b,), decisions) @ triangle,
                ]
            )
        polygons.append(np.array(points))
    return polygons


def _segment_margin(start, end, centers, radius):
    direction = end - start
    length2 = direction @ direction
    t = (
        np.clip((centers - start) @ direction / length2, 0.0, 1.0)
        if length2 > 0.0
        else np.zeros(len(centers))
    )
    return float(
        np.min(np.linalg.norm(start + t[:, None] * direction - centers, axis=1))
        - radius
    )


def _distances_to_segments(point, starts, ends):
    directions = ends - starts
    length2 = np.sum(directions**2, axis=1)
    t = np.divide(
        np.sum((point - starts) * directions, axis=1),
        length2,
        out=np.zeros(len(starts)),
        where=length2 > 0.0,
    )
    return np.linalg.norm(
        point - starts - np.clip(t, 0.0, 1.0)[:, None] * directions, axis=1
    )


def _signature(point, polygons, triangle, tolerance):
    normal = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
    normal /= np.linalg.norm(normal)
    signature = []
    for polygon in polygons:
        if (
            np.min(_distances_to_segments(point, polygon[:-1], polygon[1:]))
            <= tolerance
        ):
            raise ReferenceUnresolved('Point is marginal to a covered cycle')
        vectors = polygon - point
        cross = np.cross(vectors[:-1], vectors[1:]) @ normal
        dots = np.sum(vectors[:-1] * vectors[1:], axis=1)
        turns = float(np.arctan2(cross, dots).sum() / (2 * np.pi))
        winding = round(turns)
        if abs(turns - winding) > 1e-8:
            raise ReferenceUnresolved('Winding has no resolved integer value')
        signature.append(int(winding) % 2)
    return signature


def _free_point(triangle, centers, radius, weights, tolerance):
    weights = np.asarray(weights, dtype=float)
    if (
        weights.shape != (3,)
        or not np.isfinite(weights).all()
        or np.min(weights) <= 0.0
        or abs(weights.sum() - 1.0) > 1e-12
    ):
        raise ValueError('Invalid free interior barycentric witness')
    weights = weights / weights.sum()
    point = weights @ triangle
    if _segment_margin(point, point, centers, radius) <= tolerance:
        raise ValueError('Free witness is blocked by an expanded atom')
    if (
        np.min(_distances_to_segments(point, triangle, np.roll(triangle, -1, axis=0)))
        <= tolerance
    ):
        raise ReferenceUnresolved('Free witness is marginal to the triangle boundary')
    return point


def _algebraic_candidates(triangle, centers, radius, certificate, tolerance):
    """Discover witnesses at restricted nearest-center diagram vertices.

    These are candidates, never a topology oracle. Inactive disks miss the
    triangle with a verified margin; all points are still checked against every
    atom. A finite discovery failure remains unresolved.
    """
    active = [
        row['sets'][0]
        for row in certificate['decisions']
        if len(row['sets']) == 1 and row['sets'][0] >= 0 and row['intersects']
    ]
    edges = triangle[1:] - triangle[0]
    gram = edges @ edges.T
    axis = edges[0] / np.linalg.norm(edges[0])
    normal = np.cross(*edges)
    normal /= np.linalg.norm(normal)
    basis = np.array([axis, np.cross(normal, axis)])
    projected = (centers - triangle[0]) @ basis.T
    offsets = np.sum((centers - triangle[0]) ** 2, axis=1)

    def interior(weights):
        if np.min(weights) < -1e-12:
            return None
        weights = np.maximum(0.0, weights)
        weights /= weights.sum()
        if np.min(weights) == 0.0:
            point = weights @ triangle
            margin = _segment_margin(point, point, centers, radius)
            if margin <= tolerance:
                return None
            distance = np.linalg.norm(triangle.mean(axis=0) - point)
            step = min(0.001, margin / (4 * max(distance, tolerance)))
            weights = (1 - step) * weights + step / 3
        return weights

    for a, b, c in combinations(active, 3):
        matrix = 2 * np.array(
            [projected[b] - projected[a], projected[c] - projected[a]]
        )
        if abs(np.linalg.det(matrix)) <= 1e-14:
            continue
        xy = np.linalg.solve(
            matrix, np.array([offsets[b] - offsets[a], offsets[c] - offsets[a]])
        )
        point = triangle[0] + xy @ basis
        tail = np.linalg.solve(gram, edges @ (point - triangle[0]))
        weights = interior(np.array([1 - tail.sum(), *tail]))
        if weights is not None:
            yield weights
    for i, j in combinations(range(3), 2):
        direction = triangle[j] - triangle[i]
        for a, b in combinations(active, 2):
            denominator = 2 * direction @ (centers[a] - centers[b])
            if abs(denominator) <= 1e-14:
                continue
            t = (
                np.sum((triangle[i] - centers[a]) ** 2)
                - np.sum((triangle[i] - centers[b]) ** 2)
            ) / denominator
            if 0.0 <= t <= 1.0:
                weights = np.zeros(3)
                weights[i] = 1 - t
                weights[j] = t
                weights = interior(weights)
                if weights is not None:
                    yield weights


def _candidates(triangle, centers, radius, certificate, tolerance, extra):
    yield np.full(3, 1.0 / 3)
    yield from extra
    yield from _algebraic_candidates(triangle, centers, radius, certificate, tolerance)
    for weights in [*np.eye(3), *(np.ones(3) - np.eye(3)) / 2]:
        yield 0.999 * weights + 0.001 / 3
    directions = triangle[1:] - triangle[0]
    tail = np.linalg.solve(directions @ directions.T, np.sum(directions**2, axis=1) / 2)
    weights = np.array([1.0 - tail.sum(), *tail])
    if np.min(weights) >= 0.0:
        yield 0.999 * weights + 0.001 / 3
    for order in (8, 16, 32, 64):
        for a in range(1, order):
            for b in range(1, order - a):
                yield np.array([a, b, order - a - b]) / order


def build_face_regions(
    triangle: np.ndarray,
    centers: np.ndarray,
    expanded_radius: float,
    convex_certificate: dict[str, Any],
    *,
    tolerance: float = 1e-6,
    extra_weights: Any = (),
    max_point_tests: int = 8192,
    max_cycles: int = 128,
) -> dict[str, Any]:
    """Discover independent free-region witnesses distinguished by covered loops.

    Parameters
    ----------
    triangle, centers : numpy.ndarray
        Carrier and all atomic centers in angstroms.
    expanded_radius, tolerance : float
        Common expanded radius and decision margin in angstroms.
    convex_certificate : dict
        Complete independently checked convex intersection evidence.
    extra_weights : sequence, optional
        Additional candidate barycentric weights, independently checked here.
    max_point_tests, max_cycles : int
        Explicit ceilings for discovery and covered-cycle support.

    Returns
    -------
    dict
        Exactly the independently counted number of separated free witnesses.

    Raises
    ------
    ValueError
        Evidence, margins or bounded complete localization cannot be established.
    """
    verified = verify_face_certificate(
        triangle, centers, expanded_radius, convex_certificate, tolerance=tolerance
    )
    count = verified['free_components']
    cycles = _cycles(convex_certificate) if count else []
    if len(cycles) > max_cycles:
        raise ReferenceUnresolved('Covered-cycle budget exhausted')
    polygons = _polygons(triangle, convex_certificate, cycles)
    regions = []
    signatures = set()
    tested = 0
    for weights in (
        _candidates(
            triangle,
            centers,
            expanded_radius,
            convex_certificate,
            tolerance,
            extra_weights,
        )
        if count
        else ()
    ):
        if tested >= max_point_tests:
            raise ReferenceUnresolved('Free-point discovery budget exhausted')
        tested += 1
        try:
            point = _free_point(triangle, centers, expanded_radius, weights, tolerance)
        except ValueError:
            continue
        signature = _signature(point, polygons, triangle, tolerance)
        if tuple(signature) in signatures:
            continue
        regions.append(
            {'barycentric_weights': weights.tolist(), 'winding_signature': signature}
        )
        signatures.add(tuple(signature))
        if len(regions) == count:
            break
    if len(regions) != count:
        raise ReferenceUnresolved('Incomplete independent free-region witnesses')
    return {
        'schema': 'topomt.convex-face-regions.angstrom/2',
        'cycles': cycles,
        'regions': regions,
        'point_tests': tested,
    }


def verify_face_regions(
    triangle: np.ndarray,
    centers: np.ndarray,
    expanded_radius: float,
    convex_certificate: dict[str, Any],
    region_certificate: dict[str, Any],
    *,
    tolerance: float = 1e-6,
    max_cycles: int = 128,
) -> dict[str, Any]:
    """Verify distinct winding witnesses exhaust an independently counted face.

    Parameters
    ----------
    triangle, centers : numpy.ndarray
        Carrier and all atomic centers, in angstroms.
    expanded_radius, tolerance : float
        Common expanded radius and required decision margin, in angstroms.
    convex_certificate, region_certificate : dict
        Complete convex and free-region evidence.
    max_cycles : int
        Maximum accepted number of covered support cycles.

    Returns
    -------
    dict
        Independently counted components and resolved local correspondence.

    Raises
    ------
    ValueError
        Witness, cycle, margin or component inventory cannot be verified.
    """
    count = verify_face_certificate(
        triangle, centers, expanded_radius, convex_certificate, tolerance=tolerance
    )['free_components']
    cycles = _cycles(convex_certificate) if count else []
    if (
        region_certificate.get('schema') != 'topomt.convex-face-regions.angstrom/2'
        or region_certificate['cycles'] != cycles
        or len(cycles) > max_cycles
    ):
        raise ValueError('Invalid covered-cycle inventory')
    regions = region_certificate['regions']
    if len(regions) != count:
        raise ValueError('Incomplete free-region witness inventory')
    polygons = _polygons(triangle, convex_certificate, cycles)
    signatures = set()
    for row in regions:
        point = _free_point(
            triangle, centers, expanded_radius, row['barycentric_weights'], tolerance
        )
        signature = _signature(point, polygons, triangle, tolerance)
        if row['winding_signature'] != signature or tuple(signature) in signatures:
            raise ValueError('False or repeated free-region winding signature')
        signatures.add(tuple(signature))
    return {'free_components': count, 'localization': 'resolved'}


def _inward_weights(triangle, face, edge, interval, centers, radius, tolerance):
    t = sum(interval) / 2
    boundary = np.zeros(3)
    boundary[face.index(edge[0])] = 1 - t
    boundary[face.index(edge[1])] = t
    point = boundary @ triangle
    margin = _segment_margin(point, point, centers, radius)
    if margin <= tolerance:
        raise ReferenceUnresolved('Seam midpoint lacks a free margin')
    distance = np.linalg.norm(triangle.mean(axis=0) - point)
    step = min(0.1, margin / (4 * max(distance, tolerance)))
    weights = (1 - step) * boundary + step / 3
    inside = _free_point(triangle, centers, radius, weights, tolerance)
    if _segment_margin(point, inside, centers, radius) <= tolerance:
        raise ReferenceUnresolved('Seam has no verified free inward segment')
    return weights


def _label(triangle, centers, radius, convex, regions, weights, tolerance):
    point = _free_point(triangle, centers, radius, weights, tolerance)
    signature = _signature(
        point, _polygons(triangle, convex, regions['cycles']), triangle, tolerance
    )
    matches = [
        index
        for index, row in enumerate(regions['regions'])
        if row['winding_signature'] == signature
    ]
    if len(matches) != 1:
        raise ReferenceUnresolved('Seam point lacks a unique proven region label')
    return matches[0]


def build_region_certificate(
    input_file: Path, protocol_file: Path, prior_candidate_file: Path
) -> dict[str, Any]:
    """Reuse frozen convex evidence, then discover complete region/seam witnesses.

    Parameters
    ----------
    input_file, protocol_file, prior_candidate_file : Path
        Frozen input, v2 protocol and exact preceding independent certificate.

    Returns
    -------
    dict
        Complete fixed-angstrom evidence without a claimed global answer.

    Raises
    ------
    ValueError
        Identity, scope, margins or bounded discovery cannot be accepted.
    """
    import hashlib
    import json

    from devtools.verify_small_probe_boundary import _edge_intervals, _model

    centers, radius, tolerance, faces, edges, protocol, input_hash, protocol_hash = (
        _model(input_file, protocol_file, protocol_version=2)
    )
    raw = prior_candidate_file.read_bytes()
    if (
        hashlib.sha256(raw).hexdigest()
        != protocol['predecessor']['candidate_certificate_sha256']
    ):
        raise ValueError('Independent predecessor certificate identity differs')
    prior = json.loads(raw)
    if (
        prior['input_sha256'] != input_hash
        or prior['protocol_sha256'] != protocol['predecessor']['protocol_sha256']
        or prior['schema'] != 'topomt.benchlab.small-probe-boundary.angstrom/1'
    ):
        raise ValueError('Independent predecessor context differs')
    if [tuple(row['atom_indices']) for row in prior['faces']] != faces or [
        tuple(row['atom_indices']) for row in prior['seams']
    ] != edges:
        raise ValueError('Incomplete predecessor hull inventory')
    if protocol['budgets']['max_grid_order'] != 64:
        raise ValueError('Unsupported point-discovery grid policy')
    seams = []
    extra: dict[int, list[np.ndarray]] = {index: [] for index in range(len(faces))}
    for edge, row in zip(edges, prior['seams'], strict=True):
        intervals = _edge_intervals(
            centers[edge[0]], centers[edge[1]], centers, radius, tolerance
        )
        if intervals != row['free_t_intervals']:
            raise ValueError('Predecessor seam no longer matches the query')
        incident = [index for index, face in enumerate(faces) if set(edge) <= set(face)]
        for index in incident:
            for interval in intervals:
                extra[index].append(
                    _inward_weights(
                        centers[list(faces[index])],
                        faces[index],
                        edge,
                        interval,
                        centers,
                        radius,
                        tolerance,
                    )
                )
        seams.append(
            {
                'atom_indices': list(edge),
                'free_t_intervals': intervals,
                'connections': [],
            }
        )
    records = []
    tested = 0
    for index, (face, row) in enumerate(zip(faces, prior['faces'], strict=True)):
        remaining = protocol['budgets']['max_point_tests'] - tested
        local = build_face_regions(
            centers[list(face)],
            centers,
            radius,
            row['convex_intersections'],
            tolerance=tolerance,
            extra_weights=extra[index],
            max_point_tests=min(8192, remaining),
            max_cycles=protocol['budgets']['max_cycles_per_face'],
        )
        tested += local['point_tests']
        records.append(
            {
                'atom_indices': list(face),
                'convex_intersections': row['convex_intersections'],
                'localization': local,
            }
        )
    for seam in seams:
        edge = tuple(seam['atom_indices'])
        incident = [index for index, face in enumerate(faces) if set(edge) <= set(face)]
        for interval in seam['free_t_intervals']:
            sides = []
            for index in incident:
                triangle = centers[list(faces[index])]
                weights = _inward_weights(
                    triangle, faces[index], edge, interval, centers, radius, tolerance
                )
                region = _label(
                    triangle,
                    centers,
                    radius,
                    records[index]['convex_intersections'],
                    records[index]['localization'],
                    weights,
                    tolerance,
                )
                sides.append(
                    {
                        'face_index': index,
                        'region_index': region,
                        'barycentric_weights': weights.tolist(),
                    }
                )
            seam['connections'].append(sides)
    return {
        'schema': 'topomt.benchlab.small-probe-regions.angstrom/2',
        'length_unit': 'angstrom',
        'input_sha256': input_hash,
        'protocol_sha256': protocol_hash,
        'predecessor_certificate_sha256': hashlib.sha256(raw).hexdigest(),
        'faces': records,
        'seams': seams,
        'work': {'point_tests': tested},
        'origin_paths': [],
    }


def verify_region_certificate(
    input_file: Path, protocol_file: Path, certificate: dict[str, Any]
) -> dict[str, Any]:
    """Check exhaustive face regions and every seam before accepting a total count.

    Parameters
    ----------
    input_file, protocol_file : Path
        Frozen input and matching v2 numerical/work protocol.
    certificate : dict
        Complete face-region, seam and optional positive-path evidence.

    Returns
    -------
    dict
        Independently verified global count, supports and separate path status.

    Raises
    ------
    ValueError
        Units, identity, support, witness or completeness cannot be established.
    """
    from devtools.verify_small_probe_boundary import _edge_intervals, _model

    centers, radius, tolerance, faces, edges, protocol, input_hash, protocol_hash = (
        _model(input_file, protocol_file, protocol_version=2)
    )
    if (
        certificate.get('schema') != 'topomt.benchlab.small-probe-regions.angstrom/2'
        or certificate.get('length_unit') != 'angstrom'
        or certificate['input_sha256'] != input_hash
        or certificate['protocol_sha256'] != protocol_hash
        or certificate['predecessor_certificate_sha256']
        != protocol['predecessor']['candidate_certificate_sha256']
    ):
        raise ValueError('Region certificate units, schema or identity differs')
    if [tuple(row['atom_indices']) for row in certificate['faces']] != faces or [
        tuple(row['atom_indices']) for row in certificate['seams']
    ] != edges:
        raise ValueError('Incomplete region hull inventory')
    parents = {}
    face_counts = []
    decisions = 0
    for index, (face, row) in enumerate(zip(faces, certificate['faces'], strict=True)):
        checked = verify_face_certificate(
            centers[list(face)],
            centers,
            radius,
            row['convex_intersections'],
            tolerance=tolerance,
        )
        decisions += checked['decision_count']
        if decisions > protocol['budgets']['intersection_decisions']:
            raise ValueError('Convex inventory budget exceeded')
        verified = verify_face_regions(
            centers[list(face)],
            centers,
            radius,
            row['convex_intersections'],
            row['localization'],
            tolerance=tolerance,
            max_cycles=protocol['budgets']['max_cycles_per_face'],
        )
        count = verified['free_components']
        face_counts.append(count)
        for region in range(count):
            parents[index, region] = (index, region)

    def root(key):
        while parents[key] != key:
            key = parents[key]
        return key

    free_seams = 0
    for edge, row in zip(edges, certificate['seams'], strict=True):
        intervals = _edge_intervals(
            centers[edge[0]], centers[edge[1]], centers, radius, tolerance
        )
        if intervals != row['free_t_intervals'] or len(row['connections']) != len(
            intervals
        ):
            raise ValueError('Incorrect or incomplete free-seam inventory')
        incident = [index for index, face in enumerate(faces) if set(edge) <= set(face)]
        if len(incident) != 2:
            raise ValueError('Reference hull is not manifold')
        for interval, sides in zip(intervals, row['connections'], strict=True):
            if [side['face_index'] for side in sides] != incident:
                raise ValueError('Incomplete seam-side associations')
            keys = []
            for side in sides:
                index = side['face_index']
                triangle = centers[list(faces[index])]
                face_record = certificate['faces'][index]
                weights = side['barycentric_weights']
                region = _label(
                    triangle,
                    centers,
                    radius,
                    face_record['convex_intersections'],
                    face_record['localization'],
                    weights,
                    tolerance,
                )
                if side['region_index'] != region:
                    raise ValueError('False seam region assignment')
                t = sum(interval) / 2
                midpoint = (1 - t) * centers[edge[0]] + t * centers[edge[1]]
                interior = _free_point(triangle, centers, radius, weights, tolerance)
                if _segment_margin(midpoint, interior, centers, radius) <= tolerance:
                    raise ValueError('Blocked seam attachment segment')
                keys.append((index, region))
            parents[root(keys[0])] = root(keys[1])
        free_seams += bool(intervals)
    if radius <= tolerance:
        raise ValueError('Hull vertices are not strictly excluded')
    groups: dict[tuple[int, int], list[list[int]]] = {}
    for key in parents:
        groups.setdefault(root(key), []).append(list(key))
    result = {
        'schema': 'topomt.benchlab.small-probe-regions-verification/2',
        'input_sha256': input_hash,
        'protocol_sha256': protocol_hash,
        'opening_component_count': len(groups),
        'hull_face_count': len(faces),
        'free_face_count': sum(bool(count) for count in face_counts),
        'face_region_count': sum(face_counts),
        'free_seam_count': free_seams,
        'components_face_regions': list(groups.values()),
        'source_faces': [list(face) for face in faces],
        'complete_inventory': True,
        'origin_path_status': 'not_computed',
        'scope': 'Independent fixed-hull count and localization; aperture area/global bottleneck not established',
    }
    paths = certificate.get('origin_paths', [])
    if paths:
        seen = set()
        margins = []
        for path in paths:
            index = path['component_index']
            node = [path['face_index'], path['region_index']]
            if (
                type(index) is not int
                or not 0 <= index < len(groups)
                or index in seen
                or node not in result['components_face_regions'][index]
            ):
                raise ValueError('False or repeated origin-path component association')
            checked = _validate_origin_path(
                centers, radius, tolerance, protocol, faces, certificate['faces'], path
            )
            margins.append(checked)
            seen.add(index)
        result['origin_path_status'] = (
            'resolved' if len(seen) == len(groups) else 'unresolved'
        )
        result['origin_connected_patch_count'] = len(seen)
        result['origin_path_margins'] = margins
    return result


def _outward_normal(triangle, centers):
    normal = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
    normal /= np.linalg.norm(normal)
    if (centers.mean(axis=0) - triangle[0]) @ normal > 0.0:
        normal = -normal
    return normal


def _validate_origin_path(
    centers, radius, tolerance, protocol, faces, face_records, path
):
    origin = np.asarray(protocol['origin'], dtype=float)
    if origin.shape != (3,) or not np.isfinite(origin).all():
        raise ValueError('Invalid reference origin')
    for face in faces:
        triangle = centers[list(face)]
        if (origin - triangle[0]) @ _outward_normal(triangle, centers) >= -tolerance:
            raise ValueError('Reference origin is not strictly inside this hull')
    index = path['face_index']
    triangle = centers[list(faces[index])]
    point = _free_point(
        triangle, centers, radius, path['barycentric_weights'], tolerance
    )
    row = face_records[index]
    region = _label(
        triangle,
        centers,
        radius,
        row['convex_intersections'],
        row['localization'],
        path['barycentric_weights'],
        tolerance,
    )
    if region != path['region_index']:
        raise ValueError('Origin path attaches to another free region')
    normal = _outward_normal(triangle, centers)
    direction = np.asarray(path['ray_direction'], dtype=float)
    if (
        direction.shape != (3,)
        or not np.isfinite(direction).all()
        or not np.allclose(direction, normal, rtol=0.0, atol=1e-12)
    ):
        raise ValueError('Invalid outward reference ray')
    segment = _segment_margin(origin, point, centers, radius)
    nearest = np.maximum(0.0, (centers - point) @ direction)
    ray = float(
        np.min(np.linalg.norm(point + nearest[:, None] * direction - centers, axis=1))
        - radius
    )
    if min(segment, ray) <= tolerance:
        raise ValueError('Origin path or infinite continuation is blocked')
    return {'segment_margin_angstroms': segment, 'ray_margin_angstroms': ray}


def build_origin_paths(
    input_file: Path, protocol_file: Path, certificate: dict[str, Any]
) -> list[dict[str, Any]]:
    """Discover independent positive common-origin paths; failures stay unavailable.

    Parameters
    ----------
    input_file, protocol_file : Path
        Frozen input and v2 protocol with the original origin and work ceiling.
    certificate : dict
        Already verified independent boundary-region evidence.

    Returns
    -------
    list of dict
        Positive paths only; a missing path never excludes curved alternatives.

    Raises
    ------
    ValueError
        The underlying independent boundary evidence is invalid.
    """
    from devtools.verify_small_probe_boundary import _model

    geometry = _model(input_file, protocol_file, protocol_version=2)
    centers, radius, tolerance, faces, _, protocol, _, _ = geometry
    base = {**certificate, 'origin_paths': []}
    topology = verify_region_certificate(input_file, protocol_file, base)
    paths: list[dict[str, Any]] = []
    attempts = certificate['work']['point_tests']
    for component_index, nodes in enumerate(topology['components_face_regions']):
        found = False
        for face_index, region_index in nodes:
            row = certificate['faces'][face_index]
            triangle = centers[list(faces[face_index])]
            for representative in row['localization']['regions']:
                if attempts >= protocol['budgets']['max_point_tests']:
                    return paths
                attempts += 1
                path = {
                    'component_index': component_index,
                    'face_index': face_index,
                    'region_index': region_index,
                    'barycentric_weights': representative['barycentric_weights'],
                    'ray_direction': _outward_normal(triangle, centers).tolist(),
                }
                try:
                    _validate_origin_path(
                        centers,
                        radius,
                        tolerance,
                        protocol,
                        faces,
                        certificate['faces'],
                        path,
                    )
                except ValueError:
                    continue
                paths.append(path)
                found = True
                break
            if found:
                break
    return paths
