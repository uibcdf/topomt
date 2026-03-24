from __future__ import annotations
from typing import Any
import numpy as np

def digest_binder_coords(binder_coords: Any, caller: str | None = None) -> Any:
    """
    Digest the 'binder_coords' argument.
    """
    if binder_coords is None:
        return None
    if isinstance(binder_coords, np.ndarray):
        return binder_coords
    return np.array(binder_coords)
