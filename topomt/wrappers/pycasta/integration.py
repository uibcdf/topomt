from pathlib import Path
import tempfile

import numpy as np
from scipy.spatial import Delaunay

from topomt import Topography
from topomt import pyunitwizard as puw
from topomt.features import Pocket
from topomt.wrappers._common import import_upstream_module, prepare_wrapper_input_pdb


def get_topography_with_pycasta(
    molecular_system,
    *,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    upstream_root: str | Path | None = None,
    **kwargs,
) -> Topography:
    if kwargs:
        unexpected = ', '.join(sorted(kwargs))
        raise TypeError(f'Unsupported wrapper kwargs for pycasta: {unexpected}')

    with tempfile.TemporaryDirectory(prefix='topomt_pycasta_') as tmpdir_name:
        tmpdir = Path(tmpdir_name)
        input_pdb, selected_atom_indices = prepare_wrapper_input_pdb(
            molecular_system,
            tmpdir=tmpdir,
            selection=selection,
            structure_indices=structure_indices,
            syntax=syntax,
        )

        run_analysis = import_upstream_module(
            'run_analysis',
            upstream_root=upstream_root,
        )
        result = run_analysis.process_pdb(str(input_pdb))

        protein_coords_ang = np.asarray(result['protein_coords'], dtype=float)
        simplices = Delaunay(protein_coords_ang).simplices

        topography = Topography(
            molecular_system=molecular_system,
            selection=selection,
            structure_indices=structure_indices,
        )

        for pocket_index, tetra_indices in enumerate(result.get('ranked_pockets', [])):
            tetra_indices = np.asarray(tetra_indices, dtype=int)
            tetra_indices = tetra_indices[(tetra_indices >= 0) & (tetra_indices < len(simplices))]
            if tetra_indices.size == 0:
                continue

            local_atom_indices = np.unique(simplices[tetra_indices].reshape(-1))
            atom_indices = selected_atom_indices[local_atom_indices].tolist()
            center_nm = protein_coords_ang[local_atom_indices].mean(axis=0) / 10.0
            volume_nm3 = float(result['pocket_volumes'][pocket_index]) / 1000.0

            topography.add_feature(
                Pocket(
                    atom_indices=sorted(atom_indices),
                    center=puw.quantity(center_nm, 'nm'),
                    volume=puw.quantity(volume_nm3, 'nm**3'),
                    score=volume_nm3,
                    source='pycasta',
                    source_id=f'pycasta:{pocket_index}',
                )
            )

        return topography
