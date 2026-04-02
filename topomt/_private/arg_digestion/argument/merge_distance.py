import numpy as np

from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError


def digest_merge_distance(merge_distance, caller=None):
    if puw.is_quantity(merge_distance):
        return puw.standardize(merge_distance)

    if isinstance(merge_distance, (int, float, np.number)):
        return puw.quantity(float(merge_distance), 'angstroms')

    raise ArgumentError(
        arg_name='merge_distance',
        value=merge_distance,
        caller=caller,
        reason='merge_distance must be a quantity or a number.',
    )
