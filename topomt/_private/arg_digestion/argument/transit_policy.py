from topomt._private.smonitor import ArgumentError


def digest_transit_policy(transit_policy, caller=None):
    if transit_policy in {'resident_only', 'with_connectors'}:
        return transit_policy

    raise ArgumentError(
        arg_name='transit_policy',
        value=transit_policy,
        caller=caller,
        reason="transit_policy must be resident_only or with_connectors.",
    )
