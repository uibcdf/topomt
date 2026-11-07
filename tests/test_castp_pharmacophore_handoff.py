"""CASTp consumer admission contracts; synthetic files are not prepared science."""

import builtins
import copy
import hashlib
import json
import sys
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest

import devtools.qualify_pharmacophore_handoff as consumer
from topomt.provider_output import ProviderRun

CASTP_PROFILE = 'original-castpfold-source-handoff-1'
EXISTING_PROFILES = (
    ('original-fpocket-source-handoff-1', 'fpocket', 'cli'),
    ('original-pocketeer-source-handoff-1', 'pocketeer', 'library'),
    ('original-alphaspace2-source-handoff-1', 'alphaspace2', 'library'),
    ('original-pycasta-source-handoff-1', 'pycasta', 'library'),
)
RECIPE = {
    'pocket_id': 'Pocket 1',
    'feature': 'hydrophobicity',
    'projection_direction': (1.0, 0.0, 0.0),
    'distance': '0.30 nm',
    'radius': '0.15 nm',
}


class RecoveryReached(Exception):
    """Stop the contract test before optional molecular recognition."""


@pytest.fixture
def admission_case(tmp_path, monkeypatch):
    source = SimpleNamespace(
        chemical_states=SimpleNamespace(
            n_chemical_states=1, reference_chemical_state_index=0
        )
    )
    monkeypatch.setattr(consumer.msm, 'convert', lambda *args, **kwargs: source)
    monkeypatch.setattr(
        consumer.msm,
        'get',
        lambda *args, **kwargs: consumer.puw.quantity(np.zeros((2, 2, 3)), 'nm'),
    )
    monkeypatch.setattr(
        consumer, 'reference_chemical_context', lambda *args, **kwargs: {'unit': True}
    )
    original_import = builtins.__import__

    def no_consumer_import(name, *args, **kwargs):
        if name.split('.')[0] == 'pharmacophoremt' and not create.allow_consumer:
            raise AssertionError('Recognition must not run in admission tests.')
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', no_consumer_import)

    def create(
        *,
        profile=CASTP_PROFILE,
        provider='castp',
        backend='files',
        frame=None,
        server='castpfold',
    ):
        handoff = tmp_path / 'handoff'
        handoff.mkdir()
        source_file = handoff / 'source.h5msm'
        source_file.write_bytes(b'Unit admission fixture; not a molecular source.\n')
        original = tmp_path / 'original-files'
        original.mkdir()
        pdb = original / 'submitted.pdb'
        pdb.write_bytes(b'REMARK Unit admission fixture only.\n')
        output = original / 'output'
        output.mkdir()
        metadata = {
            'structure_indices': [1] if frame is None else frame,
            'server': server,
            'selection': [0, 1],
            'submitted_atom_indices': [0, 1],
        }
        run = ProviderRun.capture(provider, backend, pdb, output, metadata=metadata)
        run.save(handoff / 'original.zip')
        receipt = {
            'profile': profile,
            'chemical_state': {'count': 1, 'reference_index': 0},
            'structure_index': 1,
            'checks': {'unit_admission_fixture': True},
            'source_sha256': hashlib.sha256(source_file.read_bytes()).hexdigest(),
            'run_id': run.run_id,
        }
        (handoff / 'receipt.json').write_text(json.dumps(receipt))
        return SimpleNamespace(
            handoff=handoff, output=tmp_path / 'consumer', run=run, source=source
        )

    create.allow_consumer = False
    return create


def test_castpfold_profile_uses_public_saved_recovery(admission_case, monkeypatch):
    case = admission_case()

    def recover(source, **kwargs):
        assert source is case.source
        assert kwargs == {
            'method': 'castpfold',
            'backend': 'files',
            'bundle_file': case.handoff / 'original.zip',
        }
        raise RecoveryReached

    monkeypatch.setattr(consumer.tmt, 'get_provider_output', recover)
    with pytest.raises(RecoveryReached):
        consumer.consume(case.handoff, case.output, **RECIPE)
    assert not case.output.exists()


@pytest.mark.parametrize('frame', [1, [0], [], [1, 1], [True], [1.0], '1'])
def test_castpfold_rejects_invalid_saved_frame_before_recovery(
    admission_case, monkeypatch, frame
):
    case = admission_case(frame=frame)

    def forbidden(*args, **kwargs):
        raise AssertionError('An invalid saved frame reached recovery.')

    monkeypatch.setattr(consumer.tmt, 'get_provider_output', forbidden)
    with pytest.raises(ValueError, match='run identity|structure context'):
        consumer.consume(case.handoff, case.output, **RECIPE)
    assert not case.output.exists()


@pytest.mark.parametrize('server', ['castp3', None, ''])
def test_castpfold_rejects_wrong_server_before_recovery(
    admission_case, monkeypatch, server
):
    case = admission_case(server=server)

    def forbidden(*args, **kwargs):
        raise AssertionError('An invalid server reached recovery.')

    monkeypatch.setattr(consumer.tmt, 'get_provider_output', forbidden)
    with pytest.raises(ValueError, match='server'):
        consumer.consume(case.handoff, case.output, **RECIPE)
    assert not case.output.exists()


@pytest.mark.parametrize('backend', ['server', 'library'])
def test_castpfold_rejects_wrong_backend_before_recovery(
    admission_case, monkeypatch, backend
):
    case = admission_case(backend=backend)

    def forbidden(*args, **kwargs):
        raise AssertionError('An invalid backend reached recovery.')

    monkeypatch.setattr(consumer.tmt, 'get_provider_output', forbidden)
    with pytest.raises(ValueError, match='run identity'):
        consumer.consume(case.handoff, case.output, **RECIPE)
    assert not case.output.exists()


def test_castpfold_rejects_changed_recovered_identity(admission_case, monkeypatch):
    case = admission_case()
    monkeypatch.setattr(
        consumer.tmt,
        'get_provider_output',
        lambda *args, **kwargs: SimpleNamespace(run=object()),
    )
    with pytest.raises(ValueError, match='Recovered original castp run identity'):
        consumer.consume(case.handoff, case.output, **RECIPE)
    assert not case.output.exists()


def _consumer_stubs(monkeypatch, case, *, empty=False):
    """Exercise recorder composition with explicit stubs, not molecular recognition."""
    package = ModuleType('pharmacophoremt')
    package.__version__ = 'unit-contract-stub'
    io = ModuleType('pharmacophoremt.io')
    modeler = ModuleType('pharmacophoremt.modeler')
    calls = []
    model = SimpleNamespace(
        metadata={},
        n_interaction_sites=1,
        interaction_sites=[
            SimpleNamespace(
                features=['hydrophobicity'],
                metadata={'atom_indices': [0]},
                center=consumer.puw.quantity([0.30, 0.0, 0.0], 'nm'),
                shape=SimpleNamespace(radius=consumer.puw.quantity(0.15, 'nm')),
                essential=True,
                weight=1,
            )
        ],
    )

    def get_features(source, **kwargs):
        assert source is case.source
        assert kwargs == {
            'selection': [0, 1],
            'structure_index': 1,
            'chemical_state': 0,
            'features': ['hydrophobicity'],
        }
        calls.append('recognition')
        return {'features': [] if empty else [{'atom_indices': [0]}]}

    def project(inventory, **kwargs):
        calls.append('projection')
        assert len(inventory['features']) == 1
        assert len(kwargs['projection_specs']) == 1
        spec = kwargs['projection_specs'][0]
        assert spec['feature_index'] == 0 and spec['distance'] == '0.30 nm'
        assert kwargs['radius'] == '0.15 nm'
        np.testing.assert_array_equal(
            consumer.puw.get_value(spec['projection_direction']), [1.0, 0.0, 0.0]
        )
        return model

    def save(model, path):
        path.write_text('{"unit_contract_stub": true}\n')

    io.to_json = save
    io.load_json = lambda path: copy.deepcopy(model)
    modeler.get_features = get_features
    modeler.from_receptor_projections = project
    monkeypatch.setitem(sys.modules, 'pharmacophoremt', package)
    monkeypatch.setitem(sys.modules, 'pharmacophoremt.io', io)
    monkeypatch.setitem(sys.modules, 'pharmacophoremt.modeler', modeler)
    monkeypatch.setattr(
        consumer.tmt,
        'get_provider_output',
        lambda *args, **kwargs: SimpleNamespace(
            run=case.run,
            pockets=[
                SimpleNamespace(
                    source_id='Pocket 1', atom_indices=(0, 1), atom_role='lining_atoms'
                )
            ],
        ),
    )
    return calls


def test_castpfold_receipt_preserves_original_route(admission_case, monkeypatch):
    case = admission_case()
    admission_case.allow_consumer = True
    calls = _consumer_stubs(monkeypatch, case)
    receipt = consumer.consume(case.handoff, case.output, **RECIPE)
    route = {'provider': 'castp', 'backend': 'files', 'server': 'castpfold'}
    for key, value in route.items():
        assert receipt[key] == value and receipt['context'][key] == value
    assert receipt['context']['original_run_id'] == case.run.run_id
    assert receipt['context']['pocket_id'] == 'Pocket 1'
    assert receipt['sites'][0]['essential'] is True
    assert receipt['sites'][0]['weight'] == 1
    assert calls == ['recognition', 'projection']
    assert all(receipt['checks'].values())
    assert json.loads((case.output / 'receipt.json').read_text()) == receipt


def test_castpfold_empty_hydrophobic_recognition_has_no_fallback(
    admission_case, monkeypatch
):
    case = admission_case()
    admission_case.allow_consumer = True
    calls = _consumer_stubs(monkeypatch, case, empty=True)
    with pytest.raises(ValueError, match='no hydrophobic features'):
        consumer.consume(case.handoff, case.output, **RECIPE)
    assert calls == ['recognition']
    assert not case.output.exists()


def test_castpfold_native_chemistry_failure_propagates(admission_case, monkeypatch):
    case = admission_case()
    admission_case.allow_consumer = True
    calls = _consumer_stubs(monkeypatch, case)
    native_error = RuntimeError('Native declared chemistry is inconsistent.')

    def reject_chemistry(*args, **kwargs):
        calls.append('owner_rejection')
        raise native_error

    monkeypatch.setattr(
        sys.modules['pharmacophoremt.modeler'], 'get_features', reject_chemistry
    )
    with pytest.raises(RuntimeError) as raised:
        consumer.consume(case.handoff, case.output, **RECIPE)
    assert raised.value is native_error
    assert calls == ['owner_rejection']
    assert not case.output.exists()


@pytest.mark.parametrize('profile,provider,backend', EXISTING_PROFILES)
def test_castp_route_fields_do_not_change_existing_receipts(
    admission_case, monkeypatch, profile, provider, backend
):
    case = admission_case(profile=profile, provider=provider, backend=backend, frame=1)
    admission_case.allow_consumer = True
    _consumer_stubs(monkeypatch, case)
    receipt = consumer.consume(case.handoff, case.output, **RECIPE)
    for key in ('provider', 'backend', 'server'):
        assert key not in receipt and key not in receipt['context']


@pytest.mark.parametrize('profile,provider,backend', EXISTING_PROFILES)
def test_existing_profiles_preserve_integer_frame_admission(
    admission_case, monkeypatch, profile, provider, backend
):
    case = admission_case(profile=profile, provider=provider, backend=backend, frame=1)

    def recover(source, **kwargs):
        assert source is case.source
        assert kwargs['method'] == provider and kwargs['backend'] == 'files'
        if provider != 'fpocket':
            assert kwargs['bundle_file'] == case.handoff / 'original.zip'
        raise RecoveryReached

    monkeypatch.setattr(consumer.tmt, 'get_provider_output', recover)
    with pytest.raises(RecoveryReached):
        consumer.consume(case.handoff, case.output, **RECIPE)


@pytest.mark.parametrize('profile,provider,backend', EXISTING_PROFILES)
@pytest.mark.parametrize('frame', [[1], True])
def test_existing_profiles_do_not_accept_castp_frame_schema(
    admission_case, monkeypatch, profile, provider, backend, frame
):
    case = admission_case(
        profile=profile, provider=provider, backend=backend, frame=frame
    )

    def forbidden(*args, **kwargs):
        raise AssertionError('An invalid legacy profile reached recovery.')

    monkeypatch.setattr(consumer.tmt, 'get_provider_output', forbidden)
    with pytest.raises(ValueError, match='structure context'):
        consumer.consume(case.handoff, case.output, **RECIPE)
