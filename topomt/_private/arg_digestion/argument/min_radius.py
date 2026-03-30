from __future__ import annotations

from typing import Any

import numpy as np

from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError


def digest_min_radius(min_radius: Any, caller: str | None = None) -> Any:
    if puw.is_quantity(min_radius):
        return puw.standardize(min_radius)

    if isinstance(min_radius, (int, float, np.number)):
        return puw.quantity(float(min_radius), 'angstroms')

    raise ArgumentError(
        arg_name='min_radius',
        value=min_radius,
        caller=caller,
        reason='min_radius must be a quantity or a number.',
    )
