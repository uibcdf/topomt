from __future__ import annotations
from typing import Any
from topomt._pyunitwizard import pyunitwizard as puw

def digest_min_radius(min_radius: Any, caller: str | None = None) -> Any:
    """
    Digest the 'min_radius' argument.
    If it's a number, assume Angstroms. If it's a quantity, standardize.
    """
    if puw.is_quantity(min_radius):
        # We can use puw.get_value to convert or just return as quantity
        # For consistency with the rest of the toolkit, let's keep it as quantity if it was one.
        return puw.standardize(min_radius)
    
    if isinstance(min_radius, (int, float, np.number)):
        return puw.quantity(float(min_radius), 'angstroms')
        
    # Fallback to smonitor ArgumentError if available
    from topomt._private.smonitor import ArgumentError
    return ArgumentError(arg_name='min_radius', value=min_radius, caller=caller, 
                         reason="min_radius must be a quantity or a number.")

import numpy as np
