"""Public original MOLE execution and engine-independent recovery."""

from typing import Any

from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.original_provider_arguments import OPTIONS, PIPELINES

from .output import MoleOutput


@arg_digest(**OPTIONS, map=PIPELINES['mole'])
def get_output(
    molecular_system: Any = None, *, backend: str = 'cli', **options: Any
) -> MoleOutput:
    """Return original MOLE channels, cavities and recoverable evidence.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Full source with one selected frame and a reference chemical state.
    backend : str, default='cli'
        Original execution or engine-independent 'files' recovery.
    **options
        MOLE options documented in the original local provider guide. Select an
        executable with mole_cmd. Omit origin for automatic origins, or supply
        a three-coordinate length quantity. Physical scalars accept angstroms
        or compatible quantities. Default workers=1, memory_mb=1024 (managed
        heap cap), timeout=300 seconds. Files accepts only bundle_file.

    Returns
    -------
    MoleOutput
        Original channels and cavity/void records, preserving original kinds,
        profiles, meshes, descriptors and source evidence.

    Raises
    ------
    ArgumentError
        If an option or physical/resource constraint is invalid.
    UnknownArgumentError
        If an option is outside this provider's admitted contract.
    ProviderUnavailableError
        If the selected executable is absent.
    ProviderExecutionError
        If execution, completion or original output validation fails.
    ValueError
        If saved evidence or its source context is inconsistent.

    Examples
    --------
    >>> output = get_output(source, mole_cmd='/tools/mole2')  # doctest: +SKIP
    >>> output.channels[0].geometries['centerline'].radii  # doctest: +SKIP
    """
    from topomt.third_party._execution import get_output as execute

    return execute('mole', molecular_system, backend, options)
