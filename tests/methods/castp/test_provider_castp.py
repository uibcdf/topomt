import warnings
import zipfile
from pathlib import Path

import pytest

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt.get_topography import get_topography
from topomt.io.load_CASTp import _parse_mouth_info_file, _parse_poc_info_file
from topomt.provider_output import ProviderRun

SERVER_ZIP = Path('topomt/data/CASTp_3.0_server/1tcd.zip')
FOLD_ZIP = Path('topomt/data/CASTpFold_server/1psn.zip')


def test_castp_mouth_info_n_mth_is_count_not_parent_id(tmp_path):
    with zipfile.ZipFile(SERVER_ZIP) as archive:
        mouth_info = tmp_path / '1tcd.mouthInfo'
        mouth_info.write_bytes(archive.read('1tcd.mouthInfo'))

    parsed = _parse_mouth_info_file(mouth_info)
    assert parsed[2]['n_mouths'] == 3
    assert parsed[2]['pocket_ids'] == {2}


@pytest.mark.parametrize('structure_id', ['1a4j', '1hiv', '1stp', '2pk4', '3ptb'])
def test_castp_mouth_aggregates_match_original_rows(structure_id, tmp_path):
    zip_path = SERVER_ZIP.with_name(f'{structure_id}.zip')
    with zipfile.ZipFile(zip_path) as archive:
        mouth_info = tmp_path / f'{structure_id}.mouthInfo'
        mouth_info.write_bytes(archive.read(f'{structure_id}.mouthInfo'))
        poc_info = tmp_path / f'{structure_id}.pocInfo'
        poc_info.write_bytes(archive.read(f'{structure_id}.pocInfo'))
    expected = {
        mouth_id: row
        for mouth_id, row in _parse_mouth_info_file(mouth_info).items()
        if row['n_mouths'] > 0
    }
    expected_pockets = _parse_poc_info_file(poc_info)
    topography = tmt.third_party.castp.load_topography(zip_file=zip_path)

    surfaces = _castp_surface_features(topography)
    assert len(surfaces) == len(expected_pockets)
    for feature in surfaces:
        source_id = int(feature.source_id.split()[1])
        assert puw.get_value(
            feature.solvent_accessible_area, to_unit='angstroms**2'
        ) == pytest.approx(
            puw.get_value(
                expected_pockets[source_id]['solvent_accessible_area'],
                to_unit='angstroms**2',
            )
        )
    mouths = topography.get_features(by='type', value='mouth')
    assert len(mouths) == len(expected)
    for mouth in mouths:
        source_id = int(mouth.source_id.split()[1])
        assert mouth.n_mouths == expected[source_id]['n_mouths']
        assert mouth.provider_aggregates_multiple_mouths == (mouth.n_mouths > 1)
        assert {
            parent.source_id for parent in topography.parents_of(mouth.feature_id)
        } == {f'Pocket {source_id}'}


def _castp_surface_features(topography):
    feature_types = ('pocket', 'void', 'channel', 'branched_channel')
    features = []
    for feature_type in feature_types:
        features.extend(topography.get_features(by='type', value=feature_type))
    return features


def test_castp_provider_load_topography_reads_server_zip(tmp_path):
    topography = tmt.third_party.castp.load_topography(
        zip_file=SERVER_ZIP,
    )

    assert len(_castp_surface_features(topography)) == 78
    assert len(topography.get_features(by='type', value='mouth')) == 42
    assert len(topography.provider_runs) == 1
    run = next(iter(topography.provider_runs.values()))
    assert run.get_artifact('input/1tcd.zip') == SERVER_ZIP.read_bytes()
    with zipfile.ZipFile(SERVER_ZIP) as archive:
        assert run.get_artifact('output/1tcd.pocInfo') == archive.read('1tcd.pocInfo')
    assert all(
        feature.provider_run_id == run.run_id
        for feature in _castp_surface_features(topography)
    )
    mouth_2 = next(
        mouth
        for mouth in topography.get_features(by='type', value='mouth')
        if mouth.source_id == 'Mouth 2'
    )
    assert mouth_2.n_mouths == 3
    assert {
        parent.source_id for parent in topography.parents_of(mouth_2.feature_id)
    } == {'Pocket 2'}
    pocket_1 = next(
        feature
        for feature in _castp_surface_features(topography)
        if feature.source_id == 'Pocket 1'
    )
    mouth_1 = next(
        mouth
        for mouth in topography.get_features(by='type', value='mouth')
        if mouth.source_id == 'Mouth 1'
    )
    for name, original, unit, normalized, source_field, issue in (
        ('solvent_accessible_area', 57.751, 'angstroms**2', 0.57751, 'Area_sa', 45),
        ('molecular_surface_area', 171.53, 'angstroms**2', 1.7153, 'Area_ms', 46),
        ('solvent_accessible_length', 77.154, 'angstroms', 7.7154, 'Len_sa', 47),
        ('molecular_surface_length', 85.95, 'angstroms', 8.595, 'Len_ms', 48),
    ):
        measurement = mouth_1.external_measurements[name]
        assert measurement.original_value == pytest.approx(original)
        assert measurement.original_unit == unit
        assert measurement.source_artifact == 'output/1tcd.mouthInfo'
        assert measurement.source_field == f'mouthInfo[1].{source_field}'
        assert (
            measurement.issue_url == f'https://github.com/uibcdf/topomt/issues/{issue}'
        )
        assert puw.get_value(getattr(mouth_1, name)) == pytest.approx(normalized)
    for feature, name, original, unit, source_field, issue in (
        (pocket_1, 'length', 234.656, 'angstroms', 'pocInfo[1].Lenth', 49),
        (
            pocket_1,
            'surface_triangles_excluding_mouth_count',
            108,
            '1',
            'pocInfo[1].cnr',
            50,
        ),
        (pocket_1, 'n_mouths', 1, '1', 'pocInfo[1].N_mth', 51),
        (mouth_1, 'n_triangles', 24, '1', 'mouthInfo[1].Ntri', 52),
        (mouth_1, 'n_mouths', 1, '1', 'mouthInfo[1].N_mth', 51),
    ):
        measurement = feature.external_measurements[name]
        assert measurement.original_value == pytest.approx(original)
        assert measurement.original_unit == unit
        assert measurement.source_field == source_field
        assert (
            measurement.issue_url == f'https://github.com/uibcdf/topomt/issues/{issue}'
        )
    assert puw.get_value(pocket_1.length, to_unit='nm') == pytest.approx(23.4656)
    assert all(
        mouth.provider_run_id == run.run_id
        for mouth in topography.get_features(by='type', value='mouth')
    )
    for name, original, unit, normalized, source_field, issue in (
        ('solvent_accessible_area', 283.364, 'angstroms**2', 2.83364, 'Area_sa', 41),
        ('molecular_surface_area', 456.907, 'angstroms**2', 4.56907, 'Area_ms', 42),
        ('solvent_accessible_volume', 165.990, 'angstroms**3', 0.16599, 'Vol_sa', 43),
        ('molecular_surface_volume', 637.990, 'angstroms**3', 0.63799, 'Vol_ms', 44),
    ):
        measurement = pocket_1.external_measurements[name]
        assert measurement.original_value == pytest.approx(original)
        assert measurement.original_unit == unit
        assert measurement.run_id == run.run_id
        assert measurement.source_artifact == 'output/1tcd.pocInfo'
        assert measurement.source_field == f'pocInfo[1].{source_field}'
        assert (
            measurement.issue_url == f'https://github.com/uibcdf/topomt/issues/{issue}'
        )
        assert puw.get_value(getattr(pocket_1, name)) == pytest.approx(normalized)
    bundle = tmp_path / 'castp_run.zip'
    run.save(bundle)
    assert ProviderRun.load(bundle).artifacts == run.artifacts


def test_castpfold_real_zip_uses_job_named_files_and_native_definitions():
    topography = tmt.third_party.castp.load_topography(zip_file=FOLD_ZIP)
    run = next(iter(topography.provider_runs.values()))
    pocket_1 = next(
        feature
        for feature in _castp_surface_features(topography)
        if feature.source_id == 'Pocket 1'
    )
    mouth_1 = next(
        feature
        for feature in topography.get_features(by='type', value='mouth')
        if feature.source_id == 'Mouth 1'
    )

    with zipfile.ZipFile(FOLD_ZIP) as archive:
        names = archive.namelist()
        poc_info_name = next(name for name in names if name.endswith('.pocInfo'))
        mouth_info_name = next(name for name in names if name.endswith('.mouthInfo'))
        contribution_name = next(
            name for name in names if name.endswith('.contrib.csv')
        )
        bulb_name = next(name for name in names if name.endswith('.bulb.json'))
        poc_row = archive.read(poc_info_name).decode().splitlines()[1].split()
        mouth_row = archive.read(mouth_info_name).decode().splitlines()[1].split()
        assert run.get_artifact(f'output/{poc_info_name}') == archive.read(
            poc_info_name
        )
        assert run.get_artifact('output/README.txt') == archive.read('README.txt')
        assert run.get_artifact(f'output/{contribution_name}') == archive.read(
            contribution_name
        )
        assert run.get_artifact(f'output/{bulb_name}') == archive.read(bulb_name)
    assert len(_castp_surface_features(topography)) == 41
    assert pocket_1.provider_run_id == run.run_id
    assert pocket_1.surface_triangles_excluding_mouth_count == int(poc_row[9])
    assert pocket_1.corner_points_count is None
    assert (
        pocket_1.external_measurements[
            'surface_triangles_excluding_mouth_count'
        ].source_field
        == 'pocInfo[1].cnr'
    )
    assert (
        'surface triangles excluding the mouth triangles'
        in pocket_1.external_measurements[
            'surface_triangles_excluding_mouth_count'
        ].definition.lower()
    )
    assert puw.get_value(pocket_1.length, to_unit='angstroms') == pytest.approx(
        float(poc_row[8])
    )
    assert pocket_1.external_measurements['length'].source_artifact == (
        f'output/{poc_info_name}'
    )
    assert puw.get_value(mouth_1.solvent_accessible_area, to_unit='angstroms**2') == (
        pytest.approx(float(mouth_row[4]))
    )
    assert mouth_1.n_mouths == int(mouth_row[3])


def test_castp_provider_server_castpfold_loads_server_zip(monkeypatch, tmp_path):
    server_module = __import__(
        'topomt.third_party.castp.servers.castpfold',
        fromlist=['CastpFoldClient'],
    )

    submitted = {}

    def fake_submit(self, pdb_path, **kwargs):
        submitted['pdb_path'] = Path(pdb_path)
        submitted['pdb_bytes'] = Path(pdb_path).read_bytes()
        submitted['kwargs'] = kwargs
        return 'j_mock'

    def fake_download(self, jobid, **kwargs):
        submitted['jobid'] = jobid
        submitted['download_kwargs'] = kwargs
        return SERVER_ZIP.read_bytes()

    monkeypatch.setattr(server_module.CastpFoldClient, 'submit', fake_submit)
    monkeypatch.setattr(
        server_module.CastpFoldClient,
        'download_result_zip_bytes',
        fake_download,
    )

    topography = tmt.third_party.castp.get_topography(
        tmt.demo['TcTIM']['1tcd.pdb'],
        backend='server',
        server='castpfold',
        probe_radius=1.4,
        email='N/A',
        wait=0,
        extra_wait=0,
        retries=0,
        output_zip_file=tmp_path / 'castpfold.zip',
    )

    assert submitted['pdb_path'].suffix == '.pdb'
    assert submitted['kwargs']['email'] == 'N/A'
    assert (tmp_path / 'castpfold.zip').read_bytes() == SERVER_ZIP.read_bytes()
    assert len(_castp_surface_features(topography)) == 78
    assert len(topography.get_features(by='type', value='mouth')) == 42
    run = next(iter(topography.provider_runs.values()))
    assert run.get_artifact('input/1tcd.pdb') == submitted['pdb_bytes']
    assert (
        run.get_artifact('output/raw_server_zip/castpfold.zip')
        == SERVER_ZIP.read_bytes()
    )
    assert run.metadata['server'] == 'castpfold'
    assert run.metadata['jobid'] == 'j_mock'


def test_get_topography_castp_server_routes_without_digest_warnings(monkeypatch):
    api_module = __import__(
        'topomt.third_party.castp.api',
        fromlist=['get_topography'],
    )

    def fake_provider(molecular_system, **kwargs):
        return tmt.Topography(molecular_system=molecular_system)

    monkeypatch.setattr(api_module, 'get_topography', fake_provider)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        topo = get_topography(
            tmt.demo['TcTIM']['1tcd.pdb'],
            method='castp',
            backend='server',
            server='castpfold',
            probe_radius=1.4,
            email='N/A',
            wait=0,
            extra_wait=0,
            retries=0,
        )

    assert isinstance(topo, tmt.Topography)
    assert not any(
        type(item.message).__name__ == 'DigestNotDigestedWarning' for item in caught
    )


def test_get_topography_castpfold_kept_as_compatibility_alias(monkeypatch):
    api_module = __import__(
        'topomt.third_party.castp.api',
        fromlist=['get_topography'],
    )

    called = {}

    def fake_provider(molecular_system, **kwargs):
        called['kwargs'] = kwargs
        return tmt.Topography(molecular_system=molecular_system)

    monkeypatch.setattr(api_module, 'get_topography', fake_provider)

    topo = get_topography(
        tmt.demo['TcTIM']['1tcd.pdb'],
        method='castpfold',
        probe_radius=1.4,
        email='N/A',
        wait=0,
        extra_wait=0,
        retries=0,
    )

    assert isinstance(topo, tmt.Topography)
    assert called['kwargs']['backend'] == 'server'
    assert called['kwargs']['server'] == 'castpfold'


def test_castp_provider_server_castp3_loads_server_zip(monkeypatch, tmp_path):
    server_module = __import__(
        'topomt.third_party.castp.servers.castp3',
        fromlist=['Castp3Client'],
    )

    submitted = {}

    def fake_submit(self, pdb_path, **kwargs):
        submitted['pdb_path'] = Path(pdb_path)
        submitted['kwargs'] = kwargs
        return 'j_mock_castp3'

    def fake_download(self, jobid, **kwargs):
        submitted['jobid'] = jobid
        submitted['download_kwargs'] = kwargs
        return SERVER_ZIP.read_bytes()

    monkeypatch.setattr(server_module.Castp3Client, 'submit', fake_submit)
    monkeypatch.setattr(
        server_module.Castp3Client,
        'download_result_zip_bytes',
        fake_download,
    )

    topography = tmt.third_party.castp.get_topography(
        tmt.demo['TcTIM']['1tcd.pdb'],
        backend='server',
        server='castp3',
        probe_radius=1.4,
        email='null',
        wait=0,
        extra_wait=0,
        retries=0,
        output_zip_file=tmp_path / 'castp3.zip',
    )

    assert submitted['pdb_path'].suffix == '.pdb'
    assert submitted['kwargs']['email'] == 'null'
    assert (tmp_path / 'castp3.zip').read_bytes() == SERVER_ZIP.read_bytes()
    assert len(_castp_surface_features(topography)) == 78
    assert len(topography.get_features(by='type', value='mouth')) == 42


def test_get_topography_castp3_kept_as_compatibility_alias(monkeypatch):
    api_module = __import__(
        'topomt.third_party.castp.api',
        fromlist=['get_topography'],
    )

    called = {}

    def fake_provider(molecular_system, **kwargs):
        called['kwargs'] = kwargs
        return tmt.Topography(molecular_system=molecular_system)

    monkeypatch.setattr(api_module, 'get_topography', fake_provider)

    topo = get_topography(
        tmt.demo['TcTIM']['1tcd.pdb'],
        method='castp3',
        probe_radius=1.4,
        email='null',
        wait=0,
        extra_wait=0,
        retries=0,
    )

    assert isinstance(topo, tmt.Topography)
    assert called['kwargs']['backend'] == 'server'
    assert called['kwargs']['server'] == 'castp3'
