import numpy as np

from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError


def digest_probe_radius(probe_radius, caller=None):
    if puw.is_quantity(probe_radius):
        return puw.standardize(probe_radius)

    if isinstance(probe_radius, (int, float, np.number)):
        return puw.quantity(float(probe_radius), 'angstroms')

    raise ArgumentError(
        arg_name='probe_radius',
        value=probe_radius,
        caller=caller,
        reason='probe_radius must be a quantity or a number.',
    )
