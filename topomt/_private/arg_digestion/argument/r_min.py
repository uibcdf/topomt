import numpy as np

from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError


def digest_r_min(r_min, caller=None):
    if puw.is_quantity(r_min):
        return puw.standardize(r_min)

    if isinstance(r_min, (int, float, np.number)):
        return puw.quantity(float(r_min), 'angstroms')

    raise ArgumentError(
        arg_name='r_min',
        value=r_min,
        caller=caller,
        reason='r_min must be a quantity or a number.',
    )
