"""
TopoMT
Short description
"""

# versioningit
from ._version import __version__

def __print_version__():
    print("TopoMT version " + __version__)

from ._pyunitwizard import pyunitwizard

from . import config
config.setup_logging(level="WARNING", capture_warnings=True, simplify_warning_format=True)

from smonitor.integrations import ensure_configured
from ._private.smonitor import PACKAGE_ROOT

ensure_configured(PACKAGE_ROOT)

from .demo import demo

from . import features
from .topography.Topography import Topography
from .delaunay_mesh import DelaunayMesh
from .weighted_delaunay_mesh import WeightedDelaunayMesh
from .get_delaunay_mesh import get_delaunay_mesh
from .get_topography import get_topography
from .get_pockets import get_pockets, show_pockets

from . import io

from . import third_party
from . import dfnd
from . import tools

__all__ = ['Topography', 'DelaunayMesh', 'WeightedDelaunayMesh', 'get_delaunay_mesh']
