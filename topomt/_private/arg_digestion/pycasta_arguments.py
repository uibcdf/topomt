"""Original pyCASTA argument admission without importing its scripts."""

from pathlib import Path
from typing import Any

from argdigest import register_pipeline
from argdigest.core.context import Context

from .external_arguments import (
    _error,
    digest_chemical_state,
    digest_molecular_system,
    digest_path,
    digest_selection,
    digest_skip_digestion,
    digest_structure_indices,
    digest_syntax,
    digest_upstream_root,
)

API_CALLER = 'topomt.third_party.pycasta.api.get_output'
LIBRARY_CALLER = 'topomt.third_party.pycasta.library.get_topography'
FILES_CALLER = 'topomt.third_party.pycasta.files.load_output'
LIBRARY_PARAMETERS = (
    'selection',
    'structure_indices',
    'syntax',
    'upstream_root',
    'chemical_state',
)
FILES_PARAMETERS = ('bundle_file',)


def normalize_backend(caller: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    """Normalize this provider's route before its option domain is consulted."""
    normalized = dict(kwargs)
    if isinstance(normalized.get('backend'), str):
        normalized['backend'] = normalized['backend'].lower()
    return normalized


def digest_bundle_file(bundle_file: Any, caller: str | None = None) -> Path:
    return digest_path(bundle_file, 'bundle_file', caller)


@register_pipeline(kind='pycasta', name='original_backend')
def digest_original_backend(value: Any, context: Context) -> str:
    if isinstance(value, str) and value.lower() in {'library', 'wrapper', 'files'}:
        backend = value.lower()
        if backend == 'files' and context.all_args.get('bundle_file') is None:
            _error(
                'bundle_file',
                None,
                context.function_name,
                'Saved pyCASTA output requires bundle_file.',
            )
        return backend
    _error(
        'backend',
        value,
        context.function_name,
        'Expected library, wrapper or files for original output.',
    )


@register_pipeline(kind='pycasta', name='gateway_backend')
def digest_gateway_backend(value: Any, context: Context) -> str:
    if isinstance(value, str) and value.lower() in {'native', 'library', 'wrapper'}:
        return value.lower()
    _error(
        'backend', value, context.function_name, 'Expected native, library or wrapper.'
    )


@register_pipeline(kind='pycasta', name='skip')
def digest_skip(value: Any, context: Context) -> bool:
    return digest_skip_digestion(value, caller=context.function_name)


ARGUMENT_DIGESTERS = {
    'molecular_system': digest_molecular_system,
    'selection': digest_selection,
    'structure_indices': digest_structure_indices,
    'syntax': digest_syntax,
    'upstream_root': digest_upstream_root,
    'chemical_state': digest_chemical_state,
    'bundle_file': digest_bundle_file,
    'skip_digestion': digest_skip_digestion,
}
OPTIONS = {
    'digestion_source': 'topomt._private.arg_digestion.pycasta_arguments',
    'digestion_style': 'registry',
    'standardizer': normalize_backend,
    'function_source': 'topomt._private.arg_digestion.function.pycasta',
    'domain_source': 'topomt._private.arg_digestion.domain.pycasta',
}
GATEWAY_PIPELINES = {
    'backend': {'kind': 'pycasta', 'rules': ['gateway_backend']},
    'skip_digestion': {'kind': 'pycasta', 'rules': ['skip']},
}
ORIGINAL_PIPELINES = {
    **GATEWAY_PIPELINES,
    'backend': {'kind': 'pycasta', 'rules': ['original_backend']},
}
