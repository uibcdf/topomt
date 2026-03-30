from topomt._private.smonitor import ArgumentError


def digest_fpocket_cmd(fpocket_cmd, caller=None):
    if isinstance(fpocket_cmd, str):
        return fpocket_cmd

    raise ArgumentError(
        arg_name='fpocket_cmd',
        value=fpocket_cmd,
        caller=caller,
        reason='fpocket_cmd must be a string.',
    )
