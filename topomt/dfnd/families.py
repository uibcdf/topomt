"""Canonical DFND component family names — single source of truth.

The raw classifier (``graph._classify_component``) emits these strings; every
consumer (``components.SIDE_BY_FAMILY``, ``interfaces``, the viewer palette and
filters) imports the names from here instead of re-typing string literals, so
renaming a family is a one-line change. This module deliberately depends on
nothing else in the package (no import cycles).

Wet families are organised by the cross-product (number of mouths to OCEAN) x
(residence). See ``devguide/DFND/Overview.md``. Historical note: the ``channel``
family was named ``multi_external_link`` until 2026-06.
"""

from __future__ import annotations

#                              mouths | residence
VOID = 'void'                        # 0      | resident
DEGENERATE_SUBPROBE = 'degenerate_subprobe'  # 0      | non-resident
POCKET = 'pocket'                    # 1      | resident
SURFACE_CONCAVITY = 'surface_concavity'      # 1      | non-resident
CHANNEL = 'channel'                  # >=2    | resident
NONRESIDENT_PASSAGE = 'nonresident_passage'  # >=2    | non-resident
PERCOLATING = 'percolating'          # spans the whole system
DRY_BANK = 'dry_bank'                # the dry-network side

# side is derived from family (mirrors how a feature's shape is derived from its
# feature_type in features/_feature_constants.py).
SIDE_BY_FAMILY = {
    VOID: 'wet',
    POCKET: 'wet',
    CHANNEL: 'wet',
    SURFACE_CONCAVITY: 'wet',
    NONRESIDENT_PASSAGE: 'wet',
    DEGENERATE_SUBPROBE: 'wet',
    PERCOLATING: 'wet',
    DRY_BANK: 'dry',
}

WET_FAMILIES = tuple(f for f, side in SIDE_BY_FAMILY.items() if side == 'wet')
DRY_FAMILIES = tuple(f for f, side in SIDE_BY_FAMILY.items() if side == 'dry')

# the resident families surfaced by default in the viewer / public catalog (the
# "main" concavity families; the non-resident and percolating ones are secondary).
PRIMARY_WET_FAMILIES = (POCKET, VOID, CHANNEL)
