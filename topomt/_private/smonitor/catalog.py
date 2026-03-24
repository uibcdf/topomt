# SMonitor signal catalog for TopoMT

CATALOG = {
    "signals": {
        "topomt.get_topography": {
            "tags": ["api", "topography"],
            "extra_required": ["method"],
        },
        "topomt.pocketeer": {
            "tags": ["method", "pocketeer"],
        },
        "topomt.fpocket": {
            "tags": ["wrapper", "fpocket"],
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
    },
}

CODES = {
    "SIGNALS": CATALOG["signals"],
    "ERRORS": CATALOG["errors"],
    "WARNINGS": CATALOG["warnings"],
}
