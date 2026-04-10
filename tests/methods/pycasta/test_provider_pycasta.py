from pathlib import Path
import sys
import warnings

import pytest

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt.get_topography import get_topography


UPSTREAM_ROOT = Path('/home/diego/repos@others/pycasta/src/pycasta')
BOUND_DIR = UPSTREAM_ROOT / 'data' / 'bounded'


def _load_upstream_pycasta():
    if not UPSTREAM_ROOT.exists():
        pytest.skip('local pycasta upstream mirror is not available')

    if str(UPSTREAM_ROOT) not in sys.path:
        sys.path.insert(0, str(UPSTREAM_ROOT))

    import run_analysis  # noqa: PLC0415

    return run_analysis


def _pocket_features(topography):
    return sorted(
        topography.get_features(by='type', value='pocket'),
        key=lambda pocket: pocket.score,
        reverse=True,
    )


def test_pycasta_provider_library_matches_upstream_reference_for_2pk4():
    run_analysis = _load_upstream_pycasta()
    pdb_path = BOUND_DIR / '2pk4.pdb'
    upstream = run_analysis.process_pdb(str(pdb_path))

    provider_topography = tmt.third_party.pycasta.get_topography(
        str(pdb_path),
        backend='library',
        upstream_root=str(UPSTREAM_ROOT),
    )
    provider_pockets = _pocket_features(provider_topography)

    assert len(provider_pockets) == len(upstream['ranked_pockets']) == 1
    assert puw.get_value(provider_pockets[0].volume, to_unit='nm**3') == pytest.approx(
        upstream['pocket_volumes'][0] / 1000.0
    )


def test_get_topography_pycasta_routes_without_digest_warnings(monkeypatch):
    provider_module = __import__(
        'topomt.third_party.pycasta.api',
        fromlist=['get_topography'],
    )

    def fake_provider(molecular_system, **kwargs):
        return tmt.Topography(molecular_system=molecular_system)

    monkeypatch.setattr(provider_module, 'get_topography', fake_provider)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        topo = get_topography(
            tmt.demo['TcTIM']['1tcd.pdb'],
            method='pycasta',
            implementation='wrapper',
            upstream_root='/tmp/pycasta',
        )

    assert isinstance(topo, tmt.Topography)
    assert not any(type(item.message).__name__ == 'DigestNotDigestedWarning' for item in caught)
