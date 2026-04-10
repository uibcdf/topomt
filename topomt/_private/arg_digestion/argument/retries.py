import numpy as np

from topomt._private.smonitor import ArgumentError


def digest_retries(retries, caller=None):
    if isinstance(retries, (int, np.integer)) and int(retries) >= 0:
        return int(retries)

    raise ArgumentError(
        arg_name='retries',
        value=retries,
        caller=caller,
        reason='retries must be a non-negative integer.',
    )
