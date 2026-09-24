from ._feature_constants import (
    _DIMENSIONALITY_BY_FEATURE_TYPE as _DIMENSIONALITY_BY_FEATURE_TYPE,
)
from ._feature_constants import (
    _FEATURE_PREFIXES as _FEATURE_PREFIXES,
)
from ._feature_constants import (
    _FEATURE_TYPE_ALIASES as _FEATURE_TYPE_ALIASES,
)
from ._feature_constants import (
    _FEATURE_TYPE_TO_CLASS_NAME as _FEATURE_TYPE_TO_CLASS_NAME,
)
from ._feature_constants import (
    _FEATURE_TYPES_BY_SHAPE_TYPE as _FEATURE_TYPES_BY_SHAPE_TYPE,
)
from ._feature_constants import (
    _SHAPE_TYPE_BY_FEATURE_TYPE as _SHAPE_TYPE_BY_FEATURE_TYPE,
)
from .BaseFeature import BaseFeature
from .BranchedChannel import BranchedChannel
from .Channel import Channel
from .Cleft import Cleft
from .Feature0D import Feature0D
from .Feature1D import Feature1D
from .Feature2D import Feature2D
from .Groove import Groove
from .Mouth import Mouth
from .OpenConcavity import OpenConcavity
from .Percolating import Percolating
from .Pocket import Pocket
from .Void import Void

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
