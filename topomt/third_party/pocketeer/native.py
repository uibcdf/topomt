import molsysmt as msm

from topomt import Topography, pyunitwizard as puw
from topomt.features import Pocket
from topomt.third_party.pocketeer._native_impl import pocketeer as _native_pocketeer


def get_topography(
    molecular_system,
    *,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    **kwargs,
) -> Topography:
    """Run the local Pocketeer implementation and return a Topography."""

    topography = Topography(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
    )

    pockets_data, spheres, atom_indices = _native_pocketeer(
        molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        return_atom_indices=True,
        **kwargs,
    )
    del spheres

    for pocket_record in pockets_data:
        all_atom_indices = set()
        for sphere in pocket_record.spheres:
            all_atom_indices.update(atom_indices[index] for index in sphere.atom_indices)

        pocket_feature = Pocket(
            atom_indices=sorted(all_atom_indices),
            center=puw.quantity(pocket_record.centroid, 'nm'),
            volume=puw.quantity(pocket_record.volume, 'nm**3'),
            score=pocket_record.score,
            source='pocketeer',
            source_id=f'pocketeer:{pocket_record.pocket_id}',
        )
        topography.add_feature(pocket_feature)

    return topography
