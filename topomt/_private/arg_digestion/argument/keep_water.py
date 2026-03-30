from topomt._private.smonitor import ArgumentError


def digest_keep_water(keep_water, caller=None):
    if isinstance(keep_water, bool):
        return keep_water

    raise ArgumentError(
        arg_name='keep_water',
        value=keep_water,
        caller=caller,
        reason='keep_water must be boolean.',
    )
