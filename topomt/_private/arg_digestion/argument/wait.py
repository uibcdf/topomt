import numpy as np

from topomt._private.smonitor import ArgumentError


def digest_wait(wait, caller=None):
    if isinstance(wait, (int, np.integer)) and int(wait) >= 0:
        return int(wait)

    raise ArgumentError(
        arg_name='wait',
        value=wait,
        caller=caller,
        reason='wait must be a non-negative integer.',
    )
