import importlib
import json
import sys
import warnings
from pathlib import Path

import numpy as np
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
    import biotite.structure as struc

    filtered_indices = np.arange(len(atomarray))
    filtered_indices = filtered_indices[atomarray.element[filtered_indices] != 'H']
    filtered_indices = filtered_indices[
        ~struc.filter_solvent(atomarray[filtered_indices])
    ]
    filtered_indices = filtered_indices[~atomarray.hetero[filtered_indices]]

    for provider_pocket, upstream_pocket in zip(
        provider_pockets[:5], upstream_pockets[:5]
    ):
        assert puw.get_value(provider_pocket.volume, to_unit='nm**3') == pytest.approx(
            upstream_pocket.volume / 1000.0
        )
        assert provider_pocket.score == pytest.approx(upstream_pocket.score)
        assert provider_pocket.alpha_sphere_ids == upstream_pocket.sphere_ids
        assert provider_pocket.n_alpha_spheres == upstream_pocket.n_spheres
        assert provider_pocket.n_provider_residues == len(upstream_pocket.residues)
        assert provider_pocket.provider_residues == upstream_pocket.residues
        assert provider_pocket.provider_mask.tolist() == upstream_pocket.mask.tolist()
        assert provider_pocket.alpha_sphere_provider_atom_indices == [
            sphere.atom_indices for sphere in upstream_pocket.spheres
        ]
        assert provider_pocket.alpha_sphere_defining_atom_indices == [
            filtered_indices[sphere.atom_indices].tolist()
            for sphere in upstream_pocket.spheres
        ]
        assert puw.get_value(
            provider_pocket.alpha_sphere_mean_sasa, to_unit='angstroms**2'
        ).tolist() == pytest.approx(
            [sphere.mean_sasa for sphere in upstream_pocket.spheres]
        )
        assert set(provider_pocket.external_measurements) == {'volume', 'score'}
        assert puw.get_value(
            provider_pocket.external_measurements['volume'].value,
            to_unit='angstroms**3',
        ) == pytest.approx(upstream_pocket.volume)
        assert set(provider_pocket.alpha_sphere_measurements) == set(
            upstream_pocket.sphere_ids
        )
        for sphere in upstream_pocket.spheres:
            measurements = provider_pocket.alpha_sphere_measurements[sphere.sphere_id]
            assert measurements['mean_sasa'].original_value == sphere.mean_sasa
            assert measurements['mean_sasa'].issue_url.endswith('/issues/30')
            assert measurements['radius'].original_value == sphere.radius

    assert len(provider_topography.provider_runs) == 1
    run = next(iter(provider_topography.provider_runs.values()))
    assert run.provider == 'pocketeer'
    assert run.backend == 'library'
    assert run.metadata['version'] == upstream_pocketeer.__version__
    assert run.get_artifact('input/6qrd.pdb') == pdb_path.read_bytes()
    assert run.metadata['filtered_input_atom_indices'] == filtered_indices.tolist()
    exported = json.loads(run.get_artifact('output/pocketeer_pockets.json'))
    mask_snapshot = json.loads(run.get_artifact('output/topomt_masks.json'))
    assert len(exported) == len(mask_snapshot['pockets']) == len(upstream_pockets)
    for output_pocket, original_pocket, mask_record in zip(
        exported, upstream_pockets, mask_snapshot['pockets']
    ):
        assert output_pocket['pocket_id'] == original_pocket.pocket_id
        assert 'mask' not in output_pocket
        assert output_pocket['residues'] == [
            {'chain_id': chain, 'res_id': res_id, 'res_name': name}
            for chain, res_id, name in original_pocket.residues
        ]
        assert (
            output_pocket['spheres'][0]['atom_indices']
            == original_pocket.spheres[0].atom_indices
        )
        assert mask_record['pocket_id'] == original_pocket.pocket_id
        assert mask_record['mask'] == original_pocket.mask.tolist()


def test_pocketeer_provider_keeps_nondefault_probe_and_atom_filter(upstream_pocketeer):
    pdb_path = POCKETEER_REPO / 'tests' / 'data' / '2xjx.pdb'
    atomarray = upstream_pocketeer.load_structure(str(pdb_path))
    parameters = {
        'polar_probe_radius': 1.7,
        'ignore_hetero': False,
        'min_spheres': 5,
    }
    upstream_pockets = upstream_pocketeer.find_pockets(atomarray, **parameters)
    provider_topography = tmt.third_party.pocketeer.get_topography(
        str(pdb_path),
        backend='library',
        upstream_root=str(POCKETEER_REPO / 'src'),
        **parameters,
    )
    run = next(iter(provider_topography.provider_runs.values()))
    assert run.metadata['parameters'] == parameters
    assert len(provider_topography) == len(upstream_pockets) > 0

    import biotite.structure as struc

    filtered_indices = np.arange(len(atomarray))
    filtered_indices = filtered_indices[atomarray.element[filtered_indices] != 'H']
    filtered_indices = filtered_indices[
        ~struc.filter_solvent(atomarray[filtered_indices])
    ]
    assert run.metadata['filtered_input_atom_indices'] == filtered_indices.tolist()
    for original in upstream_pockets:
        mapped = next(
            pocket
            for pocket in provider_topography.values()
            if pocket.source_id == f'pocketeer:{original.pocket_id}'
        )
        assert mapped.provider_mask.tolist() == original.mask.tolist()
        assert mapped.alpha_sphere_ids == original.sphere_ids
        assert mapped.alpha_sphere_defining_atom_indices == [
            filtered_indices[sphere.atom_indices].tolist()
            for sphere in original.spheres
        ]
        assert puw.get_value(
            mapped.alpha_sphere_mean_sasa, to_unit='angstroms**2'
        ).tolist() == pytest.approx([sphere.mean_sasa for sphere in original.spheres])


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
    assert not any(
        type(item.message).__name__ == 'DigestNotDigestedWarning' for item in caught
    )
