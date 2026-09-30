from typing import Any

from topomt.topography.Topography import Topography

from .output import FpocketOutput


def get_topography(
    molecular_system,
    *,
    backend: str = 'cli',
    **kwargs,
) -> Topography:
    """Return a Topography through the selected fpocket backend."""

    backend_lower = backend.lower()

    if backend_lower in {'cli', 'wrapper'}:
        from .cli import get_topography as cli_get_topography

        return cli_get_topography(molecular_system, **kwargs)

    if backend_lower == 'native':
        from .native import get_topography as native_get_topography

        return native_get_topography(molecular_system, **kwargs)

    if backend_lower == 'topomt':
        from .topomt import get_topography as topomt_get_topography

        return topomt_get_topography(molecular_system, **kwargs)

    raise ValueError(
        f"Unknown fpocket backend {backend!r}. Supported: 'cli', 'native', 'topomt'."
    )


def get_pockets(
    molecular_system,
    *,
    backend: str = 'cli',
    **kwargs,
):
    """Return fpocket-derived pocket features from the selected backend."""

    topography = get_topography(
        molecular_system,
        backend=backend,
        **kwargs,
    )
    return list(topography.get_features(by='type', value='pocket'))


def load_topography(
    molecular_system,
    *,
    pdb_file,
    output_dir,
    **kwargs,
) -> Topography:
    """Load fpocket persisted output into a Topography."""

    from .files import load_topography as load_topography_from_files

    return load_topography_from_files(
        molecular_system,
        pdb_file=pdb_file,
        output_dir=output_dir,
        **kwargs,
    )


def get_output(
    molecular_system: Any = None, *, backend: str = 'cli', **kwargs: Any
) -> FpocketOutput:
    """Return original fpocket results with shared pocket access.

    Parameters
    ----------
    molecular_system : molecular system, optional
        MolSysMT-compatible source input.
    backend : str, default='cli'
        Original route: cli, wrapper or files. Local reproductions are not substituted.
    **kwargs
        Execution/import options documented by the corresponding legacy adapter,
        including selection, structure_indices and provider-specific settings.

    Returns
    -------
    FpocketOutput
        Detached records, available geometry and recoverable original evidence.

    Raises
    ------
    ValueError
        If the backend or result evidence is unsupported or inconsistent.

    Examples
    --------
    >>> result = get_output('protein.pdb')  # doctest: +SKIP
    >>> pockets = result.pockets  # doctest: +SKIP
    """
    from topomt.third_party.output import _from_topography

    backend = backend.lower()
    if backend == 'files':
        if molecular_system is None:
            molecular_system = kwargs.get('pdb_file')
        topography = load_topography(molecular_system, **kwargs)
    elif backend in {'cli', 'wrapper'}:
        topography = get_topography(molecular_system, backend=backend, **kwargs)
    else:
        raise ValueError(f'Unsupported original fpocket backend: {backend!r}')
    return _from_topography(topography, FpocketOutput)
