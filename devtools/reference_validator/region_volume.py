"""Produce bounded certified region volumes, with explicit unmet precision."""

import hashlib
import os
from copy import deepcopy
from fractions import Fraction
from heapq import heappop, heappush
from pathlib import Path
from typing import Any, Literal

from .analytic_volume import volume_certificate
from .model import Model, _record, record_digest
from .power_contracts import bounding_box
from .storage import _encode_record, read_record_with_digest
from .verify import verify
from .verify.corner_volume import corner_bounds
from .verify.geometry import cell_is_free, volume
from .verify.region_volume import (
    _box_children,
    _leaf_state,
    _volume_kernel,
    check_region_volume,
)
from .volume_request import VolumeRequest


def _refine(
    model: Model, cert: dict[str, Any], topology: dict[str, Any], ceiling: int
) -> dict[str, Any]:
    if type(ceiling) is not int or not 1 <= ceiling <= 4096:
        raise ValueError('Integration requires a finite leaf ceiling in 1..4096')
    cert['step_leaf_ceiling'] = ceiling
    if not topology['regions']:
        cert['leaves'] = []
        return cert
    root = bounding_box(model)
    boxes = {}
    for path in cert['leaves']:
        box = root
        for digit in path:
            box = _box_children(box)[int(digit)]
        boxes[path] = box
    states = {
        p: _leaf_state(model, cert['topology_certificate'], topology, b)
        for p, b in boxes.items()
    }
    candidates: list[tuple[Fraction, str]] = []
    for p, b in boxes.items():
        if states[p][0] == 'unknown' and len(p) < cert['limits']['max_depth']:
            heappush(candidates, (-volume(b), p))
    # This ledger guides producer search only. The independent reader still
    # reconstructs coverage, classifications and all region allocations.
    request = VolumeRequest.from_record(cert['request'])
    lower = {r['region_id']: Fraction() for r in topology['regions']}
    unknown = Fraction()
    domain_volume = volume(model.domain)
    whole_free = len(lower) == 1 and cell_is_free(model, model.domain)

    def update(box, state, sign):
        nonlocal unknown
        kind, region = state
        if kind == 'free':
            if region not in lower:
                raise ValueError('Invalid producer region assignment')
            lower[region] += sign * volume(box)
        elif kind == 'unknown':
            unknown += sign * volume(box)

    for path, box in boxes.items():
        update(box, states[path], 1)

    def satisfied():
        if whole_free:
            return request.satisfied(domain_volume, domain_volume)
        total_lower = sum(lower.values(), Fraction())
        total_upper = min(domain_volume, total_lower + unknown)
        return request.satisfied(total_lower, total_upper) and all(
            request.satisfied(
                value, min(value + unknown, total_upper - (total_lower - value))
            )
            for value in lower.values()
        )

    next_check = len(boxes)
    while True:
        if len(boxes) >= next_check:
            if satisfied():
                break
            next_check = max(next_check + 1, 2 * next_check)
        if not candidates or len(boxes) + 7 > ceiling:
            break
        _, path = heappop(candidates)
        box = boxes.pop(path)
        update(box, states.pop(path), -1)
        for i, b in enumerate(_box_children(box)):
            key = path + str(i)
            boxes[key] = b
            states[key] = _leaf_state(model, cert['topology_certificate'], topology, b)
            update(b, states[key], 1)
            if states[key][0] == 'unknown' and len(key) < cert['limits']['max_depth']:
                heappush(candidates, (-volume(b), key))
    cert['leaves'] = sorted(boxes)
    return cert


def region_volume_certificate(
    model: Model,
    topology_certificate: object,
    request: VolumeRequest,
    *,
    max_leaves: int = 4096,
    max_depth: int = 24,
    method: Literal[
        'adaptive_boxes', 'analytic_single_region', 'analytic_corner_regions'
    ] = 'adaptive_boxes',
) -> dict[str, Any]:
    """Propose certified total/region bounds under a finite integration envelope.

    Parameters
    ----------
    model : Model
        Frozen all-atom numerical model and convex domain.
    topology_certificate : object
        Complete power-cell proof; independently checked before labeling.
    request : VolumeRequest
        Required absolute and/or relative volume precision.
    max_leaves : int
        Finite frontier ceiling for this step, at most 4096.
    max_depth : int
        Fixed subdivision depth ceiling, at most 24.
    method : str
        Adaptive box bounds, contained-ball single-region assignment, or
        the admitted symmetric eight-corner boundary integral.

    Returns
    -------
    dict
        Unverified volume proof; requested precision may remain unresolved.

    Raises
    ------
    ValueError
        Invalid model, geometry, proof, request, lineage or work envelope.
    """
    if type(max_leaves) is not int or not 1 <= max_leaves <= 4096:
        raise ValueError('Integration requires a leaf ceiling in 1..4096')
    if type(max_depth) is not int or not 0 <= max_depth <= 24:
        raise ValueError('Integration depth must be in 0..24')
    proof = deepcopy(topology_certificate)
    topology = verify(model, proof)
    if topology['kind'] != 'power_cell_topology':
        raise ValueError('Complete power-cell topology required')
    cert = {
        'schema': 'topomt.reference-validator.certificate/1',
        'kind': 'region_volume',
        'model_sha256': model.digest,
        'arithmetic': 'rational-exact/1',
        'method': method,
        'topology_certificate': proof,
        'request': request.to_record(),
        'limits': {'max_depth': max_depth, 'max_leaves': 4096},
        'step_leaf_ceiling': max_leaves,
        'leaves': [''],
        'analytic_certificate': None,
        'parent_certificate_sha256': None,
        'kernel': _volume_kernel(),
    }
    if method == 'analytic_corner_regions':
        if len(topology['regions']) != 8:
            raise ValueError('Boundary assignment requires eight complete regions')
        cert['leaves'] = []
        for bits in [64, 128, 256, 512, 1024, 2048]:
            cert['analytic_certificate'] = {'scheme': 'cube-cap-wedge/1', 'bits': bits}
            bounds = corner_bounds(model, cert['analytic_certificate'])
            if request.satisfied(bounds.lower, bounds.upper):
                break
            if request.absolute_nm3 == 0 or request.relative == 0:
                break
        return cert
    if method == 'analytic_single_region':
        if len(topology['regions']) != 1:
            raise ValueError('Analytic assignment needs one complete region')
        cert['leaves'] = []
        cert['analytic_certificate'] = volume_certificate(model, request)
        return cert
    if method != 'adaptive_boxes':
        raise ValueError('Unsupported integration method')
    return _refine(model, cert, topology, max_leaves)


def refine_region_volume(
    model: Model, certificate: object, *, max_leaves: int = 4096
) -> dict[str, Any]:
    """Recheck saved coverage and continue only the same source/request kernel.

    Parameters
    ----------
    model : Model
        Same frozen numerical model.
    certificate : object
        Complete saved volume proof with the same source/kernel/request.
    max_leaves : int
        New operational step ceiling within the fixed 4096-leaf envelope.

    Returns
    -------
    dict
        Refined proof preserving the parent digest and all remaining uncertainty.

    Raises
    ------
    ValueError
        Invalid model, geometry, proof, request, lineage or work envelope.
    """
    check_region_volume(model, certificate)
    if not isinstance(certificate, dict):
        raise ValueError('Region volume must be a record')
    if (
        certificate['kernel'] != _volume_kernel()
        or certificate['method'] != 'adaptive_boxes'
    ):
        raise ValueError('Refinement requires the same adaptive integration kernel')
    if max_leaves < len(certificate['leaves']):
        raise ValueError('Cannot coarsen the saved partition')
    cert = deepcopy(certificate)
    cert['parent_certificate_sha256'] = record_digest(certificate)
    return _refine(model, cert, verify(model, cert['topology_certificate']), max_leaves)


def save_region_bundle(directory: Path, model: Model, certificate: object) -> None:
    """Independently verify and publish an exclusive manifest-last volume bundle.

    Parameters
    ----------
    directory : Path
        Exclusive new bundle directory.
    model : Model
        Original numerical model.
    certificate : object
        Proof to detach and independently verify before writing.

    Returns
    -------
    None
        Write Model/proof and then the checksum commit manifest.

    Raises
    ------
    ValueError
        Invalid model, geometry, proof, request, lineage or work envelope.
    """
    saved = deepcopy(certificate)
    check_region_volume(model, saved)
    payloads = {
        name: _encode_record(value)
        for name, value in [
            ('model.json', model.to_record()),
            ('certificate.json', saved),
        ]
    }
    files = {n: hashlib.sha256(p).hexdigest() for n, p in payloads.items()}
    manifest = _encode_record(
        {'schema': 'topomt.reference-validator.region-bundle/1', 'files': files}
    )
    directory.mkdir(parents=True, exist_ok=False)
    for name, payload in payloads.items():
        with (directory / name).open('xb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    with (directory / 'MANIFEST.json').open('xb') as stream:
        stream.write(manifest)
        stream.flush()
        os.fsync(stream.fileno())


def load_region_bundle(directory: Path, model: Model) -> dict[str, Any]:
    """Read precisely the hashed records and independently recheck saved bounds.

    Parameters
    ----------
    directory : Path
        Complete manifest-backed saved bundle.
    model : Model
        Original exact model to match and check.

    Returns
    -------
    dict
        Independently checked proof from precisely the hashed bytes.

    Raises
    ------
    ValueError
        Invalid model, geometry, proof, request, lineage or work envelope.
    """
    try:
        manifest, _ = read_record_with_digest(directory / 'MANIFEST.json')
        manifest = _record(manifest, {'schema', 'files'})
        if manifest['schema'] != 'topomt.reference-validator.region-bundle/1':
            raise ValueError('Unsupported region bundle')
        files = _record(manifest['files'], {'model.json', 'certificate.json'})
        records = {}
        for name, digest in files.items():
            value, actual = read_record_with_digest(directory / name)
            if actual != digest:
                raise ValueError('Region bundle digest differs')
            records[name] = value
        if records['model.json'] != model.to_record():
            raise ValueError('Region bundle model differs')
        check_region_volume(model, records['certificate.json'])
        return records['certificate.json']
    except OSError as exc:
        raise ValueError('Incomplete region bundle') from exc
