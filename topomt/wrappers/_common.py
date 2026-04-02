import shutil
import sys
from importlib import import_module
from pathlib import Path

import molsysmt as msm
import numpy as np


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

    original_pdb = get_original_pdb_path(molecular_system)
    if original_pdb is not None and selection == 'all' and structure_indices == 0:
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
        if upstream_root is None:
            raise ModuleNotFoundError(
                f"Optional upstream package '{module_name}' is not installed. "
                f"Install it or pass upstream_root to the wrapper-backed path."
            ) from original_exc

        upstream_root = Path(upstream_root).expanduser().resolve()
        search_root = upstream_root
        if upstream_root.is_file():
            search_root = upstream_root.parent

        if str(search_root) not in sys.path:
            sys.path.insert(0, str(search_root))

        return import_module(module_name)
