# DepDigest configuration for TopoMT
from topomt._private.smonitor import LibraryNotFoundError

LIBRARIES: dict[str, dict[str, str | None]] = {
    'ackredit': {
        'type': 'soft',
        'pypi': None,
        'conda': 'ackredit',
        'channel': 'uibcdf',
    },
    'numpy': {'type': 'hard', 'pypi': 'numpy'},
    'scipy': {'type': 'hard', 'pypi': 'scipy'},
    'molsysmt': {'type': 'hard', 'pypi': 'molsysmt'},
    'numba': {'type': 'hard', 'pypi': 'numba'},
    'biotite': {'type': 'soft', 'pypi': 'biotite'},
    'pocketeer': {'type': 'soft', 'pypi': 'pocketeer', 'conda': None},
    'alphaspace2': {'type': 'soft', 'pypi': 'alphaspace2', 'conda': None},
    'pycasta': {'type': 'soft', 'pypi': 'pycasta', 'conda': None},
    'pyKVFinder': {'type': 'soft', 'pypi': 'pyKVFinder', 'conda': None},
    'povme': {'type': 'soft', 'pypi': None, 'conda': None},
    'hole': {
        'type': 'soft',
        'kind': 'executable',
        'executable': 'hole',
        'pypi': None,
        'conda': None,
    },
    'pisa': {
        'type': 'soft',
        'kind': 'executable',
        'executable': 'pisa',
        'pypi': None,
        'conda': None,
    },
    'povme_python': {
        'type': 'soft',
        'kind': 'executable',
        'executable': 'python',
        'pypi': None,
        'conda': None,
    },
    'molovol': {
        'type': 'soft',
        'kind': 'executable',
        'executable': 'molovol',
        'pypi': None,
        'conda': None,
    },
    'xvfb': {
        'type': 'soft',
        'kind': 'executable',
        'executable': 'Xvfb',
        'pypi': None,
        'conda': 'xorg-xvfb-server',
        'channel': 'conda-forge',
    },
    'mole': {
        'type': 'soft',
        'kind': 'executable',
        'executable': 'mole2',
        'pypi': None,
        'conda': None,
    },
    'ghecom': {
        'type': 'soft',
        'kind': 'executable',
        'executable': 'ghecom',
        'pypi': None,
        'conda': None,
    },
    'java': {
        'type': 'soft',
        'kind': 'executable',
        'executable': 'java',
        'pypi': None,
        'conda': 'openjdk',
        'channel': 'conda-forge',
    },
    'pykvfinder_python': {
        'type': 'soft',
        'kind': 'executable',
        'executable': 'python',
        'pypi': None,
        'conda': None,
    },
    'mdtraj': {'type': 'soft', 'pypi': 'mdtraj'},
    'fpocket': {
        'type': 'soft',
        'kind': 'executable',
        'executable': 'fpocket',
        'pypi': None,
        'conda': 'fpocket',
        'channel': 'conda-forge',
    },
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
DOC_URL = 'https://uibcdf.org/topomt/content/user/third_party_engines.html'
