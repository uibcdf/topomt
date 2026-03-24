# DepDigest configuration for TopoMT
from topomt._private.smonitor import LibraryNotFoundError

LIBRARIES = {
    'numpy': {'type': 'hard', 'pypi': 'numpy'},
    'scipy': {'type': 'hard', 'pypi': 'scipy'},
    'molsysmt': {'type': 'hard', 'pypi': 'molsysmt'},
    'pyunitwizard': {'type': 'hard', 'pypi': 'pyunitwizard'},
    'nglview': {'type': 'soft', 'pypi': 'nglview'},
    'py3Dmol': {'type': 'soft', 'pypi': 'py3Dmol'},
    'skimage': {'type': 'soft', 'pypi': 'scikit-image'},
    'argdigest': {'type': 'soft', 'pypi': 'argdigest'},
    'smonitor': {'type': 'soft', 'pypi': 'smonitor'},
}

MAPPING = {
    'nglview_NGLWidget': 'nglview',
    'py3Dmol_view': 'py3Dmol',
    'skimage_measure': 'skimage',
}

SHOW_ALL_CAPABILITIES = True
EXCEPTION_CLASS = LibraryNotFoundError
