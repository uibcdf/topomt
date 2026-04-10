import importlib
import sys
from pathlib import Path

import molsysmt as msm
import numpy as np
import pytest

from topomt.third_party.pocketeer._native_impl import pocketeer

POCKETEER_REPO = Path.home() / 'repos@others' / 'pocketeer'


@pytest.fixture(scope='module')
def upstream_pocketeer():
    sys.path.insert(0, str(POCKETEER_REPO / 'src'))
    try:
        pocketeer_module = importlib.import_module('pocketeer')
    except ModuleNotFoundError as exc:
        pytest.skip(f"Upstream pocketeer dependency missing: {exc}")
    yield pocketeer_module
    sys.path.remove(str(POCKETEER_REPO / 'src'))


def test_pocketeer_parity_with_upstream(upstream_pocketeer):
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

    molsys = msm.convert(str(pdb_path), to_form='molsysmt.MolSys')
    local_pockets, _ = pocketeer(
        molecular_system=molsys,
        selection='all',
        r_min=3.0,
        r_max=6.0,
        sasa_threshold=20.0,
        merge_distance=1.75,
        min_spheres=35,
        syntax='MolSysMT',
    )

    assert len(local_pockets) >= len(upstream_pockets)
    paired = zip(sorted(local_pockets, key=lambda p: p.score, reverse=True), upstream_pockets)
    for local, upstream in paired:
        local_volume_a3 = local.volume * 1000.0
        if upstream.volume > 0:
            assert abs(local_volume_a3 - upstream.volume) / upstream.volume < 0.6
        assert abs(local.score - upstream.score) < 2.5
        assert local.centroid.shape == upstream.centroid.shape
