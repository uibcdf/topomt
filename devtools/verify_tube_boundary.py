"""Independent complete tube hull inventory using wall covers and end-face nerves."""

import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
from scipy.spatial import ConvexHull

from devtools.verify_closed_shell_wall_cover import _values, verify_triangle_cover
from devtools.verify_origin_access_bracket import build_cover
from devtools.verify_small_probe_boundary import (
    ReferenceUnresolved,
    _Budget,
    _edge_intervals,
    build_face_certificate,
    verify_face_certificate,
)


def boundary_model(input_file: Path, protocol_file: Path) -> dict[str, Any]:
    """Recover a complete, disjoint tube hull wall/end partition.

    Parameters
    ----------
    input_file, protocol_file : Path
        Frozen ball input and preceding hybrid-boundary protocol.

    Returns
    -------
    dict
        Explicit angstrom geometry, complete hull inventory and ring-based roles.
        Face indices are local array indices; source_atom_indices maps their atoms.

    Raises
    ------
    ValueError
        Identity, units, radius or complete nominal grid is unsupported.
    """
    payload = input_file.read_bytes()
    protocol_bytes = protocol_file.read_bytes()
    fixture = json.loads(payload)
    protocol = json.loads(protocol_bytes)
    if (
        protocol['schema'] != 'topomt.benchlab.tube-boundary-protocol/1'
        or protocol['case'] != fixture['case_id']
        or protocol['input_sha256'] != hashlib.sha256(payload).hexdigest()
        or protocol['length_unit'] != 'angstroms'
    ):
        raise ValueError('Tube boundary identity or units differ')
    centers = _values(fixture['coordinates'], 'coordinates', 'angstroms')
    radii = _values(fixture['atom_radii'], 'atom_radii', 'angstroms')
    grid = fixture['nominal_grid']
    width = grid['n_angles']
    rings = grid['n_rings']
    if (
        len(centers) != width * rings
        or not np.isfinite(centers).all()
        or not np.isfinite(radii).all()
        or np.any(radii < 0)
        or not np.all(radii == radii[0])
    ):
        raise ValueError('Unsupported equal-radius nominal tube grid')
    if (
        protocol['budgets']['optimizer_iterations_per_call'] != 100
        or protocol['decision_margin_angstroms'] <= 0
    ):
        raise ValueError('Unsupported reference solver/margin policy')
    hull = ConvexHull(centers)
    faces = sorted(tuple(sorted(map(int, face))) for face in hull.simplices)
    ends = [
        i
        for i, face in enumerate(faces)
        if all(atom < width for atom in face)
        or all(atom >= len(centers) - width for atom in face)
    ]
    return {
        'centers': centers,
        'radii': radii,
        'hull_faces': [list(face) for face in faces],
        'wall_face_indices': [i for i in range(len(faces)) if i not in ends],
        'end_face_indices': ends,
        'n_angles': width,
        'source_atom_indices': fixture['source_atom_indices'],
        'protocol': protocol,
        'protocol_sha256': hashlib.sha256(protocol_bytes).hexdigest(),
    }


def build_boundary(input_file: Path, protocol_file: Path) -> dict[str, Any]:
    """Discover wall-cover leaves and complete end-face convex evidence.

    Parameters
    ----------
    input_file, protocol_file : Path
        Original input and predeclared partition/work protocol.

    Returns
    -------
    dict
        Fixed-angstrom candidate with exhaustive hull/edge inventory.

    Raises
    ------
    ValueError
        Geometry, finite cover or convex witness budget cannot be accepted.
    """
    model = boundary_model(input_file, protocol_file)
    p = model['protocol']
    limits = p['budgets']
    centers, radii = model['centers'], model['radii']
    faces = model['hull_faces']
    walls = np.asarray([faces[i] for i in model['wall_face_indices']], dtype=int)
    leaves, work = build_cover(
        centers,
        radii,
        walls,
        p['probe_angstroms'],
        p['decision_margin_angstroms'],
        limits['maximum_cover_depth'],
        limits['maximum_cover_nodes'],
    )
    budget = _Budget(limits['intersection_decisions'], limits['solver_calls'])
    ends = [
        {
            'face_index': index,
            'convex_intersections': build_face_certificate(
                centers[faces[index]],
                centers,
                float(radii[0] + p['probe_angstroms']),
                tolerance=p['decision_margin_angstroms'],
                budget=budget,
            ),
        }
        for index in model['end_face_indices']
    ]
    edges = sorted(
        {tuple(sorted(edge)) for face in faces for edge in combinations(face, 2)}
    )
    return {
        'schema': 'topomt.benchlab.tube-boundary-certificate/1',
        'length_unit': 'angstroms',
        'input_sha256': p['input_sha256'],
        'protocol_sha256': model['protocol_sha256'],
        'hull_faces': faces,
        'wall_face_indices': model['wall_face_indices'],
        'wall_cover': leaves,
        'end_faces': ends,
        'seams': [
            {
                'atom_indices': list(edge),
                'free_t_intervals': _edge_intervals(
                    centers[edge[0]],
                    centers[edge[1]],
                    centers,
                    float(radii[0] + p['probe_angstroms']),
                    p['decision_margin_angstroms'],
                ),
            }
            for edge in edges
        ],
        'work': {
            'wall_cover_nodes': work,
            'intersection_decisions': budget.used_decisions,
            'solver_calls': budget.used_solvers,
        },
    }


def verify_boundary(
    input_file: Path, protocol_file: Path, certificate: dict[str, Any]
) -> dict[str, Any]:
    """Verify complete wall coverage and end/seam regions before counting patches.

    Parameters
    ----------
    input_file, protocol_file : Path
        Exact original input and protocol.
    certificate : dict
        Retained complete independent boundary candidate.

    Returns
    -------
    dict
        Strict-free hull count, mapped supports, end labels and work/margin data.
        This establishes no aperture area or interior transport by itself.

    Raises
    ------
    ValueError
        Context, units, completeness, witness or bounded receiving scope fails.
    """
    model = boundary_model(input_file, protocol_file)
    p = model['protocol']
    limits = p['budgets']
    centers, radii = model['centers'], model['radii']
    faces = model['hull_faces']
    tol = p['decision_margin_angstroms']
    expanded = float(radii[0] + p['probe_angstroms'])
    if (
        certificate.get('schema') != 'topomt.benchlab.tube-boundary-certificate/1'
        or certificate.get('length_unit') != 'angstroms'
        or certificate['input_sha256'] != p['input_sha256']
        or certificate['protocol_sha256'] != model['protocol_sha256']
        or certificate['hull_faces'] != faces
        or certificate['wall_face_indices'] != model['wall_face_indices']
    ):
        raise ValueError('Tube boundary context or full hull differs')
    walls = np.asarray([faces[i] for i in model['wall_face_indices']], dtype=int)
    cover = verify_triangle_cover(
        centers,
        radii,
        walls,
        certificate['wall_cover'],
        p['probe_angstroms'],
        tol,
        length_unit='angstroms',
        maximum_depth=limits['maximum_cover_depth'],
        maximum_nodes=limits['maximum_cover_nodes'],
    )
    if [row['face_index'] for row in certificate['end_faces']] != model[
        'end_face_indices'
    ]:
        raise ValueError('Incomplete/reordered end-face inventory')
    counts = dict.fromkeys(model['wall_face_indices'], 0)
    decisions = 0
    for row in certificate['end_faces']:
        index = row['face_index']
        result = verify_face_certificate(
            centers[faces[index]],
            centers,
            expanded,
            row['convex_intersections'],
            tolerance=tol,
            max_decisions=limits['intersection_decisions'],
        )
        count = result['free_components']
        decisions += result['decision_count']
        if count not in (0, 1):
            raise ReferenceUnresolved(
                'Multiple end-face regions need independently localized seams'
            )
        counts[index] = count
    if (
        decisions > limits['intersection_decisions']
        or certificate['work']['solver_calls'] > limits['solver_calls']
        or certificate['work']['wall_cover_nodes'] > limits['maximum_cover_nodes']
    ):
        raise ValueError('Boundary reference work ceiling exceeded')
    parents = {index: index for index, count in counts.items() if count}

    def root(index):
        while parents[index] != index:
            index = parents[index]
        return index

    edges = sorted(
        {tuple(sorted(edge)) for face in faces for edge in combinations(face, 2)}
    )
    if [tuple(row['atom_indices']) for row in certificate['seams']] != edges:
        raise ValueError('Incomplete/reordered hull seam inventory')
    free_seams = 0
    for edge, row in zip(edges, certificate['seams'], strict=True):
        expected = _edge_intervals(
            centers[edge[0]], centers[edge[1]], centers, expanded, tol
        )
        if expected != row['free_t_intervals']:
            raise ValueError('Free seam intervals differ')
        incident = [i for i, face in enumerate(faces) if set(edge) <= set(face)]
        if len(incident) != 2:
            raise ValueError('Hull boundary is not a complete two-manifold')
        if expected:
            if any(counts[i] != 1 for i in incident):
                raise ValueError('Free seam disagrees with a covered face')
            parents[root(incident[0])] = root(incident[1])
            free_seams += 1
    if expanded <= tol:
        raise ValueError('Hull vertices lack strict own-ball exclusion')
    groups: dict[int, list[int]] = {}
    for index in parents:
        groups.setdefault(root(index), []).append(index)
    labels = []
    supports = []
    for group in groups.values():
        atoms = {atom for i in group for atom in faces[i]}
        labels.append(
            'negative_z'
            if all(atom < model['n_angles'] for atom in atoms)
            else 'positive_z'
            if all(atom >= len(centers) - model['n_angles'] for atom in atoms)
            else 'unclassified_or_spanning_ends'
        )
        supports.append(
            [[model['source_atom_indices'][atom] for atom in faces[i]] for i in group]
        )
    return {
        'schema': 'topomt.benchlab.tube-boundary-verification/1',
        'length_unit': 'angstroms',
        'input_sha256': p['input_sha256'],
        'protocol_sha256': model['protocol_sha256'],
        'opening_component_count': len(groups),
        'component_end_labels': labels,
        'components_faces_source_atom_indices': supports,
        'complete_hull_faces': len(faces),
        'covered_wall_faces': len(model['wall_face_indices']),
        'end_faces': len(model['end_face_indices']),
        'free_end_faces': sum(counts.values()),
        'free_seams': free_seams,
        'convex_intersection_decisions': decisions,
        'wall_cover': cover,
        'scope': 'Complete strict-free hull boundary patches, not interior global cavity count, aperture area or globally maximal bottleneck',
    }
