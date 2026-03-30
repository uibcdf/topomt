from __future__ import annotations

from typing import Any

import numpy as np

from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError


def digest_max_radius(max_radius: Any, caller: str | None = None) -> Any:
    if puw.is_quantity(max_radius):
        return puw.standardize(max_radius)

    if isinstance(max_radius, (int, float, np.number)):
        return puw.quantity(float(max_radius), 'angstroms')

    raise ArgumentError(
        arg_name='max_radius',
        value=max_radius,
        caller=caller,
        reason='max_radius must be a quantity or a number.',
    )
