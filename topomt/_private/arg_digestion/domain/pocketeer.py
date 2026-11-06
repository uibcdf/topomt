"""Declared original Pocketeer parameters without importing the optional engine."""

from inspect import signature

from argdigest import Domain

from ..pocketeer_arguments import PROVIDER_PARAMETERS


def _options() -> tuple[str, ...]:
    from topomt.third_party.pocketeer.files import load_output
    from topomt.third_party.pocketeer.library import get_topography

    return tuple(
        sorted(
            (
                set(signature(get_topography).parameters)
                - {'molecular_system', 'skip_digestion', 'kwargs'}
            )
            | (
                set(signature(load_output).parameters)
                - {'molecular_system', 'skip_digestion'}
            )
            | set(PROVIDER_PARAMETERS)
        )
    )


DOMAINS = [
    Domain(name='pocketeer_options', members=_options),
    Domain(name='pocketeer_parameters', members=PROVIDER_PARAMETERS),
]
