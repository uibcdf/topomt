import importlib
import sys
from pathlib import Path

import mdtraj as md
import pytest

from topomt import pyunitwizard as puw
from topomt.get_topography import get_topography
from topomt.third_party.alphaspace2.library import (
    _patch_alphaspace2_mdtraj_sasa,
    _patch_alphaspace2_numpy_compatibility,
)


UPSTREAM_REPO = Path.home() / 'repos@others' / 'AlphaSpace2'
TEST_PDB = Path('topomt/data/fpocket4/sample/1GG0.pdb')


def _import_upstream_alphaspace2():
    if not UPSTREAM_REPO.exists():
        pytest.skip('local AlphaSpace2 upstream mirror is not available')

    if str(UPSTREAM_REPO) not in sys.path:
        sys.path.insert(0, str(UPSTREAM_REPO))

    module = importlib.import_module('alphaspace2')
    _patch_alphaspace2_numpy_compatibility()
    _patch_alphaspace2_mdtraj_sasa(module)
    return module


def _pocket_features(topography):
    return sorted(
        topography.get_features(by='type', value='pocket'),
        key=lambda pocket: int(pocket.source_id.split(':')[-1]),
    )


def test_alphaspace2_wrapper_matches_upstream_snapshot_on_reference_system():
    upstream = _import_upstream_alphaspace2()
    receptor = md.load(str(TEST_PDB))
    snapshot = upstream.Snapshot()
    snapshot.run(receptor)

    min_vertices = 20
    wrapper_topography = get_topography(
        str(TEST_PDB),
        method='alphaspace2',
        implementation='wrapper',
        upstream_root=str(UPSTREAM_REPO),
        min_vertices=min_vertices,
    )
    wrapper_pockets = _pocket_features(wrapper_topography)
    upstream_pockets = [
        pocket for pocket in snapshot.pockets if len(pocket.alpha_index) >= min_vertices
    ]

    assert len(wrapper_pockets) == len(upstream_pockets)

    for wrapper_pocket, upstream_pocket in zip(wrapper_pockets[:5], upstream_pockets[:5]):
        assert puw.get_value(wrapper_pocket.volume, to_unit='nm**3') == pytest.approx(
            upstream_pocket.space / 1000.0
        )
        assert wrapper_pocket.score == pytest.approx(upstream_pocket.score)
        assert len(puw.get_value(wrapper_pocket.alpha_sphere_radii, to_unit='nm')) == len(
            upstream_pocket.alpha_index
        )


def test_alphaspace2_wrapper_smoke_on_demo_system():
    wrapper_topography = get_topography(
        str(TEST_PDB),
        method='alphaspace2',
        implementation='wrapper',
        upstream_root=str(UPSTREAM_REPO),
        min_vertices=20,
    )

    assert len(wrapper_topography.get_features(by='type', value='pocket')) > 0
