"""CASTp raw and saved boundaries retain distinct option ownership."""

from argdigest import FunctionContract

from ..castp_arguments import API_CALLER, FILES_CALLER, RECOVERY_CALLER

CONTRACTS = [
    FunctionContract(caller=API_CALLER, admits='castp_original_options'),
    FunctionContract(caller=FILES_CALLER, admits='castp_raw_options'),
    FunctionContract(caller=RECOVERY_CALLER, admits='signature'),
]
