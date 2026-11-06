"""Prepared pyCASTA pockets compose public recognition and query tools."""

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

INPUT_SHA256 = 'a42ef9868578ba16c62d52a1267d24160b973dca0d50dbc804ca46b6b2fe316a'
RECIPE = dict(
    pocket_id='pycasta:0',
    projection_direction=(1.0, 0.0, 0.0),
    distance='0.30 nm',
    radius='0.15 nm',
)


def test_supported_profile_checks_source_bytes_before_recognition(tmp_path):
    candidate = tmp_path / 'candidate'
    candidate.mkdir()
    (candidate / 'source.h5msm').write_bytes(b'changed source')
    receipt = {
        'profile': 'original-pycasta-source-handoff-1',
        'chemical_state': {'count': 1, 'reference_index': 0},
        'structure_index': 1,
        'checks': {'source': True},
        'source_sha256': '0' * 64,
    }
    (candidate / 'receipt.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='source.*checksum'):
        consume(candidate, tmp_path / 'consumer', **RECIPE)
    assert not (tmp_path / 'consumer').exists()


@pytest.fixture(scope='module')
def handoff(tmp_path_factory):
    value = os.environ.get('TOPOMT_PREPARED_RECEPTOR')
    if not value:
        pytest.skip('explicit checksum-qualified prepared receptor required')
    installed = distribution('pycasta')
    import pycasta

    assert installed.version == '1.0.8'
    assert (
        Path(pycasta.__file__).resolve()
        == Path(installed.locate_file('pycasta/__init__.py')).resolve()
    )
    source = Path(value)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == INPUT_SHA256
    from devtools.qualify_pycasta_handoff import qualify

    destination = tmp_path_factory.mktemp('pycasta_prepared') / 'handoff'
    receipt = qualify(source, destination)
    assert receipt['profile'] == 'original-pycasta-source-handoff-1'
    assert receipt['provider'] == 'pycasta' and receipt['backend'] == 'library'
    assert receipt['distribution_version'] == '1.0.8'
    assert receipt['selection_is_nonconsecutive']
    assert receipt['structure_index'] == 1
    assert receipt['chemical_state'] == {'count': 1, 'reference_index': 0}
    assert all(receipt['checks'].values()) and receipt['pocket_count'] > 0
    assert RECIPE['pocket_id'] in receipt['pocket_ids']
    run = ProviderRun.load(destination / 'original.zip')
    assert receipt['provider_source_sha256'] == run.metadata['source_sha256']
    assert (
        receipt['source_sha256']
        == hashlib.sha256((destination / 'source.h5msm').read_bytes()).hexdigest()
    )
    return destination


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_original_pocket_builds_and_roundtrips_public_query(handoff, tmp_path, policy):
    from pharmacophoremt.io import load_json

    with puw.context(standard_units=[*policy, 'radians']):
        receipt = consume(handoff, tmp_path / 'consumer', **RECIPE)
        model = load_json(tmp_path / 'consumer/query.json')
        assert receipt['profile'] == 'pycasta-pharmacophoremt-hydrophobic-control-1'
        assert model.n_interaction_sites == receipt['site_count'] > 0
        assert all(receipt['checks'].values())
        run = ProviderRun.load(handoff / 'original.zip')
        assert receipt['context']['original_run_id'] == run.run_id
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
            assert site.features == ['hydrophobicity']
            assert puw.get_value(site.shape.radius, to_unit='nm') == pytest.approx(0.15)
            assert site.essential is True and site.weight == 1
        assert model.ref_struct == 1
        assert model.metadata['source_inventory']['chemical_state'] == 0
        assert model.metadata['topomt_handoff']['pocket_id'] == RECIPE['pocket_id']


def test_saved_consumer_never_imports_original_detector(handoff, tmp_path):
    script = """
import importlib.abc
import sys
from pathlib import Path
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pycasta', 'run_analysis'}:
            raise AssertionError('Original detector import attempted: ' + fullname)
sys.meta_path.insert(0, Block())
from devtools.qualify_pharmacophore_handoff import consume
receipt = consume(Path(sys.argv[1]), Path(sys.argv[2]), pocket_id='pycasta:0',
    projection_direction=(1., 0., 0.), distance='0.30 nm', radius='0.15 nm')
assert receipt['site_count'] > 0 and all(receipt['checks'].values())
assert not {'pycasta', 'run_analysis'}.intersection(sys.modules)
"""
    result = subprocess.run(
        [sys.executable, '-B', '-c', script, str(handoff), str(tmp_path / 'consumer')],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
