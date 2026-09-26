from pathlib import Path
from typing import Any

import molsysmt as msm

from topomt import pyunitwizard as puw
from topomt.features.Pocket import Pocket
from topomt.provider_output import ExternalMeasurement, ProviderRun
from topomt.third_party.fpocket.model import FpocketPocket, FpocketResult
from topomt.third_party.fpocket.parser import parse_fpocket_output
from topomt.topography.Topography import Topography

# Parsed key -> (feature name, original label, unit, calculation issue, definition).
# The info report is rounded to three decimals; pocket PDB/PQR headers may carry
# more digits and are retained separately in provider_raw_fields and ProviderRun.
_FPOCKET_INFO_FIELDS: dict[str, tuple[str, str, str, int | None, str]] = {
    'score': ('score', 'Score', '1', None, 'fpocket pocket ranking score'),
    'druggability_score': (
        'druggability_score',
        'Druggability Score',
        '1',
        None,
        'fpocket druggability model score',
    ),
    'n_alpha_spheres': (
        'n_alpha_spheres',
        'Number of Alpha Spheres',
        '1',
        None,
        'count of alpha spheres assigned to the pocket',
    ),
    'Total SASA': (
        'total_sasa',
        'Total SASA',
        'angstroms**2',
        20,
        'fpocket solvent-accessible area with its 1.4-angstrom probe',
    ),
    'Polar SASA': (
        'polar_sasa',
        'Polar SASA',
        'angstroms**2',
        21,
        'polar-atom contribution to fpocket 1.4-angstrom-probe SASA',
    ),
    'Apolar SASA': (
        'apolar_sasa',
        'Apolar SASA',
        'angstroms**2',
        22,
        'apolar-atom contribution to fpocket 1.4-angstrom-probe SASA',
    ),
    'volume': (
        'volume',
        'Volume',
        'angstroms**3',
        None,
        'fpocket pocket volume approximation',
    ),
    'local_hydrophobic_density_score': (
        'local_hydrophobic_density_score',
        'Mean local hydrophobic density',
        '1',
        None,
        'mean number of overlapping apolar neighbors per apolar alpha sphere',
    ),
    'mean_alpha_sphere_radius': (
        'mean_alpha_sphere_radius',
        'Mean alpha sphere radius',
        'angstroms',
        None,
        'mean radius of pocket alpha spheres',
    ),
    'mean_alpha_sphere_sasa': (
        'mean_alpha_sphere_solvent_access',
        'Mean alp. sph. solvent access',
        '1',
        23,
        'mean center-to-contact-barycenter distance divided by alpha-sphere radius',
    ),
    'apolar_alpha_sphere_ratio': (
        'apolar_alpha_sphere_ratio',
        'Apolar alpha sphere proportion',
        '1',
        None,
        'apolar alpha-sphere count divided by all pocket alpha spheres',
    ),
    'hydrophobicity_score': (
        'hydrophobicity_score',
        'Hydrophobicity score',
        '1',
        24,
        'mean fpocket hydrophobicity-table value over distinct lining residues',
    ),
    'volume_score': (
        'volume_score',
        'Volume score',
        '1',
        25,
        'mean fpocket volume-table value over distinct lining residues',
    ),
    'polarity_score': (
        'polarity_score',
        'Polarity score',
        '1',
        26,
        'sum of fpocket polarity-table values over distinct lining residues',
    ),
    'charge_score': (
        'charge_score',
        'Charge score',
        '1',
        27,
        'sum of fpocket charge-table values over distinct lining residues',
    ),
    'Proportion of polar atoms': (
        'proportion_polar_atoms',
        'Proportion of polar atoms',
        'percent',
        28,
        'percentage of contacted atoms with fpocket electronegativity above 2.7',
    ),
    'Alpha sphere density': (
        'alpha_sphere_density',
        'Alpha sphere density',
        'angstroms',
        None,
        'mean pairwise distance between pocket alpha-sphere centers',
    ),
    'Cent. of mass - Alpha Sphere max dist': (
        'alpha_sphere_max_distance',
        'Cent. of mass - Alpha Sphere max dist',
        'angstroms',
        None,
        'maximum pairwise distance between alpha-sphere centers',
    ),
    'Flexibility': (
        'flexibility',
        'Flexibility',
        '1',
        29,
        'contacted-atom mean B factor min-max normalized across detected pockets',
    ),
}


def fpocket_result_to_topography(
    molecular_system,
    fpocket_result: FpocketResult,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    backend: str = 'files',
    provider_metadata: dict[str, Any] | None = None,
) -> Topography:
    topography, serial_to_index = _build_topography_and_atom_map(
        molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
    )
    info_name = f'{fpocket_result.source_pdb.stem}_info.txt'
    run_metadata = {
        'selection': selection,
        'structure_indices': structure_indices,
        'syntax': syntax,
        'atom_serial_to_index': {
            str(key): value for key, value in serial_to_index.items()
        },
    }
    if provider_metadata:
        run_metadata.update(provider_metadata)
    run = ProviderRun.capture(
        'fpocket',
        backend,
        fpocket_result.source_pdb,
        fpocket_result.output_dir,
        metadata=run_metadata,
    )
    topography.add_provider_run(run)

    for fpocket_pocket in fpocket_result.pockets:
        provider_atom_indices = [
            serial_to_index.get(atom_serial)
            for atom_serial in fpocket_pocket.atom_serials
        ]
        atom_indices = [
            atom_index for atom_index in provider_atom_indices if atom_index is not None
        ]

        pocket = _fpocket_pocket_to_feature(
            fpocket_pocket,
            atom_indices,
            provider_atom_indices,
            run,
            info_name,
            fpocket_result.metadata,
        )
        topography.add_feature(pocket)

    return topography


def load_topography(
    molecular_system,
    *,
    pdb_file: str | Path,
    output_dir: str | Path,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    backend: str = 'files',
    provider_metadata: dict[str, Any] | None = None,
) -> Topography:
    fpocket_result = parse_fpocket_output(pdb_file, output_dir)
    return fpocket_result_to_topography(
        molecular_system,
        fpocket_result,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
        backend=backend,
        provider_metadata=provider_metadata,
    )


def _build_serial_to_atom_index_map(
    molecular_system,
    selection: str = 'all',
    syntax: str = 'MolSysMT',
) -> dict[int, int]:
    molsys = msm.convert(molecular_system, to_form='molsysmt.MolSys')
    selected_atom_indices = msm.select(
        molsys,
        selection=selection,
        syntax=syntax,
    )
    atom_table = molsys.topology.atoms

    mapping = {}
    for atom_index in selected_atom_indices:
        atom_serial = atom_table.iloc[atom_index]['atom_id']
        if atom_serial is None:
            continue

        try:
            atom_serial = int(atom_serial)
        except (TypeError, ValueError):
            continue

        mapping[atom_serial] = atom_index

    return mapping


def _build_topography_and_atom_map(
    molecular_system,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
) -> tuple[Topography, dict[int, int]]:
    try:
        topography = Topography(
            molecular_system=molecular_system,
            selection=selection,
            structure_indices=structure_indices,
        )
        serial_to_index = _build_serial_to_atom_index_map(
            topography._molsys,
            selection=selection,
            syntax=syntax,
        )
        return topography, serial_to_index
    except Exception:
        original_pdb = _get_original_pdb_path(molecular_system)
        if original_pdb is None or selection != 'all' or structure_indices != 0:
            raise

        topography = Topography(
            molecular_system=None,
            selection=selection,
            structure_indices=structure_indices,
        )
        topography._molecular_system = molecular_system
        serial_to_index = _build_serial_to_atom_index_map_from_pdb(original_pdb)
        return topography, serial_to_index


def _build_serial_to_atom_index_map_from_pdb(pdb_path: Path) -> dict[int, int]:
    mapping = {}
    atom_index = 0

    with pdb_path.open() as file_handle:
        for line in file_handle:
            if line.startswith(('ATOM  ', 'HETATM')):
                atom_serial = int(line[6:11])
                mapping[atom_serial] = atom_index
                atom_index += 1

    return mapping


def _get_original_pdb_path(molecular_system) -> Path | None:
    if isinstance(molecular_system, (str, Path)):
        path = Path(molecular_system).expanduser().resolve()
        if path.exists() and path.suffix.lower() == '.pdb':
            return path

    return None


def _fpocket_pocket_to_feature(
    fpocket_pocket: FpocketPocket,
    atom_indices: list[int],
    provider_atom_indices: list[int | None],
    run: ProviderRun,
    info_name: str,
    global_info: dict,
) -> Pocket:
    external_measurements: dict[str, ExternalMeasurement] = {}
    info_fields = global_info.get(f'Pocket {fpocket_pocket.pocket_id}', {})
    mapped_keys: set[str] = set()
    for parsed_key, (
        name,
        field,
        unit,
        issue,
        definition,
    ) in _FPOCKET_INFO_FIELDS.items():
        if parsed_key not in info_fields:
            continue
        original_value = info_fields[parsed_key]
        if not isinstance(original_value, (int, float)):
            continue
        mapped_keys.add(parsed_key)
        value = (
            puw.quantity(original_value, unit)
            if unit.startswith('angstroms')
            else original_value
        )
        external_measurements[name] = ExternalMeasurement(
            value=value,
            original_value=original_value,
            original_unit=unit,
            source_field=field,
            source_artifact=f'output/{info_name}',
            run_id=run.run_id,
            definition=definition,
            issue_url=(
                f'https://github.com/uibcdf/topomt/issues/{issue}' if issue else None
            ),
            status='external_only' if issue else 'topomt_available',
        )

    unmapped_provider_fields = {
        key: value for key, value in info_fields.items() if key not in mapped_keys
    }
    sphere_artifact = f'output/pockets/pocket{fpocket_pocket.file_pocket_id}_vert.pqr'
    if not any(name == sphere_artifact for name, _ in run.artifacts):
        sphere_artifact = None
    atom_artifact = f'output/pockets/pocket{fpocket_pocket.file_pocket_id}_atm.pdb'
    unmapped_atom_serials = [
        serial
        for serial, atom_index in zip(
            fpocket_pocket.atom_serials, provider_atom_indices
        )
        if atom_index is None
    ]

    pocket = Pocket(
        atom_indices=sorted(atom_indices),
        provider_atom_serials=fpocket_pocket.atom_serials.copy(),
        provider_atom_indices=provider_atom_indices,
        unmapped_atom_serials=unmapped_atom_serials,
        atom_source_artifact=atom_artifact,
        center=fpocket_pocket.center,
        volume=fpocket_pocket.volume,
        score=fpocket_pocket.score,
        druggability_score=fpocket_pocket.druggability_score,
        n_alpha_spheres=fpocket_pocket.n_alpha_spheres,
        mean_alpha_sphere_radius=fpocket_pocket.mean_alpha_sphere_radius,
        mean_alpha_sphere_sasa=fpocket_pocket.mean_alpha_sphere_sasa,
        mean_b_factor=fpocket_pocket.mean_b_factor,
        hydrophobicity_score=fpocket_pocket.hydrophobicity_score,
        polarity_score=fpocket_pocket.polarity_score,
        volume_score=fpocket_pocket.volume_score,
        convex_hull_volume=fpocket_pocket.convex_hull_volume,
        charge_score=fpocket_pocket.charge_score,
        local_hydrophobic_density_score=fpocket_pocket.local_hydrophobic_density_score,
        n_apolar_alpha_spheres=fpocket_pocket.n_apolar_alpha_spheres,
        apolar_alpha_sphere_ratio=fpocket_pocket.apolar_alpha_sphere_ratio,
        alpha_sphere_centers=fpocket_pocket.alpha_sphere_centers,
        alpha_sphere_radii=fpocket_pocket.alpha_sphere_radii,
        alpha_sphere_ids=fpocket_pocket.alpha_sphere_ids,
        alpha_sphere_charges=fpocket_pocket.alpha_sphere_charges,
        alpha_sphere_types=fpocket_pocket.alpha_sphere_types,
        alpha_sphere_source_artifact=sphere_artifact,
        source='fpocket',
        source_id=f'fpocket:{fpocket_pocket.pocket_id}',
        provider_run_id=run.run_id,
        provider_raw_fields=fpocket_pocket.raw.copy(),
        unmapped_provider_fields=unmapped_provider_fields,
        external_measurements=external_measurements,
    )
    for name in (
        'total_sasa',
        'polar_sasa',
        'apolar_sasa',
        'mean_alpha_sphere_solvent_access',
        'proportion_polar_atoms',
        'alpha_sphere_density',
        'alpha_sphere_max_distance',
        'flexibility',
    ):
        measurement = external_measurements.get(name)
        if measurement is None:
            continue
        setattr(pocket, name, measurement.value)
    return pocket
