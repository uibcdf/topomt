"""Optional real-provider composition with PharmacophoreMT public operations."""

import hashlib
import json
import os
from pathlib import Path

import molsysmt as msm
import numpy as np
import pytest

from devtools.qualify_fpocket_handoff import qualify
from devtools.qualify_pharmacophore_handoff import consume
from topomt import pyunitwizard as puw

pytestmark = pytest.mark.skipif(
    not (
        os.environ.get('TOPOMT_FPOCKET_CMD')
        and os.environ.get('TOPOMT_PREPARED_RECEPTOR')
    ),
    reason='explicit original engine and checksum-qualified prepared receptor required',
)
INPUT_SHA256 = 'a42ef9868578ba16c62d52a1267d24160b973dca0d50dbc804ca46b6b2fe316a'
RECIPE = dict(
    pocket_id='fpocket:1',
    projection_direction=(1.0, 0.0, 0.0),
    distance='0.30 nm',
    radius='0.15 nm',
)


@pytest.fixture(scope='module')
def handoff(tmp_path_factory):
    source = Path(os.environ['TOPOMT_PREPARED_RECEPTOR'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == INPUT_SHA256
    destination = tmp_path_factory.mktemp('prepared_handoff') / 'original'
    qualify(source, os.environ['TOPOMT_FPOCKET_CMD'], destination)
    return destination


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_original_pocket_builds_persisted_explicit_consumer_sites(
    handoff, tmp_path, policy
):
    from pharmacophoremt.io import load_json

    with puw.context(standard_units=policy):
        receipt = consume(handoff, tmp_path / 'consumer', **RECIPE)
        model = load_json(tmp_path / 'consumer/query.json')
        assert receipt['site_count'] > 0
        assert all(receipt['checks'].values())
        assert all(
            row['center']['unit'] == row['radius']['unit'] == 'nm'
            for row in receipt['sites']
        )
        assert model.n_interaction_sites == receipt['site_count']
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
                coordinates[indices[0]] + [0.30, 0.0, 0.0],
                atol=1e-12,
                rtol=0,
            )
            assert site.features == ['hydrophobicity']
            assert puw.get_value(site.shape.radius, to_unit='nm') == pytest.approx(0.15)
            assert site.essential and site.weight == 1
        assert model.ref_struct == 1
        assert model.metadata['topomt_handoff']['pocket_id'] == 'fpocket:1'
        assert model.metadata['source_inventory']['chemical_state'] == 0


@pytest.mark.parametrize('change', ['missing_state', 'wrong_frame'])
def test_missing_or_conflicting_consumer_context_is_rejected(handoff, tmp_path, change):
    receipt = json.loads((handoff / 'receipt.json').read_text())
    if change == 'missing_state':
        receipt.pop('chemical_state')
    else:
        receipt['structure_index'] = 0
    candidate = tmp_path / 'candidate'
    candidate.mkdir()
    (candidate / 'receipt.json').write_text(json.dumps(receipt))
    # Context admission happens before opening the absent scientific artifacts.
    with pytest.raises(ValueError, match='chemical.state|structure.*context'):
        consume(candidate, tmp_path / 'consumer', **RECIPE)
    assert not (tmp_path / 'consumer').exists()


def test_changed_source_bytes_are_rejected_before_consumer_recognition(
    handoff, tmp_path
):
    candidate = tmp_path / 'candidate'
    candidate.mkdir()
    (candidate / 'receipt.json').write_bytes((handoff / 'receipt.json').read_bytes())
    (candidate / 'source.h5msm').write_bytes(b'changed source')
    with pytest.raises(ValueError, match='source.*checksum'):
        consume(candidate, tmp_path / 'consumer', **RECIPE)


def test_raw_pdb_chemistry_failure_remains_a_provider_failure():
    from pharmacophoremt.modeler import get_features

    source = msm.convert(
        Path('topomt/data/CASTp_3.0_server/3ptb.pdb'), to_form='molsysmt.MolSys'
    )
    with pytest.raises(
        msm.StructuralInconsistencyError, match='connectivity declared complete'
    ):
        get_features(source, features=['hydrophobicity'], chemical_state=0)
