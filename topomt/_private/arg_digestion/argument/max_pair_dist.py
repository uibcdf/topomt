import numpy as np
from topomt import pyunitwizard as puw
from ...exceptions import ArgumentError

def digest_max_pair_dist(max_pair_dist, caller=None):

    if puw.is_quantity(max_pair_dist):
        if puw.check(max_pair_dist, dimensionality={'[L]':1}):
            return puw.standardize(max_pair_dist)

    raise ArgumentError('max_pair_dist', value=max_pair_dist, caller=caller, message=None)

