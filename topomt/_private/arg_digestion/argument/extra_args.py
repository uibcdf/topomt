from topomt._private.smonitor import ArgumentError


def digest_extra_args(extra_args, caller=None):
    if extra_args is None:
        return None

    if isinstance(extra_args, (list, tuple)) and all(
        isinstance(item, str) for item in extra_args
    ):
        return list(extra_args)

    raise ArgumentError(
        arg_name='extra_args',
        value=extra_args,
        caller=caller,
        reason='extra_args must be None or a list/tuple of strings.',
    )
