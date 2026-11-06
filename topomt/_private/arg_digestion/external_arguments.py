"""Reusable argument admission for original molecular-provider boundaries."""

from numbers import Integral
from pathlib import Path
from typing import Any, NoReturn

import numpy as np

from .provider_dispatch import ProviderDispatchArgumentError


def _error(argument: str, value: Any, caller: str | None, reason: str) -> NoReturn:
    raise ProviderDispatchArgumentError(
        arg_name=argument, value=value, caller=caller, reason=reason
    )


def digest_path(value: Any, argument: str, caller: str | None) -> Path:
    """Admit an explicit file/directory path without touching the filesystem."""
    if isinstance(value, (str, Path)) and str(value).strip() and '\0' not in str(value):
        return Path(value)
    _error(argument, value, caller, 'Expected a nonempty path string or pathlib.Path.')


def digest_upstream_root(upstream_root: Any, caller: str | None = None) -> str | None:
    """Admit an optional original-engine source-import root."""
    if upstream_root is None:
        return None
    return str(
        digest_path(upstream_root, 'upstream_root', caller).expanduser().resolve()
    )


def digest_molecular_system(
    molecular_system: Any, backend: str | None = None, caller: str | None = None
) -> Any:
    # Molecular-form support, source inventory and identity belong to MolSysMT.
    if molecular_system is None:
        _error(
            'molecular_system',
            molecular_system,
            caller,
            'A molecular source is required.',
        )
    return molecular_system


def digest_chemical_state(chemical_state: Any, caller: str | None = None) -> str | int:
    """Admit a reference-state selector; source agreement is adapter-owned."""
    if isinstance(chemical_state, str) and chemical_state == 'reference':
        return chemical_state
    if (
        isinstance(chemical_state, Integral)
        and not isinstance(chemical_state, bool)
        and int(chemical_state) >= 0
    ):
        return int(chemical_state)
    _error(
        'chemical_state',
        chemical_state,
        caller,
        'Expected reference or a nonnegative integer chemical_state index.',
    )


def _indices(
    value: Any, argument: str, caller: str | None, single: bool = False
) -> Any:
    if isinstance(value, Integral) and not isinstance(value, bool) and int(value) >= 0:
        return value
    if isinstance(value, (list, tuple, range, np.ndarray)):
        try:
            array = np.asarray(value)
        except (TypeError, ValueError):
            _error(argument, value, caller, 'Expected a flat integer index axis.')
        if array.ndim == 1 and array.size and (not single or array.size == 1):
            if all(
                isinstance(i, Integral) and not isinstance(i, bool) and int(i) >= 0
                for i in value
            ):
                return value
    reason = (
        'Expected a nonempty one-dimensional sequence of nonnegative integer indices.'
    )
    if single:
        reason = 'Expected exactly one input coordinate frame: a single nonnegative integer index.'
    _error(argument, value, caller, reason)


def _selection(value: Any, argument: str, caller: str | None) -> Any:
    if isinstance(value, str) and value.strip():
        return value
    return _indices(value, argument, caller)


def digest_selection(selection: Any, caller: str | None = None) -> Any:
    return _selection(selection, 'selection', caller)


def _structure_indices(value: Any, argument: str, caller: str | None) -> Any:
    # These legacy selectors require source-dependent frame-count admission later.
    if value is None or isinstance(value, str) and value.lower() == 'all':
        return value
    return _indices(value, argument, caller, single=True)


def digest_structure_indices(structure_indices: Any, caller: str | None = None) -> Any:
    return _structure_indices(structure_indices, 'structure_indices', caller)


def _syntax(value: Any, argument: str, caller: str | None) -> str:
    from topomt._private.exceptions import ArgumentError

    from .argument.syntax import digest_syntax as owning_digest

    try:
        return owning_digest(value, caller=caller)
    except ArgumentError:
        _error(
            argument, value, caller, 'Expected a supported MolSysMT selection syntax.'
        )


def digest_syntax(syntax: Any, caller: str | None = None) -> str:
    return _syntax(syntax, 'syntax', caller)


def digest_skip_digestion(skip_digestion: Any, caller: str | None = None) -> bool:
    if type(skip_digestion) is bool:
        return skip_digestion
    _error('skip_digestion', skip_digestion, caller, 'Expected a literal boolean.')
