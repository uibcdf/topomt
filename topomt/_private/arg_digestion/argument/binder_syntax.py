"""Digest the AlphaSpace2 reference selection syntax."""

from .syntax import digest_syntax


def digest_binder_syntax(binder_syntax, caller=None):
    """Normalize the reference selection syntax."""
    return digest_syntax(binder_syntax, caller=caller)
