import hashlib
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


def _json_ready(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _normalize_upstream_pocketeer_kwargs(kwargs):
    normalized = dict(kwargs)

    distance_keys = ('r_min', 'r_max', 'polar_probe_radius', 'merge_distance')
    for key in distance_keys:
        value = normalized.get(key, None)
        if value is not None and puw.is_quantity(value):
            normalized[key] = float(puw.get_value(value, to_unit='angstroms'))

    sasa_threshold = normalized.get('sasa_threshold', None)
    if sasa_threshold is not None and puw.is_quantity(sasa_threshold):
        normalized['sasa_threshold'] = float(
            puw.get_value(sasa_threshold, to_unit='angstroms**2')
        )

    min_spheres = normalized.get('min_spheres', None)
    if min_spheres is not None:
        normalized['min_spheres'] = int(min_spheres)

    return normalized


@dep_digest('pocketeer', when={'upstream_root': None})
@dep_digest('biotite')
def get_topography(
    molecular_system,
    *,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    upstream_root: str | None = None,
    **kwargs,
) -> Topography:
    """Run the upstream Pocketeer Python library and return a Topography."""

    with tempfile.TemporaryDirectory(prefix='topomt_pocketeer_') as tmpdir_name:
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
        normalized_kwargs = _normalize_upstream_pocketeer_kwargs(kwargs)
        pockets = upstream.find_pockets(
            atomarray,
            **normalized_kwargs,
        )
        if len(atomarray) != len(selected_atom_indices):
            raise ValueError(
                'Pocketeer input atom count differs from the selected molecular system; '
                'atom identities cannot be mapped safely.'
            )

        import biotite.structure as struc

        filtered_atom_indices: np.ndarray = np.arange(len(atomarray), dtype=int)
        if normalized_kwargs.get('ignore_hydrogens', True):
            filtered_atom_indices = filtered_atom_indices[
                atomarray.element[filtered_atom_indices] != 'H'
            ]
        if normalized_kwargs.get('ignore_water', True):
            filtered_atom_indices = filtered_atom_indices[
                ~struc.filter_solvent(atomarray[filtered_atom_indices])
            ]
        if normalized_kwargs.get('ignore_hetero', True):
            filtered_atom_indices = filtered_atom_indices[
                ~atomarray.hetero[filtered_atom_indices]
            ]

        output_dir = tmpdir / 'results'
        output_dir.mkdir()
        upstream.write_pockets_json(str(output_dir / 'pocketeer_pockets.json'), pockets)
        (output_dir / 'topomt_masks.json').write_text(
            json.dumps(
                {
                    'schema_version': 1,
                    'pockets': [
                        {
                            'pocket_id': pocket.pocket_id,
                            'mask': np.asarray(pocket.mask, dtype=bool).tolist(),
                        }
                        for pocket in pockets
                    ],
                },
                sort_keys=True,
            )
        )
        api_file = Path(upstream.find_pockets.__code__.co_filename)
        with api_file.open('rb') as file_handle:
            api_sha256 = hashlib.file_digest(file_handle, 'sha256').hexdigest()
        run = ProviderRun.capture(
            'pocketeer',
            'library',
            input_pdb,
            output_dir,
            metadata={
                'version': upstream.__version__,
                'api_sha256': api_sha256,
                'parameters': _json_ready(normalized_kwargs),
                'selection': selection,
                'structure_indices': _json_ready(structure_indices),
                'syntax': syntax,
                'selected_atom_indices': selected_atom_indices.tolist(),
                'filtered_input_atom_indices': filtered_atom_indices.tolist(),
            },
        )

        topography = Topography(
            molecular_system=molecular_system,
            selection=selection,
            structure_indices=structure_indices,
        )
        topography.add_provider_run(run)

        for pocket in pockets:
            local_atom_indices = np.flatnonzero(np.asarray(pocket.mask, dtype=bool))
            atom_indices = selected_atom_indices[local_atom_indices].tolist()
            sphere_ids = [sphere.sphere_id for sphere in pocket.spheres]
            alpha_sphere_centers = np.asarray(
                [sphere.center for sphere in pocket.spheres],
                dtype=float,
            )
            alpha_sphere_radii = np.asarray(
                [sphere.radius for sphere in pocket.spheres],
                dtype=float,
            )
            alpha_sphere_mean_sasa = np.asarray(
                [sphere.mean_sasa for sphere in pocket.spheres], dtype=float
            )
            sphere_provider_atom_indices = [
                sphere.atom_indices.copy() for sphere in pocket.spheres
            ]
            sphere_atom_indices = [
                selected_atom_indices[
                    filtered_atom_indices[sphere.atom_indices]
                ].tolist()
                for sphere in pocket.spheres
            ]
            artifact = 'output/pocketeer_pockets.json'
            external_measurements = {
                'volume': ExternalMeasurement(
                    value=puw.quantity(float(pocket.volume), 'angstroms**3'),
                    original_value=float(pocket.volume),
                    original_unit='angstroms**3',
                    source_field='volume',
                    source_artifact=artifact,
                    run_id=run.run_id,
                    definition='Pocketeer voxel-estimated pocket volume',
                    issue_url=None,
                    status='topomt_available',
                ),
                'score': ExternalMeasurement(
                    value=float(pocket.score),
                    original_value=float(pocket.score),
                    original_unit='1',
                    source_field='score',
                    source_artifact=artifact,
                    run_id=run.run_id,
                    definition='Pocketeer pocket quality score',
                    issue_url=None,
                    status='topomt_available',
                ),
            }
            sphere_measurements = {}
            for index, sphere in enumerate(pocket.spheres):
                sphere_measurements[sphere.sphere_id] = {
                    'radius': ExternalMeasurement(
                        value=puw.quantity(float(sphere.radius), 'angstroms'),
                        original_value=float(sphere.radius),
                        original_unit='angstroms',
                        source_field=f'spheres[{index}].radius',
                        source_artifact=artifact,
                        run_id=run.run_id,
                        definition='radius of the alpha sphere through four atoms',
                        issue_url=None,
                        status='topomt_available',
                    ),
                    'mean_sasa': ExternalMeasurement(
                        value=puw.quantity(float(sphere.mean_sasa), 'angstroms**2'),
                        original_value=float(sphere.mean_sasa),
                        original_unit='angstroms**2',
                        source_field=f'spheres[{index}].mean_sasa',
                        source_artifact=artifact,
                        run_id=run.run_id,
                        definition='mean Biotite SASA of four defining atoms',
                        issue_url='https://github.com/uibcdf/topomt/issues/30',
                        status='external_only',
                    ),
                }

            topography.add_feature(
                Pocket(
                    atom_indices=sorted(atom_indices),
                    center=puw.quantity(
                        np.asarray(pocket.centroid, dtype=float) / 10.0, 'nm'
                    ),
                    volume=puw.quantity(float(pocket.volume) / 1000.0, 'nm**3'),
                    score=float(pocket.score),
                    source='pocketeer',
                    source_id=f'pocketeer:{pocket.pocket_id}',
                    alpha_sphere_centers=puw.quantity(
                        alpha_sphere_centers / 10.0, 'nm'
                    ),
                    alpha_sphere_radii=puw.quantity(alpha_sphere_radii / 10.0, 'nm'),
                    alpha_sphere_mean_sasa=puw.quantity(
                        alpha_sphere_mean_sasa, 'angstroms**2'
                    ),
                    alpha_sphere_ids=sphere_ids,
                    alpha_sphere_provider_atom_indices=sphere_provider_atom_indices,
                    alpha_sphere_defining_atom_indices=sphere_atom_indices,
                    n_alpha_spheres=len(pocket.spheres),
                    n_provider_residues=len(pocket.residues),
                    provider_residues=list(pocket.residues),
                    provider_mask=np.asarray(pocket.mask, dtype=bool).copy(),
                    provider_mask_source_artifact='output/topomt_masks.json',
                    provider_run_id=run.run_id,
                    external_measurements=external_measurements,
                    alpha_sphere_measurements=sphere_measurements,
                )
            )

        return topography
