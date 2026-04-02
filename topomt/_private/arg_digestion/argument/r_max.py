import numpy as np

from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError


def digest_r_max(r_max, caller=None):
    if puw.is_quantity(r_max):
        return puw.standardize(r_max)

    if isinstance(r_max, (int, float, np.number)):
        return puw.quantity(float(r_max), 'angstroms')

    raise ArgumentError(
        arg_name='r_max',
        value=r_max,
        caller=caller,
        reason='r_max must be a quantity or a number.',
    )
