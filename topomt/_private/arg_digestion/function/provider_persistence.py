"""Saved execution context is restored, never overridden by new options."""

from argdigest import FunctionContract

from ..provider_persistence import LOAD_CALLER, SAVE_CALLER

CONTRACTS = [
    FunctionContract(caller=LOAD_CALLER, admits='signature'),
    FunctionContract(caller=SAVE_CALLER, admits='signature'),
]
