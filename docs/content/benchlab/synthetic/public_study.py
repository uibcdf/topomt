"""Shared, downloadable reader helpers for the three frozen BenchLab studies.

This is study support, not a new TopoMT API. It runs the public dispatcher or
independent reference checkers, never an original provider or a server request.
"""

import hashlib
import json
import runpy
import sys
from pathlib import Path

import molsysmt as msm
import numpy as np
from pyunitwizard import QuantityRecord

import topomt as tmt
from topomt import pyunitwizard as puw


def quantity(record: dict, field: str, unit: str = 'angstroms'):
    """Restore the record with explicit receiver units."""
    return QuantityRecord.from_dict(record).to_quantity(field=field, unit=unit)


def read(path: Path) -> dict:
    """Read a retained JSON record without rewriting it."""
    return json.loads(path.read_text())


def receive(directory: Path, probe: float, min_size: int = 0) -> tmt.Topography:
    """Receive the original full-precision ball input through the public API."""
    directory = directory.resolve()
    protocol = read(directory / 'artifacts/public_topography_v1/protocol.json')
    input_path = directory.parent.parent / protocol['input_file']
    if hashlib.sha256(input_path.read_bytes()).hexdigest() != protocol['input_sha256']:
        raise ValueError('Frozen case input does not match its public protocol')
    fixture = read(input_path)
    source_case = protocol['source_case']
    source_dir = directory.parent / source_case / 'artifacts' / f'{source_case}_v1'
    source_path = source_dir / 'input.json'
    expected = fixture.get('parent_input', {}).get('sha256', protocol['input_sha256'])
    if hashlib.sha256(source_path.read_bytes()).hexdigest() != expected:
        raise ValueError('Frozen parent input does not match its source identity')
    source = read(source_path)
    system = msm.convert(str(source_dir / 'input.pdb'), to_form='molsysmt.MolSys')
    coords = puw.get_value(
        quantity(source['coordinates'], 'coordinates'), to_unit='angstroms'
    )
    msm.set(system, coordinates=puw.quantity(coords[None], 'angstroms'))
    selected = protocol['selection']
    radii = msm.physchem.get_atomic_radius(
        system, element='atom', selection=selected, definition='vdw'
    )
    np.testing.assert_allclose(
        puw.get_value(radii, to_unit='angstroms'),
        puw.get_value(
            quantity(fixture['atom_radii'], 'atom_radii'), to_unit='angstroms'
        ),
        rtol=0,
        atol=1e-14,
    )
    query = {
        key: quantity(value, key) if isinstance(value, dict) else value
        for key, value in protocol['query'].items()
    }
    query.update(epsilon=quantity(fixture['epsilon'], 'epsilon'), min_size=min_size)
    topo = tmt.get_topography(
        system,
        method='dfnd',
        selection=selected,
        probe_radius=puw.quantity(probe, 'angstroms'),
        **query,
    )
    np.testing.assert_allclose(
        puw.get_value(topo.input_context.coordinates, to_unit='angstroms'),
        puw.get_value(
            quantity(fixture['coordinates'], 'coordinates'), to_unit='angstroms'
        ),
        rtol=0,
        atol=1e-13,
    )
    assert topo.input_context.atom_indices.tolist() == selected
    return topo


def describe(topo: tmt.Topography) -> dict:
    """Summarize actual results without equating native links with free patches."""
    raw = topo.dfnd.raw
    return {
        'public_types': [type(feature).__name__ for feature in topo.values()],
        'raw_resident_regions': len(raw['wet_components']),
        'native_exterior_links': len(raw['external_links']),
        'public_mouths': len(topo.get_features(by='type', value='mouth')),
        'physical_view_status': 'present'
        if 'boundary_connectivity' in raw
        else 'not_available',
        'result_key': raw['parameters']['result_key'],
    }


def reference(directory: Path) -> dict:
    """Replay the existing independent certificate; no DFND result is its oracle."""
    case = directory.name
    folder, script = {
        'regular_tetrahedron': (
            'boundary_connectivity_v1',
            'verify_tetrahedron_boundary.py',
        ),
        'closed_shell': ('wall_certificate_v1', 'verify_closed_shell_wall_cover.py'),
        'shell_with_opening': (
            'opening_connectivity_v1',
            'verify_opening_connectivity.py',
        ),
    }[case]
    data = directory / 'artifacts' / folder
    tools = Path(__file__).resolve().parents[4] / 'devtools'
    previous_path = sys.path[:]
    try:
        sys.path.insert(0, str(tools))
        checker = runpy.run_path(str(tools / script))['verify_certificate']
        verified = checker(
            directory / 'artifacts' / f'{case}_v1/input.json',
            data / 'protocol.json',
            read(data / 'certificate.json'),
        )
    finally:
        sys.path[:] = previous_path
    assert verified == read(data / 'verification.json')
    return verified
