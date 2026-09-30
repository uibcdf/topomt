"""Digest the AlphaSpace2 reference frame selection."""

from .structure_indices import digest_structure_indices


def digest_binder_structure_indices(binder_structure_indices, caller=None):
    """Validate reference frame indices."""
    return digest_structure_indices(binder_structure_indices, caller=caller)
