import numpy as np

from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError


def digest_sasa_threshold(sasa_threshold, caller=None):
    if puw.is_quantity(sasa_threshold):
        return puw.standardize(sasa_threshold)

    if isinstance(sasa_threshold, (int, float, np.number)):
        return puw.quantity(float(sasa_threshold), 'angstroms**2')

    raise ArgumentError(
        arg_name='sasa_threshold',
        value=sasa_threshold,
        caller=caller,
        reason='sasa_threshold must be a quantity or a number.',
    )
