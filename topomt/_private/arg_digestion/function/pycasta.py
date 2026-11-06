"""Original pyCASTA option ownership follows the selected route."""

from argdigest import FunctionContract

CONTRACTS = [
    FunctionContract(
        caller_pattern='topomt.third_party.pycasta.api.*',
        admits='pycasta_options',
        description='Original execution and saved imports have separate options; native options retain their owning contract.',
    ),
]
