from __future__ import annotations

from .method import digest_method


def digest_engine(engine, caller=None):
    """Digest the deprecated alias `engine` using the canonical method rule."""

    if engine is None:
        return None

    return digest_method(engine, caller=caller)
