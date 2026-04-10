import molsysmt as msm
import numpy as np

from topomt import Topography, pyunitwizard as puw
from topomt.features import Pocket
from topomt.third_party.pycasta._native_impl import pycasta as _native_pycasta


def get_topography(
    molecular_system,
    *,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    **kwargs,
) -> Topography:
    """Run the local pyCASTA implementation and return a Topography."""

    topography = Topography(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
    )

    pockets_tet, volumes, simplices, atom_indices = _native_pycasta(
        molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        return_atom_indices=True,
        **kwargs,
    )

    for pocket_index, (pocket_tetrahedra, volume_nm3) in enumerate(zip(pockets_tet, volumes)):
        involved_local_indices = set()
        for tetra_index in pocket_tetrahedra:
            involved_local_indices.update(simplices[tetra_index])

        involved_global_indices = [atom_indices[index] for index in involved_local_indices]
        atom_coords = msm.get(
            topography.molecular_system,
            selection=involved_global_indices,
            coordinates=True,
        )[0]
        center = np.mean(puw.get_value(atom_coords, to_unit='nm'), axis=0)

        pocket_feature = Pocket(
            atom_indices=sorted(involved_global_indices),
            center=center,
            volume=volume_nm3,
            score=volume_nm3,
            source='pycasta',
            source_id=f'pycasta:{pocket_index}',
        )
        topography.add_feature(pocket_feature)

    return topography
