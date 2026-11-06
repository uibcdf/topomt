"""Original-engine pocket output dispatch, independent of DFND adoption."""

from importlib import import_module
from typing import Any

from ._private.arg_digestion import arg_digest
from ._private.arg_digestion.provider_dispatch import (
    ALIASES,
    DEFAULT_BACKENDS,
    PIPELINES,
)
from .third_party.output import ProviderOutput


@arg_digest(
    argument_digestion=False,
    standardizer=None,
    function_source='topomt._private.arg_digestion.function.provider_output',
    map=PIPELINES,
)
def get_provider_output(
    molecular_system: Any = None,
    *,
    method: str,
    backend: str | None = None,
    **kwargs: Any,
) -> ProviderOutput:
    """Run or import an original provider and return its own result object.

    Parameters
    ----------
    molecular_system : molecular system, optional
        MolSysMT-compatible source. CASTp file imports can supply their own PDB.
    method : str
        fpocket/fpocket4, pocketeer, alphaspace2, pycasta, castp/castp3/castpfold.
    backend : str, optional
        Defaults to cli for fpocket, library for Python engines, server for CASTp.
        Files are supported for fpocket and CASTp. Local reproductions are not
        admitted through this original-output entry point.
    **kwargs
        Provider execution/import options, including selection and frame.

    Returns
    -------
    ProviderOutput
        Provider-specific object with ordered pockets, representations and run.

    Raises
    ------
    ValueError
        If the provider method or original backend is invalid. Dispatch refusals
        also inherit the catalogued TopoMT ArgumentError diagnostic.
    LibraryNotFoundError
        If a requested optional Python engine is absent.

    Examples
    --------
    >>> result = get_provider_output('protein.pdb', method='fpocket')  # doctest: +SKIP
    >>> spheres = result.pockets[0].geometries['alpha_spheres']  # doctest: +SKIP
    """
    name = method
    provider = ALIASES.get(name, name)
    selected_backend = DEFAULT_BACKENDS[provider] if backend is None else backend
    if name in {'castp3', 'castpfold'}:
        if selected_backend == 'files':
            kwargs.setdefault('provider_server', name)
        else:
            if 'server' in kwargs and kwargs['server'] != name:
                raise ValueError('Server conflicts with the requested provider method')
            kwargs['server'] = name
    api = import_module(f'topomt.third_party.{provider}.api')
    return api.get_output(molecular_system, backend=selected_backend, **kwargs)
