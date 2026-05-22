from topomt._private.smonitor import ArgumentError


def digest_hydrogen_policy(hydrogen_policy, caller=None):
    if hydrogen_policy in {'exclude', 'include'}:
        return hydrogen_policy

    raise ArgumentError(
        arg_name='hydrogen_policy',
        value=hydrogen_policy,
        caller=caller,
        reason="hydrogen_policy must be exclude or include.",
    )
