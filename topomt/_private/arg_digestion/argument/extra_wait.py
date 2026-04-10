import numpy as np

from topomt._private.smonitor import ArgumentError


def digest_extra_wait(extra_wait, caller=None):
    if isinstance(extra_wait, (int, np.integer)) and int(extra_wait) >= 0:
        return int(extra_wait)

    raise ArgumentError(
        arg_name='extra_wait',
        value=extra_wait,
        caller=caller,
        reason='extra_wait must be a non-negative integer.',
    )
