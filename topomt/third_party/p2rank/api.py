"""Public original p2rank execution and source-bound saved recovery."""

from typing import Any

from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.original_provider_arguments import OPTIONS, PIPELINES

from .output import P2RankOutput


@arg_digest(**OPTIONS, map=PIPELINES['p2rank'])
def get_output(
    molecular_system: Any = None, *, backend: str = 'cli', **options: Any
) -> P2RankOutput:
    """Return original predicted ligand-binding sites and recoverable evidence.

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
    P2RankOutput
        Original records with attributed geometry, measurements and artifacts.
        Empty original success remains empty; operational failure raises.

    Raises
    ------
    ArgumentError
        If the route, option or physical/resource constraint is invalid.
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

    return execute('p2rank', molecular_system, backend, options)
