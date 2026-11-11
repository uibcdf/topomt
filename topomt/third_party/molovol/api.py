"""Public original MoloVol execution and source-bound recovery."""

from typing import Any

from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.original_provider_arguments import OPTIONS, PIPELINES

from .output import MoloVolOutput


@arg_digest(**OPTIONS, map=PIPELINES['molovol'])
def get_output(
    molecular_system: Any = None, *, backend: str = 'cli', **options: Any
) -> MoloVolOutput:
    """Return original isolated-structure MoloVol cavities and measurements.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Source with one selected frame and a reference chemical state.
    backend : {'cli', 'files'}, default='cli'
        Original local execution or engine-independent saved recovery.
    **options
        Select the executable with molovol_cmd. Physical scalars use angstroms
        or compatible quantities: probe_radius (default 1.4), grid_step (0.2),
        and optional large_probe_radius for two-probe mode. element_radii maps
        selected element symbols to explicit overrides. elements_file selects
        the original resource table; otherwise use the executable's adjacent
        inputfile/elements.txt. octree_depth defaults to 4 (admitted 0..8),
        calculate_surfaces to False, workers to 1 and timeout to 120 seconds.
        max_grid_points bounds the estimated allocation. virtual_display=None
        selects a private Xvfb only on Linux without DISPLAY; True/False make
        the choice explicit. xvfb_cmd selects that optional executable.
        Files recovery admits only bundle_file.

    Returns
    -------
    MoloVolOutput
        Original internal regions, measures and recoverable evidence. Outside
        remains in the report, without becoming an internal cavity.

    Raises
    ------
    ArgumentError
        For invalid options, units, resources or unsupported parameter groups.
    UnknownArgumentError
        For an undeclared option.
    ProviderUnavailableError
        If the selected executable, display backend or resource is unavailable.
    ProviderExecutionError
        If execution or original result validation fails.
    ValueError
        If saved evidence or source context is inconsistent.

    Examples
    --------
    >>> result = get_output(source, molovol_cmd='/tools/molovol')  # doctest: +SKIP
    >>> result.cavities[0].measurements['occupied_volume'].value  # doctest: +SKIP
    """
    from topomt.third_party._execution import get_output as execute

    return execute('molovol', molecular_system, backend, options)
