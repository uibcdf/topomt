"""Admission of original fpocket options before selecting the closed route."""

from argdigest import FunctionContract

from ..fpocket_arguments import API_CALLER

contract = FunctionContract(caller=API_CALLER, admits='fpocket_options')
