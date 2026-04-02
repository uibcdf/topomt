import numpy as np

from topomt._private.smonitor import ArgumentError


def digest_min_spheres(min_spheres, caller=None):
    if isinstance(min_spheres, (int, np.integer)) and int(min_spheres) >= 1:
        return int(min_spheres)

    raise ArgumentError(
        arg_name='min_spheres',
        value=min_spheres,
        caller=caller,
        reason='min_spheres must be a positive integer.',
    )
