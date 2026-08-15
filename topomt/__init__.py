# ruff: noqa: E402,I001
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

from . import io

from . import third_party
from . import dfnd
from . import tools

__all__ = [
    '__version__',
    '__print_version__',
    'pyunitwizard',
    'config',
    'demo',
    'features',
    'Topography',
    'DelaunayMesh',
    'WeightedDelaunayMesh',
    'get_delaunay_mesh',
    'get_topography',
    'io',
    'third_party',
    'dfnd',
    'tools',
]


# The unit policy is declared when this package is imported, not on first use.
# Reaching it lazily meant `puw.configure.report()` described an empty session
# until something happened to touch it, and a user calling PyUnitWizard
# directly after importing this package got NoStandardsError. The cost is paid
# once per process -- a second suite library costs about 2 ms -- and it is a
# cost the session pays anyway at its first unit operation.
from . import _pyunitwizard  # noqa: E402,F401
