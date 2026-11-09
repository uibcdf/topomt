import hashlib
import shutil
import tempfile
from pathlib import Path

import numpy as np

from topomt._ackredit import attributed
from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.fpocket_arguments import OPTIONS
from topomt.third_party._common import (
    prepare_wrapper_input_pdb,
    validate_single_frame_pdb,
)
from topomt.third_party.fpocket.files import load_topography as load_fpocket_topography
from topomt.third_party.fpocket.input_context import _chemical_context
from topomt.third_party.fpocket.runner import run_fpocket
from topomt.topography.Topography import Topography


@attributed('fpocket', route='original')
@arg_digest(**OPTIONS)
def get_topography(
    molecular_system,
    *,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    fpocket_cmd: str = 'fpocket',
    extra_args: list[str] | None = None,
    chemical_state: str | int = 'reference',
    skip_digestion: bool = False,
) -> Topography:
    """Run original fpocket with a declared reference chemical state.

    Parameters
    ----------
    molecular_system : molecular system
        MolSysMT-compatible input with one unambiguous reference state.
    selection : str or sequence of int, default='all'
        Nonempty source atom selection.
    structure_indices : int or list of int, default=0
        Exactly one coordinate frame.
    syntax : str, default='MolSysMT'
        Selection syntax.
    fpocket_cmd : str, default='fpocket'
        Original executable name or path.
    extra_args : list of str, optional
        Additional original-engine options.
    chemical_state : str or int, default='reference'
        The reference selector or its integer index, including a nonzero index.
        Nonreference export is unsupported by the qualified MolSysMT converter.
    skip_digestion : bool, default=False
        Internal bypass for arguments already digested by the owning boundary.

    Returns
    -------
    Topography
        Original provider records and captured execution/context evidence.

    Raises
    ------
    ValueError
        If the input frame, selection or chemical context is not admitted.
    FpocketError
        If the executable is absent or its execution fails.

    Examples
    --------
    >>> result = get_topography('protein.pdb', chemical_state='reference')  # doctest: +SKIP
    """

    context = _chemical_context(molecular_system, chemical_state)
    with tempfile.TemporaryDirectory(prefix='topomt_fpocket_') as tmpdir_name:
        tmpdir = Path(tmpdir_name)
        input_pdb, submitted_atom_indices = _prepare_fpocket_input(
            molecular_system,
            tmpdir=tmpdir,
            selection=selection,
            structure_indices=structure_indices,
            syntax=syntax,
            chemical_state=chemical_state,
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
            chemical_state=chemical_state,
            chemical_state_context=context,
            skip_digestion=True,
        )


def _prepare_fpocket_input_pdb(
    molecular_system,
    tmpdir: Path,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    chemical_state: str | int = 'reference',
) -> Path:
    return _prepare_fpocket_input(
        molecular_system, tmpdir, selection, structure_indices, syntax, chemical_state
    )[0]


def _prepare_fpocket_input(
    molecular_system,
    tmpdir: Path,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    chemical_state: str | int = 'reference',
) -> tuple[Path, np.ndarray]:
    _chemical_context(molecular_system, chemical_state)
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
    validate_single_frame_pdb(input_pdb, provider='fpocket')
    return input_pdb, atom_indices
