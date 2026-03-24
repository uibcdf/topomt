from __future__ import annotations
from typing import Any
from topomt._pyunitwizard import pyunitwizard as puw
import numpy as np

def digest_max_radius(max_radius: Any, caller: str | None = None) -> Any:
    """
    Digest the 'max_radius' argument.
    If it's a number, assume Angstroms. If it's a quantity, standardize.
    """
    if puw.is_quantity(max_radius):
        return puw.standardize(max_radius)
    
    if isinstance(max_radius, (int, float, np.number)):
        return puw.quantity(float(max_radius), 'angstroms')
        
    from topomt._private.smonitor import ArgumentError
    return ArgumentError(arg_name='max_radius', value=max_radius, caller=caller, 
                         reason="max_radius must be a quantity or a number.")
