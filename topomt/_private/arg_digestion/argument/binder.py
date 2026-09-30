"""Digest the optional molecular input used by the AlphaSpace2 library adapter."""

from .molecular_system import digest_molecular_system


def digest_binder(binder, caller=None):
    """Validate an optional reference molecular system."""
    if binder is None:
        return None
    return digest_molecular_system(binder, caller=caller)
