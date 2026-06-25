from .BaseFeature import BaseFeature
from .Feature0D import Feature0D
from .Feature1D import Feature1D
from .Feature2D import Feature2D
from .Void import Void
from .Pocket import Pocket
from .OpenConcavity import OpenConcavity
from .Groove import Groove
from .Cleft import Cleft
from .Channel import Channel
from .BranchedChannel import BranchedChannel
from .Mouth import Mouth
from .Percolating import Percolating

from ._feature_constants import _FEATURE_PREFIXES, _FEATURE_TYPE_ALIASES, _FEATURE_TYPE_TO_CLASS_NAME, \
        _FEATURE_TYPES_BY_SHAPE_TYPE, _SHAPE_TYPE_BY_FEATURE_TYPE, _DIMENSIONALITY_BY_FEATURE_TYPE

_FEATURE_TYPE_REGISTRY = {
    'base_feature': BaseFeature,
    'feature_0d': Feature0D,
    'feature_1d': Feature1D,
    'feature_2d': Feature2D,
    'pocket': Pocket,
    'open_concavity': OpenConcavity,
    'groove': Groove,
    'cleft': Cleft,
    'void': Void,
    'mouth': Mouth,
    'channel': Channel,
    'branched_channel': BranchedChannel,
    'percolating': Percolating,
}

