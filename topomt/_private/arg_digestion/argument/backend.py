from argdigest.core.caller import caller_is_one_of

from topomt._private.smonitor import ArgumentError

from ..provider_dispatch import (
    ALIASES,
    CALLER,
    ORIGINAL_BACKENDS,
    ProviderDispatchArgumentError,
)


def digest_backend(backend, caller=None, method=None):
    if caller_is_one_of(caller, (CALLER,)):
        if backend is None:
            return None
        provider = ALIASES.get(method, method)
        if isinstance(backend, str) and backend.lower() in ORIGINAL_BACKENDS[provider]:
            return backend.lower()
        raise ProviderDispatchArgumentError(
            arg_name='backend',
            value=backend,
            caller=caller,
            reason=f'backend must be an original route for {method!r}.',
        )

    if isinstance(backend, str):
        return backend.lower()

    raise ArgumentError(
        arg_name='backend',
        value=backend,
        caller=caller,
        reason='backend must be a string.',
    )
