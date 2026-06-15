"""Executable context actions for the TopoMT addon."""

from typing import Any

from .runtime import ensure_runtime
from .simplex_selection import resolve_simplices


def focus_topography_feature(
    view: Any | None = None, payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Return a normalized description of a feature-focus request."""
    return {
        'action': 'focus-topography-feature',
        'has_view': view is not None,
        'payload': {} if payload is None else dict(payload),
    }


def inspect_dfnd_tetrahedra(
    view: Any | None = None, payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Inspect DFND tetrahedra from structured refs or selected shape atoms."""
    payload = {} if payload is None else dict(payload)
    tetrahedron_ids: list[int] = []

    def add(values) -> None:
        for value in values:
            tetrahedron_id = int(value)
            if tetrahedron_id not in tetrahedron_ids:
                tetrahedron_ids.append(tetrahedron_id)

    for ref in payload.get('entity_refs', ()) or ():
        add(ref.get('tetrahedron_ids', ()))
    action_payload = payload.get('addon_action_payload', {}) or {}
    add(action_payload.get('tetrahedron_ids', ()))

    runtime = ensure_runtime(view) if view is not None else None
    topography = getattr(runtime, 'topography', None)
    contexts = [payload.get('context', {}) or {}]
    active_selection = getattr(view, 'active_selection', None)
    for item in getattr(active_selection, 'items', ()) or ():
        if item.get('source_kind') == 'shape':
            contexts.append(item)

    if topography is not None:
        for context in contexts:
            atoms = context.get('atom_indices', ()) or ()
            for item in resolve_simplices(topography, atoms):
                add(item.get('payload', {}).get('tetrahedron_ids', ()))

    if topography is not None and tetrahedron_ids:
        dfnd = getattr(topography, 'dfnd', None)
        if dfnd is not None:
            dfnd.info(tetrahedron_ids)

    return {
        'action': 'dfnd-tetrahedron-info',
        'tetrahedron_ids': tetrahedron_ids,
    }
