"""Original-provider gateways admit only their own closed option sets."""

from argdigest import FunctionContract

CONTRACTS = [
    FunctionContract(
        caller=f'topomt.third_party.{provider}.api.get_output',
        admits=f'{provider}_original_options',
    )
    for provider in ('pykvfinder', 'ghecom', 'caver', 'p2rank')
]
