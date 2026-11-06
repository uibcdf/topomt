"""Original AlphaSpace2 adapter argument contracts, independent of its engine."""

from numbers import Integral
from pathlib import Path
from typing import Any

from argdigest import register_pipeline
from argdigest.core.context import Context

from .external_arguments import (
    _chemical_state,
    _error,
    _selection,
    _structure_indices,
    _syntax,
    digest_chemical_state,
    digest_molecular_system,
    digest_path,
    digest_selection,
    digest_skip_digestion,
    digest_structure_indices,
    digest_syntax,
    digest_upstream_root,
)

API_CALLER = 'topomt.third_party.alphaspace2.api.get_output'
FILES_CALLER = 'topomt.third_party.alphaspace2.files.load_output'


def digest_bundle_file(bundle_file: Any, caller: str | None = None) -> Path:
    return digest_path(bundle_file, 'bundle_file', caller)


def digest_binder(binder: Any, caller: str | None = None) -> Any:
    # None is an unbound snapshot; support of other molecular forms belongs to
    # MolSysMT at conversion, without changing or preparing the caller's input.
    return binder


def digest_binder_chemical_state(
    binder_chemical_state: Any, caller: str | None = None
) -> str | int:
    return _chemical_state(binder_chemical_state, 'binder_chemical_state', caller)


@register_pipeline(kind='alphaspace2', name='binder_state')
def check_binder_state(value: Any, context: Context) -> Any:
    if context.all_args.get('binder') is None and value != 'reference':
        _error(
            'binder_chemical_state',
            value,
            context.function_name,
            'An explicit binder state index requires a binder.',
        )
    return value


def digest_binder_selection(binder_selection: Any, caller: str | None = None) -> Any:
    return _selection(binder_selection, 'binder_selection', caller)


def digest_binder_structure_indices(
    binder_structure_indices: Any, caller: str | None = None
) -> Any:
    return _structure_indices(
        binder_structure_indices, 'binder_structure_indices', caller
    )


def digest_binder_syntax(binder_syntax: Any, caller: str | None = None) -> str:
    return _syntax(binder_syntax, 'binder_syntax', caller)


def digest_min_vertices(min_vertices: Any, caller: str | None = None) -> int:
    if (
        isinstance(min_vertices, Integral)
        and not isinstance(min_vertices, bool)
        and int(min_vertices) > 0
    ):
        return int(min_vertices)
    _error('min_vertices', min_vertices, caller, 'Expected a positive integer.')


@register_pipeline(kind='alphaspace2', name='original_backend')
def digest_original_backend(value: Any, context: Context) -> str:
    if isinstance(value, str) and value.lower() in {'library', 'wrapper', 'files'}:
        return value.lower()
    _error(
        'backend',
        value,
        API_CALLER,
        'Expected library, wrapper or files for original output.',
    )


@register_pipeline(kind='alphaspace2', name='gateway_backend')
def digest_gateway_backend(value: Any, context: Context) -> str:
    if isinstance(value, str) and value.lower() in {'native', 'library', 'wrapper'}:
        return value.lower()
    _error(
        'backend', value, context.function_name, 'Expected native, library or wrapper.'
    )


@register_pipeline(kind='alphaspace2', name='skip')
def digest_skip(value: Any, context: Context) -> bool:
    return digest_skip_digestion(value, caller=context.function_name)


ARGUMENT_DIGESTERS = {
    'molecular_system': digest_molecular_system,
    'bundle_file': digest_bundle_file,
    'chemical_state': digest_chemical_state,
    'selection': digest_selection,
    'structure_indices': digest_structure_indices,
    'syntax': digest_syntax,
    'upstream_root': digest_upstream_root,
    'min_vertices': digest_min_vertices,
    'binder': digest_binder,
    'binder_chemical_state': digest_binder_chemical_state,
    'binder_selection': digest_binder_selection,
    'binder_structure_indices': digest_binder_structure_indices,
    'binder_syntax': digest_binder_syntax,
    'skip_digestion': digest_skip_digestion,
}
OPTIONS = {
    'digestion_source': 'topomt._private.arg_digestion.alphaspace2_arguments',
    'digestion_style': 'registry',
    'standardizer': None,
    'function_source': 'topomt._private.arg_digestion.function.alphaspace2',
    'domain_source': 'topomt._private.arg_digestion.domain.alphaspace2',
}
GATEWAY_PIPELINES = {
    'backend': {'kind': 'alphaspace2', 'rules': ['gateway_backend']},
    'skip_digestion': {'kind': 'alphaspace2', 'rules': ['skip']},
}
ORIGINAL_PIPELINES = {
    **GATEWAY_PIPELINES,
    'backend': {'kind': 'alphaspace2', 'rules': ['original_backend']},
}
LIBRARY_PIPELINES = {
    'binder_chemical_state': {'kind': 'alphaspace2', 'rules': ['binder_state']},
}
