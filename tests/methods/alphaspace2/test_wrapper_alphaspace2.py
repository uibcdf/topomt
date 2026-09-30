import importlib
import json
from pathlib import Path

import numpy as np
import pytest

from topomt import pyunitwizard as puw
from topomt.get_topography import get_topography
from topomt.provider_output import ProviderRun
from topomt.third_party._common import import_upstream_module
from topomt.third_party.alphaspace2.library import (
    _initialize_unbound_contacts,
    _patch_alphaspace2_mdtraj_sasa,
    _patch_alphaspace2_numpy_compatibility,
)

UPSTREAM_REPO = Path.home() / 'repos@others' / 'AlphaSpace2'
TEST_PDB = Path('topomt/data/fpocket4/sample/1GG0.pdb')


@pytest.fixture
def upstream_alphaspace2():
    try:
        md = importlib.import_module('mdtraj')
    except ModuleNotFoundError as exc:
        if exc.name != 'mdtraj':
            raise
        pytest.skip('optional MDTraj library is not installed')
    if not UPSTREAM_REPO.exists():
        pytest.skip('local AlphaSpace2 upstream mirror is not available')

    module = import_upstream_module('alphaspace2', upstream_root=UPSTREAM_REPO)
    _patch_alphaspace2_numpy_compatibility()
    _patch_alphaspace2_mdtraj_sasa(module)
    return module, md


def _pocket_features(topography):
    return sorted(
        topography.get_features(by='type', value='pocket'),
        key=lambda pocket: int(pocket.source_id.split(':')[-1]),
    )


def test_alphaspace2_wrapper_matches_upstream_snapshot_on_reference_system(
    tmp_path, upstream_alphaspace2
):
    upstream, md = upstream_alphaspace2
    receptor = md.load(str(TEST_PDB))
    snapshot = upstream.Snapshot()
    snapshot.run(receptor)
    # PyPI 0.1.2 lacks the upstream source fix for an unbound snapshot.
    _initialize_unbound_contacts(snapshot)

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
    assert len(wrapper_topography.provider_runs) == 1
    run = next(iter(wrapper_topography.provider_runs.values()))
    assert run.provider == 'alphaspace2'
    assert run.get_artifact('input/1GG0.pdb') == TEST_PDB.read_bytes()
    state = json.loads(run.get_artifact('output/topomt_snapshot.json'))
    assert state['schema_version'] == 1
    assert set(snapshot.__dict__).issubset(state)
    assert len(state['pocket_properties']) == len(list(snapshot.pockets))
    assert len(state['beta_properties']) == snapshot.numBetas
    assert state['pocket_properties'][0]['occupied_space'] == pytest.approx(
        next(snapshot.pockets).occupiedSpace
    )
    assert np.asarray(state['_alpha_xyz']) == pytest.approx(snapshot._alpha_xyz)
    assert np.asarray(state['_alpha_space']) == pytest.approx(snapshot._alpha_space)
    assert np.asarray(state['_alpha_lining']) == pytest.approx(snapshot._alpha_lining)
    assert np.asarray(state['_beta_space']) == pytest.approx(snapshot._beta_space)
    assert np.asarray(state['_beta_scores']) == pytest.approx(snapshot._beta_scores)
    assert np.asarray(state['_alpha_space_nonpolar_ratio']) == pytest.approx(
        snapshot._alpha_space_nonpolar_ratio
    )
    assert state['_beta_alpha_index_list'] == snapshot._beta_alpha_index_list
    assert state['_pocket_alpha_index_list'] == snapshot._pocket_alpha_index_list
    assert state['_pocket_beta_index_list'] == snapshot._pocket_beta_index_list
    assert len(state['_pocket_alpha_index_list']) == len(list(snapshot.pockets))
    direct_output = tmp_path / 'upstream'
    direct_output.mkdir()
    snapshot.save(
        output_dir=str(direct_output),
        receptor=receptor,
        chimera_scripts=False,
        contact_only=False,
    )
    output_paths = sorted(path for path in direct_output.rglob('*') if path.is_file())
    assert output_paths
    for path in output_paths:
        artifact = f'output/{path.relative_to(direct_output).as_posix()}'
        assert run.get_artifact(artifact) == path.read_bytes()
    assert (
        run.get_artifact('output/pdb_out/prot.pdb')
        == (direct_output / 'pdb_out' / 'prot.pdb').read_bytes()
    )
    bundle = tmp_path / 'alphaspace2_run.zip'
    run.save(bundle)
    assert ProviderRun.load(bundle) == run

    for wrapper_pocket, upstream_pocket in zip(
        wrapper_pockets[:5], upstream_pockets[:5]
    ):
        assert puw.get_value(wrapper_pocket.volume, to_unit='nm**3') == pytest.approx(
            upstream_pocket.space / 1000.0
        )
        assert wrapper_pocket.score == pytest.approx(upstream_pocket.score)
        assert len(
            puw.get_value(wrapper_pocket.alpha_sphere_radii, to_unit='nm')
        ) == len(upstream_pocket.alpha_index)
        alpha_indices = np.asarray(upstream_pocket.alpha_index, dtype=int)
        assert wrapper_pocket.provider_run_id == run.run_id
        assert wrapper_pocket.provider_snapshot_source_artifact == (
            'output/topomt_snapshot.json'
        )
        assert wrapper_pocket.alpha_indices == alpha_indices.tolist()
        assert (
            wrapper_pocket.beta_indices
            == snapshot._pocket_beta_index_list[upstream_pocket.index]
        )
        assert wrapper_pocket.beta_alpha_indices == [
            snapshot._beta_alpha_index_list[index]
            for index in wrapper_pocket.beta_indices
        ]
        assert wrapper_pocket.beta_provider_properties == [
            state['beta_properties'][index] for index in wrapper_pocket.beta_indices
        ]
        assert (
            wrapper_pocket.alpha_lining_atom_indices
            == snapshot._alpha_lining[alpha_indices].tolist()
        )
        assert puw.get_value(
            wrapper_pocket.alpha_space, to_unit='angstroms**3'
        ).tolist() == pytest.approx(snapshot._alpha_space[alpha_indices])
        assert puw.get_value(
            wrapper_pocket.alpha_nonpolar_space, to_unit='angstroms**3'
        ).tolist() == pytest.approx(
            snapshot._alpha_space[alpha_indices]
            * snapshot._alpha_space_nonpolar_ratio[alpha_indices]
        )
        assert wrapper_pocket.alpha_nonpolar_ratio.tolist() == pytest.approx(
            snapshot._alpha_space_nonpolar_ratio[alpha_indices]
        )
        assert puw.get_value(
            wrapper_pocket.beta_nonpolar_space, to_unit='angstroms**3'
        ).tolist() == pytest.approx(
            [
                sum(
                    snapshot._alpha_space[alpha_index]
                    * snapshot._alpha_space_nonpolar_ratio[alpha_index]
                    for alpha_index in snapshot._beta_alpha_index_list[beta_index]
                )
                for beta_index in wrapper_pocket.beta_indices
            ]
        )
        assert wrapper_pocket.beta_scores == pytest.approx(
            np.asarray(snapshot._beta_scores)[wrapper_pocket.beta_indices]
        )
        assert (
            wrapper_pocket.alpha_contact.tolist()
            == np.asarray(snapshot._alpha_contact)[alpha_indices].astype(bool).tolist()
        )
        assert (
            wrapper_pocket.beta_contact.tolist()
            == np.asarray(snapshot._beta_contact)[wrapper_pocket.beta_indices]
            .astype(bool)
            .tolist()
        )
        assert puw.get_value(
            wrapper_pocket.occupied_space, to_unit='angstroms**3'
        ) == pytest.approx(upstream_pocket.occupiedSpace)
        assert puw.get_value(
            wrapper_pocket.occupied_nonpolar_space, to_unit='angstroms**3'
        ) == pytest.approx(upstream_pocket.occupiedNonpolarSpace)
        assert wrapper_pocket.occupancy == pytest.approx(upstream_pocket.occupancy)
        assert wrapper_pocket.occupancy_nonpolar == pytest.approx(
            upstream_pocket.occupancy_nonpolar
        )
        assert set(wrapper_pocket.external_measurements) == {
            'volume',
            'nonpolar_volume',
            'score',
            'occupied_space',
            'occupied_nonpolar_space',
            'occupancy',
            'occupancy_nonpolar',
        }
        assert wrapper_pocket.external_measurements['occupancy'].issue_url.endswith(
            '/issues/33'
        )
        for name, issue, reported_value in (
            ('occupied_space', 31, upstream_pocket.occupiedSpace),
            ('occupied_nonpolar_space', 32, upstream_pocket.occupiedNonpolarSpace),
            ('occupancy', 33, upstream_pocket.occupancy),
            ('occupancy_nonpolar', 34, upstream_pocket.occupancy_nonpolar),
        ):
            measurement = wrapper_pocket.external_measurements[name]
            assert measurement.original_value == pytest.approx(reported_value)
            assert measurement.source_artifact == 'output/topomt_snapshot.json'
            assert measurement.issue_url.endswith(f'/issues/{issue}')
        assert puw.get_value(
            wrapper_pocket.external_measurements['nonpolar_volume'].value,
            to_unit='angstroms**3',
        ) == pytest.approx(upstream_pocket.nonpolar_space)


def test_alphaspace2_wrapper_smoke_on_demo_system(upstream_alphaspace2):
    wrapper_topography = get_topography(
        str(TEST_PDB),
        method='alphaspace2',
        implementation='wrapper',
        upstream_root=str(UPSTREAM_REPO),
        min_vertices=20,
    )

    assert len(wrapper_topography.get_features(by='type', value='pocket')) > 0
