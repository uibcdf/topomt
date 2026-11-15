"""Propose certified analytic edge integration on complete original power cells."""

from copy import deepcopy
from typing import Any

from .model import Model
from .verify import verify
from .verify.edge_volume import BITS, SCHEME, evaluate
from .volume_request import VolumeRequest


def edge_volume_proposal(
    model: Model,
    topology_certificate: object,
    request: VolumeRequest,
    *,
    bits: int = 128,
) -> dict[str, Any]:
    """Prepare an unverified symbolic job without executing its integral.

    Parameters
    ----------
    model : Model
        Exact Model to bind; its immutable digest is retained.
    topology_certificate : object
        Untrusted topology to detach. Every geometric claim is checked by the
        independent reader, not accepted during this data-preparation step.
    request : VolumeRequest
        Original total/per-region precision requirements.
    bits : int
        Explicit finite dyadic precision from the admitted ladder.

    Returns
    -------
    dict
        Unverified certificate proposal. No completion or precision status is
        supplied; only a successful independent read can supply those states.

    Raises
    ------
    ValueError
        Invalid arithmetic selection. Bad geometric input is rejected by the
        reader and never acquires a physical interpretation from this proposal.
    """
    if type(bits) is not int or bits not in BITS:
        raise ValueError('Unsupported dyadic precision')
    return {
        'schema': 'topomt.reference-validator.certificate/1',
        'kind': 'power_edge_volume',
        'model_sha256': model.digest,
        'arithmetic': 'rational-exact/1',
        'topology_certificate': deepcopy(topology_certificate),
        'request': request.to_record(),
        'scheme': SCHEME,
        'bits': bits,
    }


def edge_volume_certificate(
    model: Model,
    topology_certificate: object,
    request: VolumeRequest,
    *,
    max_bits: int = 512,
) -> dict[str, Any]:
    """Select finite outward arithmetic precision without changing the request.

    Parameters
    ----------
    model : Model
        Frozen original numerical model in nm.
    topology_certificate : object
        Complete untrusted power-cell proof, independently checked on entry.
    request : VolumeRequest
        Absolute and relative requirements for total and each region volume.
    max_bits : int
        Finite ceiling among 64, 128, 256, 512, 1024, 2048 dyadic bits.

    Returns
    -------
    dict
        Proposed standalone proof. Fresh checking supplies precision status.

    Raises
    ------
    ValueError, ArithmeticError
        Invalid model, topology, work policy or insufficient numerical envelope.
    """
    if type(max_bits) is not int or max_bits not in BITS:
        raise ValueError('Unsupported maximum dyadic precision')
    proof = deepcopy(topology_certificate)
    checked = verify(model, proof)
    if not isinstance(proof, dict) or checked['kind'] != 'power_cell_topology':
        raise ValueError('Complete power-cell topology is required')
    cert = edge_volume_proposal(model, proof, request, bits=64)
    last = None
    for bits in BITS:
        if bits > max_bits:
            break
        cert['bits'] = bits
        try:
            result = evaluate(model, proof, checked, request, bits)
        except ArithmeticError as exc:
            last = exc
            continue
        last = None
        if result['precision_status'] == 'resolved':
            break
        if request.absolute_nm3 == 0 or request.relative == 0:
            break
    if last is not None:
        raise last
    return cert
