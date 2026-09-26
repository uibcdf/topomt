import hashlib
import inspect
import json
import tempfile
from pathlib import Path

import numpy as np
from depdigest import dep_digest

from topomt import Topography
from topomt import pyunitwizard as puw
from topomt.features import Pocket
from topomt.provider_output import ExternalMeasurement, ProviderRun
from topomt.third_party._common import import_upstream_module, prepare_wrapper_input_pdb


def _snapshot_json_value(value):
    if isinstance(value, np.ndarray):
        return _snapshot_json_value(value.tolist())
    if isinstance(value, np.generic):
        return _snapshot_json_value(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return {'nonfinite': str(value)}
    if isinstance(value, (list, tuple)):
        return [_snapshot_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _snapshot_json_value(item) for key, item in value.items()}
    return value


def _patch_alphaspace2_mdtraj_sasa(upstream):
    import inspect

    from mdtraj.geometry import _geometry

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
                    np.concatenate(
                        (protein_snapshot.xyz[0], cover_atom_coords), axis=0
                    ),
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
        return out[:, : protein_snapshot.xyz.shape[1]][0]

    functions_module.getSASA = get_sasa_compat


def _patch_alphaspace2_numpy_compatibility():
    if not hasattr(np, 'float'):
        setattr(np, 'float', float)


@dep_digest('mdtraj')
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
        if receptor.n_atoms != len(selected_atom_indices):
            raise ValueError(
                'AlphaSpace2 receptor atom count differs from the selected molecular '
                'system; lining atoms cannot be mapped safely.'
            )

        output_dir = tmpdir / 'results'
        output_dir.mkdir()
        snapshot.save(
            output_dir=str(output_dir), receptor=receptor, chimera_scripts=False
        )
        state = {
            'schema_version': 1,
            **{
                name: _snapshot_json_value(value)
                for name, value in snapshot.__dict__.items()
            },
            'pocket_properties': [
                {
                    'index': pocket.index,
                    'alpha_indices': _snapshot_json_value(pocket.alpha_index),
                    'beta_indices': _snapshot_json_value(
                        snapshot._pocket_beta_index_list[pocket.index]
                    ),
                    'space': _snapshot_json_value(pocket.space),
                    'nonpolar_space': _snapshot_json_value(pocket.nonpolar_space),
                    'score': _snapshot_json_value(pocket.score),
                    'occupied_space': _snapshot_json_value(pocket.occupiedSpace),
                    'occupied_nonpolar_space': _snapshot_json_value(
                        pocket.occupiedNonpolarSpace
                    ),
                    'occupancy': _snapshot_json_value(pocket.occupancy),
                    'occupancy_nonpolar': _snapshot_json_value(
                        pocket.occupancy_nonpolar
                    ),
                    'is_contact': bool(pocket.isContact),
                }
                for pocket in snapshot.pockets
            ],
            'beta_properties': [
                {
                    'index': beta.index,
                    'alpha_indices': _snapshot_json_value(
                        snapshot._beta_alpha_index_list[beta.index]
                    ),
                    'space': _snapshot_json_value(beta.space),
                    'nonpolar_space': _snapshot_json_value(beta.nonpolar_space),
                    'scores': _snapshot_json_value(beta.scores),
                    'score': _snapshot_json_value(beta.score),
                    'best_probe_type': beta.best_probe_type,
                    'occupied_space': _snapshot_json_value(beta.occupiedSpace),
                    'occupied_nonpolar_space': _snapshot_json_value(
                        beta.occupiedNonpolarSpace
                    ),
                    'occupancy': _snapshot_json_value(beta.occupancy),
                    'occupancy_nonpolar': _snapshot_json_value(beta.occupancy_nonpolar),
                    'is_contact': bool(beta.isContact),
                }
                for beta in snapshot.betas
            ],
        }
        (output_dir / 'topomt_snapshot.json').write_text(
            json.dumps(state, sort_keys=True, allow_nan=False)
        )
        source_file = Path(inspect.getfile(upstream.Snapshot))
        with source_file.open('rb') as file_handle:
            source_sha256 = hashlib.file_digest(file_handle, 'sha256').hexdigest()
        run = ProviderRun.capture(
            'alphaspace2',
            'library',
            input_pdb,
            output_dir,
            metadata={
                'snapshot_source_sha256': source_sha256,
                'selection': selection,
                'structure_indices': _snapshot_json_value(structure_indices),
                'syntax': syntax,
                'min_vertices': min_vertices,
                'selected_atom_indices': selected_atom_indices.tolist(),
                'snapshot_settings': {
                    name: _snapshot_json_value(getattr(snapshot, name))
                    for name in (
                        'min_r',
                        'max_r',
                        'beta_cluster_dist',
                        'pocket_cluster_dist',
                        'contact_cutoff',
                    )
                },
            },
        )

        topography = Topography(
            molecular_system=molecular_system,
            selection=selection,
            structure_indices=structure_indices,
        )
        topography.add_provider_run(run)

        for pocket_index, pocket in enumerate(snapshot.pockets):
            alpha_indices = np.asarray(pocket.alpha_index, dtype=int)
            if alpha_indices.size < min_vertices:
                continue

            lining_local_indices = np.unique(
                snapshot._alpha_lining[alpha_indices].reshape(-1)
            )
            atom_indices = selected_atom_indices[lining_local_indices].tolist()
            beta_indices = snapshot._pocket_beta_index_list[pocket_index]
            alpha_lining_local = np.asarray(
                snapshot._alpha_lining[alpha_indices], dtype=int
            )
            alpha_space = np.asarray(snapshot._alpha_space[alpha_indices], dtype=float)
            alpha_nonpolar_space = alpha_space * np.asarray(
                snapshot._alpha_space_nonpolar_ratio[alpha_indices], dtype=float
            )
            beta_nonpolar_values = []
            for beta_index in beta_indices:
                alpha_group = snapshot._beta_alpha_index_list[beta_index]
                beta_nonpolar_values.append(
                    float(
                        np.sum(
                            snapshot._alpha_space[alpha_group]
                            * snapshot._alpha_space_nonpolar_ratio[alpha_group]
                        )
                    )
                )
            beta_nonpolar_space = np.asarray(beta_nonpolar_values, dtype=float)
            beta_scores = np.asarray(snapshot._beta_scores)[beta_indices]
            reported_pocket = state['pocket_properties'][pocket_index]
            source_artifact = 'output/topomt_snapshot.json'
            external_measurements = {
                'volume': ExternalMeasurement(
                    value=puw.quantity(float(pocket.space), 'angstroms**3'),
                    original_value=float(pocket.space),
                    original_unit='angstroms**3',
                    source_field='_pocket_space',
                    source_artifact=source_artifact,
                    run_id=run.run_id,
                    definition='sum of alpha-space tetrahedron volumes in pocket',
                    issue_url=None,
                    status='topomt_available',
                ),
                'nonpolar_volume': ExternalMeasurement(
                    value=puw.quantity(float(pocket.nonpolar_space), 'angstroms**3'),
                    original_value=float(pocket.nonpolar_space),
                    original_unit='angstroms**3',
                    source_field='_alpha_space_nonpolar_ratio',
                    source_artifact=source_artifact,
                    run_id=run.run_id,
                    definition='sum of alpha-space volume times nonpolar ratio',
                    issue_url=None,
                    status='topomt_available',
                ),
                'score': ExternalMeasurement(
                    value=float(pocket.score),
                    original_value=float(pocket.score),
                    original_unit='unspecified',
                    source_field='_beta_scores',
                    source_artifact=source_artifact,
                    run_id=run.run_id,
                    definition='sum of best probe scores of pocket beta sites',
                    issue_url=None,
                    status='topomt_available',
                ),
            }
            for name, source_property, unit, issue, definition in (
                (
                    'occupied_space',
                    'occupiedSpace',
                    'angstroms**3',
                    31,
                    'sum of alpha-space volumes for binder-contact alpha sites',
                ),
                (
                    'occupied_nonpolar_space',
                    'occupiedNonpolarSpace',
                    'angstroms**3',
                    32,
                    'sum of nonpolar alpha-space volumes for contact alpha sites',
                ),
                (
                    'occupancy',
                    'occupancy',
                    '1',
                    33,
                    'occupied alpha-space volume divided by pocket volume',
                ),
                (
                    'occupancy_nonpolar',
                    'occupancy_nonpolar',
                    '1',
                    34,
                    'occupied nonpolar volume divided by nonpolar pocket volume',
                ),
            ):
                reported_value = float(getattr(pocket, source_property))
                external_measurements[name] = ExternalMeasurement(
                    value=(
                        puw.quantity(reported_value, unit)
                        if unit.startswith('angstroms')
                        else reported_value
                    ),
                    original_value=reported_value,
                    original_unit=unit,
                    source_field=f'pocket_properties[{pocket_index}].{name}',
                    source_artifact=source_artifact,
                    run_id=run.run_id,
                    definition=definition,
                    issue_url=f'https://github.com/uibcdf/topomt/issues/{issue}',
                    status='external_only',
                )

            alpha_centers_nm = (
                np.asarray(snapshot._alpha_xyz[alpha_indices], dtype=float) / 10.0
            )
            alpha_radii_nm = (
                np.asarray(snapshot._alpha_radii[alpha_indices], dtype=float) / 10.0
            )
            beta_centers_nm = (
                np.asarray(snapshot._beta_xyz[beta_indices], dtype=float) / 10.0
                if len(beta_indices) > 0
                else np.zeros((0, 3), dtype=float)
            )

            topography.add_feature(
                Pocket(
                    atom_indices=sorted(atom_indices),
                    center=puw.quantity(
                        np.asarray(pocket.centroid, dtype=float) / 10.0, 'nm'
                    ),
                    volume=puw.quantity(float(pocket.space) / 1000.0, 'nm**3'),
                    score=float(pocket.score),
                    source='alphaspace2',
                    source_id=f'alphaspace2:{pocket_index}',
                    alpha_sphere_centers=puw.quantity(alpha_centers_nm, 'nm'),
                    alpha_sphere_radii=puw.quantity(alpha_radii_nm, 'nm'),
                    beta_centers=puw.quantity(beta_centers_nm, 'nm'),
                    alpha_indices=alpha_indices.tolist(),
                    beta_indices=list(beta_indices),
                    beta_alpha_indices=[
                        list(snapshot._beta_alpha_index_list[index])
                        for index in beta_indices
                    ],
                    alpha_lining_provider_atom_indices=alpha_lining_local.tolist(),
                    alpha_lining_atom_indices=selected_atom_indices[
                        alpha_lining_local
                    ].tolist(),
                    alpha_space=puw.quantity(alpha_space, 'angstroms**3'),
                    alpha_nonpolar_space=puw.quantity(
                        alpha_nonpolar_space, 'angstroms**3'
                    ),
                    alpha_nonpolar_ratio=np.asarray(
                        snapshot._alpha_space_nonpolar_ratio[alpha_indices], dtype=float
                    ),
                    alpha_contact=np.asarray(snapshot._alpha_contact)[
                        alpha_indices
                    ].astype(bool),
                    beta_space=puw.quantity(
                        np.asarray(snapshot._beta_space)[beta_indices], 'angstroms**3'
                    ),
                    beta_nonpolar_space=puw.quantity(
                        beta_nonpolar_space, 'angstroms**3'
                    ),
                    beta_scores=beta_scores.copy(),
                    beta_contact=np.asarray(snapshot._beta_contact)[
                        beta_indices
                    ].astype(bool),
                    nonpolar_volume=puw.quantity(
                        float(pocket.nonpolar_space) / 1000.0, 'nm**3'
                    ),
                    is_contact=bool(pocket.isContact),
                    occupied_space=puw.quantity(
                        float(pocket.occupiedSpace), 'angstroms**3'
                    ),
                    occupied_nonpolar_space=puw.quantity(
                        float(pocket.occupiedNonpolarSpace), 'angstroms**3'
                    ),
                    occupancy=float(pocket.occupancy),
                    occupancy_nonpolar=float(pocket.occupancy_nonpolar),
                    provider_snapshot_properties=reported_pocket,
                    beta_provider_properties=[
                        state['beta_properties'][index] for index in beta_indices
                    ],
                    provider_snapshot_source_artifact=source_artifact,
                    provider_run_id=run.run_id,
                    external_measurements=external_measurements,
                )
            )

        return topography


get_topography_with_alphaspace2 = get_topography
