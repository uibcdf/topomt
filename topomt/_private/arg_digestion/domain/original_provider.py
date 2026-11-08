"""Static option discovery never imports an optional scientific engine."""

from argdigest import Domain

from ..original_provider_arguments import PARAMETERS

DOMAINS = [
    Domain(
        name=f'{provider}_original_options',
        members=tuple(sorted(parameters | {'bundle_file'})),
    )
    for provider, parameters in PARAMETERS.items()
]
