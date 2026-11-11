"""Case-owned reference replay and shared public straight-tube receiving."""

import sys
from pathlib import Path
from typing import Any

_root = Path(__file__).resolve().parents[5]
_previous = sys.path[:]
try:
    sys.path.insert(0, str(_root))
    from devtools.benchlab import tube_study as _shared
finally:
    sys.path[:] = _previous

read = _shared.read
quantity = _shared.quantity
describe = _shared.describe
inspect_centerlines = _shared.inspect_centerlines
_tools = _shared._tools


def receive(directory: Path, probe: float, min_size: int = 0) -> Any:
    """Receive this case's fixed atomic model through the public DFND API.

    Parameters
    ----------
    directory : Path
        Case directory, also when extracted from the complete source bundle.
    probe : float
        Probe radius in angstroms.
    min_size : int
        Public reporting cutoff, independent of the frozen scientific model.

    Returns
    -------
    topomt.Topography
        Actual native/public result with original source/radius support.

    Raises
    ------
    ValueError
        Current case identity, frozen model or assigned radii disagree.

    Examples
    --------
    >>> topo = receive(Path.cwd(), 1.4)
    """
    if read(directory / 'identity.json')['case_id'] != 'straight_tube_narrow_dense':
        raise ValueError('Current straight-tube study identity differs')
    return _shared.receive(directory, probe, min_size)


def references(directory: Path) -> dict:
    """Replay independent paths/bounds and both complete wall/end certificates."""
    with _tools():
        from devtools.verify_tube_boundary import verify_boundary
        from devtools.verify_tube_passage import verify_reference

        folder = directory / 'artifacts/straight_tube_narrow_dense_v1'
        passage = verify_reference(
            folder / 'input.json',
            folder / 'passage_v2_protocol.json',
            read(folder / 'reference_v2_certificate.json'),
        )
        boundaries = {
            str(probe): verify_boundary(
                folder / 'input.json',
                folder / f'boundary_{probe:g}A_v2_protocol.json',
                read(folder / f'boundary_{probe:g}A_v2_certificate.json'),
            )
            for probe in (1.2, 1.4)
        }
        return {'passage': passage, 'boundary': boundaries}
