import shutil
import tempfile
from pathlib import Path

import molsysmt as msm

from topomt.features.Pocket import Pocket
from topomt.topography.Topography import Topography

from .model import FpocketPocket, FpocketResult
from .parser import parse_fpocket_output
from .runner import run_fpocket


def fpocket_result_to_topography(
    molecular_system,
    fpocket_result: FpocketResult,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
) -> Topography:

    topography, serial_to_index = _build_topography_and_atom_map(
        molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
    )

    for fpocket_pocket in fpocket_result.pockets:
        atom_indices = []
        for atom_serial in fpocket_pocket.atom_serials:
            atom_index = serial_to_index.get(atom_serial)
            if atom_index is not None:
                atom_indices.append(atom_index)

        pocket = _fpocket_pocket_to_feature(fpocket_pocket, atom_indices)
        topography.add_feature(pocket)

    return topography


def load_topography_from_fpocket_output(
    molecular_system,
    pdb_file: str | Path,
    output_dir: str | Path,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
) -> Topography:

    fpocket_result = parse_fpocket_output(pdb_file, output_dir)
    return fpocket_result_to_topography(
        molecular_system,
        fpocket_result,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
    )


def get_topography_with_fpocket(
    molecular_system,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    fpocket_cmd: str = 'fpocket',
    extra_args: list[str] | None = None,
) -> Topography:

    with tempfile.TemporaryDirectory(prefix='topomt_fpocket_') as tmpdir_name:
        tmpdir = Path(tmpdir_name)
        input_pdb = _prepare_fpocket_input_pdb(
            molecular_system,
            tmpdir=tmpdir,
            selection=selection,
            structure_indices=structure_indices,
            syntax=syntax,
        )

        output_dir = run_fpocket(
            input_pdb,
            fpocket_cmd=fpocket_cmd,
            workdir=tmpdir,
            extra_args=extra_args,
        )

        return load_topography_from_fpocket_output(
            molecular_system,
            input_pdb,
            output_dir,
            selection=selection,
            structure_indices=structure_indices,
            syntax=syntax,
        )


def _prepare_fpocket_input_pdb(
    molecular_system,
    tmpdir: Path,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
) -> Path:

    original_pdb = _get_original_pdb_path(molecular_system)
    if original_pdb is not None and selection == 'all' and structure_indices == 0:
        input_pdb = tmpdir / original_pdb.name
        shutil.copy2(original_pdb, input_pdb)
        return input_pdb

    molsys = msm.convert(molecular_system, to_form='molsysmt.MolSys')
    input_pdb = tmpdir / 'input.pdb'
    pdb_text = msm.convert(
        molsys,
        to_form='string:pdb_text',
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
    )
    input_pdb.write_text(pdb_text)
    return input_pdb


def _get_original_pdb_path(molecular_system) -> Path | None:

    if isinstance(molecular_system, (str, Path)):
        path = Path(molecular_system).expanduser().resolve()
        if path.exists() and path.suffix.lower() == '.pdb':
            return path

    return None


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


def _fpocket_pocket_to_feature(fpocket_pocket: FpocketPocket, atom_indices: list[int]) -> Pocket:

    return Pocket(
        atom_indices=sorted(atom_indices),
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
        alpha_sphere_types=fpocket_pocket.alpha_sphere_types,
        source='fpocket',
        source_id=f'fpocket:{fpocket_pocket.pocket_id}',
    )
