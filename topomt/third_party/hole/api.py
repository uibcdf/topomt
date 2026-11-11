"""Public original HOLE execution and saved recovery."""

from typing import Any

from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.original_provider_arguments import OPTIONS, PIPELINES

from .output import HoleOutput


@arg_digest(**OPTIONS, map=PIPELINES['hole'])
def get_output(
    molecular_system: Any = None, *, backend: str = 'cli', **options: Any
) -> HoleOutput:
    """Return original HOLE channel results and their evidence.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Original source with one selected frame and reference chemical state.
    backend : str
        Original cli execution or files recovery.
    **options
        Closed provider-owned settings; files recovery admits only bundle_file.
        CLI requires origin (length three-vector) and direction (dimensionless
        three-vector). Optional hole_cmd and radii_file select external inputs;
        sample_step=0.5 and end_radius=10.0 use angstroms, and random_seed=12345
        fixes the original stochastic seed. Common controls select the source
        frame/reference chemistry and use workers=1, timeout=120 seconds and
        max_atoms=25000. See the HOLE user guide for original profile semantics.

    Returns
    -------
    HoleOutput
        Original channel records, source context and captured artifacts.

    Raises
    ------
    ArgumentError
        If options, physical quantities or parameter groups are invalid.
    ProviderUnavailableError
        If the selected original runtime/resources are unavailable.
    ProviderExecutionError
        If execution or complete result validation fails.
    ValueError
        If saved evidence and source context disagree.

    Examples
    --------
    >>> result = get_output(source, backend='files', bundle_file='saved.zip')  # doctest: +SKIP
    """
    from topomt.third_party._execution import get_output as execute

    return execute('hole', molecular_system, backend, options)
