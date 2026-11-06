import shutil
import sys
from importlib import import_module
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
from types import ModuleType

import molsysmt as msm
import numpy as np

from topomt._private.smonitor import LibraryNotFoundError


def installed_provider_version(module: ModuleType) -> str | None:
    """Return distribution metadata only for its matching Python package origin.

    Parameters
    ----------
    module : types.ModuleType
        Imported pure Python provider package with an ``__init__.py`` origin.

    Returns
    -------
    str or None
        Distribution version, or None for absent metadata or a source override.
        This identifies metadata; artifact-byte integrity is a separate check.

    Raises
    ------
    OSError
        If resolving the package origin fails.
    """
    origin = getattr(module, '__file__', None)
    if origin is None:
        return None
    try:
        installed = distribution(module.__name__)
    except PackageNotFoundError:
        return None
    expected = installed.locate_file(module.__name__.replace('.', '/') + '/__init__.py')
    return (
        installed.version
        if Path(origin).resolve() == Path(str(expected)).resolve()
        else None
    )


def validate_single_frame_pdb(input_pdb: Path, *, provider: str) -> None:
    """Require one nonempty submitted PDB frame before an original engine runs.

    Parameters
    ----------
    input_pdb : pathlib.Path
        Actual prepared input; implicit single-model PDB files are accepted.
    provider : str
        Engine identity used in the admission diagnostic.

    Returns
    -------
    None
        Admission succeeds without changing the submitted bytes.

    Raises
    ------
    ValueError
        If multiple explicit models or no atom rows are present.
    """
    model_count, atom_count = 0, 0
    with input_pdb.open() as handle:
        for line in handle:
            model_count += line.startswith('MODEL ')
            atom_count += line.startswith(('ATOM  ', 'HETATM'))
    if model_count > 1 or atom_count == 0:
        raise ValueError(f'{provider} requires exactly one input coordinate frame.')


def prepare_wrapper_input_pdb(
    molecular_system,
    *,
    tmpdir: Path,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
) -> tuple[Path, np.ndarray]:
    full_molsys = msm.convert(molecular_system, to_form='molsysmt.MolSys')
    # Export in source order so the returned map and the PDB atom rows agree.
    selected_atom_indices = np.sort(
        np.array(msm.select(full_molsys, selection=selection, syntax=syntax), dtype=int)
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
