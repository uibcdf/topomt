import numpy as np
from topomt import pyunitwizard as puw
from ...exceptions import ArgumentError

def digest_max_neighbor_dist(max_neighbor_dist, caller=None):

    if puw.is_quantity(max_neighbor_dist):
        if puw.check(max_neighbor_dist, dimensionality={'[L]':1}):
            return puw.standardize(max_neighbor_dist)

    raise ArgumentError('max_neighbor_dist', value=max_neighbor_dist, caller=caller, message=None)

