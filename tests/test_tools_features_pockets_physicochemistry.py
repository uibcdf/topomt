"""Tests for pocket physicochemistry helpers in topomt.tools.features."""

import numpy as np
import molsysmt as msm

import topomt as tmt
from topomt.tools.features.pockets import (
    apolar_ratio,
    get_physicochemical_properties,
    nonpolar_ratio_from_sasa,
)


def test_apolar_ratio_from_boolean_mask():

    ratio = apolar_ratio([0, 2, 3], apolar_mask=[True, False, False, True])

    assert ratio == 2.0 / 3.0


def test_nonpolar_ratio_from_sasa_uses_lining_subset():

    sasa = np.array([1.0, 2.0, 3.0, 4.0], dtype=float)
    elements = ['C', 'O', 'S', 'N']

    ratio = nonpolar_ratio_from_sasa(sasa, elements, [0, 1, 2])

    assert ratio == 1.0 / 6.00001


def test_get_physicochemical_properties_reports_residue_level_summary():

    molecular_system = msm.convert(tmt.demo['TcTIM']['1TCD.pdb'], to_form='molsysmt.MolSys')
    atom_indices = [0, 1, 2, 3, 4, 5]

    properties = get_physicochemical_properties(molecular_system, atom_indices)

    assert properties['n_atoms'] == len(atom_indices)
    assert properties['n_residues'] >= 1
    assert isinstance(properties['net_charge'], float)
    assert isinstance(properties['mean_hydrophobicity'], float)
    assert isinstance(properties['polarity_ratio'], float)
