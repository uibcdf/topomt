"""Public original POVME execution and saved recovery."""

from typing import Any

from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.original_provider_arguments import OPTIONS, PIPELINES

from .output import PovmeOutput


@arg_digest(**OPTIONS, map=PIPELINES['povme'])
def get_output(
    molecular_system: Any = None, *, backend: str = 'library', **options: Any
) -> PovmeOutput:
    """Return original POVME region results and their evidence.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Original source with one selected frame and reference chemical state.
    backend : str
        Original library execution or files recovery.
    **options
        Closed provider-owned settings; files recovery admits only bundle_file.
        Execution requires inclusion_regions; exclusion_regions and seed_regions
        are optional sphere/box lists with explicit length-quantity centers.
        Source/interpreter controls are upstream_root, pymolecule_root and
        python_cmd. grid_step=1.0 and distance_cutoff=1.09 use angstroms;
        convex_hull_exclusion=True and contiguous_points_criteria=4 retain
        original region rules. The route is serial with timeout=120 seconds,
        max_grid_points=250000 and max_candidate_pairs=10000000. Common source
        selection/frame/reference chemistry controls also apply.

    Returns
    -------
    PovmeOutput
        Original region records, source context and captured artifacts.

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

    return execute('povme', molecular_system, backend, options)
