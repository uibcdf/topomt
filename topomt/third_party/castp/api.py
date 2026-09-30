from typing import Any

from topomt.topography.Topography import Topography

from .output import CASTpOutput


def get_topography(
    molecular_system,
    *,
    backend: str = 'native',
    server: str | None = None,
    **kwargs,
) -> Topography:
    """Return a Topography through the selected CASTp backend."""

    backend_lower = backend.lower()
    server_lower = None if server is None else server.lower()

    if backend_lower in {'native'}:
        from .native import get_topography as native_get_topography

        return native_get_topography(molecular_system, **kwargs)

    if backend_lower in {'server', 'castpfold'}:
        if backend_lower == 'castpfold':
            server_lower = 'castpfold'

        if server_lower is None:
            server_lower = 'castpfold'

        if server_lower == 'castpfold':
            from .servers.castpfold import get_topography as castpfold_get_topography

            return castpfold_get_topography(molecular_system, **kwargs)

        if server_lower in {'castp3', 'castp_3.0', 'castp-3.0', 'castp30'}:
            from .servers.castp3 import get_topography as castp3_get_topography

            return castp3_get_topography(molecular_system, **kwargs)

        raise ValueError(
            f"Unknown CASTp server {server!r}. Supported: 'castpfold', 'castp3'."
        )

    raise ValueError(
        f"Unknown CASTp backend {backend!r}. Supported: 'native', 'server'."
    )


def get_pockets(
    molecular_system,
    *,
    backend: str = 'native',
    server: str | None = None,
    **kwargs,
):
    """Return pocket-like surface features from the selected CASTp backend."""

    topography = get_topography(
        molecular_system,
        backend=backend,
        server=server,
        **kwargs,
    )
    feature_types = ('pocket', 'void', 'channel', 'branched_channel')
    features = []
    for feature_type in feature_types:
        features.extend(topography.get_features(by='type', value=feature_type))
    return features


def load_topography(
    *, zip_file=None, dir_path=None, molecular_system=None, **kwargs
) -> Topography:
    """Load CASTp-family artifacts from persisted files."""

    from .files import load_topography as load_topography_from_files

    return load_topography_from_files(
        zip_file=zip_file,
        dir_path=dir_path,
        molecular_system=molecular_system,
        **kwargs,
    )


def get_output(
    molecular_system: Any = None, *, backend: str = 'server', **kwargs: Any
) -> CASTpOutput:
    """Return original castp results with shared pocket access.

    Parameters
    ----------
    molecular_system : molecular system, optional
        MolSysMT-compatible input; persisted CASTp files can supply their PDB.
    backend : str, default='server'
        Original route: server, castpfold or files. Local reproductions are not substituted.
    **kwargs
        Execution/import options documented by the corresponding legacy adapter,
        including selection, structure_indices and provider-specific settings.

    Returns
    -------
    CASTpOutput
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
        topography = load_topography(molecular_system=molecular_system, **kwargs)
    elif backend in {'server', 'castpfold'}:
        topography = get_topography(molecular_system, backend=backend, **kwargs)
    else:
        raise ValueError(f'Unsupported original CASTp backend: {backend!r}')
    if backend in {'server', 'castpfold'} and len(topography.provider_runs) == 1:
        run = next(iter(topography.provider_runs.values()))
        selected = run.metadata.get('selected_atom_indices')
        if selected is not None:
            return _from_topography(
                topography,
                CASTpOutput,
                source_molecular_system=molecular_system,
                source_structure_indices=kwargs.get('structure_indices', 0),
                atom_index_map=tuple(selected),
            )
    return _from_topography(topography, CASTpOutput)
