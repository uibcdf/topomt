import shutil
import tempfile
from pathlib import Path

import molsysmt as msm

from topomt.topography.Topography import Topography
from topomt.third_party.fpocket.files import load_topography as load_fpocket_topography
from topomt.third_party.fpocket.runner import run_fpocket


def get_topography(
    molecular_system,
    *,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    fpocket_cmd: str = 'fpocket',
    extra_args: list[str] | None = None,
) -> Topography:
    """Run the fpocket CLI and return a Topography."""

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

        return load_fpocket_topography(
            molecular_system,
            pdb_file=input_pdb,
            output_dir=output_dir,
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
