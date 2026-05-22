from topomt._private.smonitor import ArgumentError


def digest_min_size(min_size, caller=None):
    if isinstance(min_size, bool):
        raise ArgumentError(
            arg_name='min_size',
            value=min_size,
            caller=caller,
            reason='min_size must be a non-negative integer.',
        )
    if isinstance(min_size, int) and min_size >= 0:
        return min_size

    raise ArgumentError(
        arg_name='min_size',
        value=min_size,
        caller=caller,
        reason='min_size must be a non-negative integer.',
    )
