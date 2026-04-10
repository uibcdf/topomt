from pathlib import Path
import warnings

import topomt as tmt
from topomt.get_topography import get_topography


SERVER_ZIP = Path('topomt/data/CASTp_3.0_server/1tcd.zip')


def _castp_surface_features(topography):
    feature_types = ('pocket', 'void', 'channel', 'branched_channel')
    features = []
    for feature_type in feature_types:
        features.extend(topography.get_features(by='type', value=feature_type))
    return features


def test_castp_provider_load_topography_reads_server_zip():
    topography = tmt.third_party.castp.load_topography(
        zip_file=SERVER_ZIP,
    )

    assert len(_castp_surface_features(topography)) == 78
    assert len(topography.get_features(by='type', value='mouth')) == 42


def test_castp_provider_server_castpfold_loads_server_zip(monkeypatch):
    server_module = __import__(
        'topomt.third_party.castp.servers.castpfold',
        fromlist=['CastpFoldClient'],
    )

    submitted = {}

    def fake_submit(self, pdb_path, **kwargs):
        submitted['pdb_path'] = Path(pdb_path)
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
    )

    assert submitted['pdb_path'].suffix == '.pdb'
    assert submitted['kwargs']['email'] == 'N/A'
    assert len(_castp_surface_features(topography)) == 78
    assert len(topography.get_features(by='type', value='mouth')) == 42


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
    assert not any(type(item.message).__name__ == 'DigestNotDigestedWarning' for item in caught)


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


def test_castp_provider_server_castp3_loads_server_zip(monkeypatch):
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
    )

    assert submitted['pdb_path'].suffix == '.pdb'
    assert submitted['kwargs']['email'] == 'null'
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
