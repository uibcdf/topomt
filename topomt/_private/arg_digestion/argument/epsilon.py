"""Value contract for the native geometry tolerance."""

from typing import Any

from ..dfnd_arguments import digest_dfnd_length


def digest_epsilon(epsilon: Any, caller: str | None = None) -> Any:
    return digest_dfnd_length(epsilon, 'epsilon', caller)
