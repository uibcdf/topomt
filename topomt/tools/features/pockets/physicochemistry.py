"""Pocket physicochemical characterization helpers."""

from typing import Dict, List, Sequence, Union

import molsysmt as msm
import numpy as np


def apolar_ratio(
    indices: Sequence[int],
    apolar_mask: Sequence[bool] | None = None,
    types: Sequence[int] | None = None,
) -> float | None:
    """Compute the apolar fraction for a set of indices."""

    if apolar_mask is None and types is None:
        return None

    index_array = np.asarray(indices, dtype=int)
    if apolar_mask is not None:
        mask = np.asarray(apolar_mask, dtype=bool)
        return float(mask[index_array].sum()) / len(index_array) if len(index_array) else 0.0

    types_array = np.asarray(types)
    return float((types_array[index_array] == 1).sum()) / len(index_array) if len(index_array) else 0.0


def nonpolar_ratio_from_sasa(
    sasa: np.ndarray,
    atom_elements: Sequence[str],
    lining_indices: Sequence[int],
) -> float:
    """Compute the nonpolar SASA ratio for lining atoms."""

    if len(lining_indices) == 0 or len(sasa) == 0:
        return 0.0

    lining_index_array = np.asarray(lining_indices, dtype=int)
    elements = np.asarray(atom_elements)
    lining_sasa = np.asarray(sasa)[lining_index_array]
    lining_elements = elements[lining_index_array]
    nonpolar_mask = ~np.isin(lining_elements, ['O', 'N', 'S'])
    nonpolar_sasa = lining_sasa[nonpolar_mask].sum()
    total_sasa = lining_sasa.sum() + 1e-5
    return float(nonpolar_sasa / total_sasa)


def get_physicochemical_properties(
    molecular_system,
    atom_indices: List[int],
    structure_indices: int = 0,
    syntax: str = 'MolSysMT',
) -> Dict[str, Union[float, int]]:
    """Compute simple physicochemical descriptors for a set of lining atoms."""

    del structure_indices, syntax

    if not atom_indices:
        return {
            'net_charge': 0.0,
            'mean_hydrophobicity': 0.0,
            'polarity_ratio': 0.0,
            'n_residues': 0,
            'n_atoms': 0,
        }

    kd_scale = {
        'ILE': 4.5,
        'VAL': 4.2,
        'LEU': 3.8,
        'PHE': 2.8,
        'CYS': 2.5,
        'MET': 1.9,
        'ALA': 1.8,
        'GLY': -0.4,
        'THR': -0.7,
        'SER': -0.8,
        'TRP': -0.9,
        'TYR': -1.3,
        'PRO': -1.6,
        'HIS': -3.2,
        'GLU': -3.5,
        'GLN': -3.5,
        'ASP': -3.5,
        'ASN': -3.5,
        'LYS': -3.9,
        'ARG': -4.5,
    }

    charge_scale = {
        'ARG': 1.0,
        'LYS': 1.0,
        'HIS': 0.1,
        'ASP': -1.0,
        'GLU': -1.0,
    }

    polar_residues = {'ARG', 'LYS', 'HIS', 'GLU', 'ASP', 'ASN', 'GLN', 'SER', 'THR', 'TYR'}

    residue_names = msm.get(
        molecular_system,
        element='atom',
        selection=atom_indices,
        residue_name=True,
    )
    residue_indices = msm.get(
        molecular_system,
        element='atom',
        selection=atom_indices,
        residue_index=True,
    )

    unique_residues = {}
    for residue_index, residue_name in zip(residue_indices, residue_names):
        unique_residues[residue_index] = residue_name

    hydrophobicity_sum = 0.0
    charge_sum = 0.0
    polar_count = 0

    for residue_name in unique_residues.values():
        normalized_name = residue_name.upper()
        hydrophobicity_sum += kd_scale.get(normalized_name, 0.0)
        charge_sum += charge_scale.get(normalized_name, 0.0)
        if normalized_name in polar_residues:
            polar_count += 1

    n_unique = len(unique_residues)

    return {
        'net_charge': float(charge_sum),
        'mean_hydrophobicity': float(hydrophobicity_sum / n_unique) if n_unique > 0 else 0.0,
        'polarity_ratio': float(polar_count / n_unique) if n_unique > 0 else 0.0,
        'n_residues': n_unique,
        'n_atoms': len(atom_indices),
    }
