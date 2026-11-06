"""Use shared reference-state admission at the legacy dispatcher boundary."""

from typing import Any

from ..external_arguments import digest_chemical_state as _digest_chemical_state


def digest_chemical_state(chemical_state: Any, caller: str | None = None) -> str | int:
    return _digest_chemical_state(chemical_state, caller=caller)
