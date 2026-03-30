from topomt._private.smonitor import ArgumentError


def digest_keep_ions(keep_ions, caller=None):
    if isinstance(keep_ions, bool):
        return keep_ions

    raise ArgumentError(
        arg_name='keep_ions',
        value=keep_ions,
        caller=caller,
        reason='keep_ions must be boolean.',
    )
