"""Integration checks against installed distributions, without source checkouts."""

import importlib
import json
import subprocess
import sys
import zipfile
from importlib.metadata import PackageNotFoundError, distribution
from importlib.util import find_spec
from pathlib import Path

import numpy as np
import pytest

import topomt as tmt
from topomt import pyunitwizard as puw


def _require_distribution(name):
    try:
        installed = distribution(name)
    except PackageNotFoundError:
        pytest.skip(f'optional distribution {name} is not installed')
    spec = find_spec(name)
    expected_init = Path(installed.locate_file(f'{name}/__init__.py')).resolve()
    if spec is not None and spec.origin is not None:
        if Path(spec.origin).resolve() != expected_init:
            pytest.skip(
                'source checkout shadows installed engine; run this module in a fresh process'
            )
    return installed.version


@pytest.fixture
def protein_pdb(tmp_path):
    archive = Path(tmt.__file__).parent / 'data' / 'CASTpFold_server' / '2pk4.zip'
    pdb = tmp_path / '2pk4.pdb'
    with zipfile.ZipFile(archive) as files:
        pdb.write_bytes(files.read('2pk4.pdb'))
    return pdb


def test_installed_pocketeer_matches_direct_library(protein_pdb):
    _require_distribution('pocketeer')
    upstream = importlib.import_module('pocketeer')
    expected = upstream.find_pockets(upstream.load_structure(str(protein_pdb)))
    topography = tmt.third_party.pocketeer.get_topography(
        str(protein_pdb), backend='library'
    )
    pockets = list(topography.get_features(by='type', value='pocket'))
    assert len(pockets) == len(expected)
    assert expected
    references = {f'pocketeer:{pocket.pocket_id}': pocket for pocket in expected}
    for actual in pockets:
        reference = references[actual.source_id]
        assert actual.score == pytest.approx(reference.score)
        assert puw.get_value(actual.volume, to_unit='angstroms**3') == pytest.approx(
            reference.volume
        )
        assert actual.atom_indices == np.flatnonzero(reference.mask).tolist()


def test_installed_alphaspace2_matches_direct_snapshot(protein_pdb):
    _require_distribution('alphaspace2')
    import mdtraj

    from topomt.third_party.alphaspace2.library import (
        _patch_alphaspace2_mdtraj_sasa,
        _patch_alphaspace2_numpy_compatibility,
    )

    upstream = importlib.import_module('alphaspace2')
    _patch_alphaspace2_numpy_compatibility()
    _patch_alphaspace2_mdtraj_sasa(upstream)
    snapshot = upstream.Snapshot()
    snapshot.run(mdtraj.load(str(protein_pdb)))
    expected = [pocket for pocket in snapshot.pockets if len(pocket.alpha_index) >= 20]
    topography = tmt.third_party.alphaspace2.get_topography(
        str(protein_pdb), backend='library'
    )
    pockets = list(topography.get_features(by='type', value='pocket'))
    assert len(pockets) == len(expected)
    assert expected
    run = next(iter(topography.provider_runs.values()))
    state = json.loads(run.get_artifact('output/topomt_snapshot.json'))
    assert np.asarray(state['_alpha_xyz']) == pytest.approx(snapshot._alpha_xyz)
    assert np.asarray(state['_beta_scores']) == pytest.approx(snapshot._beta_scores)


def test_installed_pycasta_matches_direct_process(protein_pdb, tmp_path):
    _require_distribution('pycasta')
    script = """
import importlib.util
import json
from pathlib import Path
import sys
spec = importlib.util.find_spec('pycasta')
sys.path.insert(0, next(iter(spec.submodule_search_locations)))
import run_analysis
result = run_analysis.process_pdb(sys.argv[1])
Path(sys.argv[2]).write_text(json.dumps(result, allow_nan=True))
"""
    result_path = tmp_path / 'direct.json'
    execution = subprocess.run(
        [sys.executable, '-c', script, str(protein_pdb), str(result_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert execution.returncode == 0, execution.stderr
    expected = json.loads(result_path.read_text())
    before = set(sys.modules)
    topography = tmt.third_party.pycasta.get_topography(
        str(protein_pdb), backend='library'
    )
    assert not {'run_analysis', 'config', 'pocket_detection'} & (
        set(sys.modules) - before
    )
    pockets = list(topography.get_features(by='type', value='pocket'))
    assert len(pockets) == len(expected['ranked_pockets'])
    assert pockets
    for pocket in pockets:
        index = int(pocket.source_id.split(':')[-1])
        assert pocket.score == pytest.approx(expected['ranking_scores'][index])
        assert puw.get_value(pocket.volume, to_unit='angstroms**3') == pytest.approx(
            expected['pocket_volumes'][index]
        )
    run = next(iter(topography.provider_runs.values()))
    recorded = json.loads(run.get_artifact('output/topomt_returned_result.json'))
    assert recorded['ranked_pockets'] == expected['ranked_pockets']
    assert run.get_artifact('input/2pk4.pdb') == protein_pdb.read_bytes()
