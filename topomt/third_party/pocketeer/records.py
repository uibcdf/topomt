"""Convert original Pocketeer records through the shared TopoMT mapping."""

from typing import Any

import numpy as np

from topomt import Topography
from topomt import pyunitwizard as puw
from topomt.features import Pocket
from topomt.provider_output import ExternalMeasurement, ProviderRun


def pockets_to_topography(
    molecular_system: Any,
    pockets: list[Any],
    selected_atom_indices: np.ndarray,
    filtered_atom_indices: np.ndarray,
    run: ProviderRun,
    *,
    selection: Any,
    structure_indices: Any,
) -> Topography:
    """Map original or validated saved records without recomputing measurements.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Full source inventory and coordinates.
    pockets : list
        Original records or decoded records with their masks and sphere fields.
    selected_atom_indices : numpy.ndarray
        Submitted PDB row to source-atom map.
    filtered_atom_indices : numpy.ndarray
        Original detector's filtered to submitted-row map.
    run : ProviderRun
        Original execution evidence; its identity is retained on every field.
    selection : str or sequence of int
        Source selection.
    structure_indices : int or sequence of int
        One source frame.

    Returns
    -------
    Topography
        Mapped original measurements, geometry and available-empty pockets.

    Raises
    ------
    ValueError
        If a mapping or geometry violates Topography's contracts.
    """
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
            selected_atom_indices[filtered_atom_indices[sphere.atom_indices]].tolist()
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
                center=puw.convert(
                    puw.quantity(np.asarray(pocket.centroid, dtype=float), 'angstroms'),
                    to_unit='nm',
                ),
                volume=puw.convert(
                    puw.quantity(float(pocket.volume), 'angstroms**3'), to_unit='nm**3'
                ),
                score=float(pocket.score),
                source='pocketeer',
                source_id=f'pocketeer:{pocket.pocket_id}',
                alpha_sphere_centers=puw.convert(
                    puw.quantity(alpha_sphere_centers, 'angstroms'), to_unit='nm'
                ),
                alpha_sphere_radii=puw.convert(
                    puw.quantity(alpha_sphere_radii, 'angstroms'), to_unit='nm'
                ),
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
