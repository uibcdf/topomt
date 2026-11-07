"""Argument ownership for saving and recovering original-provider evidence."""

from pathlib import Path
from typing import Any

from argdigest import register_pipeline
from argdigest.core.context import Context

from .external_arguments import digest_molecular_system, digest_path

LOAD_CALLER = 'topomt.load_provider_output.load_provider_output'
SAVE_CALLER = 'topomt.third_party.output.ProviderOutput.save'


@register_pipeline(kind='provider_persistence', name='bundle_file')
def digest_bundle_file(value: Any, context: Context) -> Path:
    """Admit the explicit evidence path without reading or changing it."""
    return digest_path(value, 'bundle_file', LOAD_CALLER)


@register_pipeline(kind='provider_persistence', name='source')
def digest_source(value: Any, context: Context) -> Any:
    """Require a source; molecular interpretation remains with MolSysMT."""
    return digest_molecular_system(value, caller=LOAD_CALLER)


@register_pipeline(kind='provider_persistence', name='path')
def digest_output_path(value: Any, context: Context) -> Path:
    """Admit a filename rather than an implicit open file descriptor."""
    return digest_path(value, 'path', SAVE_CALLER)


OPTIONS = {
    'argument_digestion': False,
    'standardizer': None,
    'function_source': 'topomt._private.arg_digestion.function.provider_persistence',
}
LOAD_PIPELINES = {
    'bundle_file': {'kind': 'provider_persistence', 'rules': ['bundle_file']},
    'molecular_system': {'kind': 'provider_persistence', 'rules': ['source']},
}
SAVE_PIPELINES = {
    'path': {'kind': 'provider_persistence', 'rules': ['path']},
}
