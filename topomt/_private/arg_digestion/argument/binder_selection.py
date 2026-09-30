"""Digest the AlphaSpace2 reference atom selection."""

from .selection import digest_selection


def digest_binder_selection(binder_selection, binder_syntax='MolSysMT', caller=None):
    """Validate the reference selection using its own syntax."""
    return digest_selection(binder_selection, syntax=binder_syntax, caller=caller)
