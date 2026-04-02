import numpy as np

from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError


def digest_polar_probe_radius(polar_probe_radius, caller=None):
    if puw.is_quantity(polar_probe_radius):
        return puw.standardize(polar_probe_radius)

    if isinstance(polar_probe_radius, (int, float, np.number)):
        return puw.quantity(float(polar_probe_radius), 'angstroms')

    raise ArgumentError(
        arg_name='polar_probe_radius',
        value=polar_probe_radius,
        caller=caller,
        reason='polar_probe_radius must be a quantity or a number.',
    )
