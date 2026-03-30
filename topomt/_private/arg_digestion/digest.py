"""ArgDigest adapter for TopoMT."""

from argdigest import arg_digest as _argdigest_digest


def arg_digest(*args, **kwargs):
    """Return the TopoMT-configured ArgDigest decorator."""

    return _argdigest_digest(config='topomt._argdigest', *args, **kwargs)
