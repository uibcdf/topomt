"""DFND topological classification — the single source of truth for family names.

This is the catalog seed (public layer 0). The kernel (``graph.py``) delegates to
``classify_topology`` instead of assigning family strings inline, so there is one
definition of what each grounded signature
``(n_external_links, has_residence, n_wall_faces)`` is named. See
``devguide/DFND/taxonomy_architecture_decision.md``.

Phase 1 of the kernel/catalog split (the *inversion*): this reproduces the
historical family strings exactly, so the suite stays green and the green suite
is the completeness proof — if a family could not be reproduced from the grounded
signature, that family would encode something missing from the observables.
Morphological refinement (``pocket`` -> ``pocket``/``groove``) and the
``{name, confidence, marginal}`` record are later, additive layers.
"""

from __future__ import annotations

from . import families as fam


def topology_family(n_external_links: int, has_residence: bool) -> str:
    """The (mouths x residence) cross-product family (no ``percolating`` override).

    ``n_external_links`` is the number of mouths to OCEAN; ``has_residence`` is
    whether the probe can reside anywhere in the component.
    """
    if n_external_links == 0:
        return fam.VOID if has_residence else fam.DEGENERATE_SUBPROBE
    if n_external_links == 1:
        return fam.POCKET if has_residence else fam.SURFACE_CONCAVITY
    return fam.CHANNEL if has_residence else fam.NONRESIDENT_PASSAGE


def classify_topology(
    n_external_links: int, n_resident_nodes: int, n_wall_faces: int
) -> str:
    """Full topological classification from the grounded signature.

    ``percolating`` (a resident component with no enclosing wall faces, i.e. a
    fully porous/exposed region) overrides the cross-product, mirroring the
    kernel's historical behaviour.
    """
    has_residence = n_resident_nodes >= 1
    if has_residence and n_wall_faces == 0:
        return fam.PERCOLATING
    return topology_family(n_external_links, has_residence)
