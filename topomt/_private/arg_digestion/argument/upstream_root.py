from pathlib import Path

from topomt._private.smonitor import ArgumentError


def digest_upstream_root(upstream_root, caller=None):
    if upstream_root is None:
        return None

    if isinstance(upstream_root, (str, Path)):
        return str(Path(upstream_root).expanduser().resolve())

    raise ArgumentError(
        arg_name='upstream_root',
        value=upstream_root,
        caller=caller,
        reason='upstream_root must be None, a string, or a pathlib.Path.',
    )
