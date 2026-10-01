"""Independent local measurements against pinned modern CASTp server outputs."""

import json
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pytest

from devtools.castp.compare_castp3_oracles import _atom_id_lookup
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
VOID_IDS = {
    '2pk4': (4, 5, 6, 7),
    '1ifb': (1, 7, 9, 10),
    '3phv': (8, 13),
    '1hew': (3, 6, 7),
    '1cge': (14, 15, 16, 17, 19, 20, 21),
    '1a4j': (
        23,
        24,
        40,
        42,
        44,
        48,
        57,
        58,
        59,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        78,
        79,
        80,
        81,
        84,
        85,
        86,
        87,
        88,
        89,
        90,
        91,
        92,
        93,
        95,
        96,
        97,
        98,
        99,
        101,
    ),
    '1cdo': (
        14,
        17,
        24,
        25,
        27,
        29,
        33,
        34,
        35,
        38,
        40,
        42,
        43,
        45,
        46,
        47,
        48,
        50,
        51,
        54,
        55,
        58,
        59,
        60,
        61,
        62,
        64,
        67,
        68,
        69,
        71,
        72,
        73,
        75,
        76,
        78,
        79,
        80,
        81,
        82,
        83,
        84,
        85,
    ),
    '1crn': (1,),
    '1stp': (5, 8, 9),
    '2lyz': (5, 7, 8, 9, 11, 12),
    '2ifb': (1, 3, 8, 9, 13, 17),
    '1stn': (8, 9, 13, 14, 15, 16, 17),
    '1hel': (2, 8, 11, 12),
    '1snc': (5, 8, 9, 10, 11, 12, 13, 14),
    '1rob': (11, 12),
    '5dfr': (14, 15, 16),
    '3ptb': (5, 8, 9, 11, 13, 14, 15, 18, 19, 22, 23, 24, 25, 26),
    '1a6w': (11, 13, 18, 21, 23, 26, 27, 28, 29, 30, 31, 32),
    '1bmq': (18, 19, 20, 21, 22, 23, 26, 27, 28, 29, 30, 31, 32, 35, 37),
    '2tga': (6, 9, 10, 13, 14, 15, 18, 21, 22, 23, 25, 27, 28, 29, 30, 31),
    '1srf': (16, 17, 21, 24, 25, 26, 27, 28, 30, 31, 32, 33),
    '2ctv': (14, 15, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 30),
}


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
def modern_void_cache():
    """Reuse each archive's expensive geometry across scalar-parametrized rows."""
    return {'cases': {}, 'measurements': {}}


@pytest.fixture(scope='module')
def modern_void_case(tmp_path_factory, request, modern_void_cache):
    case = getattr(request, 'param', '2pk4')
    if case in modern_void_cache['cases']:
        return modern_void_cache['cases'][case]
    folder = tmp_path_factory.mktemp(f'castp_modern_voids_{case}')
    with zipfile.ZipFile(DATA / f'CASTpFold_server/{case}.zip') as archive:
        pdb_members = [name for name in archive.namelist() if name.endswith('.pdb')]
        assert len(pdb_members) == 1
        stem = Path(pdb_members[0]).stem
        for extension in ('pdb', 'poc', 'pocInfo'):
            (folder / f'{case}.{extension}').write_bytes(
                archive.read(f'{stem}.{extension}')
            )
    pdb = folder / f'{case}.pdb'
    geometry = build_castp_geometry(
        pdb,
        selection='molecule_type in ["protein", "peptide"]',
        radii_model='castp3_protor',
        solvent_radius=1.4,
    )
    serials = _atom_id_lookup(pdb)
    info = _parse_poc_info_file(folder / f'{case}.pocInfo')
    lining_atoms = _parse_poc_file(folder / f'{case}.poc')
    oracle = {
        frozenset(int(label.split('-', 1)[0]) for label in labels): {
            **info[feature_id],
            'server_id': feature_id,
        }
        for feature_id, labels in lining_atoms.items()
        if info[feature_id]['n_mouths'] == 0
    }
    expected_ids = {key for key, value in info.items() if value['n_mouths'] == 0}
    assert len(oracle) == len(expected_ids)
    assert {item['server_id'] for item in oracle.values()} == expected_ids
    result = pdb, geometry, serials, oracle
    modern_void_cache['cases'][case] = result
    return result


def _component_atom_ids(geometry, simplex_indices, serials):
    vertices = set(
        np.asarray(geometry.mesh.simplex_atom_indices)[list(simplex_indices)].ravel()
    )
    return frozenset(
        serials[int(geometry.atom_indices_map[index])] for index in vertices
    )


@pytest.fixture(scope='module')
def local_void_measurements(modern_void_case, modern_void_cache):
    pdb, geometry, serials, _oracle = modern_void_case
    if pdb.stem in modern_void_cache['measurements']:
        return modern_void_cache['measurements'][pdb.stem]
    measurements = voids_measurements(geometry, geometry.base_rank)
    observed = {
        _component_atom_ids(geometry, item.simplex_indices, serials): item
        for item in measurements.voids
    }
    assert len(observed) == len(measurements.voids)
    modern_void_cache['measurements'][pdb.stem] = observed
    return observed


@pytest.mark.parametrize('modern_void_case', VOID_IDS, indirect=True)
def test_modern_panel_void_membership(modern_void_case, local_void_measurements):
    pdb, _geometry, _serials, oracle = modern_void_case
    assert {item['server_id'] for item in oracle.values()} == set(VOID_IDS[pdb.stem])
    assert local_void_measurements.keys() == oracle.keys()


@pytest.mark.parametrize(
    'modern_void_case,feature_id,field,attribute,unit',
    [
        pytest.param(
            case, feature_id, *quantity, id=f'{case}-{feature_id}-{quantity[0]}'
        )
        for case, feature_ids in VOID_IDS.items()
        for feature_id in feature_ids
        for quantity in QUANTITIES
    ],
    indirect=['modern_void_case'],
)
def test_modern_panel_void_measurement(
    modern_void_case, local_void_measurements, feature_id, field, attribute, unit
):
    _pdb, _geometry, _serials, oracle = modern_void_case
    atom_ids, expected = next(
        (atom_ids, expected)
        for atom_ids, expected in oracle.items()
        if expected['server_id'] == feature_id
    )
    observed = getattr(local_void_measurements[atom_ids], attribute)
    assert observed == pytest.approx(
        puw.get_value(expected[field], to_unit=unit), abs=0.00050001, rel=0
    )


@pytest.mark.parametrize('modern_void_case', ['1hew'], indirect=True)
def test_castp3_profile_reproduces_pinned_1hew_void_bulbs(
    modern_void_case, local_void_measurements
):
    _pdb, geometry, _serials, oracle = modern_void_case
    atom_ids = next(ids for ids, data in oracle.items() if data['server_id'] == 7)
    component = local_void_measurements[atom_ids]
    with zipfile.ZipFile(DATA / 'CASTpFold_server/1hew.zip') as archive:
        member = next(
            name for name in archive.namelist() if name.endswith('.bulb.json')
        )
        remaining = json.loads(archive.read(member))[6]
    assert len(remaining) == len(component.simplex_indices) == 6
    for index in component.simplex_indices:
        vertices = np.asarray(geometry.mesh.simplex_atom_indices)[index]
        points = np.asarray(geometry.atom_coordinates)[vertices]
        weights = np.asarray(geometry.atom_radii)[vertices] ** 2
        # Independently solve equal-power equations instead of reusing the
        # kernel's determinant centers. Bulbs print four decimal places.
        center = np.linalg.solve(
            2 * (points[1:] - points[0]),
            np.sum(points[1:] ** 2, axis=1)
            - np.dot(points[0], points[0])
            - weights[1:]
            + weights[0],
        )
        radius = np.sqrt(np.dot(center - points[0], center - points[0]) - weights[0])
        matches = [
            position
            for position, bulb in enumerate(remaining)
            if np.max(np.abs(center - [bulb['c'][axis] for axis in 'xyz']))
            <= 0.000050001
            and abs(radius - bulb['r']) <= 0.000050001
        ]
        assert len(matches) == 1
        remaining.pop(matches[0])
    assert not remaining


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


@pytest.mark.parametrize('modern_void_case', VOID_IDS, indirect=True)
def test_native_void_metrics_reach_topography_with_units(modern_void_case, monkeypatch):
    pdb, geometry, serials, oracle = modern_void_case
    monkeypatch.setattr(_native_impl, 'build_castp_geometry', lambda *a, **k: geometry)
    records, mesh = _native_impl.castp(pdb, radii_model='castp3_protor')
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
