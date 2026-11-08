"""Value contract for native residence slack."""

from typing import Any

from ..dfnd_arguments import digest_dfnd_length


def digest_residence_tolerance(
    residence_tolerance: Any, caller: str | None = None
) -> Any:
    return digest_dfnd_length(residence_tolerance, 'residence_tolerance', caller)
