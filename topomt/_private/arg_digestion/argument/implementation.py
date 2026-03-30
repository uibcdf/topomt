from topomt._private.smonitor import ArgumentError


def digest_implementation(implementation, caller=None):
    if isinstance(implementation, str):
        implementation_lower = implementation.lower()
        if implementation_lower in {'wrapper', 'native', 'topomt'}:
            return implementation_lower

    raise ArgumentError(
        arg_name='implementation',
        value=implementation,
        caller=caller,
        reason="implementation must be 'wrapper', 'native', or 'topomt'.",
    )
