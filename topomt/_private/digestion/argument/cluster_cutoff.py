from __future__ import annotations
from typing import Any
from topomt._pyunitwizard import pyunitwizard as puw
import numpy as np

def digest_cluster_cutoff(cluster_cutoff: Any, caller: str | None = None) -> Any:
    """
    Digest the 'cluster_cutoff' argument.
    """
    if puw.is_quantity(cluster_cutoff):
        return puw.standardize(cluster_cutoff)
    if isinstance(cluster_cutoff, (int, float, np.number)):
        return puw.quantity(float(cluster_cutoff), 'angstroms')
    return cluster_cutoff # Let it pass if it's already a float? Or raise error?
