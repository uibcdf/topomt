import hashlib
import shutil
import tempfile
from pathlib import Path

import numpy as np

from topomt.third_party._common import prepare_wrapper_input_pdb
from topomt.third_party.fpocket.files import load_topography as load_fpocket_topography
from topomt.third_party.fpocket.runner import run_fpocket
from topomt.topography.Topography import Topography


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
        input_pdb, submitted_atom_indices = _prepare_fpocket_input(
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

        executable = shutil.which(fpocket_cmd)
        executable_sha256 = None
        if executable is not None:
            with Path(executable).open('rb') as file_handle:
                executable_sha256 = hashlib.file_digest(
                    file_handle, 'sha256'
                ).hexdigest()

        return load_fpocket_topography(
            molecular_system,
            pdb_file=input_pdb,
            output_dir=output_dir,
            selection=selection,
            structure_indices=structure_indices,
            syntax=syntax,
            backend='cli',
            provider_metadata={
                'executable_name': Path(fpocket_cmd).name,
                'executable_sha256': executable_sha256,
                'extra_args': list(extra_args or []),
            },
            submitted_atom_indices=submitted_atom_indices.tolist(),
        )


def _prepare_fpocket_input_pdb(
    molecular_system,
    tmpdir: Path,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
) -> Path:
    return _prepare_fpocket_input(
        molecular_system, tmpdir, selection, structure_indices, syntax
    )[0]


def _prepare_fpocket_input(
    molecular_system,
    tmpdir: Path,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
) -> tuple[Path, np.ndarray]:
    if (
        not isinstance(structure_indices, str)
        and np.asarray(structure_indices).size != 1
    ):
        raise ValueError('fpocket requires exactly one input coordinate frame.')
    input_pdb, atom_indices = prepare_wrapper_input_pdb(
        molecular_system,
        tmpdir=tmpdir,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
    )
    model_count, atom_count = 0, 0
    with input_pdb.open() as handle:
        for line in handle:
            model_count += line.startswith('MODEL ')
            atom_count += line.startswith(('ATOM  ', 'HETATM'))
    if model_count > 1 or atom_count == 0:
        raise ValueError('fpocket requires exactly one input coordinate frame.')
    return input_pdb, atom_indices
