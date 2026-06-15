"""Explicit atom-index-space helpers for the TopoMT viewer boundary."""

from collections.abc import Iterable
from typing import Any

MESH_LOCAL = 'mesh_local'
MOLECULAR_SYSTEM = 'molecular_system'
_VALID_SPACES = {MESH_LOCAL, MOLECULAR_SYSTEM}


def atom_indices(values: Iterable[int] | None, *, space: str) -> list[int]:
    """Normalize atom indices while requiring their owning space."""
    if space not in _VALID_SPACES:
        raise ValueError(f'Unknown atom index space: {space!r}')
    if values is None:
        return []
    return [int(value) for value in values]


def atom_index_payload(values: Iterable[int] | None, space: str) -> dict[str, Any]:
    """Build an addon-owned atom-index payload with an explicit space label."""
    return {
        'atom_indices': atom_indices(values, space=space),
        'atom_index_space': space,
    }


def mesh_local_from_molecular_system(
    values: Iterable[int] | None, index_map: Iterable[int]
) -> list[int]:
    """Map molecular-system atom indices into the cached DFND mesh space."""
    local_by_global = {
        int(global_id): local for local, global_id in enumerate(index_map)
    }
    normalized = [] if values is None else [int(value) for value in values]
    missing = [value for value in normalized if value not in local_by_global]
    if missing:
        raise ValueError(
            'Molecular-system atom indices are absent from the DFND mesh: '
            + ', '.join(str(value) for value in missing)
        )
    return [local_by_global[value] for value in normalized]
