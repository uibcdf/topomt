"""Submitted PDB serials must address the declared original atom axis."""

from pathlib import Path

import molsysmt as msm
import numpy as np
import pytest

import topomt as tmt
from topomt import pyunitwizard as puw

DATA = Path(tmt.__file__).parent / 'data/fpocket4/sample'


def _load(source, mapping):
    return tmt.get_provider_output(
        source,
        method='fpocket',
        backend='files',
        pdb_file=DATA / '3LKF.pdb',
        output_dir=DATA / '3LKF_out',
        submitted_atom_indices=mapping,
    )


def test_explicit_submission_map_is_independent_of_source_id_labels():
    source = msm.convert(DATA / '3LKF.pdb', to_form='molsysmt.MolSys')
    n_atoms = msm.get(source, n_atoms=True)
    msm.set(source, atom_id=[f'source-{index}' for index in range(n_atoms)])
    output = _load(source, list(range(n_atoms)))
    assert len(output.pockets) == 7
    assert len(output.pockets[0].atom_indices) > 0
    assert output.run.metadata['submitted_atom_indices'] == list(range(n_atoms))
    coordinates = puw.get_value(output.input_coordinates, to_unit='nm')
    pocket = output.pockets[0]
    np.testing.assert_array_equal(
        puw.get_value(pocket.geometries['member_atoms'].coordinates, to_unit='nm'),
        coordinates[list(pocket.atom_indices)],
    )


def test_submission_context_accepts_numpy_axes():
    n_atoms = msm.get(DATA / '3LKF.pdb', n_atoms=True)
    output = tmt.get_provider_output(
        DATA / '3LKF.pdb',
        method='fpocket',
        backend='files',
        pdb_file=DATA / '3LKF.pdb',
        output_dir=DATA / '3LKF_out',
        selection=np.arange(n_atoms),
        structure_indices=np.array([0]),
        submitted_atom_indices=list(range(n_atoms)),
    )
    assert output.run.metadata['selection'] == list(range(n_atoms))
    assert output.run.metadata['structure_indices'] == [0]


def test_submission_map_rejects_an_incompatible_source_pose():
    source = msm.convert(DATA / '3LKF.pdb', to_form='molsysmt.MolSys')
    coordinates = msm.get(source, coordinates=True)
    msm.set(source, coordinates=coordinates + puw.quantity(1.0, 'nm'))
    with pytest.raises(
        ValueError, match='(?i)submitted.*coordinates|source.*coordinates'
    ):
        _load(source, list(range(msm.get(source, n_atoms=True))))


@pytest.mark.parametrize('mapping', [[0], [0, 0], [-1], [1.5]])
def test_submission_map_rejects_invalid_atom_axes(mapping):
    with pytest.raises(ValueError, match='submission|submitted'):
        _load(DATA / '3LKF.pdb', mapping)
