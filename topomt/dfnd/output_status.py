"""Authoritative status of every DFND output.

Single source of truth for which DFND outputs are stable enough to **validate and
report**, and which are still consolidating. The human-readable counterpart lives
in ``devguide/DFND/metrics_contract.md``; the guard in
``tests/test_dfnd_output_status.py`` enforces that this registry stays in sync
with what the kernel actually emits, so:

- no experimental output is silently forgotten (every emitted output is
  classified here, with a promotion gate and a tracking reference);
- no new family/motif slips in unclassified;
- nothing marked ``experimental`` here is quietly reported as a result.

Status meanings
---------------
- ``canonical``    : stable; may be validated and reported as a DFND result.
- ``provisional``  : computed but with a precision/quality caveat; engineering
                     use only until its gate is met.
- ``experimental`` : shape may still change; carries ``flags=['experimental']``
                     in the raw records; do **not** validate or report until
                     promoted (see ``promotion_gate``).
- ``diagnostic``   : raw/internal classification, not promoted to a public
                     feature; inspected, not reported as a primary result.
- ``deferred``     : design still open; not yet a settled output.

Each entry carries the gate it must clear to become ``canonical`` and a
``blocker_ref`` pointing at the consolidation item / open question / known
limitation that tracks it.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import families as fam
from .classify import CLEFT, GROOVE, OPEN_CONCAVITY

VALID_STATUS = frozenset(
    {'canonical', 'provisional', 'experimental', 'diagnostic', 'deferred'}
)
# ``family`` = the topological classification the kernel records; ``classification``
# = a morphological refinement name emitted by the catalog (classify) on top of it.
VALID_KIND = frozenset(
    {'family', 'feature', 'motif', 'metric', 'classification'}
)


@dataclass(frozen=True)
class OutputStatus:
    status: str  # one of VALID_STATUS
    kind: str  # one of VALID_KIND
    promotion_gate: str | None  # what it needs to become canonical (None if canonical)
    blocker_ref: str | None  # consolidation item / open question / known-limitation id


OUTPUT_STATUS: dict[str, OutputStatus] = {
    # --- wet families (the families.py family strings) ---
    fam.POCKET: OutputStatus('canonical', 'family', None, None),
    fam.VOID: OutputStatus('canonical', 'family', None, None),
    fam.CHANNEL: OutputStatus('canonical', 'family', None, None),
    fam.PERCOLATING: OutputStatus('canonical', 'family', None, None),
    fam.SURFACE_CONCAVITY: OutputStatus(
        'diagnostic',
        'family',
        'stabilize the negation-defined catch-all or redefine it',
        'L3.1',
    ),
    fam.NONRESIDENT_PASSAGE: OutputStatus(
        'diagnostic',
        'family',
        'a deliberately pinched 3-D construction (no atom arrangement realizes '
        'it: thin enough to deny residence => thin transit faces, so R_gate '
        'tracks R_residence and the mouths fragment into voids)',
        'item-4 / L1.1',
    ),
    fam.DEGENERATE_SUBPROBE: OutputStatus(
        # Fixture gate met (item-4: toroidal_void @ probe 3.5, end-to-end test).
        # Stays diagnostic for an intrinsic reason: it is a probe-relative
        # artifact -- a cavity too tight for the chosen probe, which becomes a
        # void at a smaller probe -- so it is an internal signal ("shrink the
        # probe"), not a primary reportable feature.
        'diagnostic',
        'family',
        'intentionally diagnostic: probe-relative artifact, not a public feature',
        'item-4 / L1.1',
    ),
    # --- dry side ---
    fam.DRY_BANK: OutputStatus('canonical', 'family', None, None),
    # --- catalog morphological refinements (classify names on top of the family) ---
    # ``open_concavity`` is the open (occlusion<=1) refinement of a 1-mouth resident
    # family -- a GENERIC placeholder (aperture measured, shape not yet), refined
    # later into a leaf (groove/dish/funnel) when shape metrics land. The occluded
    # case keeps the name ``pocket``. Additive; not yet driving feature_type.
    OPEN_CONCAVITY: OutputStatus(
        'provisional',
        'classification',
        'quantitative shape metrics (elongation/axis) to refine into a leaf '
        '(groove/dish/funnel), plus real-system validation of the aperture split',
        'phase-3 / morphology / elongation debt',
    ),
    # ``groove`` = the elongated open-concavity leaf (morphometrics['elongation'] >=
    # threshold). The metric is grounded but the THRESHOLD is provisional -- synthetic
    # data does not separate groove from a round bowl cleanly (decision S12).
    GROOVE: OutputStatus(
        'provisional',
        'classification',
        'real-system validation of the elongation threshold (3-5 PDBs, S12)',
        'morphology / elongation debt',
    ),
    # ``cleft`` = a DEEP open canyon (morphometrics['buriedness'] >= threshold), the
    # active-site cleft. DFND sees the inter-lobe context only as depth; buriedness is a
    # RAW depth count, so the THRESHOLD is system-dependent and provisional (S12).
    CLEFT: OutputStatus(
        'provisional',
        'classification',
        'real-system validation of the buriedness threshold; a normalised depth (S12)',
        'morphology / depth',
    ),
    # --- promoted public features ---
    'Mouth': OutputStatus('canonical', 'feature', None, None),
    # Q17 (atom/residue ownership) is decided: overlapping role-based membership,
    # see interfaces.md §9. Now pending real-system validation before canonical.
    'interface': OutputStatus(
        'experimental',
        'feature',
        'real-system validation of multi-body-lining detection',
        'validation',
    ),
    # --- motifs (the four emitted motif_type strings) ---
    'depth_region': OutputStatus('canonical', 'motif', None, None),
    'external_mouth': OutputStatus('canonical', 'motif', None, None),
    # Promoted to provisional: the merge-tree scoring/persistence policy is fixed
    # and validated on the four-toy hierarchy panel + probe-sweep / persistence
    # stability (tests/test_dfnd_hierarchy.py). Real-system validation remains for
    # canonical. Emitted with flags=['provisional'].
    'throat_candidate': OutputStatus(
        'provisional',
        'motif',
        'real-system validation of the chamber/throat scoring policy',
        'Q25',
    ),
    'chamber_candidate': OutputStatus(
        'provisional',
        'motif',
        'as throat_candidate',
        'Q25',
    ),
    # the access-funnel motif (morphometrics['funnel'].is_funnel): a steady, appreciable
    # narrowing of the clearance with depth -- a directing truncated cone, distinct from
    # a tube. The metric is grounded; the gradient/steadiness THRESHOLDS are provisional.
    'funnel': OutputStatus(
        'provisional',
        'motif',
        'real-system validation of the gradient/steadiness thresholds (S12)',
        'morphology / access funnel',
    ),
    # --- derived descriptor (component.bottleneck = top throat_candidate) ---
    'bottleneck': OutputStatus(
        'provisional',
        'metric',
        'inherits throat_candidate promotion',
        'Q25',
    ),
    # --- metrics (raw-record fields; documentation-level, not runtime-guarded) ---
    'volume_topological_resident': OutputStatus('canonical', 'metric', None, None),
    # Precise on-demand solvent volume (seeded Monte Carlo, DFNDData.solvent_volume).
    'volume_solvent_resident': OutputStatus('canonical', 'metric', None, None),
    'volume_solvent_transit': OutputStatus('canonical', 'metric', None, None),
    # Fast bulk estimate kept for provenance/speed; the precise metric above now
    # exists, so this stays a provisional engineering-grade field.
    'volume_solvent_estimate': OutputStatus(
        'provisional',
        'metric',
        'superseded for precision by volume_solvent_resident/transit; kept as a '
        'fast bulk estimate',
        'item-2 / L5.1',
    ),
    'center': OutputStatus('canonical', 'metric', None, None),
    'mouth_area': OutputStatus('canonical', 'metric', None, None),
    'R_gate_min': OutputStatus('canonical', 'metric', None, None),
    'R_gate_mean': OutputStatus('canonical', 'metric', None, None),
    'R_gate_max': OutputStatus('canonical', 'metric', None, None),
    'n_mouths': OutputStatus('canonical', 'metric', None, None),
    'face_depth': OutputStatus('canonical', 'metric', None, None),
}


def names_by_kind(kind: str) -> set[str]:
    """All registered output names of a given ``kind``."""
    return {name for name, s in OUTPUT_STATUS.items() if s.kind == kind}


def names_by_status(status: str) -> set[str]:
    """All registered output names of a given ``status``."""
    return {name for name, s in OUTPUT_STATUS.items() if s.status == status}


def catalog_classification_names() -> set[str]:
    """Every name the catalog classifier may emit -- topological families plus
    morphological refinements. The guard checks that ``classify`` is total: nothing
    a component is classified as may be left unregistered."""
    return names_by_kind('family') | names_by_kind('classification')


def experimental_motif_types() -> set[str]:
    """Motif types that must be emitted with ``flags=['experimental']``."""
    return {
        name
        for name, s in OUTPUT_STATUS.items()
        if s.kind == 'motif' and s.status == 'experimental'
    }
