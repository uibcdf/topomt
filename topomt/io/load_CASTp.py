import shutil
import tempfile
from os import PathLike
from pathlib import Path
from typing import Any

import molsysmt as msm

from topomt import pyunitwizard as puw
from topomt._private.path import (
    ensure_path_exists_and_is_dir,
    ensure_path_exists_and_is_file,
)
from topomt.provider_output import ExternalMeasurement, ProviderRun

_atom_label_format = '{atom_id}-{atom_name}/{group_name}/{chain_id}'

_CASTP_POCKET_MEASUREMENTS = (
    (
        'solvent_accessible_area',
        'Area_sa',
        'angstroms**2',
        'nm**2',
        41,
        'CASTp pocket area in the Richards solvent-accessible surface model',
    ),
    (
        'molecular_surface_area',
        'Area_ms',
        'angstroms**2',
        'nm**2',
        42,
        'CASTp pocket area in the Connolly molecular-surface model',
    ),
    (
        'solvent_accessible_volume',
        'Vol_sa',
        'angstroms**3',
        'nm**3',
        43,
        'CASTp pocket volume in the Richards solvent-accessible surface model',
    ),
    (
        'molecular_surface_volume',
        'Vol_ms',
        'angstroms**3',
        'nm**3',
        44,
        'CASTp pocket volume in the Connolly molecular-surface model',
    ),
)


def _feature_type_from_n_mouths(n_mouths: int | None) -> str:
    """Return the CAST-style feature type implied by the number of mouths."""

    if n_mouths is None:
        return 'pocket'
    if n_mouths == 0:
        return 'void'
    if n_mouths == 1:
        return 'pocket'
    if n_mouths == 2:
        return 'channel'
    return 'branched_channel'


def _parse_castp_atom_record_line(
    line: str, file_path: PathLike[str], expected_marker: str
) -> tuple[str, str, str, str, int]:
    """Parse a CASTp `.poc` or `.mouth` line using fixed-width PDB-style fields."""

    if len(line) < 75:
        raise ValueError(
            f"Malformed CASTp entry in '{file_path}': expected a fixed-width PDB-like record, got {len(line)} characters."
        )

    atom_id = line[6:11].strip()
    atom_name = line[12:16].strip()
    group_name = line[17:20].strip()
    chain_id = line[21].strip()
    feature_id_text = line[66:70].strip()
    marker = line[72:75].strip()

    if marker != expected_marker:
        raise ValueError(
            f"Unexpected marker '{marker}' in '{file_path}', expected '{expected_marker}'."
        )

    if not feature_id_text.isdigit():
        raise ValueError(
            f"Malformed CASTp entry in '{file_path}': expected numeric feature id in columns 67-70, got '{feature_id_text}'."
        )

    return atom_id, atom_name, group_name, chain_id, int(feature_id_text)


def _discover_castp_files_in_dir(base_path: PathLike[str]) -> dict[str, Path]:
    """Discover CASTp-related files in the given directory (non-recursive)."""
    base_path = Path(base_path)
    discovered: dict[str, Path] = {}

    extension_to_key = {
        '.poc': 'poc',
        '.pocInfo': 'poc_info',
        '.mouth': 'mouth',
        '.mouthInfo': 'mouth_info',
        '.pdb': 'pdb',
    }

    for file_path in base_path.iterdir():
        if not file_path.is_file():
            continue
        key = extension_to_key.get(file_path.suffix)
        if key and key not in discovered:
            discovered[key] = file_path

    return discovered


def _parse_poc_file(file_path: PathLike[str]):
    file_path = Path(file_path)
    poc_id_to_atom_labels: dict[int, set[str]] = {}

    with file_path.open('r', encoding='utf-8') as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            atom_id, atom_name, group_name, chain_id, poc_id = (
                _parse_castp_atom_record_line(raw_line.rstrip('\n'), file_path, 'POC')
            )

            poc_id_to_atom_labels.setdefault(poc_id, set()).add(
                _atom_label_format.format(
                    atom_id=atom_id,
                    atom_name=atom_name,
                    group_name=group_name,
                    chain_id=chain_id,
                )
            )

    return poc_id_to_atom_labels


def _parse_mouth_file(file_path: PathLike[str]):
    file_path = Path(file_path)
    mouth_id_to_atom_labels: dict[int, set[str]] = {}

    with file_path.open('r', encoding='utf-8') as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            atom_id, atom_name, group_name, chain_id, mouth_id = (
                _parse_castp_atom_record_line(raw_line.rstrip('\n'), file_path, 'M4P')
            )

            mouth_id_to_atom_labels.setdefault(mouth_id, set()).add(
                _atom_label_format.format(
                    atom_id=atom_id,
                    atom_name=atom_name,
                    group_name=group_name,
                    chain_id=chain_id,
                )
            )

    return mouth_id_to_atom_labels


def _parse_poc_info_file(file_path: PathLike[str]) -> dict[int, dict[str, Any]]:
    file_path = Path(file_path)
    poc_id_to_poc_data: dict[int, dict[str, Any]] = {}
    with file_path.open('r', encoding='utf-8') as handle:
        header_skipped = False
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if not header_skipped:
                header_skipped = True
                continue
            fields = line.split()
            if len(fields) < 10:
                raise ValueError(
                    f"Malformed entry in '{file_path}': expected at least 10 columns, got {len(fields)}."
                )
            poc_id = int(fields[2])
            entry = {
                'n_mouths': int(fields[3]),
                'solvent_accessible_area': puw.quantity(
                    float(fields[4]), 'angstroms**2'
                ),
                'molecular_surface_area': puw.quantity(
                    float(fields[5]), 'angstroms**2'
                ),
                'solvent_accessible_volume': puw.quantity(
                    float(fields[6]), 'angstroms**3'
                ),
                'molecular_surface_volume': puw.quantity(
                    float(fields[7]), 'angstroms**3'
                ),
                'length': puw.quantity(float(fields[8]), 'angstroms'),
                'corner_points_count': int(fields[9]),
            }
            if len(fields) > 10:
                mouth_ids: list[int] = []
                for token in fields[10:]:
                    cleaned = token.rstrip(',')
                    if cleaned.isdigit():
                        mouth_ids.append(int(cleaned))
                if mouth_ids:
                    entry['mouth_ids'] = set(mouth_ids)
            poc_id_to_poc_data[poc_id] = entry
    return poc_id_to_poc_data


def _parse_mouth_info_file(file_path: PathLike) -> dict[int, dict[str, Any]]:
    file_path = Path(file_path)
    mouth_id_to_mouth_data: dict[int, dict[str, Any]] = {}
    with file_path.open('r', encoding='utf-8') as handle:
        header_skipped = False
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if not header_skipped:
                header_skipped = True
                continue
            fields = line.split()
            if len(fields) < 9:
                raise ValueError(
                    f"Malformed entry in '{file_path}': expected at least 9 columns, got {len(fields)}."
                )
            mouth_id = int(fields[2])
            entry = {
                'pocket_ids': {mouth_id},
                'n_mouths': int(fields[3]),
                'solvent_accessible_area': puw.quantity(
                    float(fields[4]), 'angstroms**2'
                ),
                'molecular_surface_area': puw.quantity(
                    float(fields[5]), 'angstroms**2'
                ),
                'solvent_accessible_length': puw.quantity(
                    float(fields[6]), 'angstroms'
                ),
                'molecular_surface_length': puw.quantity(float(fields[7]), 'angstroms'),
                'n_triangles': int(fields[8]),
            }
            if len(fields) > 9:
                entry['extra_fields'] = fields[9:]
            mouth_id_to_mouth_data[mouth_id] = entry
    return mouth_id_to_mouth_data


def load_CASTp(
    poc_file=None,
    pocInfo_file=None,
    mouth_file=None,
    mouthInfo_file=None,
    pdb_file=None,
    zip_file=None,
    dir_path=None,
    molecular_system=None,
    submitted_input_pdb=None,
    provider_backend='files',
    provider_server=None,
    provider_jobid=None,
    probe_radius=None,
):
    """
    Load CASTp data.

    """

    extracted_from_zip = False
    temporary_dir = None

    if zip_file is not None:
        ensure_path_exists_and_is_file(zip_file)
        import zipfile

        temporary_dir = tempfile.TemporaryDirectory(prefix='topomt_castp_')
        extracted_from_zip = True

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(temporary_dir.name)
        dir_path = temporary_dir.name
        if submitted_input_pdb is not None:
            raw_zip_dir = Path(dir_path) / 'raw_server_zip'
            raw_zip_dir.mkdir()
            shutil.copy2(zip_file, raw_zip_dir / Path(zip_file).name)

    try:
        if dir_path is not None:
            ensure_path_exists_and_is_dir(dir_path)
            dict_of_files_cast_files = _discover_castp_files_in_dir(dir_path)
            poc_file = dict_of_files_cast_files.get('poc', None)
            pocInfo_file = dict_of_files_cast_files.get('poc_info', None)
            mouth_file = dict_of_files_cast_files.get('mouth', None)
            mouthInfo_file = dict_of_files_cast_files.get('mouth_info', None)
            pdb_file = dict_of_files_cast_files.get('pdb', None)

        poc_id_to_atom_labels = (
            _parse_poc_file(poc_file) if poc_file is not None else None
        )
        poc_id_to_poc_data = (
            _parse_poc_info_file(pocInfo_file) if pocInfo_file is not None else None
        )
        mouth_id_to_atom_labels = (
            _parse_mouth_file(mouth_file) if mouth_file is not None else None
        )
        mouth_id_to_mouth_data = (
            _parse_mouth_info_file(mouthInfo_file)
            if mouthInfo_file is not None
            else None
        )

        from topomt.topography.Topography import Topography

        if molecular_system is None and pdb_file is not None:
            if extracted_from_zip:
                molecular_system = msm.convert(pdb_file, to_form='molsysmt.MolSys')
            else:
                molecular_system = pdb_file
        topography = Topography(molecular_system=molecular_system)
        provider_run = None
        if dir_path is not None:
            provider_input = submitted_input_pdb or zip_file or pdb_file or poc_file
            if provider_input is not None:
                provider_run = ProviderRun.capture(
                    'castp',
                    provider_backend,
                    provider_input,
                    dir_path,
                    metadata={
                        'server': provider_server,
                        'jobid': provider_jobid,
                        'probe_radius_angstroms': probe_radius,
                    },
                )
                topography.add_provider_run(provider_run)

        poc_id_to_feature_id = dict()
        mouth_id_to_feature_id = dict()

        poc_ids = set(poc_id_to_atom_labels or {}) | set(poc_id_to_poc_data or {})
        for poc_id in sorted(poc_ids):
            atom_labels = (poc_id_to_atom_labels or {}).get(poc_id)
            source_id = 'Pocket ' + str(poc_id)
            args_dict = {}
            if provider_run is not None:
                args_dict['provider_run_id'] = provider_run.run_id
                if atom_labels is not None and poc_file is not None:
                    args_dict['provider_atom_source_artifact'] = (
                        f'output/{poc_file.name}'
                    )
                if pocInfo_file is not None:
                    args_dict['provider_result_source_artifact'] = (
                        f'output/{pocInfo_file.name}'
                    )
            feature_type = 'pocket'
            if poc_id_to_poc_data is not None and poc_id in poc_id_to_poc_data:
                feature_type = _feature_type_from_n_mouths(
                    poc_id_to_poc_data[poc_id]['n_mouths']
                )
                args_dict['solvent_accessible_area'] = poc_id_to_poc_data[poc_id][
                    'solvent_accessible_area'
                ]
                args_dict['molecular_surface_area'] = poc_id_to_poc_data[poc_id][
                    'molecular_surface_area'
                ]
                args_dict['solvent_accessible_volume'] = poc_id_to_poc_data[poc_id][
                    'solvent_accessible_volume'
                ]
                args_dict['molecular_surface_volume'] = poc_id_to_poc_data[poc_id][
                    'molecular_surface_volume'
                ]
                args_dict['length'] = poc_id_to_poc_data[poc_id]['length']
                args_dict['corner_points_count'] = poc_id_to_poc_data[poc_id][
                    'corner_points_count'
                ]
                args_dict['n_mouths'] = poc_id_to_poc_data[poc_id]['n_mouths']
                attributed_measurements = {}
                for (
                    name,
                    original_field,
                    original_unit,
                    canonical_unit,
                    issue,
                    definition,
                ) in _CASTP_POCKET_MEASUREMENTS:
                    original_quantity = poc_id_to_poc_data[poc_id][name]
                    original_value = float(
                        puw.get_value(original_quantity, to_unit=original_unit)
                    )
                    canonical_quantity = puw.quantity(
                        float(puw.get_value(original_quantity, to_unit=canonical_unit)),
                        canonical_unit,
                    )
                    args_dict[name] = canonical_quantity
                    if provider_run is not None and pocInfo_file is not None:
                        attributed_measurements[name] = ExternalMeasurement(
                            value=canonical_quantity,
                            original_value=original_value,
                            original_unit=original_unit,
                            source_field=f'pocInfo[{poc_id}].{original_field}',
                            source_artifact=f'output/{pocInfo_file.name}',
                            run_id=provider_run.run_id,
                            definition=definition,
                            issue_url=f'https://github.com/uibcdf/topomt/issues/{issue}',
                            status='external_only',
                        )
                if attributed_measurements:
                    args_dict['external_measurements'] = attributed_measurements
            feature_id = topography.add_new_feature(
                feature_type=feature_type,
                atom_labels=atom_labels,
                atom_label_format=_atom_label_format,
                source='CASTp',
                source_id=source_id,
                **args_dict,
            )
            poc_id_to_feature_id[poc_id] = feature_id

        mouth_ids = set(mouth_id_to_atom_labels or {}) | {
            mouth_id
            for mouth_id, data in (mouth_id_to_mouth_data or {}).items()
            if data['n_mouths'] > 0
        }
        for mouth_id in sorted(mouth_ids):
            atom_labels = (mouth_id_to_atom_labels or {}).get(mouth_id)
            source_id = 'Mouth ' + str(mouth_id)
            args_dict = {}
            if provider_run is not None:
                args_dict['provider_run_id'] = provider_run.run_id
                if atom_labels is not None and mouth_file is not None:
                    args_dict['provider_atom_source_artifact'] = (
                        f'output/{mouth_file.name}'
                    )
                if mouthInfo_file is not None:
                    args_dict['provider_result_source_artifact'] = (
                        f'output/{mouthInfo_file.name}'
                    )
            if (
                mouth_id_to_mouth_data is not None
                and mouth_id in mouth_id_to_mouth_data
            ):
                args_dict['solvent_accessible_area'] = mouth_id_to_mouth_data[mouth_id][
                    'solvent_accessible_area'
                ]
                args_dict['molecular_surface_area'] = mouth_id_to_mouth_data[mouth_id][
                    'molecular_surface_area'
                ]
                args_dict['solvent_accessible_length'] = mouth_id_to_mouth_data[
                    mouth_id
                ]['solvent_accessible_length']
                args_dict['molecular_surface_length'] = mouth_id_to_mouth_data[
                    mouth_id
                ]['molecular_surface_length']
                args_dict['n_triangles'] = mouth_id_to_mouth_data[mouth_id][
                    'n_triangles'
                ]
                args_dict['n_mouths'] = mouth_id_to_mouth_data[mouth_id]['n_mouths']
                args_dict['provider_aggregates_multiple_mouths'] = (
                    args_dict['n_mouths'] > 1
                )
            feature_id = topography.add_new_feature(
                feature_type='mouth',
                atom_labels=atom_labels,
                atom_label_format=_atom_label_format,
                source='CASTp',
                source_id=source_id,
                **args_dict,
            )
            mouth_id_to_feature_id[mouth_id] = feature_id
            if mouth_id in poc_id_to_feature_id:
                topography.connect_features(feature_id, poc_id_to_feature_id[mouth_id])

        return topography
    finally:
        if temporary_dir is not None:
            temporary_dir.cleanup()
