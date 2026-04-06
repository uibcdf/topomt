from topomt import pyunitwizard as puw
import molsysmt as msm
from topomt._private.path import ensure_path_exists_and_is_file, ensure_path_exists_and_is_dir

from pathlib import Path
from os import PathLike
from typing import Any
import tempfile

_atom_label_format="{atom_id}-{atom_name}/{group_name}/{chain_id}"


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


def _parse_castp_atom_record_line(line: str, file_path: PathLike[str], expected_marker: str) -> tuple[str, str, str, str, int]:
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
        raise ValueError(f"Unexpected marker '{marker}' in '{file_path}', expected '{expected_marker}'.")

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
        ".poc": "poc",
        ".pocInfo": "poc_info",
        ".mouth": "mouth",
        ".mouthInfo": "mouth_info",
        ".pdb": "pdb",
    }

    for file_path in base_path.iterdir():
        if not file_path.is_file():
            continue
        key = extension_to_key.get(file_path.suffix)
        if key and key not in discovered:
            discovered[key] = file_path

    return discovered

def _parse_poc_file(file_path: PathLike[str]):

    poc_id_to_atom_labels = dict()

    with file_path.open('r', encoding='utf-8') as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            atom_id, atom_name, group_name, chain_id, poc_id = _parse_castp_atom_record_line(
                raw_line.rstrip('\n'), file_path, 'POC'
            )

            poc_id_to_atom_labels.setdefault(poc_id, set()).add(
                _atom_label_format.format(atom_id=atom_id, atom_name=atom_name, group_name=group_name, chain_id=chain_id)
            )

    return poc_id_to_atom_labels

def _parse_mouth_file(file_path: PathLike[str]):

    mouth_id_to_atom_labels = dict()

    with file_path.open('r', encoding='utf-8') as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            atom_id, atom_name, group_name, chain_id, mouth_id = _parse_castp_atom_record_line(
                raw_line.rstrip('\n'), file_path, 'M4P'
            )

            mouth_id_to_atom_labels.setdefault(mouth_id, set()).add(
                _atom_label_format.format(atom_id=atom_id, atom_name=atom_name, group_name=group_name, chain_id=chain_id)
            )

    return mouth_id_to_atom_labels


def _parse_poc_info_file(file_path: PathLike[str]) -> dict[str, dict[str, Any]]:
    poc_id_to_poc_data: dict[int, dict[str, Any]] = {}
    with file_path.open("r", encoding="utf-8") as handle:
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
                "n_mouths": int(fields[3]),
                "solvent_accessible_area": puw.quantity(float(fields[4]), "angstroms**2"),
                "molecular_surface_area": puw.quantity(float(fields[5]), "angstroms**2"),
                "solvent_accessible_volume": puw.quantity(float(fields[6]), "angstroms**3"),
                "molecular_surface_volume": puw.quantity(float(fields[7]), "angstroms**3"),
                "length": puw.quantity(float(fields[8]), "angstroms"),
                "corner_points_count": int(fields[9]),
            }
            if len(fields) > 10:
                mouth_ids: list[int] = []
                for token in fields[10:]:
                    cleaned = token.rstrip(",")
                    if cleaned.isdigit():
                        mouth_ids.append(int(cleaned))
                if mouth_ids:
                    entry["mouth_ids"] = set(mouth_ids)
            poc_id_to_poc_data[poc_id] = entry
    return poc_id_to_poc_data


def _parse_mouth_info_file(file_path: PathLike) -> dict[int, dict[str, Any]]:
    mouth_id_to_mouth_data: dict[int, dict[str, Any]] = {}
    with file_path.open("r", encoding="utf-8") as handle:
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
                "pocket_ids": set([
                    int(fields[3])
                ]) if fields[3].rstrip(":,").isdigit() else set(),
                "solvent_accessible_area": puw.quantity(float(fields[4]), "angstroms**2"),
                "molecular_surface_area": puw.quantity(float(fields[5]), "angstroms**2"),
                "solvent_accessible_length": puw.quantity(float(fields[6]), "angstroms"),
                "molecular_surface_length": puw.quantity(float(fields[7]), "angstroms"),
                "n_triangles": int(fields[8]),
            }
            if len(fields) > 9:
                for token in fields[9:]:
                    cleaned = token.rstrip(",")
                    if cleaned.isdigit():
                       entry.setdefault("pocket_ids", set()).add(int(cleaned))
            if entry.get("pocket_ids"):
                entry["pocket_ids"] = entry["pocket_ids"]
            mouth_id_to_mouth_data[mouth_id] = entry
    return mouth_id_to_mouth_data


def load_CASTp(poc_file=None, pocInfo_file=None, mouth_file=None, mouthInfo_file=None, pdb_file=None,
               zip_file=None, dir_path=None, molecular_system=None):
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

    try:
        if dir_path is not None:
            ensure_path_exists_and_is_dir(dir_path)
            dict_of_files_cast_files = _discover_castp_files_in_dir(dir_path)
            poc_file = dict_of_files_cast_files.get('poc', None)
            pocInfo_file = dict_of_files_cast_files.get('poc_info', None)
            mouth_file = dict_of_files_cast_files.get('mouth', None)
            mouthInfo_file = dict_of_files_cast_files.get('mouth_info', None)
            pdb_file = dict_of_files_cast_files.get('pdb', None)

        poc_id_to_atom_labels = _parse_poc_file(poc_file) if poc_file is not None else None
        poc_id_to_poc_data = _parse_poc_info_file(pocInfo_file) if pocInfo_file is not None else None
        mouth_id_to_atom_labels = _parse_mouth_file(mouth_file) if mouth_file is not None else None
        mouth_id_to_mouth_data = _parse_mouth_info_file(mouthInfo_file) if mouthInfo_file is not None else None

        from topomt.topography.Topography import Topography
        if molecular_system is None and pdb_file is not None:
            if extracted_from_zip:
                molecular_system = msm.convert(pdb_file, to_form='molsysmt.MolSys')
            else:
                molecular_system = pdb_file
        topography = Topography(molecular_system=molecular_system)

        poc_id_to_feature_id = dict()
        mouth_id_to_feature_id = dict()

        for poc_id, atom_labels in poc_id_to_atom_labels.items():
            source_id = 'Pocket ' + str(poc_id)
            args_dict = {}
            feature_type = 'pocket'
            if poc_id in poc_id_to_poc_data:
                feature_type = _feature_type_from_n_mouths(poc_id_to_poc_data[poc_id]['n_mouths'])
                args_dict['solvent_accessible_area'] = poc_id_to_poc_data[poc_id]['solvent_accessible_area']
                args_dict['molecular_surface_area'] = poc_id_to_poc_data[poc_id]['molecular_surface_area']
                args_dict['solvent_accessible_volume'] = poc_id_to_poc_data[poc_id]['solvent_accessible_volume']
                args_dict['molecular_surface_volume'] = poc_id_to_poc_data[poc_id]['molecular_surface_volume']
                args_dict['length'] = poc_id_to_poc_data[poc_id]['length']
                args_dict['corner_points_count'] = poc_id_to_poc_data[poc_id]['corner_points_count']
                args_dict['n_mouths'] = poc_id_to_poc_data[poc_id]['n_mouths']
            feature_id = topography.add_new_feature(feature_type=feature_type, atom_labels=atom_labels,
                                                    atom_label_format=_atom_label_format, source='CASTp',
                                                    source_id=source_id, **args_dict)
            poc_id_to_feature_id[poc_id] = feature_id

        for mouth_id, atom_labels in mouth_id_to_atom_labels.items():
            source_id = 'Mouth ' + str(mouth_id)
            args_dict = {}
            if mouth_id in mouth_id_to_mouth_data:
                args_dict['solvent_accessible_area'] = mouth_id_to_mouth_data[mouth_id]['solvent_accessible_area']
                args_dict['molecular_surface_area'] = mouth_id_to_mouth_data[mouth_id]['molecular_surface_area']
                args_dict['solvent_accessible_length'] = mouth_id_to_mouth_data[mouth_id]['solvent_accessible_length']
                args_dict['molecular_surface_length'] = mouth_id_to_mouth_data[mouth_id]['molecular_surface_length']
                args_dict['n_triangles'] = mouth_id_to_mouth_data[mouth_id]['n_triangles']
            feature_id = topography.add_new_feature(feature_type='mouth', atom_labels=atom_labels,
                                                    atom_label_format=_atom_label_format, source='CASTp',
                                                    source_id=source_id, **args_dict)
            mouth_id_to_feature_id[mouth_id] = feature_id

        return topography
    finally:
        if temporary_dir is not None:
            temporary_dir.cleanup()
