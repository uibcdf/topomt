"""Prepared AlphaSpace2 pockets compose only public molecular/consumer tools."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from importlib.metadata import distribution
from pathlib import Path
from types import SimpleNamespace

import molsysmt as msm
import numpy as np
import pytest

import topomt as tmt
from devtools.qualify_pharmacophore_handoff import consume
from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun

pytestmark = pytest.mark.skipif(
    not os.environ.get('TOPOMT_PREPARED_RECEPTOR'),
    reason='explicit checksum-qualified prepared receptor required',
)
INPUT_SHA256 = 'a42ef9868578ba16c62d52a1267d24160b973dca0d50dbc804ca46b6b2fe316a'
RECIPE = dict(
    pocket_id='alphaspace2:20',
    projection_direction=(1.0, 0.0, 0.0),
    distance='0.30 nm',
    radius='0.15 nm',
    feature='hb acceptor',
    target_direction=(-1.0, 0.0, 0.0),
)


@pytest.fixture(scope='module')
def handoff(tmp_path_factory):
    # An explicitly selected real integration fails for an absent/shadowed
    # original rather than accepting a skipped or native replacement execution.
    installed = distribution('alphaspace2')
    import alphaspace2

    assert installed.version == '0.1.2'
    assert (
        Path(alphaspace2.__file__).resolve()
        == Path(installed.locate_file('alphaspace2/__init__.py')).resolve()
    )
    source = Path(os.environ['TOPOMT_PREPARED_RECEPTOR'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == INPUT_SHA256
    from devtools.qualify_alphaspace2_handoff import qualify

    root = tmp_path_factory.mktemp('alphaspace2_prepared') / 'handoff'
    receipt = qualify(source, root)
    assert receipt['profile'] == 'original-alphaspace2-source-handoff-1'
    assert receipt['provider'] == 'alphaspace2' and receipt['backend'] == 'library'
    assert receipt['distribution_version'] == '0.1.2'
    assert receipt['selection_is_nonconsecutive']
    assert receipt['structure_index'] == 1
    assert receipt['chemical_state'] == {'count': 1, 'reference_index': 0}
    assert all(receipt['checks'].values()) and receipt['pocket_count'] == 13
    assert RECIPE['pocket_id'] in receipt['pocket_ids']
    return root


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_prepared_original_pocket_receives_public_model_and_roundtrips(
    handoff, tmp_path, policy
):
    from pharmacophoremt.io import load_json

    with puw.context(standard_units=[*policy, 'radians']):
        receipt = consume(handoff, tmp_path / 'consumer', **RECIPE)
        model = load_json(tmp_path / 'consumer/query.json')
        assert receipt['profile'] == 'alphaspace2-pharmacophoremt-hb-acceptor-control-1'
        assert (
            all(receipt['checks'].values())
            and model.n_interaction_sites == receipt['site_count'] == 2
        )
        assert (
            receipt['context']['original_run_id']
            == ProviderRun.load(handoff / 'original.zip').run_id
        )
        assert receipt['context']['membership_role'] == 'provider_lining_atoms'
        source = msm.convert(handoff / 'source.h5msm', to_form='molsysmt.MolSys')
        xyz = puw.get_value(
            msm.get(source, coordinates=True, structure_indices=1), to_unit='nm'
        )[0]
        for site in model.interaction_sites:
            indices = site.metadata['atom_indices']
            assert len(indices) == 1 and indices[0] in receipt['pocket_atom_indices']
            np.testing.assert_allclose(
                puw.get_value(site.center, to_unit='nm'),
                xyz[indices[0]] + [0.30, 0, 0],
                rtol=0,
                atol=1e-12,
            )
            assert site.features == ['hb donor']
            np.testing.assert_array_equal(
                puw.get_value(site.shape.direction, to_unit='dimensionless'),
                [-1.0, 0.0, 0.0],
            )
            assert puw.get_value(site.shape.radius, to_unit='nm') == pytest.approx(0.15)
            assert site.essential is True and site.weight == 1
        assert model.ref_struct == 1
        assert model.metadata['source_inventory']['chemical_state'] == 0
        assert model.metadata['topomt_handoff']['pocket_id'] == RECIPE['pocket_id']


def test_geometry_does_not_replace_absent_consumer_features(handoff, tmp_path):
    with pytest.raises(ValueError, match='no hydrophobic features'):
        consume(
            handoff,
            tmp_path / 'consumer',
            **{**RECIPE, 'feature': 'hydrophobicity', 'target_direction': None},
        )
    assert not (tmp_path / 'consumer').exists()


@pytest.mark.parametrize('change', ['state', 'frame', 'checks', 'profile', 'mapping'])
def test_invalid_receipt_is_rejected_before_artifact_loading(tmp_path, change):
    receipt = {
        'profile': 'original-alphaspace2-source-handoff-1',
        'chemical_state': {'count': 1, 'reference_index': 0},
        'structure_index': 1,
        'checks': {'source': True},
    }
    if change == 'state':
        receipt['chemical_state']['count'] = True
    elif change == 'frame':
        receipt['structure_index'] = True
    elif change == 'checks':
        receipt['checks']['source'] = False
    elif change == 'profile':
        receipt['profile'] = 'unknown-profile'
    else:
        receipt = []
    root = tmp_path / 'handoff'
    root.mkdir()
    (root / 'receipt.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='chemical.state|structure.*context|receipt'):
        consume(root, tmp_path / 'consumer', **RECIPE)
    assert not (tmp_path / 'consumer').exists()


def test_changed_source_bytes_do_not_reach_recognition(handoff, tmp_path):
    root = tmp_path / 'candidate'
    root.mkdir()
    (root / 'receipt.json').write_bytes((handoff / 'receipt.json').read_bytes())
    (root / 'source.h5msm').write_bytes(b'changed source')
    with pytest.raises(ValueError, match='source.*checksum'):
        consume(root, tmp_path / 'consumer', **RECIPE)


def test_absent_pocket_does_not_create_a_query(handoff, tmp_path):
    with pytest.raises(KeyError, match='Original pocket not found'):
        consume(
            handoff,
            tmp_path / 'consumer',
            **{**RECIPE, 'pocket_id': 'alphaspace2:absent'},
        )
    assert not (tmp_path / 'consumer').exists()


@pytest.mark.parametrize('membership', [None, ()])
def test_unavailable_or_empty_membership_is_not_replaced(
    handoff, tmp_path, monkeypatch, membership
):
    run = ProviderRun.load(handoff / 'original.zip')
    monkeypatch.setattr(
        tmt,
        'get_provider_output',
        lambda *a, **k: SimpleNamespace(
            run=run,
            pockets=(
                SimpleNamespace(source_id=RECIPE['pocket_id'], atom_indices=membership),
            ),
        ),
    )
    with pytest.raises(ValueError, match='membership.*unavailable|membership.*empty'):
        consume(handoff, tmp_path / 'consumer', **RECIPE)
    assert not (tmp_path / 'consumer').exists()


@pytest.mark.parametrize('change', ['run_id', 'provider_profile'])
def test_conflicting_identity_is_rejected(handoff, tmp_path, change):
    root = tmp_path / 'candidate'
    root.mkdir()
    for name in ['source.h5msm', 'original.zip']:
        shutil.copy2(handoff / name, root / name)
    receipt = json.loads((handoff / 'receipt.json').read_text())
    if change == 'run_id':
        receipt['run_id'] = '0' * 64
    else:
        receipt['profile'] = 'original-pocketeer-source-handoff-1'
    (root / 'receipt.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='run identity'):
        consume(root, tmp_path / 'consumer', **RECIPE)


def test_consumer_recovery_does_not_import_original_engines(handoff, tmp_path):
    script = """
import importlib.abc,sys
from pathlib import Path
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split('.')[0] in {'alphaspace2','mdtraj'}:
            raise AssertionError('Consumer attempted original import: '+fullname)
sys.meta_path.insert(0,Block())
from devtools.qualify_pharmacophore_handoff import consume
receipt=consume(Path(sys.argv[1]),Path(sys.argv[2]),pocket_id=sys.argv[3],projection_direction=(1.,0.,0.),distance='0.30 nm',radius='0.15 nm',feature='hb acceptor',target_direction=(-1.,0.,0.))
assert receipt['site_count']>0 and all(receipt['checks'].values())
assert not {'alphaspace2','mdtraj'}.intersection(sys.modules)
"""
    result = subprocess.run(
        [
            sys.executable,
            '-c',
            script,
            str(handoff),
            str(tmp_path / 'consumer'),
            RECIPE['pocket_id'],
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_donor_orientation_is_required_by_public_consumer(handoff, tmp_path):
    with pytest.raises(ValueError, match='target_direction') as error:
        consume(handoff, tmp_path / 'consumer', **{**RECIPE, 'target_direction': None})
    assert type(error.value).__name__ == 'ArgumentError'
    assert not (tmp_path / 'consumer').exists()


def test_bound_run_is_not_silently_consumed_as_unbound(handoff, tmp_path, monkeypatch):
    run = ProviderRun.load(handoff / 'original.zip')
    bound = SimpleNamespace(
        run_id=run.run_id,
        provider=run.provider,
        backend=run.backend,
        metadata={**run.metadata, 'binder': {'input_artifact': 'input/binder.pdb'}},
    )
    monkeypatch.setattr(ProviderRun, 'load', lambda path: bound)
    with pytest.raises(ValueError, match='requires an unbound run'):
        consume(handoff, tmp_path / 'consumer', **RECIPE)
    assert not (tmp_path / 'consumer').exists()
