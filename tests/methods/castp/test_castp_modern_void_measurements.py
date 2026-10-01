"""Independent local measurements against pinned modern CASTp server outputs."""

import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pytest

from topomt import pyunitwizard as puw
from topomt.io.load_CASTp import _parse_poc_file, _parse_poc_info_file
from topomt.third_party.castp3 import _native_impl, native
from topomt.third_party.castp3.core.castp_core import build_castp_geometry
from topomt.third_party.castp3.core.castp_core.volbl import voids_measurements

DATA = Path(__file__).resolve().parents[3] / 'topomt/data'
QUANTITIES = (
    ('solvent_accessible_area', 'area_sa', 'angstrom**2'),
    ('molecular_surface_area', 'area_ms', 'angstrom**2'),
    ('solvent_accessible_volume', 'volume_sa', 'angstrom**3'),
    ('molecular_surface_volume', 'volume_ms', 'angstrom**3'),
)


@pytest.mark.parametrize('case', ['1stp', '1tcd', '2pk4', '3ptb'])
def test_pinned_castp3_and_castpfold_geometric_outputs_agree(case):
    with (
        zipfile.ZipFile(DATA / f'CASTp_3.0_server/{case}.zip') as castp3,
        zipfile.ZipFile(DATA / f'CASTpFold_server/{case}.zip') as castpfold,
    ):
        for extension in ('poc', 'pocInfo', 'mouth', 'mouthInfo'):
            assert castp3.read(f'{case}.{extension}') == castpfold.read(
                f'{case}.{extension}'
            )
        atom_records = []
        for archive in (castp3, castpfold):
            atom_records.append(
                [
                    line
                    for line in archive.read(f'{case}.pdb').splitlines()
                    if line.startswith((b'ATOM', b'HETATM'))
                ]
            )
        assert atom_records[0] == atom_records[1]


@pytest.fixture(scope='module')
def modern_void_case(tmp_path_factory):
    folder = tmp_path_factory.mktemp('castp_modern_voids')
    with zipfile.ZipFile(DATA / 'CASTpFold_server/2pk4.zip') as archive:
        for extension in ('pdb', 'poc', 'pocInfo'):
            (folder / f'2pk4.{extension}').write_bytes(
                archive.read(f'2pk4.{extension}')
            )
    pdb = folder / '2pk4.pdb'
    geometry = build_castp_geometry(
        pdb,
        selection='molecule_type in ["protein", "peptide"]',
        radii_model='protor',
        solvent_radius=1.4,
    )
    serials = [
        int(line[6:11])
        for line in pdb.read_text().splitlines()
        if line.startswith(('ATOM', 'HETATM'))
    ]
    info = _parse_poc_info_file(folder / '2pk4.pocInfo')
    lining_atoms = _parse_poc_file(folder / '2pk4.poc')
    oracle = {
        frozenset(int(label.split('-', 1)[0]) for label in labels): info[feature_id]
        for feature_id, labels in lining_atoms.items()
        if info[feature_id]['n_mouths'] == 0
    }
    return pdb, geometry, serials, oracle


def _component_atom_ids(geometry, simplex_indices, serials):
    vertices = set(
        np.asarray(geometry.mesh.simplex_atom_indices)[list(simplex_indices)].ravel()
    )
    return frozenset(
        serials[int(geometry.atom_indices_map[index])] for index in vertices
    )


def test_local_void_sa_ms_measurements_match_modern_server(modern_void_case):
    _pdb, geometry, serials, oracle = modern_void_case
    measurements = voids_measurements(geometry, geometry.base_rank)
    observed = {
        _component_atom_ids(geometry, item.simplex_indices, serials): item
        for item in measurements.voids
    }
    assert len(measurements.voids) == len(observed) == len(oracle) == 4
    assert observed.keys() == oracle.keys()
    for atom_ids, item in observed.items():
        for field, attribute, unit in QUANTITIES:
            expected = puw.get_value(oracle[atom_ids][field], to_unit=unit)
            # These archives print three decimals. This is rounding tolerance,
            # not a tunable geometric epsilon or a relative error allowance.
            assert getattr(item, attribute) == pytest.approx(
                expected, abs=0.00050001, rel=0
            )


def test_void_measurements_respect_requested_rank(modern_void_case):
    _pdb, geometry, _serials, _oracle = modern_void_case
    original_rank = geometry.base_rank
    filled_rank = max(entry.rank for entry in geometry.master_entries)

    measurements = voids_measurements(geometry, filled_rank)

    assert not measurements.voids
    assert geometry.base_rank == original_rank


def test_native_void_metrics_reach_topography_with_units(modern_void_case, monkeypatch):
    pdb, geometry, serials, oracle = modern_void_case
    monkeypatch.setattr(_native_impl, 'build_castp_geometry', lambda *a, **k: geometry)
    records, mesh = _native_impl.castp(pdb, radii_model='protor')
    assert mesh is geometry.mesh
    for record in records:
        if record['feature_type'] != 'void':
            assert all(field not in record for field, _, _ in QUANTITIES)
    void_records = [record for record in records if record['feature_type'] == 'void']
    assert len(void_records) == len(oracle)
    for record in void_records:
        atom_ids = frozenset(serials[index] for index in record['atom_indices'])
        for field, _attribute, unit in QUANTITIES:
            assert record[field] == pytest.approx(
                puw.get_value(oracle[atom_ids][field], to_unit=unit),
                abs=0.00050001,
                rel=0,
            )

    monkeypatch.setattr(native, '_native_castp', lambda *a, **k: (records, mesh))
    topography = native.get_topography(pdb)
    for feature in topography.features.values():
        if feature.feature_type != 'void':
            assert all(
                getattr(feature, field, None) is None for field, _, _ in QUANTITIES
            )
            continue
        atom_ids = frozenset(serials[index] for index in feature.atom_indices)
        for field, _attribute, unit in QUANTITIES:
            measured = getattr(feature, field)
            assert puw.is_quantity(measured)
            assert puw.get_value(measured, to_unit=unit) == pytest.approx(
                puw.get_value(oracle[atom_ids][field], to_unit=unit),
                abs=0.00050001,
                rel=0,
            )


def test_native_void_units_preserve_consumer_policy():
    code = """
import numpy as np
import pyunitwizard as puw

puw.configure.set_default_form('pint')
puw.configure.set_default_parser('pint')
puw.configure.set_standard_units(['angstroms'], provenance='consumer-test')
from topomt.third_party.castp3 import native

values = {
    'solvent_accessible_area': (1.030, 2),
    'molecular_surface_area': (38.945, 2),
    'solvent_accessible_volume': (0.051, 3),
    'molecular_surface_volume': (21.752, 3),
}
record = {'id': 1, 'feature_type': 'void', 'atom_indices': []}
record.update({field: value for field, (value, _) in values.items()})
native._native_castp = lambda *args, **kwargs: ([record], None)
policy_before = puw.configure.get_standard_units()
topography = native.get_topography(None)
feature = next(iter(topography.features.values()))
for field, (value, power) in values.items():
    measured = getattr(feature, field)
    assert puw.is_quantity(measured)
    assert np.isclose(puw.get_value(measured, to_unit=f'angstrom**{power}'), value)
    assert np.isclose(puw.get_value(measured, to_unit=f'nm**{power}'),
                      value * 0.1**power)
assert puw.configure.get_standard_units() == policy_before
"""
    result = subprocess.run(
        [sys.executable, '-c', code], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
