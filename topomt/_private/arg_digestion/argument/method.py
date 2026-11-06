from __future__ import annotations

from typing import Any

from argdigest.core.caller import caller_is_one_of

from ..provider_dispatch import (
    ALIASES,
    CALLER,
    DEFAULT_BACKENDS,
    ProviderDispatchArgumentError,
)


def digest_method(method: str, caller: str | None = None) -> str | Any:
    """
    Digest the 'method' argument for topography detection.
    """
    if caller_is_one_of(caller, (CALLER,)):
        if isinstance(method, str):
            name = method.lower()
            if name in DEFAULT_BACKENDS or name in ALIASES:
                return name
        raise ProviderDispatchArgumentError(
            arg_name='method',
            value=method,
            caller=caller,
            reason='method must name a supported original provider.',
        )

    valid_methods = {
        'pocketeer',
        'fpocket',
        'fpocket4',
        'alphaspace2',
        'dfnd',
        'castp',
        'castpfold',
        'castp3',
        'pycasta',
    }

    if isinstance(method, str):
        method_lower = method.lower()
        if method_lower in valid_methods:
            return method_lower

    # If we are here, something is wrong.
    # ArgDigest expects us to return the error or raise it.
    from topomt._private.smonitor import TopoMTException

    class ArgumentError(TopoMTException):
        catalog_key = 'ArgumentError'

    return ArgumentError(
        arg_name='method', reason=f"Unknown method '{method}'. Valid: {valid_methods}"
    )
