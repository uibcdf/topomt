# TopoMT/_smonitor.py
from topomt._private.smonitor.catalog import CODES

PROFILE = "user"

SMONITOR = {
    "level": "WARNING",
    "trace_depth": 3,
    "capture_warnings": True,
    "capture_logging": True,
    "theme": "plain",
    "silence": ["pint", "networkx"],
}

SIGNALS = CODES["SIGNALS"]
ERRORS = CODES["ERRORS"]
WARNINGS = CODES["WARNINGS"]
