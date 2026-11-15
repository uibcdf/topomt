"""Certified box-cover integration with explicit region labels and uncertainty.

The topology proof is checked separately. The trusted local bounds are exact
linear box ranges and spherical box-distance/convex-cover predicates. No center
sample classifies a whole box. Boundary boxes remain unresolved.
"""

import hashlib
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Optional

from ..model import (
    Box,
    Model,
    _record,
    decode_scalar,
    encode_scalar,
    point,
    record_digest,
)
from ..power_contracts import bounding_box, domain_planes
from ..volume_request import VolumeRequest
from .corner_volume import corner_bounds
from .geometry import cell_is_covered, cell_is_free, split, volume
from .power_cells import _locate


def _volume_kernel() -> dict[str, Any]:
    """Identify current integration semantics for same-kernel refinement."""
    root = Path(__file__).parents[1]
    names = sorted(str(p.relative_to(root)) for p in root.rglob('*.py'))
    return {
        'algorithm': 'certified-region-box-cover/1',
        'python_version': sys.version,
        'files': {
            n: hashlib.sha256((root / n).read_bytes()).hexdigest() for n in names
        },
    }


def _box_children(box: Box) -> tuple[Box, ...]:
    """Narrow the existing exact split contract without discarding a child."""
    result: list[Box] = []
    for child in split(box):
        if not isinstance(child, Box):
            raise ValueError('Box subdivision returned a non-box child')
        result.append(child)
    if len(result) != 8:
        raise ValueError('A box split must have eight children')
    return tuple(result)


def _leaf_state(
    model: Model, proof: dict[str, Any], topology: dict[str, Any], box: Box
) -> tuple[str, Optional[str]]:
    """Trusted exact local bounds; a whole free convex box has one region."""
    inside = True
    for plane in domain_planes(model):
        lower = (
            sum(
                n * (lo if n >= 0 else hi)
                for n, lo, hi in zip(plane[:3], box.lower, box.upper)
            )
            - plane[3]
        )
        upper = (
            sum(
                n * (hi if n >= 0 else lo)
                for n, lo, hi in zip(plane[:3], box.lower, box.upper)
            )
            - plane[3]
        )
        if lower > 0:
            return 'outside', None
        inside = inside and upper <= 0
    if any(cell_is_covered(model, box, a.source_id) for a in model.atoms):
        return 'blocked', None
    if inside and cell_is_free(model, box):
        center = point([(a + b) / 2 for a, b in zip(box.lower, box.upper)])
        return 'free', _locate(model, proof, topology, center)['region_id']
    return 'unknown', None


def _summarize(
    model: Model, cert: dict[str, Any], topology: dict[str, Any]
) -> dict[str, Any]:
    """Reconstruct complete box coverage and exact conservative allocations."""
    from . import verify

    request = VolumeRequest.from_record(cert['request'])
    ids = [r['region_id'] for r in topology['regions']]
    lower = {key: Fraction() for key in ids}
    unknown = Fraction()
    counts = {'free': 0, 'blocked': 0, 'outside': 0, 'unknown': 0}
    exact_shortcut = None
    method = cert['method']
    analytic_upper = {}
    if method == 'analytic_corner_regions':
        if len(ids) != 8 or cert['leaves'] or cert['analytic_certificate'] is None:
            raise ValueError('Boundary assignment requires eight complete regions')
        bounds = corner_bounds(model, cert['analytic_certificate'])
        lower = {key: bounds.lower / 8 for key in ids}
        analytic_upper = {key: bounds.upper / 8 for key in ids}
        total_upper = bounds.upper
    elif method == 'analytic_single_region':
        if len(ids) != 1 or cert['leaves'] or cert['analytic_certificate'] is None:
            raise ValueError('Analytic assignment requires exactly one proved region')
        analytic = cert['analytic_certificate']
        if analytic['request'] != cert['request']:
            raise ValueError('Analytic request differs from region request')
        checked = verify(model, analytic)
        if checked['kind'] != 'analytic_ball_union_volume':
            raise ValueError('Expected admitted analytic volume proof')
        lower[ids[0]] = decode_scalar(checked['volume_lower'])
        total_upper = decode_scalar(checked['volume_upper'])
    elif method == 'adaptive_boxes':
        if cert['analytic_certificate'] is not None:
            raise ValueError('Adaptive route cannot carry an unrelated analytic proof')
        paths = cert['leaves']
        limits = _record(cert['limits'], {'max_depth', 'max_leaves'})
        if (
            type(limits['max_depth']) is not int
            or not 0 <= limits['max_depth'] <= 24
            or limits['max_leaves'] != 4096
            or type(limits['max_leaves']) is not int
            or type(cert['step_leaf_ceiling']) is not int
            or not 1 <= cert['step_leaf_ceiling'] <= 4096
            or not isinstance(paths, list)
            or len(paths) > cert['step_leaf_ceiling']
        ):
            raise ValueError('Invalid integration envelope')
        if not ids:
            if paths:
                raise ValueError('Empty-topology shortcut must retain no partition')
        else:
            if (
                any(
                    not isinstance(p, str)
                    or len(p) > limits['max_depth']
                    or any(c not in '01234567' for c in p)
                    for p in paths
                )
                or paths != sorted(set(paths))
                or not paths
            ):
                raise ValueError('Invalid canonical integration leaf paths')
            leaves = set(paths)
            prefixes = {p[:i] for p in paths for i in range(len(p))}
            if prefixes & leaves:
                raise ValueError('Integration leaves overlap')
            todo = [('', bounding_box(model))]
            while todo:
                path, box = todo.pop()
                if path not in leaves:
                    if path not in prefixes:
                        raise ValueError('Integration partition omits part of the root')
                    todo.extend(
                        (path + str(i), b) for i, b in enumerate(_box_children(box))
                    )
                    continue
                state, region = _leaf_state(
                    model, cert['topology_certificate'], topology, box
                )
                counts[state] += 1
                if state == 'free':
                    if region is None or region not in lower:
                        raise ValueError('Invalid free-cell region assignment')
                    lower[region] += volume(box)
                elif state == 'unknown':
                    unknown += volume(box)
        total_upper = min(
            volume(model.domain), sum(lower.values(), Fraction()) + unknown
        )
        if not ids:
            exact_shortcut = 'complete_empty_topology'
        elif len(ids) == 1 and cell_is_free(model, model.domain):
            # This independent sufficient predicate covers the entire declared
            # convex domain, including portions of a root box outside a hull.
            lower[ids[0]] = volume(model.domain)
            unknown = Fraction()
            total_upper = volume(model.domain)
            exact_shortcut = 'whole_domain_free'
    else:
        raise ValueError('Unsupported region integration method')
    total_lower = sum(lower.values(), Fraction())
    regions = []
    for key in ids:
        upper = (
            analytic_upper[key]
            if method == 'analytic_corner_regions'
            else total_upper
            if method == 'analytic_single_region'
            else min(lower[key] + unknown, total_upper - (total_lower - lower[key]))
        )
        regions.append(
            {
                'region_id': key,
                'lower': encode_scalar(lower[key]),
                'upper': encode_scalar(upper),
                'precision_status': 'resolved'
                if request.satisfied(lower[key], upper)
                else 'unresolved',
            }
        )
    all_precision = request.satisfied(total_lower, total_upper) and all(
        r['precision_status'] == 'resolved' for r in regions
    )
    return {
        'model_sha256': model.digest,
        'certificate_sha256': record_digest(cert),
        'topology_certificate_sha256': record_digest(cert['topology_certificate']),
        'topology_complete': True,
        'topology_status': 'resolved',
        'n_components': len(ids),
        'n_boundary_patches': topology['n_boundary_patches'],
        'boundary_status': 'resolved',
        'per_region_volume_status': 'resolved',
        'volume_lower': encode_scalar(total_lower),
        'volume_upper': encode_scalar(total_upper),
        'volume_unit': 'nm**3',
        'regions': regions,
        'volume_enclosure_status': 'resolved',
        'total_precision_status': 'resolved'
        if request.satisfied(total_lower, total_upper)
        else 'unresolved',
        'precision_status': 'resolved' if all_precision else 'unresolved',
        'stop_reason': None
        if all_precision
        else 'analytic_precision_envelope'
        if method == 'analytic_corner_regions'
        else 'integration_envelope',
        'leaf_states': counts,
        'method': method,
        'exact_shortcut': exact_shortcut,
        'lineage_status': 'not_checked',
    }


def check_region_volume(
    model: Model, certificate: object, *, max_leaves: int = 4096
) -> dict[str, Any]:
    """Check topology, complete integration coverage and every region enclosure.

    Parameters
    ----------
    model : Model
        Original exact all-atom model.
    certificate : object
        Untrusted volume proof with complete topology and coverage.
    max_leaves : int
        Finite reader leaf ceiling, at most 4096.

    Returns
    -------
    dict
        Verified total/per-region enclosures and separate precision states.

    Raises
    ------
    ValueError
        Invalid model, geometry, proof, request, lineage or work envelope.
    """
    from . import verify

    cert = _record(
        certificate,
        {
            'schema',
            'kind',
            'model_sha256',
            'arithmetic',
            'method',
            'topology_certificate',
            'request',
            'limits',
            'step_leaf_ceiling',
            'leaves',
            'analytic_certificate',
            'parent_certificate_sha256',
            'kernel',
        },
    )
    if (
        cert['schema'] != 'topomt.reference-validator.certificate/1'
        or cert['kind'] != 'region_volume'
        or cert['model_sha256'] != model.digest
        or cert['arithmetic'] != 'rational-exact/1'
    ):
        raise ValueError('Region volume binding or convention differs')
    if (
        type(max_leaves) is not int
        or not 1 <= max_leaves <= 4096
        or not isinstance(cert['leaves'], list)
        or len(cert['leaves']) > max_leaves
    ):
        raise ValueError('Region checking exceeds its leaf envelope')
    topology = verify(model, cert['topology_certificate'])
    if topology['kind'] != 'power_cell_topology' or not topology['topology_complete']:
        raise ValueError('Region integration requires complete power-cell topology')
    return _summarize(model, cert, topology)


def check_volume_transition(
    model: Model, parent: object, child: object
) -> dict[str, Any]:
    """Check both proofs and same-request complete refinement, not just lineage labels.

    Parameters
    ----------
    model : Model
        Original numerical model.
    parent, child : object
        Full proofs with identical topology, request and source/kernel.

    Returns
    -------
    dict
        Rechecked child bounds with checked refinement lineage.

    Raises
    ------
    ValueError
        Invalid model, geometry, proof, request, lineage or work envelope.
    """
    before, after = (
        check_region_volume(model, parent),
        check_region_volume(model, child),
    )
    if not isinstance(parent, dict) or not isinstance(child, dict):
        raise ValueError('Refinement requires certificate records')
    if (
        child['parent_certificate_sha256'] != record_digest(parent)
        or any(
            child[k] != parent[k]
            for k in ['topology_certificate', 'request', 'limits', 'kernel', 'method']
        )
        or child['method'] != 'adaptive_boxes'
    ):
        raise ValueError('Region refinement changes source, method or request')
    for path in child['leaves']:
        if not any(path.startswith(old) for old in parent['leaves']):
            raise ValueError('Region refinement coarsens an earlier leaf')
    pairs = [
        (
            before['volume_lower'],
            after['volume_lower'],
            after['volume_upper'],
            before['volume_upper'],
        )
    ]
    pairs.extend(
        (a['lower'], b['lower'], b['upper'], a['upper'])
        for a, b in zip(before['regions'], after['regions'])
    )
    if any(
        not decode_scalar(a) <= decode_scalar(b) <= decode_scalar(c) <= decode_scalar(d)
        for a, b, c, d in pairs
    ):
        raise ValueError('Region bounds are not nested')
    return {**after, 'lineage_status': 'checked'}
