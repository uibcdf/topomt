import molsysmt as msm
import numpy as np

from topomt import pyunitwizard as puw


NON_RECEPTOR_GROUP_SELECTION = 'group_type not in ["water", "ion", "small molecule"]'
HEAVY_ATOM_SELECTION = 'atom_type not in ["H"]'


def build_heavy_receptor_view(
    molecular_system,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
):
    """Build a heavy-atom receptor view and preserve global atom-index mapping."""

    molsys = msm.convert(
        molecular_system,
        to_form='molsysmt.MolSys',
        structure_indices=structure_indices,
    )
    selected_atom_indices = np.asarray(
        msm.select(molsys, selection=selection, syntax=syntax),
        dtype=int,
    )
    receptor_atom_indices = np.asarray(
        msm.select(
            molsys,
            selection=HEAVY_ATOM_SELECTION,
            mask=msm.select(
                molsys,
                selection=NON_RECEPTOR_GROUP_SELECTION,
                mask=selected_atom_indices,
                syntax='MolSysMT',
            ),
            syntax='MolSysMT',
        ),
        dtype=int,
    )
    receptor = msm.convert(
        molsys,
        to_form='molsysmt.MolSys',
        selection=receptor_atom_indices,
        syntax='MolSysMT',
    )
    coordinates = msm.get(
        molecular_system=receptor,
        coordinates=True,
        structure_indices=structure_indices,
    )[0]
    coordinates_nm = np.asarray(puw.get_value(coordinates, to_unit='nm'), dtype=float)

    return molsys, receptor, receptor_atom_indices.tolist(), coordinates_nm
