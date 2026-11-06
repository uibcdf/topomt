"""Original-provider routing policy and its scoped ArgDigest pipelines."""

from typing import Any

from argdigest import register_pipeline
from argdigest.core.context import Context

from topomt._private.smonitor import ArgumentError

CALLER = 'topomt.get_provider_output.get_provider_output'
ALIASES = {'fpocket4': 'fpocket', 'castp3': 'castp', 'castpfold': 'castp'}
DEFAULT_BACKENDS = {
    'fpocket': 'cli',
    'pocketeer': 'library',
    'alphaspace2': 'library',
    'pycasta': 'library',
    'castp': 'server',
}
ORIGINAL_BACKENDS = {
    'fpocket': {'cli', 'wrapper', 'files'},
    'pocketeer': {'library', 'wrapper', 'files'},
    'alphaspace2': {'library', 'wrapper', 'files'},
    'pycasta': {'library', 'wrapper', 'files'},
    'castp': {'server', 'castpfold', 'files'},
}


class ProviderDispatchArgumentError(ArgumentError, ValueError):
    """Keep original dispatch ValueError compatibility with catalogued diagnostics."""

    def __init__(
        self, *, arg_name: str, value: Any, caller: str | None, reason: str
    ) -> None:
        ArgumentError.__init__(
            self, arg_name=arg_name, value=value, caller=caller, reason=reason
        )


@register_pipeline(kind='provider_dispatch', name='method')
def digest_provider_method(value: Any, context: Context) -> str:
    """Apply the owning method digester to the original-output boundary."""
    from .argument.method import digest_method

    return digest_method(value, caller=CALLER)


@register_pipeline(kind='provider_dispatch', name='backend')
def digest_provider_backend(value: Any, context: Context) -> str | None:
    """Validate the backend against the already digested method."""
    from .argument.backend import digest_backend

    return digest_backend(value, method=context.all_args['method'], caller=CALLER)


# Ordered pipelines digest method before the backend's method-dependent check.
# Provider-owned molecular data and options are forwarded unchanged.
PIPELINES = {
    'method': {'kind': 'provider_dispatch', 'rules': ['method']},
    'backend': {'kind': 'provider_dispatch', 'rules': ['backend']},
}
