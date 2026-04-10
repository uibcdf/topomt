from topomt._private.smonitor import ArgumentError


def digest_email(email, caller=None):
    if isinstance(email, str):
        return email

    raise ArgumentError(
        arg_name='email',
        value=email,
        caller=caller,
        reason='email must be a string.',
    )
