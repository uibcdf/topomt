from __future__ import annotations

from typing import Any

import numpy as np

from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError


def digest_beta_cluster_cutoff(
    beta_cluster_cutoff: Any, caller: str | None = None
) -> Any:
    if puw.is_quantity(beta_cluster_cutoff):
        return puw.standardize(beta_cluster_cutoff)

    if isinstance(beta_cluster_cutoff, (int, float, np.number)):
        return puw.quantity(float(beta_cluster_cutoff), 'angstroms')

    raise ArgumentError(
        arg_name='beta_cluster_cutoff',
        value=beta_cluster_cutoff,
        caller=caller,
        reason='beta_cluster_cutoff must be a quantity or a number.',
    )
