from typing import Any

from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.alphaspace2_arguments import (
    GATEWAY_PIPELINES,
    OPTIONS,
    ORIGINAL_PIPELINES,
)
from topomt.features import Pocket
from topomt.topography.Topography import Topography

from .output import AlphaSpace2Output


@arg_digest(**OPTIONS, argument_digestion=False, map=GATEWAY_PIPELINES)
def get_topography(
    molecular_system: Any,
    *,
    backend: str = 'native',
    skip_digestion: bool = False,
    **kwargs: Any,
) -> Topography:
    """Return a Topography through the selected AlphaSpace2 backend.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Receptor supplied to the selected route.
    backend : str, default='native'
        Native implementation or original library/wrapper route.
    skip_digestion : bool, default=False
        Internal bypass for already admitted routing arguments.
    **kwargs
        Options owned by the selected route. The original library validates its
        receptor and optional binder arguments before loading its dependencies.

    Returns
    -------
    Topography
        Topographical features from the selected route.

    Raises
    ------
    ArgumentError
        If the routing arguments or selected original arguments are invalid.
    LibraryNotFoundError
        If the requested original route has an unavailable dependency.

    Examples
    --------
    >>> result = get_topography('protein.pdb', backend='library')  # doctest: +SKIP
    """

    backend_lower = backend.lower()

    if backend_lower == 'native':
        from .native import get_topography as native_get_topography

        return native_get_topography(molecular_system, **kwargs)

    if backend_lower in {'library', 'wrapper'}:
        from .library import get_topography as library_get_topography

        return library_get_topography(molecular_system, **kwargs)

    raise ValueError(
        f"Unknown AlphaSpace2 backend {backend!r}. Supported: 'native', 'library'."
    )


@arg_digest(**OPTIONS, argument_digestion=False, map=GATEWAY_PIPELINES)
def get_pockets(
    molecular_system: Any,
    *,
    backend: str = 'native',
    skip_digestion: bool = False,
    **kwargs: Any,
) -> list[Pocket]:
    """Return AlphaSpace2-derived pocket features from the selected backend.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Receptor supplied to the selected route.
    backend : str, default='native'
        Native implementation or original library/wrapper route.
    skip_digestion : bool, default=False
        Internal bypass for already admitted routing arguments.
    **kwargs
        Options forwarded to the selected topography route.

    Returns
    -------
    list of Pocket
        Pocket features supplied by that route.

    Raises
    ------
    ArgumentError
        If the routing arguments or selected original arguments are invalid.
    LibraryNotFoundError
        If the requested original route has an unavailable dependency.

    Examples
    --------
    >>> pockets = get_pockets('protein.pdb', backend='library')  # doctest: +SKIP
    """

    topography = get_topography(
        molecular_system,
        backend=backend,
        skip_digestion=True,
        **kwargs,
    )
    return list(topography.get_features(by='type', value='pocket'))


@arg_digest(**OPTIONS, argument_digestion=False, map=ORIGINAL_PIPELINES)
def get_output(
    molecular_system: Any = None,
    *,
    backend: str = 'library',
    skip_digestion: bool = False,
    **kwargs: Any,
) -> AlphaSpace2Output:
    """Return original alphaspace2 results with shared pocket access.

    Parameters
    ----------
    molecular_system : molecular system, optional
        MolSysMT-compatible source input.
    backend : str, default='library'
        Original route: library, wrapper or saved files.
    skip_digestion : bool, default=False
        Internal bypass for already admitted routing arguments.
    **kwargs
        Execution/import options documented by the corresponding legacy adapter,
        including selection, structure_indices and provider-specific settings.

    Returns
    -------
    AlphaSpace2Output
        Detached records, available geometry and recoverable original evidence.

    Raises
    ------
    ArgumentError
        If the original route, option names or argument values are invalid.
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

    if backend.lower() == 'files':
        from .files import load_output

        return load_output(molecular_system, **kwargs)
    if backend.lower() not in {'library', 'wrapper'}:
        raise ValueError(f'Unsupported original AlphaSpace2 backend: {backend!r}')
    return _from_topography(
        get_topography(
            molecular_system, backend=backend, skip_digestion=True, **kwargs
        ),
        AlphaSpace2Output,
    )
