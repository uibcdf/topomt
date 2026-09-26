import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy.spatial import Delaunay

from topomt import Topography
from topomt import pyunitwizard as puw
from topomt.features import Pocket
from topomt.provider_output import ExternalMeasurement, ProviderRun
from topomt.third_party._common import import_upstream_module, prepare_wrapper_input_pdb

_PYCASTA_WORKER = """
import json
from pathlib import Path
import sys

sys.path.insert(0, sys.argv[1])
import config
import run_analysis

result = run_analysis.process_pdb(sys.argv[2])
Path(sys.argv[3]).write_text(json.dumps(result, sort_keys=True, allow_nan=True))
Path(sys.argv[4]).write_text(json.dumps({
    'use_cgal': bool(config.USE_CGAL),
    'filter_alpha_by_sasa': bool(config.FILTER_ALPHA_BY_SASA),
    'save_alpha': bool(config.SAVE_ALPHA),
    'validation_method': config.VALIDATION_METHOD,
    'use_existing_results': bool(config.USE_EXISTING_RESULTS),
    'manual_alpha': config.MANUAL_ALPHA,
}, sort_keys=True))
"""


def _json_safe(value):
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not np.isfinite(value):
        return {'nonfinite': str(value)}
    return value


def get_topography(
    molecular_system,
    *,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    upstream_root: str | Path | None = None,
    **kwargs,
) -> Topography:
    """Run the upstream pyCASTA code and return a Topography."""

    if kwargs:
        unexpected = ', '.join(sorted(kwargs))
        raise TypeError(f'Unsupported library kwargs for pycasta: {unexpected}')

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
        output_dir = tmpdir / 'results'
        output_dir.mkdir()
        result_path = output_dir / 'topomt_returned_result.json'
        configuration_path = output_dir / 'topomt_execution_configuration.json'
        execution = subprocess.run(
            [
                sys.executable,
                '-c',
                _PYCASTA_WORKER,
                str(Path(run_analysis.__file__).resolve().parent),
                str(input_pdb),
                str(result_path),
                str(configuration_path),
            ],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            check=True,
        )
        (output_dir / 'topomt_stdout.txt').write_text(execution.stdout)
        (output_dir / 'topomt_stderr.txt').write_text(execution.stderr)
        result = json.loads(result_path.read_text())
        result_path.write_text(json.dumps(_json_safe(result), sort_keys=True))
        execution_configuration = json.loads(configuration_path.read_text())
        source_file = Path(run_analysis.__file__)
        with source_file.open('rb') as file_handle:
            source_sha256 = hashlib.file_digest(file_handle, 'sha256').hexdigest()
        run = ProviderRun.capture(
            'pycasta',
            'library',
            input_pdb,
            output_dir,
            metadata={
                'source_sha256': source_sha256,
                'version_tag': run_analysis.VERSION_TAG,
                'configuration': execution_configuration,
                'selection': selection,
                'structure_indices': _json_safe(structure_indices),
                'syntax': syntax,
                'selected_atom_indices': selected_atom_indices.tolist(),
            },
        )

        protein_coords_ang = np.asarray(result['protein_coords'], dtype=float)
        simplices = Delaunay(protein_coords_ang).simplices
        alpha_file = (
            output_dir / run_analysis.VERSION_TAG / f'{input_pdb.stem}.alpha.npz'
        )
        if not alpha_file.is_file():
            raise ValueError(
                'pyCASTA did not export an alpha array; tetrahedron-to-atom '
                'mapping cannot be verified'
            )
        with np.load(alpha_file) as alpha_output:
            original_tetrahedra = alpha_output['tetrahedra']
            original_protein_coords = alpha_output['protein_coords']
        if not np.array_equal(
            original_protein_coords, protein_coords_ang
        ) or not np.array_equal(original_tetrahedra, protein_coords_ang[simplices]):
            raise ValueError(
                'pyCASTA tetrahedron indexing differs from reconstructed '
                'Delaunay indexing; atom mapping is unsafe'
            )

        topography = Topography(
            molecular_system=molecular_system,
            selection=selection,
            structure_indices=structure_indices,
        )
        topography.add_provider_run(run)

        for pocket_index, tetra_indices in enumerate(result.get('ranked_pockets', [])):
            tetra_indices = np.asarray(tetra_indices, dtype=int)
            if np.any((tetra_indices < 0) | (tetra_indices >= len(simplices))):
                raise ValueError(
                    f'pyCASTA pocket {pocket_index} has invalid tetrahedron indices'
                )
            if tetra_indices.size == 0:
                raise ValueError(f'pyCASTA pocket {pocket_index} has no tetrahedra')

            local_atom_indices = np.unique(simplices[tetra_indices].reshape(-1))
            atom_indices = selected_atom_indices[local_atom_indices].tolist()
            center_nm = protein_coords_ang[local_atom_indices].mean(axis=0) / 10.0
            original_volume = float(result['pocket_volumes'][pocket_index])
            original_score = float(result['ranking_scores'][pocket_index])
            volume_nm3 = original_volume / 1000.0
            artifact = 'output/topomt_returned_result.json'
            external_measurements = {
                'volume': ExternalMeasurement(
                    value=puw.quantity(original_volume, 'angstroms**3'),
                    original_value=original_volume,
                    original_unit='angstroms**3',
                    source_field=f'pocket_volumes[{pocket_index}]',
                    source_artifact=artifact,
                    run_id=run.run_id,
                    definition='pyCASTA pocket volume reported by process_pdb',
                    issue_url=None,
                    status='topomt_available',
                ),
                'score': ExternalMeasurement(
                    value=original_score,
                    original_value=original_score,
                    original_unit='unspecified',
                    source_field=f'ranking_scores[{pocket_index}]',
                    source_artifact=artifact,
                    run_id=run.run_id,
                    definition='pyCASTA volume/flow-step/connectivity ranking score; unit unresolved',
                    issue_url='https://github.com/uibcdf/topomt/issues/36',
                    status='external_only',
                ),
            }

            representative_points = result.get('representative_points', [])
            representative_point = None
            if pocket_index < len(representative_points):
                original_point = [
                    float(component)
                    for component in representative_points[pocket_index]
                ]
                representative_point = puw.quantity(
                    np.asarray(original_point) / 10, 'nm'
                )
                external_measurements['representative_point'] = ExternalMeasurement(
                    value=representative_point,
                    original_value=original_point,
                    original_unit='angstroms',
                    source_field=f'representative_points[{pocket_index}]',
                    source_artifact=artifact,
                    run_id=run.run_id,
                    definition='Mean of pyCASTA pocket tetrahedron vertices with multiplicity',
                    issue_url='https://github.com/uibcdf/topomt/issues/40',
                    status='external_only',
                )

            for name, unit, source_field, issue, definition in (
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
                values = result.get(source_field, [])
                if pocket_index >= len(values):
                    continue
                reported_value = float(values[pocket_index])
                external_measurements[name] = ExternalMeasurement(
                    value=puw.quantity(
                        reported_value / (100 if name == 'mouth_area' else 10),
                        'nm**2' if name == 'mouth_area' else 'nm',
                    ),
                    original_value=reported_value,
                    original_unit=unit,
                    source_field=f'{source_field}[{pocket_index}]',
                    source_artifact=artifact,
                    run_id=run.run_id,
                    definition=definition,
                    issue_url=f'https://github.com/uibcdf/topomt/issues/{issue}',
                    status='external_only',
                )

            topography.add_feature(
                Pocket(
                    atom_indices=sorted(atom_indices),
                    center=puw.quantity(center_nm, 'nm'),
                    representative_point=representative_point,
                    volume=puw.quantity(volume_nm3, 'nm**3'),
                    score=original_score,
                    depth=external_measurements['depth'].value
                    if 'depth' in external_measurements
                    else None,
                    mouth_area=external_measurements['mouth_area'].value
                    if 'mouth_area' in external_measurements
                    else None,
                    mouth_perimeter=external_measurements['mouth_perimeter'].value
                    if 'mouth_perimeter' in external_measurements
                    else None,
                    provider_tetrahedron_indices=tetra_indices.tolist(),
                    provider_validation_method=result.get('validation_methods', [])[
                        pocket_index
                    ]
                    if pocket_index < len(result.get('validation_methods', []))
                    else None,
                    provider_run_id=run.run_id,
                    provider_result_source_artifact=artifact,
                    external_measurements=external_measurements,
                    source='pycasta',
                    source_id=f'pycasta:{pocket_index}',
                )
            )

        return topography
