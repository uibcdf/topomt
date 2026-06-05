from topomt._private.smonitor import ArgumentError


def digest_dry_adjacency(dry_adjacency, caller=None):
    if dry_adjacency in {'face', 'edge', 'vertex'}:
        return dry_adjacency

    raise ArgumentError(
        arg_name='dry_adjacency',
        value=dry_adjacency,
        caller=caller,
        reason="dry_adjacency must be 'face', 'edge' or 'vertex'.",
    )
