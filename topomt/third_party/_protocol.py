"""Private original-provider decoding helpers; no native feature admission."""

import math
from typing import Any

from topomt._pyunitwizard import pyunitwizard as puw
from topomt.provider_output import ExternalMeasurement, ProviderRun
from topomt.third_party.output import ProviderGeometry


def artifact(run: ProviderRun, name: str) -> bytes:
    """Read a required original artifact without silently treating it as empty."""
    try:
        return run.get_artifact('output/' + name)
    except KeyError as error:
        raise ValueError(
            f'{run.provider} required artifact is absent: {name}'
        ) from error


def finite(value: Any, *, nonnegative: bool = False) -> float:
    """Decode a finite protocol scalar, rejecting booleans and negative sizes."""
    if isinstance(value, bool):
        raise ValueError('Original numeric field cannot be boolean')
    number = float(value)
    if not math.isfinite(number) or nonnegative and number < 0:
        raise ValueError('Original numeric field must be finite with valid sign')
    return number


def measurement(
    run: ProviderRun, value: Any, unit: str, field: str, filename: str, definition: str
) -> ExternalMeasurement:
    """Attach protocol units and original source identity to a scalar."""
    number = finite(value)
    return ExternalMeasurement(
        value=puw.quantity(number, unit),
        original_value=number,
        original_unit=unit,
        source_field=field,
        source_artifact='output/' + filename,
        run_id=run.run_id,
        definition=definition,
        issue_url=None,
    )


def points_geometry(
    kind: str, points: list, definition: str, radii: list | None = None
) -> ProviderGeometry:
    """Convert documented angstrom coordinates to an explicit nm representation."""
    coords = tuple(tuple(finite(x) / 10 for x in row) for row in points)
    sizes = (
        None
        if radii is None
        else tuple(finite(r, nonnegative=True) / 10 for r in radii)
    )
    return ProviderGeometry(kind, coords, definition, sizes)


def pdb_points(data: bytes) -> list[tuple[str, str, tuple[float, float, float]]]:
    """Read only provider grid/point rows, retaining residue label and number."""
    rows = []
    for line in data.decode('utf-8').splitlines():
        if line.startswith(('ATOM  ', 'HETATM')):
            try:
                point = (finite(line[30:38]), finite(line[38:46]), finite(line[46:54]))
                rows.append((line[17:20].strip(), line[22:26].strip(), point))
            except (ValueError, IndexError) as error:
                raise ValueError('Malformed original PDB point row') from error
    return rows
