from topomt.topography.Topography import Topography


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
