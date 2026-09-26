"""
Optional import utilities for this library.

This module lets us use optional dependencies (like `argdigest` or `flowcite`)
without breaking the package if they are not installed.

Typical usage:
    digest, register_pipeline = optional_import(
        "argdigest", ["digest", "register_pipeline"]
    )

    scoped_usage, track_item = optional_import(
        "flowcite",
        ["scoped_usage", "track_item"],
        fallback={
            "scoped_usage": lambda target=None: (lambda fn: fn),
            "track_item": lambda *args, **kwargs: None,
        },
    )
"""

from __future__ import annotations

import importlib
import warnings
from types import ModuleType
from typing import Any


def optional_import(
    module_name: str,
    names: list[str] | None = None,
    *,
    fallback: dict[str, Any] | None = None,
    warn: bool = False,
) -> list[Any] | ModuleType | None:
    """
    Try to import a module or specific names from it. If the import fails,
    return no-op fallbacks so the rest of the library continues to work.

    Parameters
    ----------
    module_name : str
        Name of the module to import (e.g. "argdigest", "flowcite").
    names : list[str] or None
        If provided, import these attributes from the module and return them
        in a list (same order). If None, return the module itself.
    fallback : dict[str, Any], optional
        Mapping from attribute name to fallback object/function, used when
        the import fails. If not provided, a generic no-op function is used.
    warn : bool, default False
        If True, emit a warning when the import fails.

    Returns
    -------
    list[Any] or ModuleType or None
        The imported objects, or fallbacks, or None if the module was requested
        and not found.
    """
    try:
        module = importlib.import_module(module_name)
        if names is None:
            return module
        return [getattr(module, name) for name in names]

    except ImportError:
        if warn:
            warnings.warn(
                f"Optional dependency '{module_name}' is not installed. "
                'Using safe fallbacks.'
            )

        # If no specific names requested, just return None
        if names is None:
            return None

        results: list[Any] = []
        for name in names:
            if fallback and name in fallback:
                results.append(fallback[name])
            else:
                # default no-op
                def _noop(*args, **kwargs):
                    return None

                results.append(_noop)
        return results
