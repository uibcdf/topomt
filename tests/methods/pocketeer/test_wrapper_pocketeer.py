import importlib
import sys
from pathlib import Path

import pytest

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


def test_pocketeer_wrapper_matches_upstream_reference(upstream_pocketeer):
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

    wrapper_topography = get_topography(
        str(pdb_path),
        method='pocketeer',
        implementation='wrapper',
        upstream_root=str(POCKETEER_REPO / 'src'),
        r_min=3.0,
        r_max=6.0,
        polar_probe_radius=1.4,
        sasa_threshold=20.0,
        merge_distance=1.75,
        min_spheres=35,
    )
    wrapper_pockets = _pocket_features(wrapper_topography)

    assert len(wrapper_pockets) == len(upstream_pockets)

    for wrapper_pocket, upstream_pocket in zip(wrapper_pockets[:5], upstream_pockets[:5]):
        assert puw.get_value(wrapper_pocket.volume, to_unit='nm**3') == pytest.approx(
            upstream_pocket.volume / 1000.0
        )
        assert wrapper_pocket.score == pytest.approx(upstream_pocket.score)
        assert len(puw.get_value(wrapper_pocket.alpha_sphere_radii, to_unit='nm')) == len(
            upstream_pocket.spheres
        )
