import shutil
import sys
from importlib import import_module
from pathlib import Path

import molsysmt as msm
import numpy as np

from topomt._private.smonitor import LibraryNotFoundError


def prepare_wrapper_input_pdb(
    molecular_system,
    *,
    tmpdir: Path,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
) -> tuple[Path, np.ndarray]:
    full_molsys = msm.convert(molecular_system, to_form='molsysmt.MolSys')
    selected_atom_indices = np.array(
        msm.select(full_molsys, selection=selection, syntax=syntax),
        dtype=int,
    )
    if selected_atom_indices.size == 0:
        raise ValueError('Cannot submit an empty atom selection to an external engine.')

    original_pdb = get_original_pdb_path(molecular_system)
    if (
        original_pdb is not None
        and isinstance(selection, str)
        and selection == 'all'
        and np.array_equal(np.atleast_1d(structure_indices), [0])
    ):
        # Preserve exact single-frame bytes, but select rather than copy a trajectory.
        with original_pdb.open() as pdb_file:
            model_count = sum(line.startswith('MODEL ') for line in pdb_file)
        if model_count <= 1:
            input_pdb = tmpdir / original_pdb.name
            shutil.copy2(original_pdb, input_pdb)
            return input_pdb, selected_atom_indices

    input_pdb = tmpdir / 'input.pdb'
    pdb_text = msm.convert(
        full_molsys,
        to_form='string:pdb_text',
        selection=selected_atom_indices,
        structure_indices=structure_indices,
        syntax='MolSysMT',
    )
    input_pdb.write_text(pdb_text)
    return input_pdb, selected_atom_indices


def get_original_pdb_path(molecular_system) -> Path | None:
    if isinstance(molecular_system, (str, Path)):
        path = Path(molecular_system).expanduser().resolve()
        if path.exists() and path.suffix.lower() == '.pdb':
            return path

    return None


def import_upstream_module(
    module_name: str,
    *,
    upstream_root: str | Path | None = None,
):
    try:
        return import_module(module_name)
    except ModuleNotFoundError as original_exc:
        if (
            original_exc.name != module_name.split('.')[0]
            and original_exc.name != module_name
        ):
            raise
        if upstream_root is None:
            raise LibraryNotFoundError(
                library=module_name.split('.')[0]
            ) from original_exc

        upstream_root = Path(upstream_root).expanduser().resolve()
        search_root = upstream_root
        if upstream_root.is_file():
            search_root = upstream_root.parent

        inserted = str(search_root) not in sys.path
        if inserted:
            sys.path.insert(0, str(search_root))
        try:
            return import_module(module_name)
        finally:
            if inserted:
                sys.path.remove(str(search_root))
