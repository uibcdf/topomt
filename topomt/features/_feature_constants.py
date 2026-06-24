_FEATURE_PREFIXES = {
    'base_feature': 'BSF',
    'feature_0d': 'F0D',
    'feature_1d': 'F1D',
    'feature_2d': 'F2D',
    'pocket': 'POC',
    'void': 'VOI',
    'mouth': 'MOU',
    'channel': 'CHA',
    'branched_channel': 'BCH',
    'percolating': 'PRC',
}

_FEATURE_TYPE_ALIASES = {
    'BaseFeature': 'base_feature',
    'Feature0D': 'feature_0d',
    'Feature1D': 'feature_1d',
    'Feature2D': 'feature_2d',
    'Pocket': 'pocket',
    'Void': 'void',
    'Mouth': 'mouth',
    'Channel': 'channel',
    'BranchedChannel': 'branched_channel',
    'Percolating': 'percolating',
}

_FEATURE_TYPE_TO_CLASS_NAME = {
    'base_feature': 'BaseFeature',
    'feature_0d': 'Feature0D',
    'feature_1d': 'Feature1D',
    'feature_2d': 'Feature2D',
    'pocket': 'Pocket',
    'void': 'Void',
    'mouth': 'Mouth',
    'channel': 'Channel',
    'branched_channel': 'BranchedChannel',
    'percolating': 'Percolating',
}

_FEATURE_TYPES_BY_SHAPE_TYPE = {
    "point": ["feature0d", "point", "pit", "apex", "summit", "bifurcation", "saddle_point", "ridge_tip"],
    "boundary": ["feature1d", "mouth", "base_rim", "neck", "ridge", "furrow", "lip", "seam", "isthmus", "edge_loop",
                 "branch_line", "hinge_line"],
    # Only DFND component-level families. A concavity feature *type* is what the
    # DFND decomposition produces (one component = one of these). Morphological
    # refinements (groove ...) and sub-chamber roles (alcove ...) are NOT component
    # types and were removed from here -- see _PENDING_* below and
    # devguide/DFND/feature_definitions.md S5.2.1.
    "concavity": ["void", "pocket", "channel", "branched_channel"],
    "convexity": ["protrusion", "dome", "ridge", "spine", "bulge", "ridge_cap", "knob", "buttress", "pinnacle"],
    "mixed": ["feature2d", "interface", "patch", "joint", "saddle", "trench"],
    # neutral: neither concave, convex nor mixed -- a fully permeable/exposed region.
    # Added for completeness; rarely encountered when analysing real proteins.
    "neutral": ["percolating"],
}

# Vocabulary relocated out of the feature-TYPE table above: these are not
# component types, so they cannot label a whole component. They are kept here as a
# recoverable backlog, to be grounded only once their layer exists and is
# validated (the morphology label layer needs an elongation metric DFND does not
# yet compute; the chamber-role layer rides on the merge-tree hierarchy, still
# provisional). See devguide/DFND/feature_definitions.md S5.2.1.
#
# Morphological *labels* on a concavity feature (refine a type, e.g. "a pocket
# that is an open groove"); the robust grounded axis today is open<->occluded
# (morphometrics['occlusion']) and shallow<->deep (buriedness), not these names.
_PENDING_MORPHOLOGY_LABELS = ["groove", "funnel"]
# Sub-chamber *roles* inside one component (motifs on chamber_candidates): an
# antechamber, a flask bulb, a side recess. Relational, not standalone types.
_PENDING_CHAMBER_MOTIF_ROLES = ["vestibule", "ampulla", "alcove"]

_SHAPE_TYPE_BY_FEATURE_TYPE = {}
_DIMENSIONALITY_BY_FEATURE_TYPE = {}
for shape_type, feature_types in _FEATURE_TYPES_BY_SHAPE_TYPE.items():
    for feature_type in feature_types:
        _SHAPE_TYPE_BY_FEATURE_TYPE[feature_type] = shape_type
        if shape_type in ["point"]:
            _DIMENSIONALITY_BY_FEATURE_TYPE[feature_type] = 0
        elif shape_type in ["boundary"]:
            _DIMENSIONALITY_BY_FEATURE_TYPE[feature_type] = 1
        elif shape_type in ["concavity", "convexity", "mixed", "neutral"]:
            _DIMENSIONALITY_BY_FEATURE_TYPE[feature_type] = 2

