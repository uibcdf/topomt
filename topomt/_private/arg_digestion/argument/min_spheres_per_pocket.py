import numpy as np
from topomt import pyunitwizard as puw
from ...exceptions import ArgumentError

def digest_min_spheres_per_pocket(min_spheres_per_pocket, caller=None):

    if isinstance(min_spheres_per_pocket, int):
        return min_spheres_per_pocket

    raise ArgumentError('min_spheres_per_pocket', value=min_spheres_per_pocket, caller=caller, message=None)

