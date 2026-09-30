from typing import Any

from topomt.topography.Topography import Topography

from .output import PyCASTAOutput


def get_topography(
    molecular_system,
    *,
    backend: str = 'native',
    **kwargs,
) -> Topography:
    """Return a Topography through the selected pyCASTA backend."""

    backend_lower = backend.lower()

    if backend_lower == 'native':
        from .native import get_topography as native_get_topography

        return native_get_topography(molecular_system, **kwargs)

    if backend_lower in {'library', 'wrapper'}:
        from .library import get_topography as library_get_topography

        return library_get_topography(molecular_system, **kwargs)

    raise ValueError(
        f"Unknown pyCASTA backend {backend!r}. Supported: 'native', 'library'."
    )


def get_pockets(
    molecular_system,
    *,
    backend: str = 'native',
    **kwargs,
):
    """Return pyCASTA-derived pocket features from the selected backend."""

    topography = get_topography(
        molecular_system,
        backend=backend,
        **kwargs,
    )
    return list(topography.get_features(by='type', value='pocket'))


def get_output(
    molecular_system: Any = None, *, backend: str = 'library', **kwargs: Any
) -> PyCASTAOutput:
    """Return original pycasta results with shared pocket access.

    Parameters
    ----------
    molecular_system : molecular system, optional
        MolSysMT-compatible source input.
    backend : str, default='library'
        Original route: library or wrapper. Local reproductions are not substituted.
    **kwargs
        Execution/import options documented by the corresponding legacy adapter,
        including selection, structure_indices and provider-specific settings.

    Returns
    -------
    PyCASTAOutput
        Detached records, available geometry and recoverable original evidence.

    Raises
    ------
    ValueError
        If the backend or result evidence is unsupported or inconsistent.
    LibraryNotFoundError
        If the optional original engine is absent.

    Examples
    --------
    >>> result = get_output('protein.pdb')  # doctest: +SKIP
    >>> pockets = result.pockets  # doctest: +SKIP
    """
    from topomt.third_party.output import _from_topography

    if backend.lower() not in {'library', 'wrapper'}:
        raise ValueError(f'Unsupported original pyCASTA backend: {backend!r}')
    return _from_topography(
        get_topography(molecular_system, backend=backend, **kwargs), PyCASTAOutput
    )
