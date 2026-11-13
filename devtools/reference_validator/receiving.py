"""Receive a frozen four-ball case through the public quantity codec.

No inferred radius or replacement bounding box is used. General hull admission
and equality with a newly executed native input remain separate qualifications.
"""

import hashlib
import json
from pathlib import Path

from .model import Atom, Model, Tetrahedron, point, scalar


def freeze_tetrahedron(path: Path, *, probe_angstroms: float) -> Model:
    """Freeze decoded nm binary64 values for an original four-ball input.

    Parameters
    ----------
    path : Path
        Original JSON case with coordinates and explicit atomic-radius qrecs.
    probe_angstroms : float
        Explicitly named length convention for this developer receiving route.

    Returns
    -------
    Model
        Exact rational interpretation of the codec's normalized binary64 values;
        source row IDs, file hash and tetrahedral hull remain recoverable.

    Raises
    ------
    ValueError
        The model is not four-ball or its geometry is degenerate. No general
        convex hull is substituted.
    pyunitwizard.record.RecordError
        The owning codec rejects a corrupted/incompatible quantity record.
    """
    import pyunitwizard as puw
    from pyunitwizard import QuantityRecord

    with path.open('rb') as stream:
        payload = stream.read(16 * 1024**2 + 1)
    if len(payload) > 16 * 1024**2:
        raise ValueError('Pilot input exceeds 16 MiB limit')
    data = json.loads(payload)
    positions = QuantityRecord.from_dict(data['coordinates']).to_quantity(
        field='coordinates', unit='nm'
    )
    radii = QuantityRecord.from_dict(data['atom_radii']).to_quantity(
        field='atom_radii', unit='nm'
    )
    coords = puw.get_value(positions, to_unit='nm', value_type=list, dtype=float)
    radii_nm = puw.get_value(radii, to_unit='nm', value_type=list, dtype=float)
    if len(coords) != 4 or len(radii_nm) != 4:
        raise ValueError('This receiving route requires exactly four atoms')
    probe = puw.get_value(
        puw.quantity(probe_angstroms, 'angstroms'), to_unit='nm', value_type=float
    )
    atoms = tuple(
        Atom(i, point(row), scalar(r))
        for i, (row, r) in enumerate(zip(coords, radii_nm))
    )
    return Model(
        atoms,
        scalar(probe),
        Tetrahedron(tuple(a.center for a in atoms)),
        hashlib.sha256(payload).hexdigest(),
        interpretation='received_binary64_nm',
    )
