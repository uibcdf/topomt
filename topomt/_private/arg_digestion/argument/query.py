"""Admit existing typed native queries at the shared public gateway."""

from typing import Any

from topomt._private.smonitor import ArgumentError


def digest_query(query: Any, caller: str | None = None) -> Any:
    """Accept the default sentinel or an already validated DFNDQuery instance."""
    if query is None:
        return None
    from topomt.dfnd.config import DFNDQuery

    if isinstance(query, DFNDQuery):
        return query
    raise ArgumentError(
        arg_name='query',
        value=query,
        caller=caller,
        reason='query must be None or an existing DFNDQuery instance.',
    )
