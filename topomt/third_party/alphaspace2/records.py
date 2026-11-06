"""Map original AlphaSpace2 snapshot fields through one TopoMT converter."""

from typing import Any

import numpy as np

from topomt import Topography
from topomt import pyunitwizard as puw
from topomt.features import Pocket
from topomt.provider_output import ExternalMeasurement, ProviderRun


def _scalar(value: Any) -> float:
    if isinstance(value, dict):
        return float(value['nonfinite'])
    return float(value)


def _length(value: Any) -> Any:
    return puw.convert(
        puw.quantity(np.asarray(value, dtype=float), 'angstroms'), to_unit='nm'
    )


def _volume(value: Any) -> Any:
    return puw.convert(puw.quantity(float(value), 'angstroms**3'), to_unit='nm**3')


def snapshot_to_topography(
    molecular_system: Any,
    state: dict[str, Any],
    selected_atom_indices: np.ndarray,
    run: ProviderRun,
    *,
    selection: Any,
    structure_indices: Any,
    min_vertices: int,
) -> Topography:
    """Map captured fields without rerunning AlphaSpace2 clustering or scoring.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Full receptor source whose ordinal map has been validated.
    state : dict
        Original captured snapshot or a strictly validated saved snapshot.
    selected_atom_indices : numpy.ndarray
        Submitted receptor row to source index map.
    run : ProviderRun
        Original evidence, retained unchanged on every record.
    selection : str or sequence of int
        Recorded receptor selection.
    structure_indices : int or sequence of int
        Recorded single receptor frame.
    min_vertices : int
        Recorded positive adapter filter, not an original clustering option.

    Returns
    -------
    Topography
        Original fields and units in the existing pocket representation.

    Raises
    ------
    ValueError
        If an already admitted mapping or geometry violates its contract.
    """
    arrays = {
        name: np.asarray(state[name])
        for name in (
            '_alpha_lining',
            '_alpha_space',
            '_alpha_space_nonpolar_ratio',
            '_beta_scores',
            '_alpha_xyz',
            '_alpha_radii',
            '_beta_xyz',
            '_alpha_contact',
            '_beta_space',
            '_beta_contact',
        )
    }
    topography = Topography(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
    )
    topography.add_provider_run(run)

    for pocket_index, reported_pocket in enumerate(state['pocket_properties']):
        alpha_indices = np.asarray(reported_pocket['alpha_indices'], dtype=int)
        if alpha_indices.size < min_vertices:
            continue

        lining_local_indices = np.unique(
            arrays['_alpha_lining'][alpha_indices].reshape(-1)
        )
        atom_indices = selected_atom_indices[lining_local_indices].tolist()
        beta_indices = state['_pocket_beta_index_list'][pocket_index]
        alpha_lining_local = np.asarray(
            arrays['_alpha_lining'][alpha_indices], dtype=int
        )
        alpha_space = np.asarray(arrays['_alpha_space'][alpha_indices], dtype=float)
        alpha_nonpolar_space = alpha_space * np.asarray(
            arrays['_alpha_space_nonpolar_ratio'][alpha_indices], dtype=float
        )
        beta_nonpolar_values = []
        for beta_index in beta_indices:
            alpha_group = state['_beta_alpha_index_list'][beta_index]
            beta_nonpolar_values.append(
                float(
                    np.sum(
                        arrays['_alpha_space'][alpha_group]
                        * arrays['_alpha_space_nonpolar_ratio'][alpha_group]
                    )
                )
            )
        beta_nonpolar_space: np.ndarray = np.asarray(beta_nonpolar_values, dtype=float)
        beta_scores = np.asarray(arrays['_beta_scores'])[beta_indices]
        source_artifact = 'output/topomt_snapshot.json'
        external_measurements = {
            'volume': ExternalMeasurement(
                value=puw.quantity(float(reported_pocket['space']), 'angstroms**3'),
                original_value=float(reported_pocket['space']),
                original_unit='angstroms**3',
                source_field='_pocket_space',
                source_artifact=source_artifact,
                run_id=run.run_id,
                definition='sum of alpha-space tetrahedron volumes in pocket',
                issue_url=None,
                status='topomt_available',
            ),
            'nonpolar_volume': ExternalMeasurement(
                value=puw.quantity(
                    float(reported_pocket['nonpolar_space']), 'angstroms**3'
                ),
                original_value=float(reported_pocket['nonpolar_space']),
                original_unit='angstroms**3',
                source_field='_alpha_space_nonpolar_ratio',
                source_artifact=source_artifact,
                run_id=run.run_id,
                definition='sum of alpha-space volume times nonpolar ratio',
                issue_url=None,
                status='topomt_available',
            ),
            'score': ExternalMeasurement(
                value=float(reported_pocket['score']),
                original_value=float(reported_pocket['score']),
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
            reported_value = _scalar(reported_pocket[name])
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

        alpha_centers_nm = _length(arrays['_alpha_xyz'][alpha_indices])
        alpha_radii_nm = _length(arrays['_alpha_radii'][alpha_indices])
        beta_centers_nm = _length(arrays['_beta_xyz'][beta_indices])

        topography.add_feature(
            Pocket(
                atom_indices=sorted(atom_indices),
                center=_length(state['_pocket_xyz'][pocket_index]),
                volume=_volume(reported_pocket['space']),
                score=float(reported_pocket['score']),
                source='alphaspace2',
                source_id=f'alphaspace2:{pocket_index}',
                alpha_sphere_centers=alpha_centers_nm,
                alpha_sphere_radii=alpha_radii_nm,
                beta_centers=beta_centers_nm,
                alpha_indices=alpha_indices.tolist(),
                beta_indices=list(beta_indices),
                beta_alpha_indices=[
                    list(state['_beta_alpha_index_list'][index])
                    for index in beta_indices
                ],
                alpha_lining_provider_atom_indices=alpha_lining_local.tolist(),
                alpha_lining_atom_indices=selected_atom_indices[
                    alpha_lining_local
                ].tolist(),
                alpha_space=puw.quantity(alpha_space, 'angstroms**3'),
                alpha_nonpolar_space=puw.quantity(alpha_nonpolar_space, 'angstroms**3'),
                alpha_nonpolar_ratio=np.asarray(
                    arrays['_alpha_space_nonpolar_ratio'][alpha_indices], dtype=float
                ),
                alpha_contact=np.asarray(arrays['_alpha_contact'])[
                    alpha_indices
                ].astype(bool),
                beta_space=puw.quantity(
                    np.asarray(arrays['_beta_space'])[beta_indices], 'angstroms**3'
                ),
                beta_nonpolar_space=puw.quantity(beta_nonpolar_space, 'angstroms**3'),
                beta_scores=beta_scores.copy(),
                beta_contact=np.asarray(arrays['_beta_contact'])[beta_indices].astype(
                    bool
                ),
                nonpolar_volume=_volume(reported_pocket['nonpolar_space']),
                is_contact=bool(reported_pocket['is_contact']),
                occupied_space=puw.quantity(
                    float(reported_pocket['occupied_space']), 'angstroms**3'
                ),
                occupied_nonpolar_space=puw.quantity(
                    float(reported_pocket['occupied_nonpolar_space']), 'angstroms**3'
                ),
                occupancy=_scalar(reported_pocket['occupancy']),
                occupancy_nonpolar=_scalar(reported_pocket['occupancy_nonpolar']),
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
