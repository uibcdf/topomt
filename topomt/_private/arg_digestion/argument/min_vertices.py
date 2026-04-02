import numpy as np

from topomt._private.smonitor import ArgumentError


def digest_min_vertices(min_vertices, caller=None):
    if isinstance(min_vertices, (int, np.integer)) and int(min_vertices) >= 1:
        return int(min_vertices)

    raise ArgumentError(
        arg_name='min_vertices',
        value=min_vertices,
        caller=caller,
        reason='min_vertices must be a positive integer.',
    )
