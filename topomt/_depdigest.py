# DepDigest configuration for TopoMT
from topomt._private.smonitor import LibraryNotFoundError

LIBRARIES = {
    'numpy': {'type': 'hard', 'pypi': 'numpy'},
    'scipy': {'type': 'hard', 'pypi': 'scipy'},
    'molsysmt': {'type': 'hard', 'pypi': 'molsysmt'},
    'numba': {'type': 'hard', 'pypi': 'numba'},
    'biotite': {'type': 'soft', 'pypi': 'biotite'},
    'mdtraj': {'type': 'soft', 'pypi': 'mdtraj'},
    'networkx': {'type': 'soft', 'pypi': 'networkx'},
    'skimage': {'type': 'soft', 'pypi': 'scikit-image'},
    'sklearn': {'type': 'soft', 'pypi': 'scikit-learn'},
}

MAPPING = {
    'biotite_structure': 'biotite',
    'mdtraj_load': 'mdtraj',
    'networkx_Graph': 'networkx',
    'skimage_measure': 'skimage',
    'sklearn_neighbors': 'sklearn',
}

SHOW_ALL_CAPABILITIES = True
EXCEPTION_CLASS = LibraryNotFoundError
