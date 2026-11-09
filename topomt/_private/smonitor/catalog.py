from pathlib import Path

from .meta import META as META

PACKAGE_ROOT = Path(__file__).resolve().parents[2]

CATALOG = {
    'signals': {
        'topomt.get_topography': {
            'tags': ['api', 'topography'],
            'extra_required': ['method'],
        },
        'topomt.alphaspace2': {
            'tags': ['method', 'alphaspace2', 'native'],
        },
        'topomt.castp': {
            'tags': ['method', 'castp', 'native'],
        },
        'topomt.fpocket4': {
            'tags': ['method', 'fpocket4', 'native'],
        },
        'topomt.pocketeer': {
            'tags': ['method', 'pocketeer', 'native'],
        },
        'topomt.pycasta': {
            'tags': ['method', 'pycasta', 'native'],
        },
    },
    'exceptions': {
        'ProviderUnavailableError': {
            'code': 'ProviderUnavailableError',
            'user_message': "Original provider '{provider}' requires '{requirement}'.",
            'user_hint': 'Install the selected original tool or use its saved files route; consult the third-party engine guide.',
            'category': 'dependency',
        },
        'ProviderExecutionError': {
            'code': 'ProviderExecutionError',
            'user_message': "Original provider '{provider}' failed: {reason}",
            'category': 'execution',
        },
        'LibraryNotFoundError': {
            'code': 'LibraryNotFoundError',
            'user_message': "Required library '{library}' is not installed.",
            'user_hint': 'Install it in the active environment with: pip install {library}',
            'category': 'dependency',
        },
        'ExecutableNotFoundError': {
            'code': 'ExecutableNotFoundError',
            'user_message': "Required fpocket executable '{executable}' was not found.",
            'user_hint': 'Install it with: conda install -c conda-forge fpocket; or set fpocket_cmd to the executable path.',
            'category': 'dependency',
        },
        'ArgumentError': {
            'code': 'ArgumentError',
            'user_message': "Invalid argument '{arg_name}': {reason}",
            'category': 'validation',
        },
    },
    'warnings': {
        'AttributionTrackingWarning': {
            'code': 'AttributionTrackingWarning',
            'user_message': 'Optional scientific attribution failed during {operation}: {reason}',
            'user_hint': 'The scientific result retains host bibliography. Inspect its attribution status and the Ackredit installation.',
            'category': 'attribution',
        },
        'ExperimentalMethodWarning': {
            'code': 'ExperimentalMethodWarning',
            'user_message': "The method '{method}' is experimental and its API may change in future versions.",
            'category': 'api',
        },
        'NotDigestedArgumentWarning': {
            'code': 'NotDigestedArgumentWarning',
            'user_message': "The argument '{argument}' in '{caller}' was not digested.",
            'category': 'validation',
        },
        'PocketeerDelaunayWarning': {
            'code': 'PocketeerDelaunayWarning',
            'user_message': 'Pocketeer Delaunay tessellation failed: {reason}',
            'category': 'algorithm',
        },
        'PocketeerSasaBackendWarning': {
            'code': 'PocketeerSasaBackendWarning',
            'user_message': 'Pocketeer SASA backend could not run ({reason}); mean_sasa is set to 0.0 for all spheres.',
            'category': 'dependency',
        },
    },
}

CODES = {
    entry['code']: entry
    for group in ('exceptions', 'warnings')
    for entry in CATALOG[group].values()
}

SIGNALS = CATALOG['signals']
