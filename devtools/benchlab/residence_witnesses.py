"""Inspect local residence centers without changing DFND or certifying regions.

This bounded study diagnostic compares the stored center with its four local
obstacles and the complete captured atom population. A blocked center does not
exclude a different free point, a physical component or a path in its carrier.
Independent region-cover/path references retain those responsibilities.
"""

from typing import Any

import numpy as np
import pyunitwizard as puw
from pyunitwizard import QuantityRecord


def _check_unit(raw: dict, field: str, target: str) -> None:
    unit = raw['units'][field]
    quantity = (
        puw.quantity(1, unit)
        if isinstance(unit, str)
        else QuantityRecord.from_dict(unit).to_quantity(field=field, unit=target)
    )
    if float(puw.get_value(quantity, to_unit=target)) != 1.0:
        raise ValueError('Raw values do not use the declared fixed-unit schema')


def inspect_residence_witnesses(
    topography: Any, *, max_pairs: int = 250_000
) -> dict[str, Any]:
    """Compare each resident center with local and all captured atom obstacles.

    Parameters
    ----------
    topography : topomt.Topography
        Actual DFND result with its captured input context. Authored or saved
        diagnostic controls may supply the same raw/context fields explicitly;
        they do not thereby become executed public receiving evidence.
    max_pairs : int, default 250000
        Work ceiling on resident-center/atom comparisons. Centers are inspected
        sequentially, using temporary storage linear in the input atom count.

    Returns
    -------
    dict
        Detached fixed-nm point observations, component/source references,
        dimensionless barycentric weights and explicit limits. Strict physical
        clearance uses the nominal probe and the captured numerical epsilon,
        independently of local residence/permeability admission tolerances.

    Raises
    ------
    ValueError
        Geometry, source mapping, units or declared work budget is invalid.

    Examples
    --------
    >>> # report = inspect_residence_witnesses(topo)
    >>> # report['component_existence']  # no complete region proof is attempted
    >>> # 'not_determined_by_point_checks'
    """
    if isinstance(max_pairs, bool) or not isinstance(max_pairs, int) or max_pairs < 1:
        raise ValueError('Point diagnostic budget must be a positive integer')
    raw = topography.dfnd.raw
    if raw['schema_version'] != 'dfnd.raw.nm.v2':
        raise ValueError('Unsupported raw DFND schema')
    for field in ('coordinates', 'R_residence'):
        _check_unit(raw, field, 'nm')
    _check_unit(raw, 'volume', 'nm**3')
    context = topography.input_context
    coordinates = np.asarray(puw.get_value(context.coordinates, to_unit='nm'))
    radii = np.asarray(puw.get_value(context.radii, to_unit='nm'))
    source = np.asarray(context.atom_indices)
    n_atoms = len(radii)
    if (
        coordinates.shape != (n_atoms, 3)
        or radii.shape != (n_atoms,)
        or source.shape != (n_atoms,)
        or not np.issubdtype(source.dtype, np.integer)
        or len(set(source.tolist())) != n_atoms
        or not np.isfinite(coordinates).all()
        or not np.isfinite(radii).all()
        or (radii <= 0).any()
    ):
        raise ValueError('Invalid captured geometry or source map')
    parameters = raw['parameters']
    probe = float(parameters['query']['probe_radius'])
    epsilon = float(parameters['epsilon'])
    if not np.isfinite([probe, epsilon]).all() or min(probe, epsilon) < 0:
        raise ValueError('Invalid captured probe or numerical margin')
    records = {row['tetrahedron_id']: row for row in raw['tetrahedra']}
    if len(records) != len(raw['tetrahedra']):
        raise ValueError('Duplicate tetrahedron records')
    owner = {}
    unexamined = []
    for component in raw['wet_components']:
        cid = f'WET-{component["id"]}'
        resident_ids = component['resident_tetrahedron_ids']
        if not resident_ids:
            unexamined.append(cid)
        for node in resident_ids:
            if node in owner or node not in component['tetrahedron_ids']:
                raise ValueError('Invalid resident component support')
            owner[node] = cid
    if len(owner) * n_atoms > max_pairs:
        raise ValueError('Resident point diagnostic exceeds its declared budget')
    witnesses = []
    for node, cid in sorted(owner.items()):
        row = records[node]
        local = np.asarray(row['local_atom_indices'])
        if (
            local.shape != (4,)
            or not np.issubdtype(local.dtype, np.integer)
            or len(set(local.tolist())) != 4
            or (local < 0).any()
            or (local >= n_atoms).any()
            or source[local].tolist() != row['atom_indices']
        ):
            raise ValueError('Residence cell disagrees with captured source map')
        center = np.asarray(row['center'], dtype=float)
        if center.shape != (3,) or not np.isfinite(center).all():
            raise ValueError('Invalid residence center')
        clearance = np.linalg.norm(coordinates - center, axis=1) - radii
        nearest = int(clearance.argmin())
        local_clearance = float(clearance[local].min())
        cell = coordinates[local]
        # Translate before solving: support membership must not depend on the
        # distance of a rigidly translated input from the coordinate origin.
        weights3, _, rank, _ = np.linalg.lstsq(
            (cell[1:] - cell[0]).T, center - cell[0], rcond=None
        )
        weights = np.r_[1 - weights3.sum(), weights3]
        inside = bool((weights >= -1e-7).all()) if rank == 3 else None
        margin = float(clearance[nearest] - probe)
        if inside is None:
            status = 'unresolved_support'
        elif not inside:
            status = 'outside_support'
        elif margin > epsilon:
            status = 'clear'
        elif margin < -epsilon:
            status = 'blocked'
        else:
            status = 'numerically_unresolved'
        witnesses.append(
            {
                'tetrahedron_id': int(node),
                'component_id': cid,
                'source_atom_indices': source[local].tolist(),
                'center': center.tolist(),
                'candidate_kind': row['residence_candidate_kind'],
                'recorded_local_capacity': float(row['R_residence']),
                'local_clearance': local_clearance,
                'local_capacity_residual': float(row['R_residence']) - local_clearance,
                'all_atom_clearance': float(clearance[nearest]),
                'probe_margin': margin,
                'nearest_source_atom_index': int(source[nearest]),
                'nearest_atom_is_nonlocal': bool(nearest not in local),
                'barycentric_weights': weights.tolist(),
                'center_in_support': inside,
                'carrier_volume': float(row['volume_topological']),
                'point_status': status,
            }
        )
    return {
        'schema': 'topomt.benchlab.residence-witness.nm/1',
        'length_unit': 'nm',
        'volume_unit': 'nm**3',
        'barycentric_tolerance': 1e-7,
        'probe_radius': probe,
        'numerical_margin': epsilon,
        'result_key': parameters['result_key'],
        'source_atom_indices': source.tolist(),
        'atom_center_comparisons': len(owner) * n_atoms,
        'max_pairs': max_pairs,
        'witnesses': witnesses,
        'unexamined_connector_component_ids': unexamined,
        'component_existence': 'not_determined_by_point_checks',
        'paths_and_boundary': 'not_examined',
    }
