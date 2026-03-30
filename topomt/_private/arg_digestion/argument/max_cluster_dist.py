import numpy as np
from topomt import pyunitwizard as puw
from ...exceptions import ArgumentError

def digest_max_cluster_dist(max_cluster_dist, caller=None):

    if puw.is_quantity(max_cluster_dist):
        if puw.check(max_cluster_dist, dimensionality={'[L]':1}):
            return puw.standardize(max_cluster_dist)

    raise ArgumentError('max_cluster_dist', value=max_cluster_dist, caller=caller, message=None)

