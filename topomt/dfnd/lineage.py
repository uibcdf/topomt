"""Cross-frame component matching — the dynamic-identity layer over the static
keys.

Pure post-processing: given the components of two DFND results (e.g. consecutive
MD frames), infer correspondences by **exact** ``support_key`` equality (when the
triangulation coincides) and by **lining overlap** (Jaccard of atom indices)
otherwise. Atom indices are stable across frames (same system), so the overlap is
robust even when the Delaunay triangulation flips and ``support_key`` changes.

This is the basis for ``track_id`` / a lineage graph across a trajectory: a
one-to-many match is a *split*, many-to-one a *merge*. Building the multi-frame
tracks and event labels is a separate step on top of these pairwise matches. See
``devguide/DFND/dynamic_topology.md`` and the component-identity contract in
``object_model.md``.
"""

from __future__ import annotations

from typing import Any, Iterable


def _get(component: Any, name: str) -> Any:
    if isinstance(component, dict):
        return component.get(name)
    return getattr(component, name, None)


def _atoms(component: Any) -> set[int]:
    return {int(a) for a in (_get(component, 'atom_indices') or [])}


def jaccard(a: set[int], b: set[int]) -> float:
    """Jaccard overlap of two index sets (0 when both are empty)."""
    if not a and not b:
        return 0.0
    union = len(a | b)
    return (len(a & b) / union) if union else 0.0


def match_results(
    components_a: Iterable[Any],
    components_b: Iterable[Any],
    *,
    min_jaccard: float = 0.2,
) -> list[dict[str, Any]]:
    """Match components between two results (frames).

    Parameters
    ----------
    components_a, components_b
        Iterables of components (``Component`` objects or raw record dicts) each
        carrying ``component_key``, ``support_key`` and ``atom_indices``.
    min_jaccard
        Minimum lining-atom Jaccard for an inexact (overlap) match.

    Returns
    -------
    list of dict
        One record per matched pair::

            {'a': component_key_a, 'b': component_key_b,
             'jaccard': float, 'exact': bool}

        Exact matches (equal ``support_key``) get ``jaccard=1.0`` and
        ``exact=True``. One-to-many (split) and many-to-one (merge) are both
        represented as multiple records sharing an ``a`` or a ``b``.
    """
    comps_a = list(components_a)
    comps_b = list(components_b)
    atoms_a = [_atoms(c) for c in comps_a]
    atoms_b = [_atoms(c) for c in comps_b]

    support_b: dict[Any, int] = {}
    for j, comp in enumerate(comps_b):
        support = _get(comp, 'support_key')
        if support is not None:
            support_b.setdefault(support, j)

    matches: list[dict[str, Any]] = []
    for i, comp_a in enumerate(comps_a):
        key_a = _get(comp_a, 'component_key')
        support_a = _get(comp_a, 'support_key')

        if support_a is not None and support_a in support_b:
            j = support_b[support_a]
            matches.append({
                'a': key_a,
                'b': _get(comps_b[j], 'component_key'),
                'jaccard': 1.0,
                'exact': True,
            })
            continue

        for j, comp_b in enumerate(comps_b):
            score = jaccard(atoms_a[i], atoms_b[j])
            if score >= min_jaccard:
                matches.append({
                    'a': key_a,
                    'b': _get(comp_b, 'component_key'),
                    'jaccard': score,
                    'exact': False,
                })

    return matches
