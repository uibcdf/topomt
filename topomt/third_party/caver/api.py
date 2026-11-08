"""Public original caver execution and source-bound saved recovery."""

from typing import Any

from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.original_provider_arguments import OPTIONS, PIPELINES

from .output import CaverOutput


@arg_digest(**OPTIONS, map=PIPELINES['caver'])
def get_output(
    molecular_system: Any = None, *, backend: str = 'cli', **options: Any
) -> CaverOutput:
    """Return original ordered tunnel profiles and recoverable evidence.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Full source inventory with one selected frame and a reference chemical
        state. No preparation or chemical-state inference is performed.
    backend : str, default='cli'
        Original cli execution or engine-independent 'files' recovery.
    **options
        Provider-owned options documented in the third-party engine guide.
        All runners default to one worker and a 300-second timeout. Selection,
        structure_indices, chemical_state and syntax use MolSysMT conventions.
        For files, supply only bundle_file; saved context cannot be overridden.

    Returns
    -------
    CaverOutput
        Original records with attributed geometry, measurements and artifacts.
        Empty original success remains empty; operational failure raises.

    Raises
    ------
    ArgumentError
        If the route, option or physical/resource constraint is invalid.
    UnknownArgumentError
        If an option is outside this provider's admitted contract.
    ProviderUnavailableError
        If a selected original executable is unavailable.
    LibraryNotFoundError
        If a required optional Python engine is absent.
    ProviderExecutionError
        If original execution fails, times out or exceeds the capture budget.
    ValueError
        If original output or saved source context is inconsistent.

    Examples
    --------
    >>> output = get_output(source, backend='files', bundle_file='original.zip')  # doctest: +SKIP
    """
    from topomt.third_party._execution import get_output as execute

    return execute('caver', molecular_system, backend, options)
