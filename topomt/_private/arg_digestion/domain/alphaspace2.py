"""Original AlphaSpace2 options follow the closed adapter's signature."""

from inspect import signature

from argdigest import Domain


def _options() -> tuple[str, ...]:
    from topomt.third_party.alphaspace2.library import get_topography

    return tuple(
        sorted(
            set(signature(get_topography).parameters)
            - {'molecular_system', 'skip_digestion'}
        )
    )


domain = Domain(name='alphaspace2_options', members=_options)
