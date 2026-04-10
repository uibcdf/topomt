from pathlib import Path
import tempfile

import numpy as np

from topomt import Topography
from topomt import pyunitwizard as puw
from topomt.features import Pocket
from topomt.third_party._common import import_upstream_module, prepare_wrapper_input_pdb


def _patch_alphaspace2_mdtraj_sasa(upstream):
    from mdtraj.geometry import _geometry
    import inspect

    try:
        sasa_signature = inspect.signature(_geometry._sasa)
    except (TypeError, ValueError):
        return

    if len(sasa_signature.parameters) != 6:
        return

    functions_module = import_upstream_module(
        'alphaspace2.functions',
        upstream_root=None,
    )

    def get_sasa_compat(protein_snapshot, cover_atom_coords=None):
        probe_radius = 0.14
        n_sphere_points = 960

        if cover_atom_coords is None:
            xyz = np.array(protein_snapshot.xyz, dtype=np.float32)
            atom_radii = [
                functions_module._ATOMIC_RADII[atom.element.symbol]
                for atom in protein_snapshot.topology.atoms
            ]
        else:
            xyz = np.array(
                np.expand_dims(
                    np.concatenate((protein_snapshot.xyz[0], cover_atom_coords), axis=0),
                    axis=0,
                ),
                dtype=np.float32,
            )
            atom_radii = [
                functions_module._ATOMIC_RADII[atom.element.symbol]
                for atom in protein_snapshot.topology.atoms
            ] + [0.17 for _ in range(xyz.shape[1] - protein_snapshot.xyz.shape[1])]

        radii = np.array(atom_radii, np.float32) + probe_radius
        atom_mapping = np.arange(xyz.shape[1], dtype=np.int32)
        atom_selection_mask = np.ones(xyz.shape[1], dtype=np.int32)
        out = np.zeros((1, xyz.shape[1]), dtype=np.float32)
        _geometry._sasa(
            xyz,
            radii,
            int(n_sphere_points),
            atom_mapping,
            atom_selection_mask,
            out,
        )
        return out[:, :protein_snapshot.xyz.shape[1]][0]

    functions_module.getSASA = get_sasa_compat


def _patch_alphaspace2_numpy_compatibility():
    if not hasattr(np, 'float'):
        setattr(np, 'float', float)


def get_topography(
    molecular_system,
    *,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    upstream_root: str | Path | None = None,
    min_vertices: int = 20,
    **kwargs,
) -> Topography:
    if kwargs:
        unexpected = ', '.join(sorted(kwargs))
        raise TypeError(f'Unsupported wrapper kwargs for alphaspace2: {unexpected}')

    with tempfile.TemporaryDirectory(prefix='topomt_alphaspace2_') as tmpdir_name:
        tmpdir = Path(tmpdir_name)
        input_pdb, selected_atom_indices = prepare_wrapper_input_pdb(
            molecular_system,
            tmpdir=tmpdir,
            selection=selection,
            structure_indices=structure_indices,
            syntax=syntax,
        )

        import mdtraj as md

        upstream = import_upstream_module('alphaspace2', upstream_root=upstream_root)
        _patch_alphaspace2_numpy_compatibility()
        _patch_alphaspace2_mdtraj_sasa(upstream)
        receptor = md.load(str(input_pdb))
        snapshot = upstream.Snapshot()
        snapshot.run(receptor)

        topography = Topography(
            molecular_system=molecular_system,
            selection=selection,
            structure_indices=structure_indices,
        )

        for pocket_index, pocket in enumerate(snapshot.pockets):
            alpha_indices = np.asarray(pocket.alpha_index, dtype=int)
            if alpha_indices.size < min_vertices:
                continue

            lining_local_indices = np.unique(snapshot._alpha_lining[alpha_indices].reshape(-1))
            atom_indices = selected_atom_indices[lining_local_indices].tolist()
            beta_indices = snapshot._pocket_beta_index_list[pocket_index]

            alpha_centers_nm = np.asarray(snapshot._alpha_xyz[alpha_indices], dtype=float) / 10.0
            alpha_radii_nm = np.asarray(snapshot._alpha_radii[alpha_indices], dtype=float) / 10.0
            beta_centers_nm = (
                np.asarray(snapshot._beta_xyz[beta_indices], dtype=float) / 10.0
                if len(beta_indices) > 0
                else np.zeros((0, 3), dtype=float)
            )

            topography.add_feature(
                Pocket(
                    atom_indices=sorted(atom_indices),
                    center=puw.quantity(np.asarray(pocket.centroid, dtype=float) / 10.0, 'nm'),
                    volume=puw.quantity(float(pocket.space) / 1000.0, 'nm**3'),
                    score=float(pocket.score),
                    source='alphaspace2',
                    source_id=f'alphaspace2:{pocket_index}',
                    alpha_sphere_centers=puw.quantity(alpha_centers_nm, 'nm'),
                    alpha_sphere_radii=puw.quantity(alpha_radii_nm, 'nm'),
                    beta_centers=puw.quantity(beta_centers_nm, 'nm'),
                    nonpolar_volume=puw.quantity(float(pocket.nonpolar_space) / 1000.0, 'nm**3'),
                    is_contact=bool(pocket.isContact),
                )
            )

        return topography


get_topography_with_alphaspace2 = get_topography
