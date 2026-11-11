"""Public original PISA execution and saved recovery."""

from typing import Any

from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.original_provider_arguments import OPTIONS, PIPELINES

from .output import PisaOutput


@arg_digest(**OPTIONS, map=PIPELINES['pisa'])
def get_output(
    molecular_system: Any = None, *, backend: str = 'cli', **options: Any
) -> PisaOutput:
    """Return original PISA interface results and their evidence.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Original source with one selected frame and reference chemical state.
    backend : str
        Original cli execution or files recovery.
    **options
        Closed provider-owned settings; files recovery admits only bundle_file.
        CLI uses pisa_cmd and requires pisa_home with original setup resources.
        The selected route analyzes the supplied assembly with --as-is and
        does not predict assemblies. Common controls select one source frame,
        selection/reference chemistry, workers=1, timeout=120 seconds per
        command and max_atoms=25000. See the PISA user guide for original
        interface/contact and acquisition semantics.

    Returns
    -------
    PisaOutput
        Original interface records, source context and captured artifacts.

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

    return execute('pisa', molecular_system, backend, options)
