"""Value contract for native face-permeability slack."""

from typing import Any

from ..dfnd_arguments import digest_dfnd_length


def digest_permeability_tolerance(
    permeability_tolerance: Any, caller: str | None = None
) -> Any:
    return digest_dfnd_length(permeability_tolerance, 'permeability_tolerance', caller)
