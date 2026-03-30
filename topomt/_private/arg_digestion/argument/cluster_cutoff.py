from __future__ import annotations

from typing import Any

import numpy as np

from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError


def digest_cluster_cutoff(cluster_cutoff: Any, caller: str | None = None) -> Any:
    if puw.is_quantity(cluster_cutoff):
        return puw.standardize(cluster_cutoff)

    if isinstance(cluster_cutoff, (int, float, np.number)):
        return puw.quantity(float(cluster_cutoff), 'angstroms')

    raise ArgumentError(
        arg_name='cluster_cutoff',
        value=cluster_cutoff,
        caller=caller,
        reason='cluster_cutoff must be a quantity or a number.',
    )
