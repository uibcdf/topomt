from topomt.third_party.fpocket._native_impl import (
    _build_native_state,
    _native_topography_from_state,
    _normalize_structure_indices,
)


def get_topography(
    molecular_system,
    *,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    keep_water: bool = False,
    keep_ions: bool = False,
    keep_small_molecules: bool = False,
    include_group_names: list[str] | tuple[str, ...] | set[str] | None = None,
    exclude_group_names: list[str] | tuple[str, ...] | set[str] | None = None,
    **kwargs,
):
    """Run the TopoMT-specific fpocket variant."""

    structure_indices = _normalize_structure_indices(structure_indices)
    state = _build_native_state(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
        keep_water=keep_water,
        keep_ions=keep_ions,
        keep_small_molecules=keep_small_molecules,
        include_group_names=include_group_names,
        exclude_group_names=exclude_group_names,
        implementation='topomt',
    )
    return _native_topography_from_state(
        state,
        molecular_system=molecular_system,
        source='fpocket-topomt',
        source_prefix='fpocket-topomt',
    )
