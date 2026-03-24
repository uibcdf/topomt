from topomt.wrappers.fpocket.integration import get_topography_with_fpocket


def fpocket4(
    molecular_system,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    fpocket_cmd: str = 'fpocket',
    extra_args: list[str] | None = None,
    syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
):
    """
    Run the external fpocket binary and map its output to a Topography object.

    This method is intended to preserve fpocket's detected pockets, atom
    membership, ranking, and primary descriptors rather than approximate them
    with a native TopoMT implementation.
    """

    return get_topography_with_fpocket(
        molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
        fpocket_cmd=fpocket_cmd,
        extra_args=extra_args,
    )
