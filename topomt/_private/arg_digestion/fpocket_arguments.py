"""Value contracts for the original fpocket CLI and persisted-file boundaries."""

from numbers import Integral
from pathlib import Path
from string import hexdigits
from typing import Any

import numpy as np
from argdigest import register_pipeline
from argdigest.core.context import Context

from .external_arguments import (
    _error,
    _indices,
    digest_molecular_system,
    digest_selection,
    digest_skip_digestion,
    digest_structure_indices,
    digest_syntax,
)
from .provider_dispatch import ORIGINAL_BACKENDS

API_CALLER = 'topomt.third_party.fpocket.api.get_output'
FILES_CALLER = 'topomt.third_party.fpocket.files.load_topography'


def digest_backend(backend: Any, caller: str | None = None) -> str:
    if isinstance(backend, str) and backend.lower() in ORIGINAL_BACKENDS['fpocket']:
        return backend.lower()
    _error('backend', backend, caller, 'backend must be cli, wrapper or files.')


def digest_fpocket_cmd(fpocket_cmd: Any, caller: str | None = None) -> str:
    if isinstance(fpocket_cmd, str) and fpocket_cmd.strip() and '\0' not in fpocket_cmd:
        return fpocket_cmd
    _error(
        'fpocket_cmd',
        fpocket_cmd,
        caller,
        'Expected a nonempty executable name or path string.',
    )


def digest_extra_args(extra_args: Any, caller: str | None = None) -> list[str] | None:
    if extra_args is None:
        return None
    if isinstance(extra_args, (list, tuple)) and all(
        isinstance(i, str) and '\0' not in i for i in extra_args
    ):
        return list(extra_args)
    _error(
        'extra_args',
        extra_args,
        caller,
        'Expected None or a list/tuple of argument strings.',
    )


def digest_chemical_state(
    chemical_state: Any, caller: str | None = None
) -> str | int | None:
    if chemical_state is None and caller == FILES_CALLER:
        return None
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


def _path(value: Any, argument: str, caller: str | None) -> Path:
    if isinstance(value, (str, Path)) and str(value).strip() and '\0' not in str(value):
        return Path(value)
    _error(argument, value, caller, 'Expected a nonempty path string or pathlib.Path.')


def digest_pdb_file(pdb_file: Any, caller: str | None = None) -> Path:
    return _path(pdb_file, 'pdb_file', caller)


def digest_output_dir(output_dir: Any, caller: str | None = None) -> Path:
    return _path(output_dir, 'output_dir', caller)


def digest_provider_metadata(
    provider_metadata: Any, caller: str | None = None
) -> dict | None:
    managed = {
        'selection',
        'structure_indices',
        'syntax',
        'atom_serial_to_index',
        'submitted_atom_indices',
        'chemical_state_context',
    }
    if provider_metadata is None:
        return provider_metadata
    if isinstance(provider_metadata, dict) and not managed.intersection(
        provider_metadata
    ):
        return provider_metadata
    _error(
        'provider_metadata',
        provider_metadata,
        caller,
        'Expected None or metadata without adapter-owned source-context fields.',
    )


def digest_submitted_atom_indices(
    submitted_atom_indices: Any, caller: str | None = None
) -> list[int] | None:
    if submitted_atom_indices is None:
        return None
    indices = _indices(submitted_atom_indices, 'submitted_atom_indices', caller)
    array = np.asarray(indices)
    if (
        array.ndim != 1
        or array.dtype.kind not in 'iu'
        or len(np.unique(array)) != len(array)
    ):
        _error(
            'submitted_atom_indices',
            indices,
            caller,
            'Expected a unique one-dimensional submitted atom map.',
        )
    return array.tolist()


def digest_chemical_state_context(
    chemical_state_context: Any, caller: str | None = None
) -> dict | None:
    if chemical_state_context is None:
        return None
    value = chemical_state_context
    keys = {
        'index',
        'reference_index',
        'state_count',
        'state_id',
        'pdb_chemistry_sha256',
    }
    if isinstance(value, dict) and set(value) == keys:
        numbers = [value[k] for k in ('index', 'reference_index', 'state_count')]
        digest = value['pdb_chemistry_sha256']
        if (
            all(type(i) is int for i in numbers)
            and 0 <= numbers[0] == numbers[1] < numbers[2]
        ):
            if (
                isinstance(digest, str)
                and len(digest) == 64
                and all(c in hexdigits for c in digest)
            ):
                return value
    _error(
        'chemical_state_context',
        value,
        caller,
        'Invalid saved chemical-state context schema; source agreement is checked separately.',
    )


@register_pipeline(kind='fpocket', name='backend')
def digest_api_backend(value: Any, context: Context) -> str:
    return digest_backend(value, caller=API_CALLER)


@register_pipeline(kind='fpocket', name='gateway_backend')
def digest_gateway_backend(value: Any, context: Context) -> str:
    if isinstance(value, str) and value.lower() in {
        'cli',
        'wrapper',
        'native',
        'topomt',
    }:
        return value.lower()
    _error(
        'backend',
        value,
        context.function_name,
        'Expected cli, wrapper, native or topomt.',
    )


@register_pipeline(kind='fpocket', name='skip')
def digest_gateway_skip(value: Any, context: Context) -> bool:
    return digest_skip_digestion(value, caller=context.function_name)


GATEWAY_PIPELINES = {
    'backend': {'kind': 'fpocket', 'rules': ['gateway_backend']},
    'skip_digestion': {'kind': 'fpocket', 'rules': ['skip']},
}


ARGUMENT_DIGESTERS = {
    'backend': digest_backend,
    'molecular_system': digest_molecular_system,
    'selection': digest_selection,
    'structure_indices': digest_structure_indices,
    'syntax': digest_syntax,
    'fpocket_cmd': digest_fpocket_cmd,
    'extra_args': digest_extra_args,
    'chemical_state': digest_chemical_state,
    'pdb_file': digest_pdb_file,
    'output_dir': digest_output_dir,
    'provider_metadata': digest_provider_metadata,
    'submitted_atom_indices': digest_submitted_atom_indices,
    'chemical_state_context': digest_chemical_state_context,
    'skip_digestion': digest_skip_digestion,
}
OPTIONS = {
    'digestion_source': 'topomt._private.arg_digestion.fpocket_arguments',
    'digestion_style': 'registry',
    'standardizer': None,
    'function_source': 'topomt._private.arg_digestion.function.fpocket',
    'domain_source': 'topomt._private.arg_digestion.domain.fpocket',
}
