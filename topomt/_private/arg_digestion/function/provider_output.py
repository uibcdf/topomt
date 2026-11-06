"""The dispatcher delegates provider-specific option contracts to their owners."""

from argdigest import FunctionContract

from ..provider_dispatch import CALLER

contract = FunctionContract(
    caller=CALLER,
    admits='any',
    description=(
        'Provider options are delegated to the selected adapter, including dynamic '
        'optional-library keywords. This first boundary digests method/backend only; '
        'it does not certify provider-specific keyword or value contracts.'
    ),
)
