"""Receive fixed sphere inputs and exact domains through the public quantity codec.

No inferred radius or replacement bounding box is used. General hull admission
and equality with a newly executed native input remain separate qualifications.
"""

from fractions import Fraction
from pathlib import Path
from typing import Any, Optional

from .hull_model import CenterSource
from .model import Atom, HullDomain, Model, Tetrahedron, point, scalar
from .storage import read_record_with_digest


def freeze_centers(path: Path) -> CenterSource:
    """Freeze original coordinates as an exact nm center-only proof source.

    Parameters
    ----------
    path : Path
        Original JSON case with its integrity-bearing coordinate quantity record.

    Returns
    -------
    CenterSource
        Exact normalized binary64 centers, original row IDs and input hash.
        Radii/probe are not consumed by a center-hull proof. This is not a
        molecular model, free-volume receiving or fresh DFND input comparison.

    Raises
    ------
    ValueError, TypeError
        Record, coordinates or input/work representation is invalid.
    pyunitwizard.record.RecordError
        The owning quantity codec rejects corrupted/incompatible coordinates.
    """
    import pyunitwizard as puw
    from pyunitwizard import QuantityRecord

    data, digest = read_record_with_digest(path)
    quantity = QuantityRecord.from_dict(data['coordinates']).to_quantity(
        field='coordinates', unit='nm'
    )
    coordinates = puw.get_value(quantity, to_unit='nm', value_type=list, dtype=float)
    return CenterSource(
        tuple(point(row) for row in coordinates),
        tuple(range(len(coordinates))),
        digest,
        interpretation='received_binary64_nm',
    )


def _receive_spheres(
    path: Path, probe_angstroms: float
) -> tuple[tuple[Atom, ...], Fraction, str]:
    import pyunitwizard as puw
    from pyunitwizard import QuantityRecord

    data, digest = read_record_with_digest(path)
    positions = QuantityRecord.from_dict(data['coordinates']).to_quantity(
        field='coordinates', unit='nm'
    )
    radii = QuantityRecord.from_dict(data['atom_radii']).to_quantity(
        field='atom_radii', unit='nm'
    )
    coords = puw.get_value(positions, to_unit='nm', value_type=list, dtype=float)
    radii_nm = puw.get_value(radii, to_unit='nm', value_type=list, dtype=float)
    if len(coords) != len(radii_nm):
        raise ValueError('Every center requires exactly one atomic radius')
    probe = puw.get_value(
        puw.quantity(probe_angstroms, 'angstroms'), to_unit='nm', value_type=float
    )
    atoms = tuple(
        Atom(i, point(row), scalar(r))
        for i, (row, r) in enumerate(zip(coords, radii_nm))
    )
    return atoms, scalar(probe), digest


def freeze_tetrahedron(path: Path, *, probe_angstroms: float) -> Model:
    """Freeze a four-ball case with its original tetrahedral observation domain.

    Parameters
    ----------
    path : Path
        Original JSON case with coordinates and atomic-radius quantity records.
    probe_angstroms : float
        Explicit probe length in angstroms, converted through PyUnitWizard.

    Returns
    -------
    Model
        Exact received binary64 nm values, all rows, input hash and tetrahedron.

    Raises
    ------
    ValueError
        The input is not four-ball, or the geometry/values are invalid.
    pyunitwizard.record.RecordError
        The owning codec rejects a corrupted or incompatible quantity record.
    """
    atoms, probe, digest = _receive_spheres(path, probe_angstroms)
    if len(atoms) != 4:
        raise ValueError('This receiving route requires exactly four atoms')
    return Model(
        atoms,
        probe,
        Tetrahedron(tuple(a.center for a in atoms)),
        digest,
        interpretation='received_binary64_nm',
    )


def freeze_hull_model(
    path: Path, *, probe_angstroms: float, certificate: Optional[dict[str, Any]] = None
) -> Model:
    """Freeze all spheres and use their independently checked center hull as domain.

    Parameters
    ----------
    path : Path
        Original JSON case containing integrity-bearing coordinate/radius records.
    probe_angstroms : float
        Explicit probe length in angstroms, converted through PyUnitWizard.
    certificate : dict, optional
        Reusable original hull proof for this exact coordinate/file/frame source.
        Without it, construct a new proof within the bounded hull envelope.

    Returns
    -------
    Model
        All received atoms/radii and the probe, plus a verified finite center hull.
        No occupancy, region inventory or fresh native-input equality is inferred.

    Raises
    ------
    ValueError
        Source/proof, full-dimensional geometry or bounded admission fails.
    pyunitwizard.record.RecordError
        The owning codec rejects a corrupted or incompatible quantity record.
    """
    atoms, probe, digest = _receive_spheres(path, probe_angstroms)
    source = CenterSource(
        tuple(a.center for a in atoms),
        tuple(a.source_id for a in atoms),
        digest,
        interpretation='received_binary64_nm',
    )
    if certificate is None:
        from .center_hull import hull_certificate

        certificate = hull_certificate(source)
    return Model(
        atoms,
        probe,
        HullDomain(source.to_record(), certificate),
        digest,
        interpretation='received_binary64_nm',
    )
