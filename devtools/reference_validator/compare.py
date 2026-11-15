"""Compare explicit native spatial supports with checked physical references.

All numbers belong to the same exact numerical Model. Local candidate reporting
does not acquire a physical guarantee or morphological label from this report.
"""

from copy import deepcopy
from fractions import Fraction
from typing import Any, Optional

from .model import Model, encode_point, point, record_digest
from .verify import verify
from .verify.geometry import _squared, contains, segment_is_free
from .verify.power_cells import query_anchors


def compare_reference_claims(
    model: Model,
    topology_certificate: object,
    *,
    native_model: Model,
    points: dict[str, tuple[Fraction, Fraction, Fraction]],
    paths: dict[str, list[tuple[Fraction, Fraction, Fraction]]],
    carrier_tetrahedra: Optional[dict[str, list[list[int]]]] = None,
) -> dict[str, Any]:
    """Compare bounded point/path supports and source-tetrahedron carrier unions.

    Parameters
    ----------
    model : Model
        Reference numerical model; all coordinates are exact nm.
    topology_certificate : object
        Complete independently checked power-cell proof.
    native_model : Model
        Explicit captured model attached to the native supports; must match.
    points : dict
        At most 32 named exact probe-center positions.
    paths : dict
        At most 32 paths, each with 2..256 exact vertices.
    carrier_tetrahedra : dict or None
        At most 32 named unions, each with at most 512 source tetrahedra.

    Returns
    -------
    dict
        Scoped physical support checks, with no inferred morphology or solver error.

    Raises
    ------
    ValueError
        Invalid model, geometry, proof, request, lineage or work envelope.
    """
    if model.to_record() != native_model.to_record():
        raise ValueError('Native and reference numerical models differ')
    if len(points) > 32 or len(paths) > 32:
        raise ValueError('Comparison exceeds the bounded point/path envelope')
    if not isinstance(topology_certificate, dict):
        raise ValueError('Comparison requires a topology record')
    query = query_anchors(model, topology_certificate, anchors=points, pairs=[])
    checked = verify(model, topology_certificate)
    path_results = {}
    for name, vertices in paths.items():
        if not isinstance(name, str) or not name or not 2 <= len(vertices) <= 256:
            raise ValueError('Invalid path support or path-point envelope')
        received = [point(x) for x in vertices]
        clear = all(
            segment_is_free(model, a, b) for a, b in zip(received, received[1:])
        )
        path_results[name] = {
            'all_atom_free': clear,
            'domain': 'whole_declared_convex_domain',
            'native_carrier_coverage': 'not_checked',
            'segment_count': len(received) - 1,
            'points': [encode_point(x) for x in received],
            'length_unit': 'nm',
        }
    carriers = {}
    atoms = {a.source_id: a for a in model.atoms}
    if carrier_tetrahedra is None:
        carrier_tetrahedra = {}
    if len(carrier_tetrahedra) > 32:
        raise ValueError('Comparison exceeds the carrier envelope')
    for name, rows in carrier_tetrahedra.items():
        if not isinstance(name, str) or not name or not 1 <= len(rows) <= 512:
            raise ValueError('Invalid carrier inventory')
        cells = []
        for ids in rows:
            if (
                len(ids) != 4
                or any(type(i) is not int or i not in atoms for i in ids)
                or len(set(ids)) != 4
            ):
                raise ValueError('Carrier tetrahedron has invalid source identities')
            carrier_vertices = tuple(atoms[i].center for i in ids)
            if not all(contains(model.domain, x) for x in carrier_vertices):
                raise ValueError(
                    'Carrier support is not contained in the reference domain'
                )
            # Vertex containment proves containment of their convex hull even
            # for a flat carrier. No full-dimensional carrier Model is needed
            # for this sufficient exclusion statement.
            cells.append(carrier_vertices)
        empty = checked['n_components'] == 0 or all(
            any(
                all(
                    _squared(v, a.center) <= (a.radius + model.probe) ** 2 for v in cell
                )
                for a in model.atoms
            )
            for cell in cells
        )
        carriers[name] = {
            'physical_state': 'empty' if empty else 'unresolved',
            'proof_route': 'whole_domain_exclusion'
            if checked['n_components'] == 0
            else 'whole_tetrahedron_covers'
            if empty
            else 'no_complete_carrier_proof',
            'source_tetrahedra': deepcopy(rows),
            'domain_containment': 'verified_by_convexity',
        }
    return {
        'schema': 'topomt.reference-validator.spatial-comparison/1',
        'model_sha256': model.digest,
        'topology_certificate_sha256': record_digest(topology_certificate),
        'numerical_model_match': 'exact',
        'length_unit': 'nm',
        'reference_region_count': checked['n_components'],
        'reference_boundary_patch_count': checked['n_boundary_patches'],
        'reference_boundary_incidence': checked['boundary_patches'],
        'points': query['locations'],
        'paths': path_results,
        'carriers': carriers,
        'morphology_status': 'not_inferred',
        'native_algorithm_correctness': 'not_inferred_from_local_support_checks',
    }
