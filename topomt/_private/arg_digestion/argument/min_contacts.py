import numpy as np
from topomt import pyunitwizard as puw
from ...exceptions import ArgumentError

def digest_min_contacts(min_contacts, caller=None):

    if isinstance(min_contacts, (int, np.integer)):
        return min_contacts

    raise ArgumentError('min_contacts', value=min_contacts, caller=caller, message=None)

