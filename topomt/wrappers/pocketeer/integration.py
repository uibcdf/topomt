import tempfile

import numpy as np

from topomt import Topography
from topomt import pyunitwizard as puw
from topomt.features import Pocket
from topomt.wrappers._common import import_upstream_module, prepare_wrapper_input_pdb


def get_topography_with_pocketeer(
    molecular_system,
    *,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    upstream_root: str | None = None,
    **kwargs,
) -> Topography:
    with tempfile.TemporaryDirectory(prefix='topomt_pocketeer_') as tmpdir_name:
        tmpdir = tempfile.Path(tmpdir_name) if hasattr(tempfile, 'Path') else None
        if tmpdir is None:
            from pathlib import Path

            tmpdir = Path(tmpdir_name)

        input_pdb, selected_atom_indices = prepare_wrapper_input_pdb(
            molecular_system,
            tmpdir=tmpdir,
            selection=selection,
            structure_indices=structure_indices,
            syntax=syntax,
        )

        upstream = import_upstream_module('pocketeer', upstream_root=upstream_root)
        atomarray = upstream.load_structure(str(input_pdb))
        pockets = upstream.find_pockets(atomarray, **kwargs)

        topography = Topography(
            molecular_system=molecular_system,
            selection=selection,
            structure_indices=structure_indices,
        )

        for pocket in pockets:
            local_atom_indices = np.flatnonzero(np.asarray(pocket.mask, dtype=bool))
            atom_indices = selected_atom_indices[local_atom_indices].tolist()
            alpha_sphere_centers = np.asarray(
                [sphere.center for sphere in pocket.spheres],
                dtype=float,
            )
            alpha_sphere_radii = np.asarray(
                [sphere.radius for sphere in pocket.spheres],
                dtype=float,
            )

            topography.add_feature(
                Pocket(
                    atom_indices=sorted(atom_indices),
                    center=puw.quantity(np.asarray(pocket.centroid, dtype=float) / 10.0, 'nm'),
                    volume=puw.quantity(float(pocket.volume) / 1000.0, 'nm**3'),
                    score=float(pocket.score),
                    source='pocketeer',
                    source_id=f'pocketeer:{pocket.pocket_id}',
                    alpha_sphere_centers=puw.quantity(alpha_sphere_centers / 10.0, 'nm'),
                    alpha_sphere_radii=puw.quantity(alpha_sphere_radii / 10.0, 'nm'),
                )
            )

        return topography
