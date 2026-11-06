"""Build the same attributed pyCASTA records for live and saved original runs."""

from typing import Any

import numpy as np

from topomt import Topography
from topomt import pyunitwizard as puw
from topomt.features import Pocket
from topomt.provider_output import ExternalMeasurement, ProviderRun


def result_to_topography(
    molecular_system: Any,
    state: dict[str, Any],
    protein_atom_indices: np.ndarray,
    run: ProviderRun,
    *,
    selection: Any,
    structure_indices: Any,
) -> Topography:
    """Attach validated original descriptors without changing their definitions."""
    result, coords, simplices = (
        state['result'],
        state['protein_coords'],
        state['simplices'],
    )
    topography = Topography(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
    )
    topography.add_provider_run(run)
    artifact = 'output/topomt_returned_result.json'
    for pocket_index, tetra_indices in enumerate(result['ranked_pockets']):
        local = np.unique(simplices[tetra_indices].reshape(-1))
        atom_indices = protein_atom_indices[local].tolist()
        volume = result['pocket_volumes'][pocket_index]
        score = result['ranking_scores'][pocket_index]

        def measurement(
            value, original, unit, field, definition, issue=None, status='external_only'
        ):
            return ExternalMeasurement(
                value=value,
                original_value=original,
                original_unit=unit,
                source_field=f'{field}[{pocket_index}]',
                source_artifact=artifact,
                run_id=run.run_id,
                definition=definition,
                issue_url=None
                if issue is None
                else f'https://github.com/uibcdf/topomt/issues/{issue}',
                status=status,
            )

        measurements = {
            'volume': measurement(
                puw.quantity(volume, 'angstroms**3'),
                volume,
                'angstroms**3',
                'pocket_volumes',
                'pyCASTA pocket volume reported by process_pdb',
                status='topomt_available' if np.isfinite(volume) else 'external_only',
            ),
            'score': measurement(
                score,
                score,
                'unspecified',
                'ranking_scores',
                'pyCASTA volume/flow-step/connectivity ranking score; unit unresolved',
                36,
            ),
        }
        representative_point = None
        points = result.get('representative_points', [])
        if pocket_index < len(points):
            original = points[pocket_index]
            representative_point = puw.quantity(np.asarray(original) / 10.0, 'nm')
            measurements['representative_point'] = measurement(
                representative_point,
                original,
                'angstroms',
                'representative_points',
                'Mean of pyCASTA pocket tetrahedron vertices with multiplicity',
                40,
            )
        for name, unit, field, issue, definition in (
            (
                'depth',
                'angstroms',
                'pocket_depths',
                37,
                'pyCASTA reported depth; source index-space formula under audit',
            ),
            (
                'mouth_area',
                'angstroms**2',
                'mouth_area',
                38,
                'pyCASTA mouth area computed from its mouth geometry',
            ),
            (
                'mouth_perimeter',
                'angstroms',
                'mouth_perimeter',
                39,
                'pyCASTA mouth boundary length',
            ),
        ):
            values = result.get(field, [])
            if pocket_index < len(values):
                original = values[pocket_index]
                value = puw.quantity(
                    original / (100 if name == 'mouth_area' else 10),
                    'nm**2' if name == 'mouth_area' else 'nm',
                )
                measurements[name] = measurement(
                    value, original, unit, field, definition, issue
                )
        validations = result.get('validation_methods', [])
        topography.add_feature(
            Pocket(
                atom_indices=sorted(atom_indices),
                center=puw.quantity(coords[local].mean(axis=0) / 10.0, 'nm'),
                representative_point=representative_point,
                volume=puw.quantity(volume / 1000.0, 'nm**3'),
                score=score,
                depth=measurements['depth'].value if 'depth' in measurements else None,
                mouth_area=measurements['mouth_area'].value
                if 'mouth_area' in measurements
                else None,
                mouth_perimeter=measurements['mouth_perimeter'].value
                if 'mouth_perimeter' in measurements
                else None,
                provider_tetrahedron_indices=tetra_indices,
                provider_validation_method=validations[pocket_index]
                if pocket_index < len(validations)
                else None,
                provider_run_id=run.run_id,
                provider_result_source_artifact=artifact,
                external_measurements=measurements,
                source='pycasta',
                source_id=f'pycasta:{pocket_index}',
            )
        )
    return topography
