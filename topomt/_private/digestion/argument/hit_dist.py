from __future__ import annotations
from typing import Any
from topomt._pyunitwizard import pyunitwizard as puw
import numpy as np

def digest_hit_dist(hit_dist: Any, caller: str | None = None) -> Any:
    """
    Digest the 'hit_dist' argument.
    """
    if puw.is_quantity(hit_dist):
        return puw.standardize(hit_dist)
    if isinstance(hit_dist, (int, float, np.number)):
        return puw.quantity(float(hit_dist), 'angstroms')
    return hit_dist
