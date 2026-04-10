import importlib
import warnings
from pathlib import Path
import sys

import pytest

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt.get_topography import get_topography


POCKETEER_REPO = Path.home() / 'repos@others' / 'pocketeer'


@pytest.fixture(scope='module')
def upstream_pocketeer():
    repo_src = POCKETEER_REPO / 'src'
    if not repo_src.exists():
        pytest.skip('local pocketeer upstream mirror is not available')

    sys.path.insert(0, str(repo_src))
    try:
        yield importlib.import_module('pocketeer')
    finally:
        sys.path.remove(str(repo_src))


def _pocket_features(topography):
    return sorted(
        topography.get_features(by='type', value='pocket'),
        key=lambda pocket: pocket.score,
        reverse=True,
    )


def test_pocketeer_provider_library_matches_upstream_reference(upstream_pocketeer):
    pdb_path = POCKETEER_REPO / 'tests' / 'data' / '6qrd.pdb'
    atomarray = upstream_pocketeer.load_structure(str(pdb_path))
    upstream_pockets = upstream_pocketeer.find_pockets(
        atomarray,
        r_min=3.0,
        r_max=6.0,
        polar_probe_radius=1.4,
        sasa_threshold=20.0,
        merge_distance=1.75,
        min_spheres=35,
        ignore_hydrogens=True,
        ignore_water=True,
        ignore_hetero=True,
    )

    provider_topography = tmt.third_party.pocketeer.get_topography(
        str(pdb_path),
        backend='library',
        upstream_root=str(POCKETEER_REPO / 'src'),
        r_min=3.0,
        r_max=6.0,
        polar_probe_radius=1.4,
        sasa_threshold=20.0,
        merge_distance=1.75,
        min_spheres=35,
    )
    provider_pockets = _pocket_features(provider_topography)

    assert len(provider_pockets) == len(upstream_pockets)

    for provider_pocket, upstream_pocket in zip(provider_pockets[:5], upstream_pockets[:5]):
        assert puw.get_value(provider_pocket.volume, to_unit='nm**3') == pytest.approx(
            upstream_pocket.volume / 1000.0
        )
        assert provider_pocket.score == pytest.approx(upstream_pocket.score)


def test_get_topography_pocketeer_routes_without_digest_warnings(monkeypatch):
    provider_module = __import__(
        'topomt.third_party.pocketeer.api',
        fromlist=['get_topography'],
    )

    def fake_provider(molecular_system, **kwargs):
        return tmt.Topography(molecular_system=molecular_system)

    monkeypatch.setattr(provider_module, 'get_topography', fake_provider)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        topo = get_topography(
            tmt.demo['TcTIM']['1tcd.pdb'],
            method='pocketeer',
            implementation='wrapper',
            upstream_root='/tmp/pocketeer',
            r_min=3.0,
            r_max=6.0,
            polar_probe_radius=1.4,
            sasa_threshold=20.0,
            merge_distance=1.75,
            min_spheres=35,
        )

    assert isinstance(topo, tmt.Topography)
    assert not any(type(item.message).__name__ == 'DigestNotDigestedWarning' for item in caught)
