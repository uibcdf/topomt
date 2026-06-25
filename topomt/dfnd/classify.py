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


# --- morphological refinement (catalog level; not kernel families) -----------

# The open (occlusion<=1) refinement of a 1-mouth resident concavity is a
# **generic** placeholder: we can measure the aperture (open vs occluded) but not
# yet the *shape* (elongation/axis), so we cannot yet name the leaf. It is
# provisional and refines, when shape metrics land, into a leaf -- groove
# (elongated, with an axis), a round dish, a funnel, ... -- or stays open_concavity.
OPEN_CONCAVITY = 'open_concavity'
# The first refined leaf of ``open_concavity``: an elongated open concavity with a
# defined long axis (a surface furrow). ``GROOVE`` refines the generic when the shape
# metric (``morphometrics['elongation']``) clears the threshold below.
GROOVE = 'groove'
# A second leaf of ``open_concavity``: a DEEP open canyon (the active-site cleft
# between two lobes). DFND sees the inter-lobe context only as depth, so ``CLEFT``
# refines the generic when ``morphometrics['buriedness']`` (the deepest residence
# depth from the mouth) clears the threshold below. It is checked BEFORE groove (a
# deep canyon is a cleft even if elongated).
CLEFT = 'cleft'

# The feature-catalog backbone: the generic feature(s) per shape-type -- the
# refinement target for a component we cannot yet name to a specific leaf. Recorded
# here so the backbone is one source in code; the full sheet (refined leaves, the
# metric that refines each, component correspondence, motifs, status) lives in
# devguide/DFND/feature_catalog.md. Create a shape-type's generic WHEN DFND promotes
# components in it (concavity now; convexity/mixed when their promotion is built).
GENERIC_FEATURE_BY_SHAPE_TYPE = {
    # concavity: resident families + the non-resident-shadow generic
    'concavity': (
        fam.VOID, fam.POCKET, OPEN_CONCAVITY, fam.CHANNEL, 'non_resident_contact',
    ),
    # solid side (dry): surface relief vs internal core -- future (no promotion yet)
    'convexity': ('generic_convexity', 'buried_core'),
    'mixed': ('interface',),  # partial -- detected via n_dry_contacts
    'boundary': ('mouth', 'neck', 'generic_boundary'),  # mouth done; neck = constriction
    'point': ('generic_point',),  # future
}

# |occlusion - 1| within this band -> the pocket/open_concavity call is marginal.
_OCCLUSION_MARGIN = 0.1
# |occlusion - 1| at/above which the pocket/open_concavity call is fully confident
# (occlusion 2 or 0 -> 1.0). Confidence ramps linearly from the threshold.
_OCCLUSION_FULL_CONFIDENCE = 1.0
# PROVISIONAL, tunable threshold (the elongation debt, decision S12): an open concavity
# whose shape elongation (max/second PCA std of its residence centers) is at/above this
# is the leaf ``groove``; below it stays the generic ``open_concavity``. Synthetic data
# does not yet separate groove from a round bowl cleanly -- validate on real PDBs before
# treating it as canonical. ``_GROOVE_MARGIN`` flags a near-threshold call as marginal.
_GROOVE_ELONGATION = 2.5
_GROOVE_MARGIN = 0.3
# PROVISIONAL, tunable threshold for the ``cleft`` leaf: an open concavity whose
# buriedness (deepest residence depth from the mouth, a RAW topological-depth count --
# so the threshold is system/discretization-dependent, hence provisional, S12) is
# at/above this is a deep canyon (a cleft); below it the elongation test (groove)
# applies. Calibrated against a real cleft (1hel lysozyme buriedness 13) vs a shallow
# groove (6).
_CLEFT_BURIEDNESS = 10
_CLEFT_MARGIN = 1


def classify(
    n_external_links: int,
    n_resident_nodes: int,
    n_wall_faces: int,
    occlusion: float | None = None,
    elongation: float | None = None,
    buriedness: float | None = None,
) -> dict:
    """Catalog morphological classification: ``{name, confidence, marginal}``.

    Refines the 1-mouth resident family by aperture -- ``pocket`` (occluded,
    ``occlusion > 1``) vs ``open_concavity`` (open, ``occlusion <= 1``). The open
    case is a **generic** leaf (we measure aperture but not yet shape), refined
    later into ``groove``/``dish``/``funnel``/... when shape metrics land; the
    occluded case keeps the community name ``pocket``. Occlusion is
    name-determining only for one mouth (S5 criterion); all other families pass
    through. This is the **additive** morphology layer (coexists with the kernel
    ``family``; does not yet drive ``feature_type``).

    **Confidence is per-threshold** (decision S7): the topological names are exact
    given the grounded signature, so ``confidence = 1.0`` (their probe-margin is a
    separate first-class view, ``component.characteristic_radii``); the
    morphological pocket/open_concavity call rides the ``occlusion = 1`` threshold,
    so its confidence ramps with ``|occlusion - 1|`` (its own unit, a ratio), and
    ``marginal`` flags an occlusion within the boundary band.
    """
    family = classify_topology(n_external_links, n_resident_nodes, n_wall_faces)
    if family != fam.POCKET or occlusion is None:
        return {'name': family, 'confidence': 1.0, 'marginal': False}

    occ_margin = abs(occlusion - 1.0)
    confidence = min(1.0, occ_margin / _OCCLUSION_FULL_CONFIDENCE)
    if occlusion > 1.0:  # occluded -> the community pocket
        return {
            'name': fam.POCKET,
            'confidence': confidence,
            'marginal': occ_margin <= _OCCLUSION_MARGIN,
        }

    # open (occlusion <= 1): refine the generic open_concavity to a leaf (provisional,
    # S12). cleft (a DEEP canyon, by buriedness) is checked BEFORE groove (an ELONGATED
    # furrow, by elongation) -- a deep canyon is a cleft even if elongated. marginal if
    # near any threshold.
    near_cleft = (
        buriedness is not None and abs(buriedness - _CLEFT_BURIEDNESS) <= _CLEFT_MARGIN
    )
    near_groove = (
        elongation is not None and abs(elongation - _GROOVE_ELONGATION) <= _GROOVE_MARGIN
    )
    marginal = occ_margin <= _OCCLUSION_MARGIN or near_cleft or near_groove
    if buriedness is not None and buriedness >= _CLEFT_BURIEDNESS:
        name = CLEFT
    elif elongation is not None and elongation >= _GROOVE_ELONGATION:
        name = GROOVE
    else:
        name = OPEN_CONCAVITY
    return {'name': name, 'confidence': confidence, 'marginal': marginal}
