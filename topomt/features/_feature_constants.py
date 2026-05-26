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
    "concavity": ["void", "pocket", "channel", "branched_channel", "groove", "funnel", "vestibule", "ampulla",
                  "alcove"],
    "convexity": ["protrusion", "dome", "ridge", "spine", "bulge", "ridge_cap", "knob", "buttress", "pinnacle"],
    "mixed": ["feature2d", "interface", "patch", "joint", "saddle", "trench"],
    # neutral: neither concave, convex nor mixed -- a fully permeable/exposed region.
    # Added for completeness; rarely encountered when analysing real proteins.
    "neutral": ["percolating"],
}

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

