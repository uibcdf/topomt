"""Consumer contracts over original provider results, independent of DFND."""

import importlib
import json
import shutil
import subprocess
import sys
import zipfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np
import pytest

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt.features import Pocket
from topomt.provider_output import ProviderRun

ROOT = Path(tmt.__file__).parent
FP_PDB = ROOT / 'data/fpocket4/sample/3LKF.pdb'
FP_OUT = ROOT / 'data/fpocket4/sample/3LKF_out'
CASTP_ZIP = ROOT / 'data/CASTp_3.0_server/1tcd.zip'


def test_fpocket_output_preserves_original_fields_and_consumer_geometry(tmp_path):
    result = tmt.get_provider_output(
        FP_PDB,
        method='fpocket',
        backend='files',
        pdb_file=FP_PDB,
        output_dir=FP_OUT,
    )
    assert type(result).__name__ == 'FpocketOutput'
    assert result.schema_version == 1
    assert len(result.pockets) == 7
    assert [p.source_id for p in result.pockets] == [
        f'fpocket:{i}' for i in range(1, 8)
    ]
    pocket = result.pockets[0]
    assert pocket.record_kind == 'pocket'
    assert pocket.run_id == result.run.run_id
    assert pocket.fields['score'] == pytest.approx(33.9933)
    measurement = pocket.measurements['volume']
    assert measurement.original_value == pytest.approx(645.303)
    assert puw.get_value(measurement.value, to_unit='angstroms**3') == pytest.approx(
        645.303
    )
    assert measurement.definition and measurement.source_artifact.endswith('_info.txt')
    spheres = pocket.geometries['alpha_spheres']
    # This fixture uses zero-based filenames but one-based reported pocket IDs.
    assert (
        pocket.fields['alpha_sphere_source_artifact']
        == 'output/pockets/pocket0_vert.pqr'
    )
    pqr = FP_OUT / 'pockets/pocket0_vert.pqr'
    first = next(
        line for line in pqr.read_text().splitlines() if line.startswith('ATOM')
    )
    expected = [float(first[start : start + 8]) for start in (30, 38, 46)]
    assert puw.get_value(spheres.coordinates, to_unit='angstroms')[0] == pytest.approx(
        expected
    )
    assert len(puw.get_value(spheres.radii, to_unit='nm')) == 76
    assert 'member_atoms' in pocket.geometries
    assert 'exact_region' not in pocket.geometries
    assert not hasattr(pocket, 'topography')
    bundle = tmp_path / 'original.zip'
    result.run.save(bundle)
    assert (
        ProviderRun.load(bundle).get_artifact('input/3LKF.pdb') == FP_PDB.read_bytes()
    )
    # Consumer-returned dictionaries and quantities cannot alter the retained result.
    pocket.fields['provider_raw_fields'].clear()
    pocket.measurements.clear()
    coordinates = spheres.coordinates
    puw.get_value(coordinates)[0, 0] = 10000.0
    assert pocket.fields['provider_raw_fields']
    assert pocket.measurements
    assert puw.get_value(spheres.coordinates, to_unit='angstroms')[0] == pytest.approx(
        expected
    )


def test_fpocket_output_survives_temporary_input_and_output_removal(tmp_path):
    pdb = tmp_path / FP_PDB.name
    shutil.copy2(FP_PDB, pdb)
    out = tmp_path / FP_OUT.name
    shutil.copytree(FP_OUT, out)
    result = tmt.third_party.fpocket.get_output(
        pdb,
        backend='files',
        pdb_file=pdb,
        output_dir=out,
    )
    shutil.rmtree(out)
    pdb.unlink()
    assert result.run.get_artifact('input/3LKF.pdb') == FP_PDB.read_bytes()
    assert result.pockets[0].geometries['member_atoms'].coordinates.shape[1] == 3
    assert result.input_coordinates.shape[1] == 3


def test_castp_output_preserves_all_reported_pockets_and_aggregate_relationships():
    result = tmt.get_provider_output(
        method='castp', backend='files', zip_file=CASTP_ZIP
    )
    assert type(result).__name__ == 'CASTpOutput'
    assert len(result.pockets) == 78  # Includes legacy void/channel classifications.
    assert len(result.records) == 120
    assert result.run.get_artifact('input/1tcd.zip') == CASTP_ZIP.read_bytes()
    aggregate = next(r for r in result.records if r.source_id == 'Mouth 2')
    assert aggregate.record_kind == 'mouth_aggregate'
    assert aggregate.fields['n_mouths'] == 3
    assert aggregate.parent_source_ids == ('Pocket 2',)
    assert 'exact_region' not in aggregate.geometries
    assert (
        next(p for p in result.pockets if p.source_id == 'Pocket 2').record_kind
        == 'pocket'
    )


def test_castp_output_remaps_selected_server_atoms_to_source(tmp_path, monkeypatch):
    import molsysmt as msm

    from topomt.third_party.castp import api

    selected_indices = [10, 12, 14, 18]
    selected = msm.convert(
        FP_PDB, selection=selected_indices, to_form='molsysmt.MolSys'
    )
    out = tmp_path / 'output'
    out.mkdir()
    run = ProviderRun.capture(
        'castp',
        'server',
        FP_PDB,
        out,
        metadata={'selected_atom_indices': selected_indices},
    )
    topography = tmt.Topography(molecular_system=selected)
    topography.add_provider_run(run)
    topography.add_feature(
        Pocket(
            source='CASTp',
            source_id='Pocket 1',
            provider_run_id=run.run_id,
            atom_indices=[0, 2],
        )
    )
    monkeypatch.setattr(api, 'get_topography', lambda *args, **kwargs: topography)
    result = api.get_output(FP_PDB, selection=selected_indices)
    assert result.pockets[0].atom_indices == (10, 14)
    coordinates = puw.get_value(result.input_coordinates, to_unit='nm')
    assert len(coordinates) > len(selected_indices)
    assert puw.get_value(
        result.pockets[0].geometries['member_atoms'].coordinates, to_unit='nm'
    ) == pytest.approx(coordinates[[10, 14]])


@pytest.mark.parametrize(
    'server,client_name',
    [
        ('castp3', 'Castp3Client'),
        ('castpfold', 'CastpFoldClient'),
    ],
)
def test_castp_original_server_output_with_mocked_transport(
    server, client_name, monkeypatch
):
    module = importlib.import_module(f'topomt.third_party.castp.servers.{server}')
    client = getattr(module, client_name)
    submitted = {}

    def submit(self, pdb_path, **kwargs):
        submitted['input'] = Path(pdb_path).read_bytes()
        return 'fixture_job'

    monkeypatch.setattr(client, 'submit', submit)
    monkeypatch.setattr(
        client,
        'download_result_zip_bytes',
        lambda *args, **kwargs: CASTP_ZIP.read_bytes(),
    )
    result = tmt.get_provider_output(tmt.demo['TcTIM']['1tcd.pdb'], method=server)
    assert len(result.pockets) == 78
    assert result.run.backend == 'server'
    assert result.run.metadata['server'] == server
    assert result.run.metadata['structure_indices'] == [0]
    assert result.run.metadata['selected_atom_indices'] == list(
        range(len(result.input_points_nm))
    )
    assert result.run.get_artifact('input/1tcd.pdb') == submitted['input']


def test_output_geometry_respects_consumer_unit_policy():
    code = """
import pyunitwizard as puw
puw.configure.set_default_form('pint')
puw.configure.set_default_parser('pint')
puw.configure.set_standard_units(['angstroms'], provenance='consumer-test')
from topomt.third_party.output import PocketGeometry
geometry = PocketGeometry('sites', ((1., 2., 3.),), 'Provider sites', (0.2,))
assert puw.configure.report()['provenance'] == 'consumer-test'
assert puw.get_value(geometry.coordinates, to_unit='angstroms').tolist() == [[10., 20., 30.]]
assert puw.get_value(geometry.radii, to_unit='angstroms').tolist() == [2.]
"""
    result = subprocess.run(
        [sys.executable, '-c', code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    'provider,class_name,backend',
    [
        ('fpocket', 'FpocketOutput', 'cli'),
        ('pocketeer', 'PocketeerOutput', 'library'),
        ('alphaspace2', 'AlphaSpace2Output', 'library'),
        ('pycasta', 'PyCASTAOutput', 'library'),
        ('castp', 'CASTpOutput', 'server'),
    ],
)
def test_output_detaches_from_legacy_registry(
    provider, class_name, backend, tmp_path, monkeypatch
):
    module = importlib.import_module(f'topomt.third_party.{provider}.api')
    input_pdb = tmp_path / 'input.pdb'
    input_pdb.write_text('END\n')
    out = tmp_path / 'output'
    out.mkdir()
    run = ProviderRun.capture(provider, backend, input_pdb, out)
    topo = tmt.Topography()
    topo.add_provider_run(run)
    feature = Pocket(
        source=provider,
        source_id='upstream:17',
        provider_run_id=run.run_id,
        atom_indices=[],
        custom={'array': np.array([1.0, 2.0])},
    )
    topo.add_feature(feature)
    monkeypatch.setattr(module, 'get_topography', lambda *args, **kwargs: topo)
    result = module.get_output(None)
    assert type(result).__name__ == class_name
    feature.custom['array'][0] = 100
    topo.remove_feature(feature.feature_id)
    assert result.pockets[0].fields['custom']['array'].tolist() == [1.0, 2.0]
    assert result.pockets[0].source_id == 'upstream:17'
    assert result.pockets[0].geometries == {}
    assert result.input_coordinates is None


@pytest.mark.parametrize('method', ['dfnd', 'unknown'])
def test_new_output_api_rejects_nonprovider_methods(method):
    with pytest.raises(ValueError, match='method'):
        tmt.get_provider_output(method=method)


@pytest.mark.parametrize(
    'method', ['fpocket', 'pocketeer', 'alphaspace2', 'pycasta', 'castp']
)
def test_new_output_api_does_not_silently_run_local_reproductions(method):
    with pytest.raises(ValueError, match='backend'):
        tmt.get_provider_output(method=method, backend='native')


def test_source_atom_mapping_for_selected_fpocket_input(monkeypatch):
    from topomt.third_party.fpocket import files

    original = object()
    selected = object()
    calls = []
    monkeypatch.setattr(
        files, 'Topography', lambda **kwargs: type('T', (), {'_molsys': selected})()
    )
    monkeypatch.setattr(
        files,
        '_build_serial_to_atom_index_map',
        lambda molecular_system, **kwargs: calls.append(molecular_system) or {7: 5},
    )
    _, mapping = files._build_topography_and_atom_map(
        original, selection='chain_id=="B"'
    )
    assert calls == [original]
    assert mapping == {7: 5}


def test_pocketeer_residue_membership_is_not_geometric_lining(tmp_path, monkeypatch):
    from topomt.third_party.pocketeer import api

    out = tmp_path / 'output'
    out.mkdir()
    run = ProviderRun.capture('pocketeer', 'library', FP_PDB, out)
    topography = tmt.Topography(molecular_system=FP_PDB)
    topography.add_provider_run(run)
    topography.add_feature(
        Pocket(
            source='pocketeer',
            source_id='pocketeer:1',
            provider_run_id=run.run_id,
            atom_indices=list(range(10)),
            alpha_sphere_defining_atom_indices=[[1, 3, 5, 7]],
        )
    )
    monkeypatch.setattr(api, 'get_topography', lambda *args, **kwargs: topography)
    pocket = api.get_output(FP_PDB).pockets[0]
    assert pocket.atom_role == 'pocket_residue_atoms'
    assert pocket.atom_indices == tuple(range(10))
    members = pocket.geometries['member_atoms']
    lining = pocket.geometries['lining_atoms']
    assert len(members.points_nm) == 10
    assert len(lining.points_nm) == 4
    assert 'sphere-defining' in lining.definition


@pytest.mark.parametrize(
    'points,radii',
    [
        (((float('nan'), 0.0, 0.0),), None),
        (((0.0, 0.0, 0.0),), (-1.0,)),
        (((0.0, 0.0, 0.0),), (1.0, 2.0)),
        (((0.0, 0.0),), None),
    ],
)
def test_consumer_geometry_rejects_invalid_coordinates_and_radii(points, radii):
    from topomt.third_party.output import PocketGeometry

    with pytest.raises(ValueError):
        PocketGeometry('alpha_spheres', points, 'Reported spheres', radii)


def test_geometry_has_explicit_units_and_converts_lengths():
    from topomt.third_party.output import PocketGeometry

    geometry = PocketGeometry(
        'alpha_spheres', ((1.0, 2.0, 3.0),), 'Reported spheres', (0.2,)
    )
    assert puw.get_value(geometry.coordinates, to_unit='angstroms').tolist() == [
        [10.0, 20.0, 30.0]
    ]
    assert puw.get_value(geometry.radii, to_unit='angstroms').tolist() == [2.0]


@pytest.mark.parametrize('provider', ['pocketeer', 'alphaspace2', 'pycasta'])
def test_installed_engine_produces_consumer_output(provider, tmp_path):
    try:
        version(provider)
    except PackageNotFoundError:
        pytest.skip(f'optional engine {provider} is not installed')
    pdb = tmp_path / '2pk4.pdb'
    with zipfile.ZipFile(ROOT / 'data/CASTpFold_server/2pk4.zip') as archive:
        pdb.write_bytes(archive.read('2pk4.pdb'))
    result = tmt.get_provider_output(pdb, method=provider)
    assert result.run.backend == 'library'
    assert result.pockets
    assert result.run.get_artifact('input/2pk4.pdb') == pdb.read_bytes()
    assert all(p.measurements and p.geometries['member_atoms'] for p in result.pockets)
    if provider == 'alphaspace2':
        state = json.loads(result.run.get_artifact('output/topomt_snapshot.json'))
        assert state['_alpha_xyz']


@pytest.mark.skipif(
    shutil.which('fpocket') is None, reason='optional fpocket executable absent'
)
def test_fpocket_cli_produces_consumer_output():
    result = tmt.get_provider_output(FP_PDB, method='fpocket')
    assert result.run.backend == 'cli'
    assert result.pockets
    assert result.run.get_artifact('output/3LKF_info.txt')
