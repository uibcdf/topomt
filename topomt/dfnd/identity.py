"""Deterministic identity helpers for static DFND components."""

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np


def _canonical_value(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return _canonical_value(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {
            str(key): _canonical_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_canonical_value(item) for item in value]
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    raise TypeError(f'Unsupported identity value: {type(value).__name__}')


def _digest(prefix: str, value: Any) -> str:
    payload = json.dumps(
        _canonical_value(value),
        allow_nan=False,
        separators=(',', ':'),
        sort_keys=True,
    ).encode('utf-8')
    return f'{prefix}-{hashlib.sha256(payload).hexdigest()}'


def canonical_tetrahedron_support(
    tetrahedra: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    """Return sorted atom-defined tetrahedron identities."""
    return tuple(
        sorted(
            tuple(sorted(int(atom) for atom in tetrahedron))
            for tetrahedron in tetrahedra
        )
    )


def support_key(tetrahedra: Sequence[Sequence[int]]) -> str:
    """Return the exact structural-support key for a component."""
    return _digest('support', canonical_tetrahedron_support(tetrahedra))


def canonical_face_support(
    faces: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    """Return sorted atom-defined face identities."""
    return tuple(sorted(tuple(sorted(int(atom) for atom in face)) for face in faces))


def external_link_support_key(faces: Sequence[Sequence[int]]) -> str:
    """Return the exact face-support key for an external link."""
    return _digest('external-link-support', canonical_face_support(faces))


def substrate_key(substrate: Mapping[str, Any]) -> str:
    """Return the exact key for the atom-indexed numerical substrate."""
    return _digest('substrate', substrate)


def result_key(substrate: Mapping[str, Any], parameters: Mapping[str, Any]) -> str:
    """Return the exact contextual key for one DFND result."""
    return _digest('result', {'substrate': substrate, 'parameters': parameters})


def component_key(result_key_value: str, side: str, support_key_value: str) -> str:
    """Return the contextual key for one classified component."""
    if side not in {'wet', 'dry'}:
        raise ValueError("side must be 'wet' or 'dry'")
    return _digest(
        'component',
        {
            'result_key': result_key_value,
            'side': side,
            'support_key': support_key_value,
        },
    )


def external_link_key(
    parent_component_key: str, external_link_support_key_value: str
) -> str:
    """Return the contextual key for one external link."""
    return _digest(
        'external-link',
        {
            'parent_component_key': parent_component_key,
            'support_key': external_link_support_key_value,
        },
    )


def motif_key(
    parent_component_key: str, motif_type: str, motif_support_key_value: str
) -> str:
    """Return the contextual key for one typed component motif."""
    return _digest(
        'motif',
        {
            'parent_component_key': parent_component_key,
            'motif_type': motif_type,
            'support_key': motif_support_key_value,
        },
    )


def component_sort_key(record: Mapping[str, Any]) -> tuple[int, str]:
    """Sort components by descending node count, then exact support."""
    node_count = record.get('n_nodes', record.get('size'))
    if node_count is None:
        raise KeyError("component record requires 'n_nodes' or 'size'")
    return -int(node_count), str(record['support_key'])
