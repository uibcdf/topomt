"""Original AlphaSpace2 admits its adapter options; native options stay owned."""

from argdigest import FunctionContract

from ..alphaspace2_arguments import API_CALLER

CONTRACTS = [
    FunctionContract(caller=API_CALLER, admits='alphaspace2_options'),
    FunctionContract(
        caller='topomt.third_party.alphaspace2.api.get_topography',
        admits='any',
        description='Original arguments are enforced at the closed library leaf; native options retain their owning contract.',
    ),
    FunctionContract(
        caller='topomt.third_party.alphaspace2.api.get_pockets',
        admits='any',
        description='Options pass through the same validated gateway.',
    ),
]
