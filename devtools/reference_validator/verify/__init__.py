"""Independent bounded certificate checking; never imports producer search."""

import hashlib
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from ..model import (
    Box,
    Model,
    _record,
    decode_point,
    encode_scalar,
    record_digest,
)
from .geometry import (
    cell_is_covered,
    cell_is_free,
    contains,
    point_is_free,
    segment_is_free,
    split,
    volume,
)


@dataclass(frozen=True)
class Limits:
    """Explicit checker work limits; these do not change the physical model."""

    max_atoms: int = 512
    max_leaves: int = 4096
    max_depth: int = 24
    max_path_points: int = 4096

    def __post_init__(self) -> None:
        if any(type(v) is not int or v < 1 for v in vars(self).values()):
            raise ValueError('Checker limits must be positive integers')


def _partition(model: Model, cert: dict[str, Any], limits: Limits) -> dict[str, Any]:
    leaves = cert['leaves']
    if not isinstance(leaves, list) or not 1 <= len(leaves) <= limits.max_leaves:
        raise ValueError('Invalid leaf count or checker leaf budget exceeded')
    refinement = _record(cert['refinement'], {'max_depth', 'max_leaves'})
    if (
        type(refinement['max_depth']) is not int
        or refinement['max_depth'] < 0
        or type(refinement['max_leaves']) is not int
        or refinement['max_leaves'] < 1
    ):
        raise ValueError('Invalid producer refinement request')
    by_path = {}
    arity = 8 if isinstance(model.domain, Box) else 2
    for leaf in leaves:
        if not isinstance(leaf, dict):
            raise ValueError('Leaf must be a record')
        state = leaf.get('state')
        _record(
            leaf,
            {'path', 'state', 'atom_id'} if state == 'blocked' else {'path', 'state'},
        )
        if state not in {'blocked', 'free', 'unknown'}:
            raise ValueError('Unknown leaf state')
        path = leaf['path']
        if (
            not isinstance(path, str)
            or len(path) > limits.max_depth
            or any(c not in '01234567'[:arity] for c in path)
            or path in by_path
        ):
            raise ValueError('Invalid, duplicate or over-budget leaf path')
        if len(path) > refinement['max_depth']:
            raise ValueError('Leaf exceeds recorded producer depth')
        if state == 'blocked' and type(leaf['atom_id']) is not int:
            raise ValueError('Covering atom ID must be an integer')
        by_path[path] = leaf
    if len(leaves) > refinement['max_leaves']:
        raise ValueError('Leaves exceed recorded producer count')
    prefixes = {path[:i] for path in by_path for i in range(len(path))}
    if prefixes.intersection(by_path):
        raise ValueError('Ancestor and descendant leaves overlap')
    # A complete tree must provide every child of each internal node. This
    # checks coverage without trusting a producer's volume sum or leaf count.
    for prefix in prefixes:
        if any(
            prefix + str(i) not in prefixes and prefix + str(i) not in by_path
            for i in range(arity)
        ):
            raise ValueError('Partition omits a child region')
    lower, upper = Fraction(), Fraction()
    states = set()
    stack = [('', model.domain)]
    while stack:
        path, cell = stack.pop()
        if path not in by_path:
            if path not in prefixes:
                raise ValueError('Partition does not cover root')
            stack.extend((path + str(i), child) for i, child in enumerate(split(cell)))
            continue
        leaf = by_path[path]
        state = leaf['state']
        states.add(state)
        if state == 'blocked':
            if not cell_is_covered(model, cell, leaf['atom_id']):
                raise ValueError('Claimed full-cell cover is false')
        elif state == 'free':
            if not cell_is_free(model, cell):
                raise ValueError('Claimed full-cell availability is unproved')
            lower += volume(cell)
            upper += volume(cell)
        else:
            upper += volume(cell)
    # These two finite convex-domain cases have complete proofs. No general
    # component count is inferred from mixed/unknown leaves or small error.
    count = 0 if states == {'blocked'} else 1 if states == {'free'} else None
    return {
        'volume_lower': encode_scalar(lower),
        'volume_upper': encode_scalar(upper),
        'volume_unit': 'nm**3',
        'volume_enclosure_status': 'resolved',
        'precision_status': 'not_requested',
        'n_components': count,
        'topology_complete': count is not None,
        'topology_status': 'resolved' if count is not None else 'unresolved',
        'unresolved_leaves': sum(leaf['state'] == 'unknown' for leaf in leaves),
    }


def verify(
    model: Model, certificate: object, *, limits: Limits = Limits()
) -> dict[str, Any]:
    """Check a selected certificate independently of its production/search.

    Parameters
    ----------
    model : Model
        Original immutable numerical model in nm.
    certificate : object
        Portable partition, path or point proof record.
    limits : Limits
        Explicit work ceilings. Exceeding them rejects checking; it never
        supplies a negative geometric answer.

    Returns
    -------
    dict
        Checked model/certificate identities and the proved finite observations.
        An accepted partition can still have unknown topology/volume precision.

    Raises
    ------
    ValueError
        A proof, binding, schema, convention or work limit is invalid.
    """
    if len(model.atoms) > limits.max_atoms:
        raise ValueError('Checker atom budget exceeded')
    if not isinstance(certificate, dict):
        raise ValueError('Certificate must be a record')
    common = {'schema', 'kind', 'model_sha256', 'arithmetic'}
    kind = certificate.get('kind')
    if kind == 'partition':
        extra = {'leaves', 'refinement'}
    elif kind == 'path':
        extra = {'points'}
    elif kind == 'point':
        extra = {'point', 'claim'}
    else:
        raise ValueError('Unsupported certificate kind')
    cert = _record(certificate, common | extra)
    if (
        cert['schema'] != 'topomt.reference-validator.certificate/1'
        or cert['arithmetic'] != 'rational-exact/1'
        or cert['model_sha256'] != model.digest
    ):
        raise ValueError('Certificate schema, arithmetic or model binding differs')
    result: dict[str, Any] = {
        'schema': 'topomt.reference-validator.verification/1',
        'verification_status': 'accepted',
        'kind': kind,
        'model_sha256': model.digest,
        'certificate_sha256': record_digest(cert),
        'trusted_arithmetic': 'stdlib-fraction/1',
        'topology_complete': False,
        'n_components': None,
        'topology_status': 'not_computed',
        'python_version': sys.version,
        'verifier_files_sha256': {
            name: hashlib.sha256(
                (Path(__file__).parents[1] / name).read_bytes()
            ).hexdigest()
            for name in ('model.py', 'verify/__init__.py', 'verify/geometry.py')
        },
    }
    if kind == 'partition':
        result.update(_partition(model, cert, limits))
    elif kind == 'path':
        raw_points = cert['points']
        if (
            not isinstance(raw_points, list)
            or not 2 <= len(raw_points) <= limits.max_path_points
        ):
            raise ValueError('Invalid path or path-point budget exceeded')
        points = [decode_point(p) for p in raw_points]
        if not all(segment_is_free(model, a, b) for a, b in zip(points, points[1:])):
            raise ValueError('Path collides or leaves its declared domain')
        result['path_validated'] = True
        result['connectivity_status'] = 'resolved'
        result['connected'] = True
    else:
        x = decode_point(cert['point'])
        state = (
            'outside_domain'
            if not contains(model.domain, x)
            else 'free'
            if point_is_free(model, x)
            else 'blocked'
        )
        if cert['claim'] != state:
            raise ValueError('Point claim does not match exact all-atom geometry')
        result['point_state'] = state
        result['occupancy_status'] = 'resolved'
    return result
