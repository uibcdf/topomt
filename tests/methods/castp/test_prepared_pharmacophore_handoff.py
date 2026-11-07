"""Opt-in saved CASTpFold composition; no live service or release qualification."""

import hashlib
import json
import os
import socket
from pathlib import Path
from urllib import request

import molsysmt as msm
import numpy as np
import pytest

import topomt as tmt
from devtools.qualify_pharmacophore_handoff import consume
from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun
from topomt.third_party.castp.servers.castpfold import CastpFoldClient

PROFILE = 'original-castpfold-source-handoff-1'
EXPECTED_SITE_COUNT = 16
EXPECTED_SOURCE_ATOM_INDICES = [
    364,
    387,
    388,
    671,
    672,
    702,
    711,
    712,
    730,
    842,
    844,
    845,
    971,
    1005,
    1796,
    1806,
]
RECIPE = {
    'pocket_id': 'Pocket 1',
    'feature': 'hydrophobicity',
    'projection_direction': (1.0, 0.0, 0.0),
    'distance': '0.30 nm',
    'radius': '0.15 nm',
}


@pytest.fixture
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Saved CASTpFold consumption attempted network access.')

    monkeypatch.setattr(socket, 'create_connection', forbidden)
    monkeypatch.setattr(socket.socket, 'connect', forbidden)
    monkeypatch.setattr(socket.socket, 'connect_ex', forbidden)
    monkeypatch.setattr(request, 'urlopen', forbidden)
    monkeypatch.setattr(CastpFoldClient, 'submit', forbidden)
    monkeypatch.setattr(CastpFoldClient, 'download_result_zip_bytes', forbidden)


@pytest.fixture
def handoff(no_network):
    value = os.environ.get('TOPOMT_CASTPFOLD_PREPARED_HANDOFF')
    if not value:
        pytest.skip('explicit qualified prepared CASTpFold handoff required')
    root = Path(value)
    evidence = json.loads((root / 'receipt.json').read_text())
    assert evidence['profile'] == PROFILE
    assert evidence['server'] == 'castpfold'
    assert type(evidence['structure_index']) is int
    assert evidence['structure_index'] == 1
    assert evidence['chemical_state'] == {'count': 1, 'reference_index': 0}
    assert all(type(value) is int for value in evidence['chemical_state'].values())
    assert evidence['checks'] and all(
        value is True for value in evidence['checks'].values()
    )
    source = root / 'source.h5msm'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == evidence['source_sha256']
    run = ProviderRun.load(root / 'original.zip')
    assert run.run_id == evidence['run_id']
    assert run.provider == 'castp' and run.backend == 'files'
    assert run.metadata['server'] == 'castpfold'
    assert run.metadata['structure_indices'] == [1]
    assert type(run.metadata['structure_indices'][0]) is int
    return root, evidence, run


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_saved_prepared_pocket_builds_public_query_without_network(
    handoff, tmp_path, policy
):
    root, evidence, run = handoff
    source_file, bundle_file = root / 'source.h5msm', root / 'original.zip'
    source_bytes, bundle_bytes = source_file.read_bytes(), bundle_file.read_bytes()
    with puw.context(standard_units=[*policy, 'radians']):
        # Import the optional consumer only after the application chooses units.
        from pharmacophoremt.io import load_json

        source = msm.convert(source_file, to_form='molsysmt.MolSys')
        assert msm.get(source, n_atoms=True, n_structures=True) == [4047, 2]
        assert source.chemical_states is not None
        assert source.chemical_states.n_chemical_states == 1
        assert source.chemical_states.reference_chemical_state_index == 0
        coordinates = puw.get_value(msm.get(source, coordinates=True), to_unit='nm')
        before = coordinates.copy()
        output = tmt.get_provider_output(
            source, method='castpfold', backend='files', bundle_file=bundle_file
        )
        assert output.run == run
        pocket = next(
            record for record in output.pockets if record.source_id == 'Pocket 1'
        )
        assert pocket.atom_indices is not None and pocket.atom_indices
        receipt = consume(root, tmp_path / 'consumer', **RECIPE)
        model = load_json(tmp_path / 'consumer/query.json')
        assert receipt['profile'] == 'castp-pharmacophoremt-hydrophobic-control-1'
        assert receipt['site_count'] == model.n_interaction_sites > 0
        assert model.n_interaction_sites == EXPECTED_SITE_COUNT
        assert receipt['checks'] and all(
            value is True for value in receipt['checks'].values()
        )
        route = {'provider': 'castp', 'backend': 'files', 'server': 'castpfold'}
        assert all(receipt[key] == value for key, value in route.items())
        expected_context = {
            **route,
            'original_run_id': run.run_id,
            'pocket_id': 'Pocket 1',
            'source_sha256': evidence['source_sha256'],
            'structure_index': 1,
            'chemical_state': 0,
            'membership_role': pocket.atom_role,
            'interpretation': 'explicit analytical projection; not binding relevance',
        }
        assert receipt['context'] == expected_context
        assert model.metadata['topomt_handoff'] == expected_context
        assert receipt['pocket_atom_indices'] == list(pocket.atom_indices)
        assert model.ref_struct == 1
        assert model.metadata['source_inventory']['chemical_state'] == 0
        recognized_atoms = []
        for site in model.interaction_sites:
            indices = site.metadata['atom_indices']
            assert len(indices) == 1 and indices[0] in pocket.atom_indices
            recognized_atoms.extend(indices)
            np.testing.assert_allclose(
                puw.get_value(site.center, to_unit='nm'),
                coordinates[1, indices[0]] + [0.30, 0, 0],
                rtol=0,
                atol=1e-12,
            )
            assert site.features == ['hydrophobicity']
            assert puw.get_value(site.shape.radius, to_unit='nm') == pytest.approx(0.15)
            assert site.essential is True and site.weight == 1
        assert len(set(recognized_atoms)) == model.n_interaction_sites
        assert recognized_atoms == EXPECTED_SOURCE_ATOM_INDICES
        assert [site['atom_indices'][0] for site in receipt['sites']] == (
            EXPECTED_SOURCE_ATOM_INDICES
        )
        np.testing.assert_array_equal(
            puw.get_value(msm.get(source, coordinates=True), to_unit='nm'), before
        )
    assert source_file.read_bytes() == source_bytes
    assert bundle_file.read_bytes() == bundle_bytes
    assert ProviderRun.load(bundle_file) == run
    assert receipt['original_bundle_sha256'] == hashlib.sha256(bundle_bytes).hexdigest()
    assert json.loads((tmp_path / 'consumer/receipt.json').read_text()) == receipt
