"""Prepared-receptor composition uses original Pocketeer and public consumer tools."""

import hashlib
import json
import os
import subprocess
import sys
from importlib.metadata import distribution
from pathlib import Path

import molsysmt as msm
import numpy as np
import pytest

from devtools.qualify_pharmacophore_handoff import consume
from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun

pytestmark = pytest.mark.skipif(
    not os.environ.get('TOPOMT_PREPARED_RECEPTOR'),
    reason='explicit checksum-qualified prepared receptor required',
)
INPUT_SHA256 = 'a42ef9868578ba16c62d52a1267d24160b973dca0d50dbc804ca46b6b2fe316a'
RECIPE = dict(
    pocket_id='pocketeer:0',
    projection_direction=(1.0, 0.0, 0.0),
    distance='0.30 nm',
    radius='0.15 nm',
)


@pytest.fixture(scope='module')
def handoff(tmp_path_factory):
    # An explicitly requested real integration must fail if its engine is absent
    # or shadowed; a source override is not the public 0.4.0 receiving profile.
    installed = distribution('pocketeer')
    import pocketeer

    assert installed.version == '0.4.0'
    assert (
        Path(pocketeer.__file__).resolve()
        == Path(installed.locate_file('pocketeer/__init__.py')).resolve()
    )
    source = Path(os.environ['TOPOMT_PREPARED_RECEPTOR'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == INPUT_SHA256
    from devtools.qualify_pocketeer_handoff import qualify

    destination = tmp_path_factory.mktemp('pocketeer_prepared') / 'handoff'
    receipt = qualify(source, destination)
    assert receipt['profile'] == 'original-pocketeer-source-handoff-1'
    assert receipt['provider'] == 'pocketeer' and receipt['backend'] == 'library'
    assert receipt['distribution_version'] == '0.4.0'
    assert receipt['selection_is_nonconsecutive']
    assert receipt['structure_index'] == 1
    assert receipt['chemical_state'] == {'count': 1, 'reference_index': 0}
    assert all(receipt['checks'].values()) and receipt['pocket_count'] > 0
    assert 'pocketeer:0' in receipt['pocket_ids']
    return destination


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_original_pocket_builds_persisted_public_consumer_sites(
    handoff, tmp_path, policy
):
    from pharmacophoremt.io import load_json

    with puw.context(standard_units=[*policy, 'radians']):
        receipt = consume(handoff, tmp_path / 'consumer', **RECIPE)
        model = load_json(tmp_path / 'consumer/query.json')
        assert receipt['profile'] == 'pocketeer-pharmacophoremt-hydrophobic-control-1'
        assert receipt['site_count'] > 0 and all(receipt['checks'].values())
        assert model.n_interaction_sites == receipt['site_count']
        run = ProviderRun.load(handoff / 'original.zip')
        assert receipt['context']['original_run_id'] == run.run_id
        assert receipt['context']['membership_role'] == 'pocket_residue_atoms'
        source = msm.convert(handoff / 'source.h5msm', to_form='molsysmt.MolSys')
        coordinates = puw.get_value(
            msm.get(source, coordinates=True, structure_indices=1), to_unit='nm'
        )[0]
        allowed = set(receipt['pocket_atom_indices'])
        for site in model.interaction_sites:
            indices = site.metadata['atom_indices']
            assert len(indices) == 1 and indices[0] in allowed
            np.testing.assert_allclose(
                puw.get_value(site.center, to_unit='nm'),
                coordinates[indices[0]] + [0.30, 0, 0],
                rtol=0,
                atol=1e-12,
            )
            assert site.features == ['hydrophobicity']
            assert puw.get_value(site.shape.radius, to_unit='nm') == pytest.approx(0.15)
            assert site.essential is True and site.weight == 1
        assert model.ref_struct == 1
        assert model.metadata['source_inventory']['chemical_state'] == 0
        assert model.metadata['topomt_handoff']['pocket_id'] == RECIPE['pocket_id']


@pytest.mark.parametrize(
    'change',
    [
        'missing_state',
        'ambiguous_state',
        'wrong_frame',
        'boolean_frame',
        'boolean_state',
        'failed_check',
        'unknown_profile',
        'not_mapping',
        'invalid_checks',
    ],
)
def test_invalid_receipt_context_is_rejected_before_artifact_loading(tmp_path, change):
    receipt = {
        'profile': 'original-pocketeer-source-handoff-1',
        'chemical_state': {'count': 1, 'reference_index': 0},
        'structure_index': 1,
        'checks': {'control': True},
    }
    if change == 'missing_state':
        receipt.pop('chemical_state')
    elif change == 'ambiguous_state':
        receipt['chemical_state']['reference_index'] = None
    elif change == 'wrong_frame':
        receipt['structure_index'] = 0
    elif change == 'boolean_frame':
        receipt['structure_index'] = True
    elif change == 'boolean_state':
        receipt['chemical_state']['count'] = True
    elif change == 'failed_check':
        receipt['checks']['control'] = False
    elif change == 'not_mapping':
        receipt = []
    elif change == 'invalid_checks':
        receipt['checks'] = [True]
    else:
        receipt['profile'] = 'unsupported-profile'
    candidate = tmp_path / 'candidate'
    candidate.mkdir()
    (candidate / 'receipt.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='chemical.state|structure.*context|receipt'):
        consume(candidate, tmp_path / 'consumer', **RECIPE)
    assert not (tmp_path / 'consumer').exists()


def test_changed_source_bytes_are_rejected_before_recognition(handoff, tmp_path):
    candidate = tmp_path / 'candidate'
    candidate.mkdir()
    (candidate / 'receipt.json').write_bytes((handoff / 'receipt.json').read_bytes())
    (candidate / 'source.h5msm').write_bytes(b'changed source')
    with pytest.raises(ValueError, match='source.*checksum'):
        consume(candidate, tmp_path / 'consumer', **RECIPE)


def test_unknown_pocket_is_rejected_without_creating_a_query(handoff, tmp_path):
    with pytest.raises(KeyError, match='Original pocket not found'):
        consume(
            handoff,
            tmp_path / 'consumer',
            **{**RECIPE, 'pocket_id': 'pocketeer:absent'},
        )
    assert not (tmp_path / 'consumer').exists()


def test_consumer_does_not_import_original_detection_engines(handoff, tmp_path):
    script = """
import importlib.abc
import sys
from pathlib import Path
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pocketeer','biotite'}:
            raise AssertionError('Consumer attempted detector import: '+fullname)
sys.meta_path.insert(0, Block())
from devtools.qualify_pharmacophore_handoff import consume
receipt=consume(Path(sys.argv[1]),Path(sys.argv[2]),pocket_id='pocketeer:0',
    projection_direction=(1.,0.,0.),distance='0.30 nm',radius='0.15 nm')
assert receipt['site_count'] > 0
assert all(receipt['checks'].values())
assert not {'pocketeer','biotite'}.intersection(sys.modules)
"""
    result = subprocess.run(
        [sys.executable, '-c', script, str(handoff), str(tmp_path / 'consumer')],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize('membership', [None, ()])
def test_unavailable_or_empty_membership_is_not_replaced(
    handoff, tmp_path, monkeypatch, membership
):
    from types import SimpleNamespace

    import topomt as tmt

    run = ProviderRun.load(handoff / 'original.zip')
    monkeypatch.setattr(
        tmt,
        'get_provider_output',
        lambda *args, **kwargs: SimpleNamespace(
            run=run,
            pockets=(
                SimpleNamespace(source_id='pocketeer:0', atom_indices=membership),
            ),
        ),
    )
    with pytest.raises(ValueError, match='membership.*unavailable|membership.*empty'):
        consume(handoff, tmp_path / 'consumer', **RECIPE)
    assert not (tmp_path / 'consumer').exists()


@pytest.mark.parametrize('change', ['run_id', 'provider_profile'])
def test_conflicting_original_identity_is_rejected(handoff, tmp_path, change):
    import shutil

    candidate = tmp_path / 'candidate'
    candidate.mkdir()
    for name in ('source.h5msm', 'original.zip'):
        shutil.copy2(handoff / name, candidate / name)
    receipt = json.loads((handoff / 'receipt.json').read_text())
    if change == 'run_id':
        receipt['run_id'] = '0' * 64
    else:
        receipt['profile'] = 'original-fpocket-source-handoff-1'
    (candidate / 'receipt.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='run identity'):
        consume(candidate, tmp_path / 'consumer', **RECIPE)
    assert not (tmp_path / 'consumer').exists()
