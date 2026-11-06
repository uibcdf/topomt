"""Pocketeer keeps MolSysMT chemical facts; it does not prepare chemistry."""

import copy

import molsysmt as msm
import numpy as np
import pytest
from depdigest.core import decorator as dependency_decorator

import topomt as tmt
from tests.methods.fpocket4.test_chemical_context import _with_states
from tests.methods.fpocket4.test_input_preparation import _pdb_frame
from topomt.third_party.pocketeer import library


@pytest.fixture
def source(tmp_path):
    path = tmp_path / 'seed.pdb'
    path.write_text(_pdb_frame() + 'END\n')
    return msm.convert(path, to_form='molsysmt.MolSys')


@pytest.mark.parametrize(
    'inventory,reference,selector,message',
    [
        ('two', 0, 1, 'nonreference'),
        ('two', None, 'reference', 'ambiguous'),
        ('absent', 0, 'reference', 'absent'),
        ('empty', None, 'reference', 'zero chemical states'),
        ('two', 0, True, 'chemical_state'),
        ('two', 0, None, 'chemical_state'),
    ],
)
def test_state_admission_precedes_original_execution(
    source, monkeypatch, inventory, reference, selector, message
):
    source = _with_states(source, reference=reference, inventory=inventory)
    monkeypatch.setattr(dependency_decorator, 'check_dependency', lambda *a, **k: None)

    def forbidden(*args, **kwargs):
        pytest.fail('Original Pocketeer was loaded before state admission.')

    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', forbidden)
    monkeypatch.setattr(library, 'import_upstream_module', forbidden)
    with pytest.raises(ValueError, match=message):
        tmt.get_provider_output(source, method='pocketeer', chemical_state=selector)


def test_nonzero_reference_exports_existing_charges_without_preparation(
    source, monkeypatch
):
    source = _with_states(source, reference=1)
    msm.set(source, element='atom', formal_charge=[1] * 4, chemical_state=1)
    before = copy.deepcopy(
        msm.convert(
            source.chemical_states, to_form='molsysmt.ChemicalStatesDict'
        ).to_dict()
    )
    monkeypatch.setattr(dependency_decorator, 'check_dependency', lambda *a, **k: None)

    class ObservedExport(Exception):
        pass

    def observe(*args, **kwargs):
        def load(path):
            from pathlib import Path

            rows = [
                r for r in Path(path).read_text().splitlines() if r.startswith('ATOM')
            ]
            assert [r[78:80] for r in rows] == ['1+'] * 4
            raise ObservedExport

        from types import SimpleNamespace

        return SimpleNamespace(load_structure=load)

    monkeypatch.setattr(library, 'import_upstream_module', observe)
    with pytest.raises(ObservedExport):
        tmt.get_provider_output(source, method='pocketeer', chemical_state=1)
    assert source.chemical_states.reference_chemical_state_index == 1
    np.testing.assert_equal(
        msm.convert(
            source.chemical_states, to_form='molsysmt.ChemicalStatesDict'
        ).to_dict(),
        before,
    )


def test_unknown_and_complete_empty_bond_tables_have_different_context(source):
    from topomt.third_party.pdb_context import reference_chemical_context

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
        contexts.append(reference_chemical_context(source, provider='Pocketeer'))
    assert contexts[0]['pdb_chemistry_sha256'] != contexts[1]['pdb_chemistry_sha256']
