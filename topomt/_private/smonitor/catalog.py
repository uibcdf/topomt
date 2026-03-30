from pathlib import Path

from .meta import META

PACKAGE_ROOT = Path(__file__).resolve().parents[2]

CATALOG = {
    "signals": {
        "topomt.get_topography": {
            "tags": ["api", "topography"],
            "extra_required": ["method"],
        },
        "topomt.alphaspace2": {
            "tags": ["method", "alphaspace2", "native"],
        },
        "topomt.castp": {
            "tags": ["method", "castp", "native"],
        },
        "topomt.fpocket4": {
            "tags": ["method", "fpocket4", "native"],
        },
        "topomt.pocketeer": {
            "tags": ["method", "pocketeer", "native"],
        },
        "topomt.pycasta": {
            "tags": ["method", "pycasta", "native"],
        },
    },
    "errors": {
        "LibraryNotFoundError": {
            "template": "Required library '{library}' is not installed. Please install it using '{hint}'.",
            "category": "dependency",
        },
        "ArgumentError": {
            "template": "Invalid argument '{arg_name}': {reason}",
            "category": "validation",
        },
    },
    "warnings": {
        "ExperimentalMethodWarning": {
            "template": "The method '{method}' is experimental and its API may change in future versions.",
            "category": "api",
        },
        "NotDigestedArgumentWarning": {
            "template": "The argument '{argument}' in '{caller}' was not digested.",
            "category": "validation",
        },
        "PocketeerDelaunayWarning": {
            "template": "Pocketeer Delaunay tessellation failed: {reason}",
            "category": "algorithm",
        },
        "PocketeerSasaBackendWarning": {
            "template": "Pocketeer SASA backend could not run ({reason}); mean_sasa is set to 0.0 for all spheres.",
            "category": "dependency",
        },
    },
}

CODES = {
    "SIGNALS": CATALOG["signals"],
    "ERRORS": CATALOG["errors"],
    "WARNINGS": CATALOG["warnings"],
}

SIGNALS = CATALOG["signals"]
