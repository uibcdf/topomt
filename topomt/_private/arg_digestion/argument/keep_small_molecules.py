from topomt._private.smonitor import ArgumentError


def digest_keep_small_molecules(keep_small_molecules, caller=None):
    if isinstance(keep_small_molecules, bool):
        return keep_small_molecules

    raise ArgumentError(
        arg_name='keep_small_molecules',
        value=keep_small_molecules,
        caller=caller,
        reason='keep_small_molecules must be boolean.',
    )
