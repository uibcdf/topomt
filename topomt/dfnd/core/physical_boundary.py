"""Bounded physical hull patches and component paths, with explicit nm units."""

from itertools import combinations
from typing import TYPE_CHECKING, Any

import numpy as np

from ..config import DFNDQuery
from ..identity import _digest
from .physical_arrangement import (
    _inside,
    _Unresolved,
    _value,
    decompose_face,
    segment_clearance,
)

if TYPE_CHECKING:
    from ..graph import DelaunayFlowNetwork


def _free_edge(start, end, centers, radii, tolerance):
    """Inventory strict free intervals on a closed hull edge, in unit t."""
    direction = end - start
    length = np.linalg.norm(direction)
    unit = direction / length
    positions = (centers - start) @ unit
    distances = np.linalg.norm(centers - start - positions[:, None] * unit, axis=1)
    covered = []
    marginal = False
    for position, distance, radius in zip(positions, distances, radii, strict=True):
        if distance > radius + tolerance:
            continue
        if abs(distance - radius) <= tolerance and 0.0 <= position <= length:
            marginal = True
        if distance <= radius:
            half = np.sqrt(max(0.0, radius * radius - distance * distance))
            lo, hi = max(0.0, position - half), min(length, position + half)
            if lo <= hi:
                covered.append((lo, hi))
    free = []
    cursor = 0.0
    roundoff = 256 * np.finfo(float).eps * max(1.0, length)
    for lo, hi in sorted(covered):
        if lo > cursor + roundoff:
            free.append((cursor / length, lo / length))
        cursor = max(cursor, hi)
    if cursor < length - roundoff:
        free.append((cursor / length, 1.0))
    if marginal and free:
        raise _Unresolved('hull-edge tangency within numerical margin')
    for lo, hi in free:
        if (hi - lo) * length <= tolerance or segment_clearance(
            start + ((lo + hi) / 2) * direction,
            start + ((lo + hi) / 2) * direction,
            centers,
            radii,
        ) <= tolerance:
            raise _Unresolved('hull-edge interval within numerical margin')
    return free


def _face_region(face, point):
    """Locate a seam witness in the retained analytic face decomposition."""
    frame = face['frame']
    origin = np.asarray(frame['origin'])
    basis = np.asarray(frame['basis'])
    x, y = (point - origin) @ basis.T
    roundoff = face['roundoff'] * 4
    matches = []
    for index, cell in enumerate(face['cells']):
        left, right = cell['x_span']
        if cell['kind'] == 'section':
            inside = abs(x - left) <= roundoff
        else:
            inside = left + roundoff < x < right - roundoff
        if (
            inside
            and _value(cell['lower'], x, face['disks']) - roundoff
            <= y
            <= _value(cell['upper'], x, face['disks']) + roundoff
        ):
            matches.extend(
                i
                for i, region in enumerate(face['regions'])
                if index in region['cells']
            )
    if len(set(matches)) != 1:
        raise _Unresolved('seam witness lacks a unique supported face region')
    return matches[0]


def _carrier_cover(start, end, tetrahedra):
    """Cover every segment parameter by the claimed tetrahedral union."""
    vector = end - start
    matrix = (tetrahedra[:, 1:] - tetrahedra[:, 0, None, :]).transpose(0, 2, 1)
    try:
        inverse = np.linalg.inv(matrix)
    except np.linalg.LinAlgError:
        return None
    coordinates = np.einsum('nij,nj->ni', inverse, start - tetrahedra[:, 0])
    slopes = np.einsum('nij,j->ni', inverse, vector)
    coordinates = np.column_stack((1.0 - coordinates.sum(axis=1), coordinates))
    slopes = np.column_stack((-slopes.sum(axis=1), slopes))
    epsilon = 1024 * np.finfo(float).eps
    intervals = []
    for index, (weights, delta) in enumerate(zip(coordinates, slopes, strict=True)):
        lo, hi = 0.0, 1.0
        for value, slope in zip(weights, delta, strict=True):
            if abs(slope) <= epsilon:
                if value < -epsilon:
                    lo, hi = 1.0, 0.0
                    break
            elif slope > 0:
                lo = max(lo, (-epsilon - value) / slope)
            else:
                hi = min(hi, (-epsilon - value) / slope)
        if lo <= hi:
            intervals.append((max(0.0, lo), min(1.0, hi), index))
    cursor = 0.0
    selected = []
    for lo, hi, index in sorted(intervals):
        if lo > cursor + epsilon:
            return None
        if hi > cursor:
            selected.append({'local_support_index': index, 't_interval': [lo, hi]})
            cursor = hi
    return selected if cursor >= 1.0 - epsilon else None


def compute_boundary_connectivity(
    network: 'DelaunayFlowNetwork',
    components: list[dict[str, Any]],
    query: DFNDQuery,
    result_identity: str,
) -> dict[str, Any]:
    """Compute bounded hull patches and path-supported native associations.

    The record owns recoverable clipped geometry and explicit nm units; typed
    and public views refer to its patch IDs. Native links/classes are untouched.

    Parameters
    ----------
    network : DelaunayFlowNetwork
        Captured native geometry and source map.
    components : list of dict
        Unfiltered raw wet components with carrier identity.
    query : DFNDQuery
        Probe, margin and bounded work policy.
    result_identity : str
        Canonical identity of this native query.

    Returns
    -------
    dict
        Versioned patches, recoverable support and path associations, or
        explicit noncomputed/unresolved availability with no total count.
    """
    tolerance = query.boundary_tolerance
    result: dict[str, Any] = {
        'schema': 'dfnd.physical_boundary.nm.v1',
        'status': 'not_computed',
        'n_patches': None,
        'patches': [],
        'units': {'length': 'nm', 'coordinates': 'nm'},
        'surface': {
            'kind': 'atomic_center_convex_hull',
            'definition_version': 1,
            'substrate_key': network.substrate_key,
        },
        'query': {
            'result_key': result_identity,
            'probe_radius': query.probe_radius,
            'strict_inequality': 'clearance > probe_radius',
            'exclusion_scope': 'all_selected_atoms',
            'tolerance': tolerance,
            'algorithm': 'analytic_circle_sections_v1',
            'budget': {
                'atoms': query.boundary_max_atoms,
                'faces': query.boundary_max_faces,
                'events': query.boundary_max_events,
                'path_tests': query.boundary_max_path_tests,
                'associations': query.boundary_max_associations,
            },
        },
        'component_associations': {'status': 'not_computed', 'records': []},
        'work': {'events': 0, 'path_tests': 0},
    }
    if not query.physical_boundary:
        result['reason'] = 'physical boundary analysis was not requested'
        return result
    result['status'] = 'unresolved'
    try:
        normals = _decompose_hull(network, query, result, result_identity)
        _associate_components(network, components, query, result, normals)
    except _Unresolved as error:
        result.update(
            status='unresolved', n_patches=None, patches=[], reason=str(error)
        )
    return result


def _decompose_hull(
    network: 'DelaunayFlowNetwork',
    query: DFNDQuery,
    result: dict[str, Any],
    result_identity: str,
) -> list[np.ndarray]:
    """Resolve complete face and seam inventories before accepting a total count."""
    coords = network.atom_coords
    radii = network.atom_radii + query.probe_radius
    atom_map = network.atom_indices_map
    tolerance = query.boundary_tolerance
    if len(coords) > query.boundary_max_atoms:
        raise _Unresolved('selected-atom budget exhausted')
    result['surface'].update(
        source_atom_indices=atom_map.tolist(),
        coordinates=coords.tolist(),
        atomic_radii=network.atom_radii.tolist(),
    )
    carriers = [
        tuple(map(int, face)) for _, _, face in network.mesh.get_boundary_face_records()
    ]
    if not carriers or len(carriers) > query.boundary_max_faces:
        raise _Unresolved('missing hull or hull-face budget exhausted')
    faces = []
    edge_faces: dict[tuple[int, int], list[int]] = {}
    normals = []
    for index, carrier in enumerate(carriers):
        triangle = coords[list(carrier)]
        normal = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
        norm = np.linalg.norm(normal)
        if norm <= tolerance**2:
            raise _Unresolved('degenerate hull face')
        normal /= norm
        if float((coords.mean(axis=0) - triangle[0]) @ normal) > 0:
            normal = -normal
        if float(np.max((coords - triangle[0]) @ normal)) > tolerance:
            raise _Unresolved('carrier surface is not the declared convex hull')
        normals.append(normal)
        remaining = query.boundary_max_events - result['work']['events']
        if remaining <= 0:
            raise _Unresolved('global arrangement budget exhausted')
        face = decompose_face(
            triangle, coords, radii, tolerance=tolerance, max_events=remaining
        )
        result['work']['events'] += face['work_units']
        face['source_atom_indices'] = [int(atom_map[i]) for i in carrier]
        faces.append(face)
        if face['status'] != 'resolved' or not face['inventory_complete']:
            raise _Unresolved(
                f'face {index}: {face.get("reason", "incomplete inventory")}'
            )
        for region in face['regions']:
            witness = np.asarray(region['witness'])
            if (
                witness.shape != (3,)
                or not np.isfinite(witness).all()
                or segment_clearance(witness, witness, coords, radii) <= tolerance
            ):
                raise _Unresolved(f'face {index}: invalid all-atom free witness')
            frame = face['frame']
            delta = witness - np.asarray(frame['origin'])
            if abs(
                float(delta @ np.asarray(frame['normal']))
            ) > tolerance or not _inside(
                delta @ np.asarray(frame['basis']).T,
                np.asarray(face['triangle']),
                face['roundoff'],
            ):
                raise _Unresolved(f'face {index}: witness outside its carrier')
        for edge in combinations(carrier, 2):
            edge_faces.setdefault((min(edge), max(edge)), []).append(index)
    if any(len(incident) != 2 for incident in edge_faces.values()):
        raise _Unresolved('incomplete or nonmanifold hull seam inventory')
    result['surface']['faces'] = faces
    parents = {}
    seams = []
    for index, face in enumerate(faces):
        for region in range(len(face['regions'])):
            parents[index, region] = (index, region)

    def root(key):
        while parents[key] != key:
            parents[key] = parents[parents[key]]
            key = parents[key]
        return key

    for edge, incident in sorted(edge_faces.items()):
        start, end = coords[list(edge)]
        intervals = _free_edge(start, end, coords, radii, tolerance)
        seam = {
            'source_atom_indices': [int(atom_map[i]) for i in edge],
            'face_indices': incident,
            'free_t_intervals': [list(interval) for interval in intervals],
        }
        for lo, hi in intervals:
            point = start + ((lo + hi) / 2) * (end - start)
            keys = [(i, _face_region(faces[i], point)) for i in incident]
            parents[root(keys[0])] = root(keys[1])
        seams.append(seam)
    result['surface']['seams'] = seams
    groups: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for key in parents:
        groups.setdefault(root(key), []).append(key)
    for group in groups.values():
        selectors = [
            {'face_index': face, 'region_index': region}
            for face, region in sorted(group)
        ]
        face_ids = sorted({face for face, _ in group})
        support = {
            'kind': 'hull_free_patch',
            'surface_substrate_key': network.substrate_key,
            'carrier_faces_source_atom_indices': [
                faces[i]['source_atom_indices'] for i in face_ids
            ],
            'face_regions': selectors,
            'recovery': 'surface.faces[face_index].regions[region_index]; analytic cells and all surface atomic radii plus query probe',
        }
        patch_id = _digest(
            'physical-patch',
            {
                'result_key': result_identity,
                'regions': sorted(
                    [
                        {
                            'source_atoms': sorted(faces[face]['source_atom_indices']),
                            'representative': faces[face]['regions'][region]['witness'],
                        }
                        for face, region in group
                    ],
                    key=lambda item: (item['source_atoms'], item['representative']),
                ),
            },
        )
        result['patches'].append(
            {
                'patch_id': patch_id,
                'support': support,
                'evidence': {
                    'connectivity': 'resolved',
                    'inventory_complete': True,
                    'within_faces': 'complete analytic critical-section arrangement',
                    'seams': 'complete all-atom edge intervals',
                },
                'association_candidates': [
                    {
                        'face_index': face,
                        'point': faces[face]['regions'][region]['witness'],
                    }
                    for face, region in group
                ],
            }
        )
    result.update(status='resolved', n_patches=len(groups))
    return normals


def _associate_components(
    network: 'DelaunayFlowNetwork',
    components: list[dict[str, Any]],
    query: DFNDQuery,
    result: dict[str, Any],
    normals: list[np.ndarray],
) -> None:
    """Keep path search and allocation bounded independently of patch topology."""
    coords = network.atom_coords
    radii = network.atom_radii + query.probe_radius
    tolerance = query.boundary_tolerance
    if len(components) * result['n_patches'] > query.boundary_max_associations:
        result['component_associations'] = {
            'status': 'unresolved',
            'records': [],
            'reason': 'component/patch pair budget exhausted',
        }
        return
    associations = []
    all_resolved = True
    for component in components:
        for patch in result['patches']:
            association = {
                'component_key': component['component_key'],
                'support_key': component['support_key'],
                'patch_id': patch['patch_id'],
                'status': 'unresolved',
                'reason': 'no compatible straight path established; curved paths are not excluded',
            }
            nodes = component['tetrahedron_ids']
            tetrahedra = coords[network.tetra_atoms[nodes]]
            candidates = [
                np.asarray(component['center']),
                *network.tetra_residence_centers[component['resident_tetrahedron_ids']],
            ]
            found = False
            for attachment in patch['association_candidates']:
                point = np.asarray(attachment['point'])
                normal = normals[attachment['face_index']]
                for start in candidates:
                    if result['work']['path_tests'] >= query.boundary_max_path_tests:
                        break
                    result['work']['path_tests'] += 1
                    margin = segment_clearance(start, point, coords, radii)
                    if margin <= tolerance:
                        continue
                    cover = _carrier_cover(start, point, tetrahedra)
                    if cover is None:
                        continue
                    if float(np.min((point - coords) @ normal)) < -tolerance:
                        continue
                    ray_t = np.maximum(0.0, (coords - point) @ normal)
                    ray_margin = float(
                        np.min(
                            np.linalg.norm(
                                point + ray_t[:, None] * normal - coords, axis=1
                            )
                            - radii
                        )
                    )
                    if ray_margin <= tolerance:
                        continue
                    for interval in cover:
                        interval['tetrahedron_id'] = int(
                            nodes[interval.pop('local_support_index')]
                        )
                    association.update(
                        status='resolved',
                        reason=None,
                        path={
                            'start': start.tolist(),
                            'attachment': point.tolist(),
                            'surface_face_index': attachment['face_index'],
                            'all_atom_clearance_margin': margin,
                            'carrier_cover': cover,
                            'carrier_roundoff_barycentric': 1024 * np.finfo(float).eps,
                            'exterior_ray_direction': normal.tolist(),
                            'exterior_ray_clearance_margin': ray_margin,
                            'exterior_rule': 'convex-hull outward normal; every atom lies in inward halfspace',
                        },
                    )
                    found = True
                    break
                if found:
                    break
            all_resolved &= found
            associations.append(association)
    result['component_associations'] = {
        'status': 'resolved' if all_resolved else 'unresolved',
        'records': associations,
    }
