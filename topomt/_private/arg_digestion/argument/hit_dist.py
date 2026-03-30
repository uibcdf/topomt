from __future__ import annotations

from typing import Any

import numpy as np

from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError


def digest_hit_dist(hit_dist: Any, caller: str | None = None) -> Any:
    if puw.is_quantity(hit_dist):
        return puw.standardize(hit_dist)

    if isinstance(hit_dist, (int, float, np.number)):
        return puw.quantity(float(hit_dist), 'angstroms')

    raise ArgumentError(
        arg_name='hit_dist',
        value=hit_dist,
        caller=caller,
        reason='hit_dist must be a quantity or a number.',
    )
