from pathlib import Path
import re

import numpy as np

from .model import FpocketPocket, FpocketResult


_HEADER_FIELD_MAP = {
    'Pocket Score': 'score',
    'Score': 'score',
    'Drug Score': 'druggability_score',
    'Druggability Score': 'druggability_score',
    'Number of alpha spheres': 'n_alpha_spheres',
    'Number of V. Vertices': 'n_alpha_spheres',
    'Number of Alpha Spheres': 'n_alpha_spheres',
    'Mean alpha-sphere radius': 'mean_alpha_sphere_radius',
    'Mean alpha sphere radius': 'mean_alpha_sphere_radius',
    'Mean alpha-sphere Solvent Acc.': 'mean_alpha_sphere_sasa',
    'Mean alpha-sphere SA': 'mean_alpha_sphere_sasa',
    'Mean alp. sph. solvent access': 'mean_alpha_sphere_sasa',
    'Mean B-factor of pocket residues': 'mean_b_factor',
    'Mean B-factor': 'mean_b_factor',
    'Hydrophobicity Score': 'hydrophobicity_score',
    'Hydrophobicity score': 'hydrophobicity_score',
    'Polarity Score': 'polarity_score',
    'Polarity score': 'polarity_score',
    'Amino Acid based volume Score': 'volume_score',
    'Volume Score': 'volume_score',
    'Volume score': 'volume_score',
    'Pocket volume (Monte Carlo)': 'volume',
    'Real volume (approximation)': 'volume',
    'Volume': 'volume',
    'Pocket volume (convex hull)': 'convex_hull_volume',
    'Charge Score': 'charge_score',
    'Charge score': 'charge_score',
    'Local hydrophobic density Score': 'local_hydrophobic_density_score',
    'Mean local hydrophobic density': 'local_hydrophobic_density_score',
    'Number of apolar alpha sphere': 'n_apolar_alpha_spheres',
    'Apolar alpha sphere proportion': 'apolar_alpha_sphere_ratio',
    'Proportion of apolar alpha sphere': 'apolar_alpha_sphere_ratio',
}


def parse_fpocket_output(pdb_file: str | Path, output_dir: str | Path) -> FpocketResult:

    pdb_file = Path(pdb_file).resolve()
    output_dir = Path(output_dir).resolve()
    pockets_dir = output_dir / 'pockets'
    metadata = _parse_global_info(output_dir / f'{pdb_file.stem}_info.txt')

    pockets = []
    if pockets_dir.exists():
        for pocket_atm in pockets_dir.glob('pocket*_atm.pdb'):
            file_pocket_id = _extract_pocket_id(pocket_atm.stem)
            props, atom_serials, reported_pocket_id = _parse_pocket_atm(pocket_atm)

            pocket_vert = pockets_dir / f'pocket{file_pocket_id}_vert.pqr'
            vert_data = _parse_pocket_vert(pocket_vert) if pocket_vert.exists() else {}

            pocket_id = reported_pocket_id if reported_pocket_id is not None else file_pocket_id
            merged_props = {}
            merged_props.update(metadata.get(f'Pocket {pocket_id}', {}))
            merged_props.update(props)
            merged_props.update(vert_data.get('raw', {}))

            pocket = FpocketPocket(
                pocket_id=pocket_id,
                file_pocket_id=file_pocket_id,
                atom_serials=atom_serials,
                center=vert_data.get('center'),
                score=_get_prop(merged_props, 'score'),
                druggability_score=_get_prop(merged_props, 'druggability_score'),
                n_alpha_spheres=_get_prop(merged_props, 'n_alpha_spheres'),
                mean_alpha_sphere_radius=_get_prop(merged_props, 'mean_alpha_sphere_radius'),
                mean_alpha_sphere_sasa=_get_prop(merged_props, 'mean_alpha_sphere_sasa'),
                mean_b_factor=_get_prop(merged_props, 'mean_b_factor'),
                hydrophobicity_score=_get_prop(merged_props, 'hydrophobicity_score'),
                polarity_score=_get_prop(merged_props, 'polarity_score'),
                volume_score=_get_prop(merged_props, 'volume_score'),
                volume=_get_prop(merged_props, 'volume'),
                convex_hull_volume=_get_prop(merged_props, 'convex_hull_volume'),
                charge_score=_get_prop(merged_props, 'charge_score'),
                local_hydrophobic_density_score=_get_prop(
                    merged_props, 'local_hydrophobic_density_score'
                ),
                n_apolar_alpha_spheres=_get_prop(merged_props, 'n_apolar_alpha_spheres'),
                apolar_alpha_sphere_ratio=_get_prop(merged_props, 'apolar_alpha_sphere_ratio'),
                alpha_sphere_centers=vert_data.get('alpha_sphere_centers'),
                alpha_sphere_radii=vert_data.get('alpha_sphere_radii'),
                alpha_sphere_types=vert_data.get('alpha_sphere_types', []),
                raw=merged_props,
            )
            pockets.append(pocket)

    pockets.sort(key=lambda pocket: pocket.pocket_id)

    return FpocketResult(
        source_pdb=pdb_file,
        output_dir=output_dir,
        pockets=pockets,
        metadata=metadata,
    )


def _extract_pocket_id(stem: str) -> int:

    match = re.search(r'pocket(\d+)', stem)
    if match is None:
        raise ValueError(f'Could not extract pocket id from {stem!r}.')

    return int(match.group(1))


def _parse_pocket_atm(pocket_file: Path) -> tuple[dict[str, float | int | str], list[int], int | None]:

    props: dict[str, float | int | str] = {}
    atom_serials: list[int] = []
    reported_pocket_id = None

    with pocket_file.open() as file_handle:
        for line in file_handle:
            if line.startswith('HEADER'):
                pocket_id = _parse_reported_pocket_id(line)
                if pocket_id is not None:
                    reported_pocket_id = pocket_id
                    continue

                field = _parse_header_field(line)
                if field is not None:
                    key, value = field
                    props[key] = value

            elif line.startswith(('ATOM  ', 'HETATM')):
                atom_serials.append(int(line[6:11]))

    return props, atom_serials, reported_pocket_id


def _parse_pocket_vert(pocket_vert: Path) -> dict[str, object]:

    props: dict[str, float | int | str] = {}
    centers = []
    radii = []
    types = []

    with pocket_vert.open() as file_handle:
        for line in file_handle:
            if line.startswith('HEADER'):
                field = _parse_header_field(line)
                if field is not None:
                    key, value = field
                    props[key] = value
                continue

            if line.startswith(('ATOM  ', 'HETATM')):
                centers.append(
                    [
                        float(line[30:38]),
                        float(line[38:46]),
                        float(line[46:54]),
                    ]
                )
                _, radius = _parse_pqr_charge_and_radius(line)
                radii.append(radius)
                types.append(line[13:16].strip())

    if len(centers) == 0:
        center = None
        centers_array = None
        radii_array = None
    else:
        centers_array = np.asarray(centers, dtype=float)
        radii_array = np.asarray(radii, dtype=float)
        center = centers_array.mean(axis=0)

    return {
        'center': center,
        'alpha_sphere_centers': centers_array,
        'alpha_sphere_radii': radii_array,
        'alpha_sphere_types': types,
        'raw': props,
    }


def _parse_pqr_charge_and_radius(line: str) -> tuple[float, float]:
    fields = line[54:].split()
    if len(fields) < 2:
        raise ValueError(f'Could not parse PQR charge/radius from line: {line!r}')

    return float(fields[0]), float(fields[1])


def _parse_global_info(info_file: Path) -> dict[str, dict[str, float | int | str]]:

    if not info_file.exists():
        return {}

    metadata: dict[str, dict[str, float | int | str]] = {}
    current_pocket = None

    with info_file.open() as file_handle:
        for line in file_handle:
            stripped = line.strip()

            if stripped == '':
                continue

            pocket_id = _parse_reported_pocket_id(stripped)
            if pocket_id is not None:
                current_pocket = f'Pocket {pocket_id}'
                metadata.setdefault(current_pocket, {})
                continue

            if ':' not in stripped or current_pocket is None:
                continue

            key, value = stripped.split(':', 1)
            metadata[current_pocket][_normalize_key(key.strip())] = _coerce_value(value.strip())

    return metadata


def _parse_reported_pocket_id(line: str) -> int | None:

    match = re.search(r'Information about the pocket\s+(\d+):', line)
    if match is None:
        match = re.match(r'Pocket\s+(\d+)\s*:', line)

    return None if match is None else int(match.group(1))


def _parse_header_field(line: str) -> tuple[str, float | int | str] | None:

    content = line[6:].strip()
    match = re.match(r'\d+\s*-\s*(.+?):\s*(.+)', content)
    if match is None:
        return None

    key = _normalize_key(match.group(1).strip())
    value = _coerce_value(match.group(2).strip())

    return key, value


def _normalize_key(key: str) -> str:

    return _HEADER_FIELD_MAP.get(key, key)


def _coerce_value(value: str) -> float | int | str:

    try:
        number = float(value)
    except ValueError:
        return value

    if number.is_integer():
        return int(number)

    return number


def _get_prop(props: dict[str, float | int | str], key: str) -> float | int | None:

    value = props.get(key)
    if isinstance(value, (int, float)):
        return value

    return None
