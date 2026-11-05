"""The original fpocket route must not silently select chemical states."""

import copy
import os
from pathlib import Path

import molsysmt as msm
import numpy as np
import pytest

import topomt as tmt
from devtools.qualify_fpocket_handoff import _same_output
from tests.methods.fpocket4.test_input_preparation import _pdb_frame
from topomt.third_party.fpocket import cli
from topomt.third_party.fpocket.input_context import _chemical_context


def _with_states(source, *, reference=0, inventory='two'):
    # Declare synthetic controls through the provider's validated public codec.
    source = msm.copy(source)
    if inventory == 'absent':
        payload = msm.convert(source, to_form='molsysmt.MolSysDict').to_dict()
        payload['chemical_states'] = None
        return msm.convert(msm.MolSysDict(payload), to_form='molsysmt.MolSys')
    else:
        chemical = msm.convert(
            source.chemical_states, to_form='molsysmt.ChemicalStatesDict'
        ).to_dict()
        if inventory == 'empty':
            chemical['states'] = []
            reference = None
        else:
            chemical['states'].append(copy.deepcopy(chemical['states'][0]))
            for index, state in enumerate(chemical['states']):
                state['state_id'] = f'analytical-state-{index}'
        chemical['reference_chemical_state_index'] = reference
        source.chemical_states = msm.convert(
            msm.ChemicalStatesDict(chemical), to_form='molsysmt.ChemicalStates'
        )
    return source


@pytest.fixture
def source(tmp_path):
    path = tmp_path / 'seed.pdb'
    path.write_text(_pdb_frame() + 'END\n')
    return msm.convert(path, to_form='molsysmt.MolSys')


@pytest.mark.parametrize(
    ('inventory', 'reference', 'selector', 'message'),
    [
        ('two', 0, 1, 'nonreference'),
        ('two', None, 'reference', 'ambiguous'),
        ('absent', 0, 'reference', 'absent'),
        ('empty', None, 'reference', 'zero chemical states'),
        ('two', 0, True, 'chemical_state'),
        ('two', 0, 'structure', 'chemical_state'),
    ],
)
def test_unsupported_state_fails_before_original_engine(
    source, monkeypatch, inventory, reference, selector, message
):
    source = _with_states(source, reference=reference, inventory=inventory)

    def forbidden(*args, **kwargs):
        pytest.fail('The original engine ran before chemical-state admission.')

    monkeypatch.setattr(cli, 'run_fpocket', forbidden)
    with pytest.raises(ValueError, match=message):
        tmt.get_provider_output(source, method='fpocket', chemical_state=selector)


def test_nonzero_reference_is_exported_without_changing_input(source, tmp_path):
    source = _with_states(source, reference=1)
    msm.set(source, element='atom', formal_charge=[1] * 4, chemical_state=1)
    path = cli._prepare_fpocket_input_pdb(source, tmp_path, chemical_state=1)
    atoms = [line for line in path.read_text().splitlines() if line.startswith('ATOM')]
    assert [line[78:80] for line in atoms] == ['1+'] * 4
    assert source.chemical_states.reference_chemical_state_index == 1
    assert msm.get(source, element='atom', formal_charge=True, chemical_state=0) is None


def test_unknown_and_known_empty_connectivity_remain_distinct(source):
    states = msm.ChemicalStates(n_atoms=4)
    states.append_state()
    payload = msm.convert(states, to_form='molsysmt.ChemicalStatesDict').to_dict()
    contexts = []
    for completeness in ('unavailable', 'complete'):
        payload['states'][0]['connectivity_completeness'] = completeness
        source.chemical_states = msm.convert(
            msm.ChemicalStatesDict(copy.deepcopy(payload)),
            to_form='molsysmt.ChemicalStates',
        )
        assert msm.get(source, n_bonds=True) == 0
        contexts.append(_chemical_context(source))
    assert contexts[0]['index'] == contexts[1]['index'] == 0
    assert contexts[0]['state_count'] == contexts[1]['state_count'] == 1
    assert contexts[0]['pdb_chemistry_sha256'] != contexts[1]['pdb_chemistry_sha256']


def test_files_recovery_preserves_and_checks_chemical_context():
    data = Path(tmt.__file__).parent / 'data/fpocket4/sample'
    source = msm.convert(data / '3LKF.pdb', to_form='molsysmt.MolSys')
    source = _with_states(source, reference=1)
    options = dict(
        method='fpocket',
        backend='files',
        pdb_file=data / '3LKF.pdb',
        output_dir=data / '3LKF_out',
        chemical_state=1,
    )
    output = tmt.get_provider_output(source, **options)
    context = output.run.metadata['chemical_state_context']
    assert context['index'] == context['reference_index'] == 1
    assert context['state_count'] == 2 and context['state_id'] == 'analytical-state-1'
    frozen = output.run.metadata
    msm.set(source, element='atom', formal_charge=1, chemical_state=1)
    assert output.run.metadata == frozen
    with pytest.raises(ValueError, match='chemical.*context'):
        tmt.get_provider_output(source, **options, chemical_state_context=context)


def test_malformed_saved_state_context_is_rejected():
    data = Path(tmt.__file__).parent / 'data/fpocket4/sample'
    with pytest.raises(ValueError, match='chemical.*context'):
        tmt.get_provider_output(
            data / '3LKF.pdb',
            method='fpocket',
            backend='files',
            pdb_file=data / '3LKF.pdb',
            output_dir=data / '3LKF_out',
            chemical_state_context={},
        )


@pytest.mark.skipif(
    not os.environ.get('TOPOMT_FPOCKET_CMD'), reason='explicit original engine required'
)
def test_real_engine_run_retains_nonzero_reference_context(tmp_path):
    source_path = Path(tmt.__file__).parent / 'data/CASTp_3.0_server/3ptb.pdb'
    source = _with_states(
        msm.convert(source_path, to_form='molsysmt.MolSys'), reference=1
    )
    output = tmt.get_provider_output(
        source,
        method='fpocket',
        chemical_state=1,
        selection="molecule_type in ['protein', 'peptide']",
        fpocket_cmd=os.environ['TOPOMT_FPOCKET_CMD'],
    )
    assert output.pockets
    context = output.run.metadata['chemical_state_context']
    assert context['index'] == 1
    artifact = tmp_path / 'original.zip'
    output.run.save(artifact)
    from topomt.provider_output import ProviderRun

    assert ProviderRun.load(artifact).metadata['chemical_state_context'] == context
    source_file = tmp_path / 'source.h5msm'
    msm.convert(source, to_form='file:h5msm', output_filename=source_file)
    restored_source = msm.convert(source_file, to_form='molsysmt.MolSys')
    run = ProviderRun.load(artifact)
    for name, data in run.artifacts:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    submitted = next((tmp_path / 'input').glob('*.pdb'))
    recovered = tmt.get_provider_output(
        restored_source,
        method='fpocket',
        backend='files',
        pdb_file=submitted,
        output_dir=tmp_path / 'output',
        selection=run.metadata['selection'],
        structure_indices=run.metadata['structure_indices'],
        submitted_atom_indices=run.metadata['submitted_atom_indices'],
        chemical_state_context=context,
    )
    assert _same_output(output, recovered)
    assert recovered.run.metadata['chemical_state_context'] == context
    original = np.asarray(output.input_points_nm).copy()
    msm.set(source, element='atom', formal_charge=1, chemical_state=1)
    np.testing.assert_array_equal(output.input_points_nm, original)
    assert output.run.metadata['chemical_state_context'] == context
