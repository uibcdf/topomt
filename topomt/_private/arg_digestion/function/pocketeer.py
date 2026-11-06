"""Pocketeer routes retain the original adapter's option ownership."""

from argdigest import FunctionContract

from ..pocketeer_arguments import API_CALLER, LIBRARY_CALLER

CONTRACTS = [
    FunctionContract(caller=API_CALLER, admits='pocketeer_options'),
    FunctionContract(caller=LIBRARY_CALLER, admits='pocketeer_parameters'),
    FunctionContract(
        caller='topomt.third_party.pocketeer.api.get_topography',
        admits='any',
        description='Original options belong to the closed library contract; native values retain their owning contract.',
    ),
    FunctionContract(
        caller='topomt.third_party.pocketeer.api.get_pockets',
        admits='any',
        description='Options are delegated through the same validated gateway.',
    ),
]
