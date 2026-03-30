from __future__ import annotations

from typing import Any

import numpy as np

from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError


def digest_binder_coords(binder_coords: Any, caller: str | None = None) -> Any:
    if binder_coords is None:
        return None

    if puw.is_quantity(binder_coords):
        value = np.asarray(puw.get_value(binder_coords), dtype=float)
        if value.ndim == 2 and value.shape[1] == 3:
            return puw.standardize(binder_coords)
        raise ArgumentError(
            arg_name='binder_coords',
            value=binder_coords,
            caller=caller,
            reason='binder_coords must have shape (n, 3).',
        )

    value = np.asarray(binder_coords, dtype=float)
    if value.ndim == 2 and value.shape[1] == 3:
        return value

    raise ArgumentError(
        arg_name='binder_coords',
        value=binder_coords,
        caller=caller,
        reason='binder_coords must have shape (n, 3).',
    )
