from topomt._private.smonitor import ArgumentError


def digest_backend(backend, caller=None):
    if isinstance(backend, str):
        return backend.lower()

    raise ArgumentError(
        arg_name='backend',
        value=backend,
        caller=caller,
        reason='backend must be a string.',
    )
