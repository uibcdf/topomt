"""Run the DFND teaching example on the exact downloaded BenchLab input."""

import argparse
import hashlib
import json
from pathlib import Path

import molsysmt as msm
import numpy as np
from pyunitwizard import QuantityRecord

from topomt import Topography, get_topography
from topomt import pyunitwizard as puw

INPUT_SHA256 = '8634f70afdaf21cb8388887f5f80ae73dc36ef4f043198a10b525a93ebde5ce3'


def analyze_tetrahedron(input_directory: Path) -> dict[float, Topography]:
    """Analyze the frozen regular tetrahedron at three probe radii in angstroms.

    Parameters
    ----------
    input_directory
        Directory containing the downloaded ``input.json`` and ``input.pdb``.

    Returns
    -------
    dict
        Probe radii in angstroms mapped to independently promoted Topography
        results. Query arguments themselves use explicit quantities.

    Raises
    ------
    ValueError
        If the frozen input changed or molecular radius assignment differs.
    FileNotFoundError
        If either downloaded input file is absent.

    Examples
    --------
    After downloading both inputs to ``tetrahedron_input``::

        results = analyze_tetrahedron(Path('tetrahedron_input'))
        void = next(iter(results[1.4].get_features(by='type', value='void')))
    """
    input_directory = Path(input_directory)
    input_bytes = (input_directory / 'input.json').read_bytes()
    if hashlib.sha256(input_bytes).hexdigest() != INPUT_SHA256:
        raise ValueError('The frozen input differs from regular_tetrahedron_v1')
    fixture = json.loads(input_bytes)

    coordinates = QuantityRecord.from_dict(fixture['coordinates']).to_quantity(
        field='coordinates', unit='angstroms'
    )
    expected_radii = QuantityRecord.from_dict(fixture['atom_radii']).to_quantity(
        field='atom_radii', unit='angstroms'
    )
    epsilon = QuantityRecord.from_dict(fixture['epsilon']).to_quantity(
        field='epsilon', unit='angstroms'
    )

    # The PDB supplies carbon dummy topology. Its rounded coordinates are not
    # the scientific input: restore the full-precision quantity record.
    system = msm.convert(str(input_directory / 'input.pdb'), to_form='molsysmt.MolSys')
    values = puw.get_value(coordinates, to_unit='angstroms')
    msm.set(system, coordinates=puw.quantity(values[None], 'angstroms'))
    received_radii = msm.physchem.get_atomic_radius(
        system, element='atom', selection='all', definition='vdw'
    )
    if not np.allclose(
        puw.get_value(received_radii, to_unit='angstroms'),
        puw.get_value(expected_radii, to_unit='angstroms'),
        rtol=0.0,
        atol=1e-14,
    ):
        raise ValueError('Molecular radius assignment differs from the frozen model')

    results = {
        probe: get_topography(
            system,
            method='dfnd',
            selection='all',
            structure_indices=0,
            hydrogen_policy='exclude',
            probe_radius=puw.quantity(probe, 'angstroms'),
            epsilon=epsilon,
            residence_tolerance=puw.quantity(0.0, 'angstroms'),
            permeability_tolerance=puw.quantity(0.0, 'angstroms'),
            transit_policy='with_connectors',
            gate_intrusion_policy='flag_only',
            dry_adjacency='face',
            min_size=0,
        )
        for probe in (1.2, 1.4, 1.7)
    }
    # Use and verify the documented default instead of assuming a radius model.
    if any(t.dfnd.network.mesh_config.radii_model != 'vdw' for t in results.values()):
        raise ValueError('DFND radius policy differs from the frozen model')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_directory', type=Path)
    arguments = parser.parse_args()
    for radius, topography in analyze_tetrahedron(arguments.input_directory).items():
        types = [feature.feature_type for feature in topography.values()]
        print(f'{radius:.1f} angstrom: {types}')
