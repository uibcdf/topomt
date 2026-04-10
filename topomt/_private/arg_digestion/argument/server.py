from topomt._private.smonitor import ArgumentError


def digest_server(server, caller=None):
    if server is None:
        return None

    if isinstance(server, str):
        return server.lower()

    raise ArgumentError(
        arg_name='server',
        value=server,
        caller=caller,
        reason='server must be None or a string.',
    )
