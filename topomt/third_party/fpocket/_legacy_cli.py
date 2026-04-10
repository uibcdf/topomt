from pathlib import Path

from topomt.features.Pocket import Pocket
from topomt.third_party.fpocket.cli import get_topography as get_topography_with_fpocket
from topomt.third_party.fpocket.files import (
    _build_topography_and_atom_map,
    _fpocket_pocket_to_feature,
    fpocket_result_to_topography,
    load_topography,
)


def load_topography_from_fpocket_output(
    molecular_system,
    pdb_file,
    output_dir,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
):
    return load_topography(
        molecular_system,
        pdb_file=pdb_file,
        output_dir=output_dir,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
    )
