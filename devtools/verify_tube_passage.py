"""Independent straight-tube path witnesses and a conservative finite-hull cover.

Only frozen coordinates, explicit radii and the nominal input grid are used.
No production DFND routine, graph, candidate path or observation is imported.
The nominal-grid bound is a covering inequality, not a cylinder-volume formula.
"""

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pyunitwizard as puw

from devtools.verify_closed_shell_wall_cover import _values


def _segments(starts, ends, centers, radii):
    delta = ends - starts
    length2 = np.sum(delta * delta, axis=1)
    offsets = centers[None] - starts[:, None]
    numerators = np.einsum('eni,ei->en', offsets, delta)
    along = np.divide(
        numerators,
        length2[:, None],
        out=np.zeros_like(numerators),
        where=length2[:, None] > 0,
    )
    along = np.clip(along, 0.0, 1.0)
    distances = np.linalg.norm(offsets - along[:, :, None] * delta[:, None], axis=2)
    return np.min(distances - radii[None], axis=1)


def polyline_clearance(
    points: np.ndarray, centers: np.ndarray, radii: np.ndarray, *, length_unit: str
) -> float:
    """Check every complete segment against every ball, returning angstrom clearance.

    Parameters
    ----------
    points, centers : numpy.ndarray
        Ordered path stations and atomic centers, shape (n, 3), in length_unit.
    radii : numpy.ndarray
        Nonnegative atomic radii, one per center, in the same explicit unit.
    length_unit : str
        Required common source length unit; receiver conversion is explicit.

    Returns
    -------
    float
        Minimum bare-ball clearance in angstroms. Negative means penetration.
        This checks this polyline only, without a globally optimal path claim.

    Raises
    ------
    ValueError
        Shapes, finite values or nonnegative radii are invalid.
    """
    factor = float(puw.get_value(puw.quantity(1.0, length_unit), to_unit='angstroms'))
    points = np.asarray(points, dtype=float) * factor
    centers = np.asarray(centers, dtype=float) * factor
    radii = np.asarray(radii, dtype=float) * factor
    if (
        points.ndim != 2
        or points.shape[1] != 3
        or len(points) < 2
        or centers.ndim != 2
        or centers.shape[1] != 3
        or not len(centers)
        or radii.shape != (len(centers),)
        or not all(np.isfinite(x).all() for x in (points, centers, radii))
        or np.any(radii < 0)
    ):
        raise ValueError('Invalid complete-segment/ball geometry')
    # Keep temporary segment/atom pairs bounded even on a longer reader path.
    batch = max(1, 262144 // len(centers))
    return min(
        float(
            np.min(
                _segments(points[i:-1][:batch], points[i + 1 :][:batch], centers, radii)
            )
        )
        for i in range(0, len(points) - 1, batch)
    )


def _model(input_file, protocol_file):
    payload = input_file.read_bytes()
    protocol_bytes = protocol_file.read_bytes()
    fixture, protocol = json.loads(payload), json.loads(protocol_bytes)
    if (
        protocol['schema'] != 'topomt.benchlab.straight-tube-protocol/1'
        or fixture['case_id'] != protocol['case']
        or hashlib.sha256(payload).hexdigest() != protocol['input_sha256']
        or protocol['length_unit'] != 'angstroms'
    ):
        raise ValueError('Frozen tube input/protocol identity differs')
    centers = _values(fixture['coordinates'], 'coordinates', 'angstroms')
    radii = _values(fixture['atom_radii'], 'atom_radii', 'angstroms')
    if (
        centers.ndim != 2
        or centers.shape[1] != 3
        or radii.shape != (len(centers),)
        or not len(centers)
        or not np.isfinite(centers).all()
        or not np.isfinite(radii).all()
        or np.any(radii < 0)
        or not np.all(radii == radii[0])
    ):
        raise ValueError('This bounded reference requires finite equal-radius balls')
    source_atoms = fixture['source_atom_indices']
    if len(source_atoms) != len(centers) or len(set(source_atoms)) != len(source_atoms):
        raise ValueError('The independent source-atom map must be one-to-one')
    grid = fixture['nominal_grid']
    if grid['axis_origin_angstroms'] != [0.0, 0.0, 0.0] or grid['axis_direction'] != [
        0.0,
        0.0,
        1.0,
    ]:
        raise ValueError('This tube bound uses the declared Cartesian +Z frame')
    return centers, radii, fixture, protocol, hashlib.sha256(protocol_bytes).hexdigest()


def model_reference(input_file: Path, protocol_file: Path) -> dict[str, Any]:
    """Compute independent axis clearance and a complete nominal-grid hull bound.

    Parameters
    ----------
    input_file, protocol_file : Path
        Frozen quantity-aware ball model and its preceding study protocol.

    Returns
    -------
    dict
        Explicit angstrom-valued axis and covering observations. The cover is
        sufficient for exclusion; failure of its bound proves no availability.

    Raises
    ------
    ValueError
        Input identity, equal-radius model or nominal grid is unsupported.
    """
    centers, radii, fixture, protocol, _ = _model(input_file, protocol_file)
    grid = fixture['nominal_grid']
    length, radius = grid['length_angstroms'], grid['radial_center_distance_angstroms']
    rings, angles = grid['n_rings'], grid['n_angles']
    if (
        type(rings) is not int
        or type(angles) is not int
        or rings < 2
        or angles < 3
        or rings * angles != len(centers)
        or not np.isfinite([length, radius]).all()
        or length <= 0
        or radius <= 0
    ):
        raise ValueError('Invalid complete nominal grid')
    z_values = np.linspace(-length / 2, length / 2, rings)
    theta = np.linspace(0.0, 2 * np.pi, angles, endpoint=False)
    nominal = np.array(
        [[radius * np.cos(a), radius * np.sin(a), z] for z in z_values for a in theta]
    )
    displacement = float(np.linalg.norm(centers - nominal, axis=1).max())
    radial_bound = float(np.linalg.norm(centers[:, :2], axis=1).max())
    z_bound = max(
        length / (2 * (rings - 1)), float(np.abs(centers[:, 2]).max()) - length / 2
    )
    radial_distance2 = max(
        radius**2,
        radial_bound**2
        + radius**2
        - 2 * radial_bound * radius * np.cos(np.pi / angles),
    )
    cover_bound = float(np.sqrt(radial_distance2 + z_bound**2) + displacement)
    distances = np.linalg.norm(centers[:, :2], axis=1) - radii
    nearest = int(np.argmin(distances))
    axis = float(distances[nearest])
    tolerance = protocol['path_reference']['decision_margin_angstroms']
    if not np.isfinite(tolerance) or tolerance <= 0:
        raise ValueError('A positive reference decision margin is required')
    probes = [row['probe_angstroms'] for row in protocol['selected_controls']]
    return {
        'length_unit': 'angstroms',
        'axis_clearance_angstroms': axis,
        'axis_limiting_source_atom': fixture['source_atom_indices'][nearest],
        'axis_limiting_point_angstroms': [0.0, 0.0, float(centers[nearest, 2])],
        'axis_clearance_is_global_bottleneck': False,
        'maximum_nominal_displacement_angstroms': displacement,
        'finite_hull_radial_bound_angstroms': radial_bound,
        'nearest_nominal_ring_z_bound_angstroms': z_bound,
        'finite_hull_cover_distance_bound_angstroms': cover_bound,
        'exclusion': {
            str(p): {
                'probe_angstroms': p,
                'coverage_margin_angstroms': float(radii.min() + p - cover_bound),
                'strictly_covered': bool(radii.min() + p - cover_bound > tolerance),
            }
            for p in probes
        },
        'proof': 'Hull convexity bounds radial norm and z; choose nearest nominal ring and angular column. Squared radial distance is convex in rho, so its maximum on [0,rho_max] is an endpoint. Add the measured maximum atom displacement by the triangle inequality. Every hull point is within this bound of an actual selected atomic center.',
    }


def _discover_path(centers, radii, controls):
    zs = np.asarray(controls['z_stations_angstroms'], dtype=float)
    axis = np.asarray(controls['xy_values_angstroms'], dtype=float)
    if (
        zs.ndim != 1
        or len(zs) < 2
        or np.any(np.diff(zs) <= 0)
        or not np.isfinite(zs).all()
        or axis.ndim != 1
        or not len(axis)
        or not np.isfinite(axis).all()
        or not np.any(axis == 0)
    ):
        raise ValueError('Invalid finite path-discovery grid')
    xy = np.array([[x, y] for x in axis for y in axis])
    layers = []
    for i, z in enumerate(zs):
        points = (
            np.array([[0.0, 0.0]])
            if i in (0, len(zs) - 1) or (z == 0 and controls['mandatory_origin'])
            else xy
        )
        layers.append(np.column_stack([points, np.full(len(points), z)]))
    points_used = sum(map(len, layers))
    if points_used > controls['maximum_points']:
        raise ValueError('Independent path point budget exhausted')
    scores = np.array([np.inf])
    history = []
    work = 0
    for previous, current in zip(layers[:-1], layers[1:], strict=True):
        next_scores = np.full(len(current), -np.inf)
        parent = np.full(len(current), -1, dtype=int)
        for j, point in enumerate(current):
            ids = np.flatnonzero(
                (
                    np.linalg.norm(previous[:, :2] - point[:2], axis=1)
                    <= controls['max_lateral_step_angstroms'] + 1e-12
                )
                & np.isfinite(scores)
            )
            # The first initial score is +infinity by definition of min-capacity.
            if len(previous) == 1 and np.isposinf(scores[0]):
                ids = (
                    np.array([0])
                    if np.linalg.norm(previous[0, :2] - point[:2])
                    <= controls['max_lateral_step_angstroms'] + 1e-12
                    else np.array([], dtype=int)
                )
            work += len(ids)
            if work > controls['maximum_edge_tests']:
                raise ValueError('Independent path edge budget exhausted')
            if not len(ids):
                continue
            clearance = _segments(
                previous[ids], np.repeat(point[None], len(ids), axis=0), centers, radii
            )
            values = np.minimum(scores[ids], clearance)
            choice = int(np.argmax(values))
            next_scores[j] = values[choice]
            parent[j] = ids[choice]
        scores = next_scores
        history.append(parent)
    if not np.isfinite(scores[0]):
        return {
            'status': 'unresolved',
            'length_unit': 'angstroms',
            'reason': 'No complete witness in the frozen grid',
            'work': {'points': points_used, 'edges': work},
        }
    chosen = [0]
    for parent in reversed(history):
        chosen.append(int(parent[chosen[-1]]))
    chosen.reverse()
    points = np.array(
        [layer[index] for layer, index in zip(layers, chosen, strict=True)]
    )
    return {
        'status': 'found',
        'length_unit': 'angstroms',
        'points_angstroms': points.tolist(),
        'minimum_clearance_angstroms': polyline_clearance(
            points, centers, radii, length_unit='angstroms'
        ),
        'work': {'points': points_used, 'edges': work},
        'scope': 'A finite-grid positive witness, not a globally optimal path or proof that other paths are absent',
    }


def build_reference(input_file: Path, protocol_file: Path) -> dict[str, Any]:
    """Discover one bounded path for independently checked receiving.

    Parameters
    ----------
    input_file, protocol_file : Path
        Unchanged quantity-aware input and preceding finite-grid protocol.

    Returns
    -------
    dict
        Fixed-angstrom candidate with input/protocol identity, path and work.
        A separate verifier must accept each whole segment and outward tail.

    Raises
    ------
    ValueError
        Input/model identity or the predeclared work limits are invalid/exhausted.
    """
    centers, radii, _, protocol, digest = _model(input_file, protocol_file)
    return {
        'schema': 'topomt.benchlab.straight-tube-reference/1',
        'length_unit': 'angstroms',
        'input_sha256': protocol['input_sha256'],
        'protocol_sha256': digest,
        'model_reference': model_reference(input_file, protocol_file),
        'path_candidate': _discover_path(centers, radii, protocol['path_reference']),
    }


def verify_reference(
    input_file: Path, protocol_file: Path, certificate: dict[str, Any]
) -> dict[str, Any]:
    """Verify context, complete segments and outward tails without searching.

    Parameters
    ----------
    input_file, protocol_file : Path
        Original input and its predeclared bounded study protocol.
    certificate : dict
        Retained path and geometric-bound candidate with explicit units.

    Returns
    -------
    dict
        Verified fixed-axis, selected-passage and finite-hull availability.
        Failure of a sufficient bound or witness is not a negative answer.

    Raises
    ------
    ValueError
        Units, identity, grid/support, clearance or budget context disagrees.
    """
    centers, radii, _, protocol, digest = _model(input_file, protocol_file)
    if (
        certificate['schema'] != 'topomt.benchlab.straight-tube-reference/1'
        or certificate.get('length_unit') != 'angstroms'
        or certificate['input_sha256'] != protocol['input_sha256']
        or certificate['protocol_sha256'] != digest
    ):
        raise ValueError('Tube reference certificate identity differs')
    model = model_reference(input_file, protocol_file)
    if certificate['model_reference'] != model:
        raise ValueError('Tube reference bound/axis observation differs')
    candidate = certificate['path_candidate']
    if candidate.get('length_unit') != 'angstroms':
        raise ValueError('Path certificate must retain its declared angstrom unit')
    minimum = None
    if candidate['status'] == 'found':
        points = np.asarray(candidate['points_angstroms'], dtype=float)
        controls = protocol['path_reference']
        zs = np.asarray(controls['z_stations_angstroms'])
        xy = np.asarray(controls['xy_values_angstroms'])
        if (
            points.shape != (len(zs), 3)
            or not np.isfinite(points).all()
            or not np.allclose(points[:, 2], zs, rtol=0, atol=1e-12)
        ):
            raise ValueError('Path stations differ from the frozen grid')
        if not np.allclose(points[[0, -1], :2], 0, rtol=0, atol=1e-12) or (
            controls['mandatory_origin']
            and not any(np.array_equal(point, [0.0, 0.0, 0.0]) for point in points)
        ):
            raise ValueError('Path endpoints/designated origin differ')
        if not np.isin(points[1:-1, :2], xy).all() or np.any(
            np.linalg.norm(np.diff(points[:, :2], axis=0), axis=1)
            > controls['max_lateral_step_angstroms'] + 1e-12
        ):
            raise ValueError('Path leaves the declared candidate grid')
        if points[0, 2] >= centers[:, 2].min() or points[-1, 2] <= centers[:, 2].max():
            raise ValueError('Path tails are not outward beyond every atom')
        minimum = polyline_clearance(points, centers, radii, length_unit='angstroms')
        if not np.isclose(
            minimum, candidate['minimum_clearance_angstroms'], rtol=0, atol=1e-12
        ):
            raise ValueError('Path clearance does not match complete segments')
        if (
            candidate['work']['points'] > controls['maximum_points']
            or candidate['work']['edges'] > controls['maximum_edge_tests']
        ):
            raise ValueError('Path discovery exceeds frozen budgets')
    elif candidate['status'] != 'unresolved':
        raise ValueError('Unknown path availability')
    tolerance = protocol['path_reference']['decision_margin_angstroms']
    rows = []
    for row in protocol['selected_controls']:
        probe = row['probe_angstroms']
        axis_delta = model['axis_clearance_angstroms'] - probe
        cover = model['exclusion'][str(probe)]
        rows.append(
            {
                'probe_angstroms': probe,
                'fixed_axis': 'clear'
                if axis_delta > tolerance
                else 'blocked'
                if axis_delta < -tolerance
                else 'marginal',
                'end_to_end_path': 'certified'
                if minimum is not None and minimum - probe > tolerance
                else 'not_established',
                'path_margin_angstroms': minimum - probe
                if minimum is not None
                else None,
                'finite_hull': 'strictly_covered'
                if cover['strictly_covered']
                else 'not_established',
            }
        )
    return {
        'schema': 'topomt.benchlab.straight-tube-verification/1',
        'length_unit': 'angstroms',
        'input_sha256': protocol['input_sha256'],
        'protocol_sha256': digest,
        'model_reference': model,
        'path_minimum_clearance_angstroms': minimum,
        'outward_tails': 'All centers lie between the two endpoint z planes; distance to every atom increases on the outward axial rays. Segment minima include endpoints.',
        'controls': rows,
        'scope': 'Checked known ball model, finite-grid passage witness and sufficient hull cover; no physical aperture area, global optimum bottleneck or biological claim',
    }
