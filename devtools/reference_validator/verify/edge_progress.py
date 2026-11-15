"""Independent reconstruction of saved canonical analytic edge work."""

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from ..model import (
    Model,
    _record,
    decode_scalar,
    encode_point,
    encode_scalar,
    record_digest,
)
from ..volume_request import VolumeRequest
from ._interval import _Interval
from .edge_volume import assigned_faces, exact_result, prepare, triangle_flux

BUNDLE_SCHEMA = 'topomt.reference-validator.edge-work-bundle/1'
WORK_SCHEMA = 'topomt.reference-validator.edge-work/1'


def kernel_identity() -> dict[str, Any]:
    """Fingerprint the numerical checker, task transport and persistence path."""
    root = Path(__file__).parents[1]
    names = (
        'model.py',
        'hull_model.py',
        'contracts.py',
        'power_contracts.py',
        'volume_request.py',
        'parallel.py',
        'edge_tasks.py',
        'storage.py',
        'verify/__init__.py',
        'verify/geometry.py',
        'verify/center_hull.py',
        'verify/polytope.py',
        'verify/power_cells.py',
        'verify/edge_volume.py',
        'verify/edge_math.py',
        'verify/boundary_volume.py',
        'verify/corner_volume.py',
        'verify/_interval.py',
        'verify/edge_progress.py',
    )
    return {
        'algorithm': 'canonical-edge-work/1',
        'python_version': sys.version,
        'files': {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in names
        },
    }


@dataclass(frozen=True)
class _Plan:
    certificate_json: str
    checked_json: str
    request: VolumeRequest
    bits: int
    pieces: tuple
    exact_json: Optional[str]
    kernel_json: str
    frontier_sha256: str
    task_ids: tuple[str, ...]
    model_sha256: str


def prepare_work(model: Model, certificate: object) -> _Plan:
    """Admit all geometry once; freeze a complete, nonadaptive signed frontier."""
    cert, checked, request = prepare(model, certificate)
    exact = exact_result(model, checked, request, cert['bits'])
    pieces = (
        tuple(assigned_faces(model, cert['topology_certificate'], checked))
        if exact is None
        else ()
    )
    frontier = record_digest(
        {
            'length_unit': 'nm',
            'pieces': [
                {
                    'center': encode_point(c),
                    'radius': encode_scalar(r),
                    'triangle': [encode_point(p) for p in tri],
                    'region_id': region,
                }
                for c, r, tri, region in pieces
            ],
        }
    )
    kernel = kernel_identity()
    model_sha = model.digest
    binding = record_digest(
        {
            'model_sha256': model_sha,
            'certificate_sha256': record_digest(cert),
            'kernel': kernel,
            'frontier_sha256': frontier,
        }
    )
    ids = tuple(
        record_digest({'binding': binding, 'piece_index': i})
        for i in range(len(pieces))
    )
    return _Plan(
        json.dumps(cert, sort_keys=True),
        json.dumps(checked, sort_keys=True),
        request,
        cert['bits'],
        pieces,
        None if exact is None else json.dumps(exact, sort_keys=True),
        json.dumps(kernel, sort_keys=True),
        frontier,
        ids,
        model_sha,
    )


def encode_bound(bound: _Interval) -> dict:
    """Retain signed rational endpoints and their explicit canonical volume unit."""
    return {
        'lower': encode_scalar(bound.lower),
        'upper': encode_scalar(bound.upper),
        'unit': 'nm**3',
    }


def _restore_progress(
    model: Model, progress: object
) -> tuple[_Plan, dict[int, _Interval]]:
    state = _record(
        progress,
        {
            'schema',
            'model_sha256',
            'certificate',
            'kernel',
            'frontier_sha256',
            'items',
            'stop_reason',
        },
    )
    plan = prepare_work(model, state['certificate'])
    if (
        state['schema'] != WORK_SCHEMA
        or state['model_sha256'] != plan.model_sha256
        or state['kernel'] != json.loads(plan.kernel_json)
        or state['frontier_sha256'] != plan.frontier_sha256
        or not isinstance(state['items'], list)
        or len(state['items']) > len(plan.pieces)
    ):
        raise ValueError('Edge work model, kernel or frontier differs')
    done: dict[int, _Interval] = {}
    for item in state['items']:
        row = _record(item, {'piece_index', 'task_sha256', 'bound'})
        i = row['piece_index']
        if (
            type(i) is not int
            or not 0 <= i < len(plan.pieces)
            or i in done
            or row['task_sha256'] != plan.task_ids[i]
        ):
            raise ValueError('Invalid or repeated edge task identity')
        raw = _record(row['bound'], {'lower', 'upper', 'unit'})
        if raw['unit'] != 'nm**3':
            raise ValueError('Edge bound requires explicit nm**3')
        bound = _Interval(decode_scalar(raw['lower']), decode_scalar(raw['upper']))
        c, r, tri, _ = plan.pieces[i]
        expected = triangle_flux(c, r, tri, plan.bits)
        if bound != expected:
            raise ValueError('Saved edge bound differs from independent reconstruction')
        done[i] = expected
    if (
        list(done) != sorted(done)
        or state['stop_reason']
        not in {'piece_budget', 'cancelled', 'failed', 'pieces_complete'}
        or (state['stop_reason'] == 'pieces_complete')
        != (len(done) == len(plan.pieces))
    ):
        raise ValueError('Edge work order or stopping state differs')
    return plan, done


def check_progress(model: Model, progress: object) -> dict[str, Any]:
    """Recompute every stored contribution without importing a producer or pool.

    Parameters
    ----------
    model : Model
        Original complete numerical model in nm.
    progress : object
        Untrusted source-bound frontier and signed arithmetic contributions.

    Returns
    -------
    dict
        Work inventory; partial arithmetic is never a whole-domain enclosure.

    Raises
    ------
    ValueError, ArithmeticError
        Wrong bindings/units, duplicate tasks, bad geometry or false bounds.
    """
    plan, done = _restore_progress(model, progress)
    return {
        'model_sha256': plan.model_sha256,
        'completed_pieces': len(done),
        'required_pieces': len(plan.pieces),
        'work_complete': len(done) == len(plan.pieces),
        'volume_enclosure_status': 'not_computed',
        'precision_status': 'not_computed',
    }
