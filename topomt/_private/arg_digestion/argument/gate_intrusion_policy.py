from topomt._private.smonitor import ArgumentError


def digest_gate_intrusion_policy(gate_intrusion_policy, caller=None):
    if gate_intrusion_policy in {'flag_only', 'block_suspect'}:
        return gate_intrusion_policy

    raise ArgumentError(
        arg_name='gate_intrusion_policy',
        value=gate_intrusion_policy,
        caller=caller,
        reason="gate_intrusion_policy must be flag_only or block_suspect.",
    )
