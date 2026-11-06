"""Admission of original fpocket options before selecting the closed route."""

from argdigest import FunctionContract

from ..fpocket_arguments import API_CALLER

contract = FunctionContract(caller=API_CALLER, admits='fpocket_options')

CONTRACTS = [
    FunctionContract(
        caller='topomt.third_party.fpocket.api.get_topography',
        admits='any',
        description='Backend-specific options are delegated; the original CLI has its own closed contract and native/variant contracts remain separately owned.',
    ),
    FunctionContract(
        caller='topomt.third_party.fpocket.api.get_pockets',
        admits='any',
        description='Options are delegated to the same validated topography gateway.',
    ),
    FunctionContract(
        caller='topomt.third_party.fpocket.api.load_topography',
        admits='fpocket_file_options',
    ),
]
