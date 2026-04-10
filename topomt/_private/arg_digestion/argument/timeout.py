import numpy as np

from topomt._private.smonitor import ArgumentError


def digest_timeout(timeout, caller=None):
    if isinstance(timeout, (int, np.integer)) and int(timeout) > 0:
        return int(timeout)

    raise ArgumentError(
        arg_name='timeout',
        value=timeout,
        caller=caller,
        reason='timeout must be a positive integer.',
    )
