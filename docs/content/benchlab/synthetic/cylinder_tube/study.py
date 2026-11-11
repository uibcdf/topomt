"""Portable straight-tube study support, with lazy native/public execution.

Reference replay imports no TopoMT. Native receiving uses MolSysMT's source
representation and verifies its radii against the frozen ball input.
"""

import hashlib
import json
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import numpy as np
import pyunitwizard as puw
from pyunitwizard import QuantityRecord


def read(path: Path) -> dict:
    """Read retained JSON without modifying its original bytes."""
    return json.loads(path.read_text())


def quantity(record: dict, field: str, unit: str = 'angstroms') -> Any:
    """Restore an explicit field and receiving unit through the quantity codec."""
    return QuantityRecord.from_dict(record).to_quantity(field=field, unit=unit)


@contextmanager
def _tools():
    root = Path(__file__).resolve().parents[5]
    previous = sys.path[:]
    try:
        sys.path.insert(0, str(root))
        yield
    finally:
        sys.path[:] = previous


def receive(directory: Path, probe: float, min_size: int = 0) -> Any:
    """Receive frozen full-precision balls through get_topography(method='dfnd').

    Parameters
    ----------
    directory : Path
        Case directory, also when extracted from the complete study bundle.
    probe : float
        Explicit probe radius in angstroms.
    min_size : int
        Reporting cutoff, independent of scientific geometry/query identity.

    Returns
    -------
    topomt.Topography
        Actual source-bound native/public result, including empty results.

    Raises
    ------
    ValueError
        Frozen input/PDB identity or original atomic radius assignment differs.
    """
    import molsysmt as msm

    import topomt

    folder = directory / 'artifacts/cylinder_tube_v1'
    protocol = read(folder / 'protocol.json')
    payload = (folder / 'input.json').read_bytes()
    if hashlib.sha256(payload).hexdigest() != protocol['input_sha256']:
        raise ValueError('Frozen tube input identity differs')
    fixture = json.loads(payload)
    if (
        hashlib.sha256((folder / 'input.pdb').read_bytes()).hexdigest()
        != fixture['catalog_history']['pdb_sha256']
    ):
        raise ValueError('Original catalog topology/PDB identity differs')
    system = msm.convert(str(folder / 'input.pdb'), to_form='molsysmt.MolSys')
    coords = quantity(fixture['coordinates'], 'coordinates')
    msm.set(
        system,
        coordinates=puw.quantity(
            puw.get_value(coords, to_unit='angstroms')[None], 'angstroms'
        ),
    )
    selection = fixture['source_atom_indices']
    assigned = msm.physchem.get_atomic_radius(
        system, element='atom', selection=selection, definition='vdw'
    )
    np.testing.assert_allclose(
        puw.get_value(assigned, to_unit='angstroms'),
        puw.get_value(
            quantity(fixture['atom_radii'], 'atom_radii'), to_unit='angstroms'
        ),
        rtol=0,
        atol=1e-14,
    )
    query = protocol['query']
    topo = topomt.get_topography(
        system,
        method='dfnd',
        selection=selection,
        probe_radius=puw.quantity(probe, 'angstroms'),
        epsilon=quantity(fixture['epsilon'], 'epsilon'),
        min_size=min_size,
        transit_policy=query['transit_policy'],
        gate_intrusion_policy=query['gate_intrusion_policy'],
        dry_adjacency=query['dry_adjacency'],
        residence_tolerance=puw.quantity(
            query['residence_tolerance_angstroms'], 'angstroms'
        ),
        permeability_tolerance=puw.quantity(
            query['permeability_tolerance_angstroms'], 'angstroms'
        ),
        boundary_tolerance=puw.quantity(
            query['boundary_tolerance_angstroms'], 'angstroms'
        ),
    )
    np.testing.assert_allclose(
        puw.get_value(topo.input_context.coordinates, to_unit='angstroms'),
        puw.get_value(coords, to_unit='angstroms'),
        rtol=0,
        atol=1e-13,
    )
    if topo.input_context.atom_indices.tolist() != selection:
        raise ValueError('Public source atom map differs')
    return topo


def describe(topo: Any) -> dict:
    """Validate and detach the actual source support, native bank and public roles."""
    with _tools():
        from devtools.benchlab.public_contract import describe_public_contract

        return describe_public_contract(topo)


def references(directory: Path) -> dict:
    """Replay independent paths/bounds and both complete wall/end certificates."""
    with _tools():
        from devtools.verify_tube_boundary import verify_boundary
        from devtools.verify_tube_passage import verify_reference

        folder = directory / 'artifacts/cylinder_tube_v1'
        passage = verify_reference(
            folder / 'input.json',
            folder / 'passage_v2_protocol.json',
            read(folder / 'reference_v2_certificate.json'),
        )
        boundaries = {
            str(probe): verify_boundary(
                folder / 'input.json',
                folder / f'boundary_{probe:g}A_v2_protocol.json',
                read(folder / f'boundary_{probe:g}A_v2_certificate.json'),
            )
            for probe in (1.2, 1.4)
        }
        return {'passage': passage, 'boundary': boundaries}


def inspect_centerlines(topo: Any) -> list[dict]:
    """Check selected native candidate segments; keep their native validation flag.

    Parameters
    ----------
    topo : topomt.Topography
        Already computed result on the original frozen ball input.

    Returns
    -------
    list of dict
        Explicit angstrom polyline/ball clearance and conditional validity for
        each native multi-link resident component. End-to-infinity tails are
        not supplied by a graph-derived interior skeleton.

    Raises
    ------
    ValueError
        Original input or recoverable candidate geometry is missing.
    """
    from topomt.dfnd.centerline import channel_skeleton

    with _tools():
        from devtools.verify_tube_passage import polyline_clearance

        centers = np.asarray(
            puw.get_value(topo.input_context.coordinates, to_unit='angstroms')
        )
        radii = np.asarray(
            puw.get_value(topo.input_context.atom_radii, to_unit='angstroms')
        )
        probe = float(
            puw.get_value(
                puw.quantity(
                    topo.dfnd.raw['parameters']['query']['probe_radius'], 'nm'
                ),
                to_unit='angstroms',
            )
        )
        rows = []
        for component in topo.dfnd.dfn.components.wet:
            if len(component.external_link_ids) < 2:
                continue
            skeleton = channel_skeleton(topo.dfnd.raw, component.raw_record)
            if skeleton is None:
                continue
            points = np.asarray(
                puw.get_value(
                    puw.quantity(skeleton['centers'], 'nm'), to_unit='angstroms'
                )
            )
            clearance = polyline_clearance(
                points, centers, radii, length_unit='angstroms'
            )
            rows.append(
                {
                    'component_id': component.component_id,
                    'component_key': component.component_key,
                    'length_unit': 'angstroms',
                    'probe_radius': probe,
                    'points': points.tolist(),
                    'tetrahedron_path': list(map(int, skeleton['tetra_path'])),
                    'minimum_all_atom_clearance': clearance,
                    'probe_margin': clearance - probe,
                    'all_segments_clear': clearance - probe > 1e-6,
                    'native_is_collision_validated': skeleton['is_collision_validated'],
                    'native_path_kind': skeleton['path_kind'],
                    'scope': 'This exact interior polyline only; native flag is unchanged and no exterior-tail/global-optimum claim follows',
                }
            )
        return rows
