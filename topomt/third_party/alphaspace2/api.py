from topomt.topography.Topography import Topography


def get_topography(
    molecular_system,
    *,
    backend: str = 'native',
    **kwargs,
) -> Topography:
    """Return a Topography through the selected AlphaSpace2 backend."""

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


def get_pockets(
    molecular_system,
    *,
    backend: str = 'native',
    **kwargs,
):
    """Return AlphaSpace2-derived pocket features from the selected backend."""

    topography = get_topography(
        molecular_system,
        backend=backend,
        **kwargs,
    )
    return list(topography.get_features(by='type', value='pocket'))
