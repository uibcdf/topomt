"""Inspect the frozen closed shell through the public molecular route."""

import hashlib
import json
from pathlib import Path

import molsysmt as msm
import numpy as np
from pyunitwizard import QuantityRecord

from topomt import Topography, get_topography
from topomt import pyunitwizard as puw

INPUT_SHA256 = 'ef19995751b2df58c8b1556011f74fa4774e924b9cd499138b8741988b650157'


def analyze_closed_shell(input_directory: Path) -> Topography:
    """Analyze the frozen shell at 0.2 angstrom with diagnostic-only intrusion.

    Parameters
    ----------
    input_directory
        Directory containing the canonical closed-shell input.json and input.pdb.

    Returns
    -------
    Topography
        Public findings with retained native geometry and input context.

    Raises
    ------
    ValueError
        If the frozen input or assigned atomic radii differ.
    FileNotFoundError
        If a required input file is absent.

    Examples
    --------
    ``topography = analyze_closed_shell(Path('shell_input'))``
    """
    input_directory = Path(input_directory)
    payload = (input_directory / 'input.json').read_bytes()
    if hashlib.sha256(payload).hexdigest() != INPUT_SHA256:
        raise ValueError('The frozen input differs from closed_shell_v1')
    fixture = json.loads(payload)
    coordinates = QuantityRecord.from_dict(fixture['coordinates']).to_quantity(
        field='coordinates', unit='angstroms'
    )
    radii = QuantityRecord.from_dict(fixture['atom_radii']).to_quantity(
        field='atom_radii', unit='angstroms'
    )
    epsilon = QuantityRecord.from_dict(fixture['epsilon']).to_quantity(
        field='epsilon', unit='angstroms'
    )
    system = msm.convert(str(input_directory / 'input.pdb'), to_form='molsysmt.MolSys')
    msm.set(
        system,
        coordinates=puw.quantity(
            puw.get_value(coordinates, to_unit='angstroms')[None], 'angstroms'
        ),
    )
    assigned = msm.physchem.get_atomic_radius(
        system, element='atom', selection='all', definition='vdw'
    )
    if not np.allclose(
        puw.get_value(assigned, to_unit='angstroms'),
        puw.get_value(radii, to_unit='angstroms'),
        rtol=0,
        atol=1e-14,
    ):
        raise ValueError('Radius assignment differs from the frozen input')
    result = get_topography(
        system,
        method='dfnd',
        selection='all',
        structure_indices=0,
        hydrogen_policy='exclude',
        probe_radius=puw.quantity(0.2, 'angstroms'),
        epsilon=epsilon,
        residence_tolerance=puw.quantity(0.0, 'angstroms'),
        permeability_tolerance=puw.quantity(0.0, 'angstroms'),
        transit_policy='with_connectors',
        gate_intrusion_policy='flag_only',
        dry_adjacency='face',
        min_size=0,
    )
    if result.dfnd.network.mesh_config.radii_model != 'vdw':
        raise ValueError('Radius policy differs from the frozen input')
    return result
