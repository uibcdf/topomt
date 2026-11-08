"""Physical scalar contracts for native DFND options at the shared gateway."""

from typing import Any

import numpy as np

from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError


def digest_dfnd_length(value: Any, name: str, caller: str | None = None) -> Any:
    """Admit a finite nonnegative length without hiding bare-number deprecation."""
    is_quantity = puw.is_quantity(value)
    try:
        raw = puw.get_value(value, to_unit='nm') if is_quantity else value
        array = np.asarray(raw)
        if array.ndim == 0 and array.dtype.kind in 'iuf':
            number = float(array)
            if np.isfinite(number) and number >= 0:
                # Native entry points own the legacy angstrom warning/conversion.
                return puw.quantity(number, 'nm') if is_quantity else number
    except (TypeError, ValueError, OverflowError):
        pass
    raise ArgumentError(
        arg_name=name,
        value=value,
        caller=caller,
        reason=f'{name} must be a finite nonnegative scalar length; bare numbers use angstroms.',
    )
