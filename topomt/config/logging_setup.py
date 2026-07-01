import logging
import warnings
from pathlib import Path
from typing import IO

_ORIGINAL_FORMATWARNING = warnings.formatwarning
_TOPOMT_ROOT = Path(__file__).resolve().parents[1]


def _parse_level(level: int | str) -> int:
    if isinstance(level, int):
        return level
    return logging._nameToLevel.get(str(level).upper(), logging.WARNING)


def setup_logging(
    level: int | str = "WARNING",
    *,
    stream: IO | None = None,
    capture_warnings: bool = True,
    simplify_warning_format: bool = True,
    logger_name: str = "topomt",
) -> logging.Logger:
    """
    Configure TopoMT logging and (optionally) capture Python warnings.

    Effects
    -------
    - Creates/gets logger `logger_name` (default: "topomt")
    - Attaches a StreamHandler if not present, with formatter:
          "TOPOMT %(levelname)s | %(message)s"
    - If capture_warnings is True:
        - logging.captureWarnings(True)
        - The "py.warnings" logger reuses the same handler/formatter
        - If simplify_warning_format is True:
            warnings.formatwarning(message, category, filename, lineno, line=None)
            -> "CategoryName: message\\n"
          (i.e., removes 'filename:lineno' prefix)
    """
    lvl = _parse_level(level)

    # Main package logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(lvl)
    logger.propagate = False

    # Ensure a single stream handler with the desired formatter
    stream_handler = None
    for h in logger.handlers:
        if isinstance(h, logging.StreamHandler):
            stream_handler = h
            break

    if stream_handler is None:
        stream_handler = logging.StreamHandler(stream)  # None -> sys.stderr
        # EXACT desired format for warnings:
        # "TOPOMT WARNING | <Category>: <message>"
        # (For normal logs, <Category> won't appear, but the prefix still matches.)
        formatter = logging.Formatter("TOPOMT %(levelname)s | %(message)s")
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # Capture Python warnings and route to logging via "py.warnings"
    if capture_warnings:
        # Simplify only warnings emitted from TopoMT itself. Python warning
        # formatting is process-global, so unrelated libraries keep the
        # formatter that was active before TopoMT setup.
        if simplify_warning_format:
            def _simple_formatwarning(message, category, filename, lineno, line=None):
                try:
                    origin = Path(filename).resolve()
                    is_topomt_warning = origin.is_relative_to(_TOPOMT_ROOT)
                except Exception:
                    is_topomt_warning = False
                if is_topomt_warning:
                    return f"{category.__name__}: {message}\n"
                return _ORIGINAL_FORMATWARNING(message, category, filename, lineno, line)
            warnings.formatwarning = _simple_formatwarning

        logging.captureWarnings(True)

        pyw = logging.getLogger("py.warnings")
        pyw.setLevel(lvl)
        pyw.handlers.clear()       # avoid duplicate handlers
        pyw.addHandler(stream_handler)
        pyw.propagate = False

    return logger
