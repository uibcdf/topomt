import numpy as np
from topomt import pyunitwizard as puw
from ...exceptions import ArgumentError

def digest_radii(radii, caller=None):

    if radii is None:
        return None

    if puw.is_quantity(radii):
        if puw.check(radii, dimensionality={'[L]':1}):
            radii_value = puw.get_value(radii)
            if isinstance(radii_value, np.ndarray):
                if radii_value.ndim == 1:
                    return puw.standardize(radii)
                elif isinstance(radii_value, (list, tuple)):
                    radii_array = np.array(radii_value)
                    if radii_array.ndim == 1:
                        return puw.standardize(radii)

    raise ArgumentError('radii', value=radii, caller=caller, message=None)

