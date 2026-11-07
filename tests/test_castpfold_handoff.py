"""Mocked CASTpFold lifecycle guards; no networking or chemistry runs."""

import base64
import hashlib
import io
import json
import zipfile
from importlib import import_module
from types import SimpleNamespace

import pytest

import devtools.qualify_castpfold_handoff as pilot
from topomt.provider_output import ProviderRun


@pytest.fixture(autouse=True)
def no_real_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Networking is forbidden in lifecycle unit tests.')

    client = import_module('topomt.third_party.castp.servers.castpfold')
    monkeypatch.setattr(client, 'urlopen', forbidden)


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    source = SimpleNamespace(
        chemical_states=SimpleNamespace(
            n_chemical_states=1, reference_chemical_state_index=0
        )
    )
    seed = tmp_path / 'seed.h5msm'
    seed.write_bytes(b'Synthetic source, not prepared chemistry.')
    root = tmp_path / 'handoff'
    monkeypatch.setattr(
        pilot, 'prepare_reference_source', lambda path: (source, [0, 2, 3])
    )
    monkeypatch.setattr(pilot.msm, 'select', lambda *a, **k: [0, 1, 2])
    monkeypatch.setattr(pilot.msm, 'get', lambda *a, **k: 4 if k.get('n_atoms') else 2)
    monkeypatch.setattr(
        pilot.msm,
        'convert',
        lambda item, **k: (
            k['output_filename'].write_bytes(b'Serialized source stub.')
            if 'output_filename' in k
            else source
        ),
    )
    monkeypatch.setattr(
        pilot.msm.physchem, 'get_chemical_readiness', lambda *a, **k: {'fields': {}}
    )

    def export(item, *, tmpdir, selection, **kwargs):
        assert selection == [0, 2]
        path = tmpdir / 'input.pdb'
        path.write_text(
            'ATOM      7  N   ALA A   1       1.000   2.000   3.000  1.00  0.00           N\nATOM     11  CA  ALA A   1       4.000   5.000   6.000  1.00  0.00           C\nEND\n'
        )
        return path, [0, 2]

    monkeypatch.setattr(pilot, 'prepare_wrapper_input_pdb', export)
    monkeypatch.setattr(pilot, '_validate_map', lambda *a, **k: None)
    monkeypatch.setattr(
        pilot,
        'source_input_context',
        lambda item, *a: {'stamp': getattr(item, 'stamp', 0)},
        raising=False,
    )
    monkeypatch.setattr(
        pilot, 'reference_chemical_context', lambda *a, **k: {'state': 0}, raising=False
    )
    pilot.prepare(seed, root)
    return root


def test_prepare_retains_explicit_heavy_map_and_state(prepared):
    receipt = json.loads((prepared / 'preflight.json').read_text())
    mapping = json.loads((prepared / 'map.json').read_text())
    assert mapping['row_to_source'] == [0, 2]
    assert mapping['serial_to_source'] == {'7': 0, '11': 2}
    assert receipt['structure_index'] == 1
    assert receipt['chemical_state'] == {'count': 1, 'reference_index': 0}
    assert all(value is True for value in receipt['checks'].values())


@pytest.mark.parametrize(
    'marker', ['{}', '{"state":"failed"}', '{"state":"submitting"}']
)
def test_existing_submission_blocks_any_resubmit(prepared, marker):
    (prepared / 'submission.json').write_text(marker)
    with pytest.raises(FileExistsError):
        pilot.submit(prepared)


@pytest.fixture
def lifecycle(prepared, monkeypatch):
    calls = []
    sources = []
    source = pilot.msm.convert(prepared / 'source.h5msm')
    output = prepared / 'mock-output'
    output.mkdir()

    class Client:
        def submit(self, path, *, probe_radius, email, submission_file):
            calls.append(('POST', str(path)))
            acknowledgement = {'success': True, 'jobid': 'j_unit'}
            raw = json.dumps(acknowledgement).encode()
            receipt = {
                'schema_version': 1,
                'provider': 'castp',
                'server': 'castpfold',
                'state': 'submitted_pending',
                'jobid': 'j_unit',
                'input_pdb': {
                    'filename': path.name,
                    'bytes': path.stat().st_size,
                    'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                },
                'parameters': {
                    'probe_radius': {'value': probe_radius, 'unit': 'angstroms'},
                    'email': email,
                },
                'endpoint': 'https://cfold.bme.uic.edu/castpfold/submit_calc.php',
                'acknowledgement': acknowledgement,
                'http': {
                    'status': 200,
                    'response_base64': base64.b64encode(raw).decode(),
                    'response_sha256': hashlib.sha256(raw).hexdigest(),
                },
            }
            with submission_file.open('x') as stream:
                json.dump(receipt, stream)
            return 'j_unit'

        def download_result_zip_bytes(self, jobid, **kwargs):
            calls.append(('GET', jobid))
            return archive.raw

    monkeypatch.setattr(pilot, 'CastpFoldClient', Client)

    def reader(item, **kwargs):
        sources.append(item)
        calls.append(('reader', kwargs))
        run = (
            ProviderRun.load(kwargs['bundle_file'])
            if 'bundle_file' in kwargs
            else ProviderRun.capture(
                'castp',
                'files',
                prepared / 'input.pdb',
                output,
                metadata={'server': 'castpfold', 'jobid': 'j_unit'},
            )
        )
        return SimpleNamespace(run=run, pockets=[SimpleNamespace(source_id='Pocket 1')])

    monkeypatch.setattr(pilot.tmt, 'get_provider_output', reader)
    monkeypatch.setattr(pilot, 'pocket_outputs_agree', lambda a, b: a.run == b.run)

    def archive(serials=(11, 7)):
        rows = (prepared / 'input.pdb').read_text().splitlines()[:2]
        by_serial = {int(row[6:11]): row for row in rows}
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as files:
            files.writestr(
                'j_unit.pdb', '\n'.join(by_serial[s] for s in serials) + '\nEND\n'
            )
        archive.raw = buffer.getvalue()

    archive()
    return SimpleNamespace(
        root=prepared, calls=calls, archive=archive, sources=sources, source=source
    )


def test_mocked_collection_preserves_returned_row_order_and_identity(lifecycle):
    case = lifecycle
    pilot.submit(case.root)
    receipt = pilot.collect(case.root)
    binding = next(value for kind, value in case.calls if kind == 'reader')
    assert binding['method'] == 'castpfold' and binding['backend'] == 'files'
    assert binding['source_atom_indices'] == binding['selection'] == [2, 0]
    assert binding['structure_indices'] == 1 and binding['chemical_state'] == 0
    assert binding['provider_jobid'] == 'j_unit' and binding['probe_radius'] == 1.4
    assert receipt['profile'] == pilot.PROFILE
    assert (receipt['provider'], receipt['backend'], receipt['server']) == (
        'castp',
        'files',
        'castpfold',
    )
    assert all(value is True for value in receipt['checks'].values())
    assert ProviderRun.load(case.root / 'original.zip').run_id == receipt['run_id']
    assert json.loads((case.root / 'receipt.json').read_text()) == receipt
    with pytest.raises(FileExistsError):
        pilot.collect(case.root)
    assert [kind for kind, _ in case.calls].count('POST') == 1


@pytest.mark.parametrize(
    'artifact', ['source.h5msm', 'input.pdb', 'map.json', 'readiness.json']
)
def test_changed_prepared_artifact_fails_before_post(lifecycle, artifact):
    (lifecycle.root / artifact).write_bytes(b'changed')
    with pytest.raises(ValueError, match='hash|artifact'):
        pilot.submit(lifecycle.root)
    assert not lifecycle.calls


@pytest.mark.parametrize(
    'field,value',
    [
        ('state', 'failed'),
        ('schema_version', True),
        ('jobid', '../escape'),
        ('parameters', None),
    ],
)
def test_invalid_submission_receipt_never_reaches_get(lifecycle, field, value):
    pilot.submit(lifecycle.root)
    path = lifecycle.root / 'submission.json'
    receipt = json.loads(path.read_text())
    receipt[field] = value
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='submission'):
        pilot.collect(lifecycle.root)
    assert not any(kind == 'GET' for kind, _ in lifecycle.calls)


@pytest.mark.parametrize('serials', [(7,), (7, 7)])
def test_every_submitted_atom_must_return_once(lifecycle, serials):
    pilot.submit(lifecycle.root)
    lifecycle.archive(serials)
    with pytest.raises(ValueError, match='submitted'):
        pilot.collect(lifecycle.root)
    assert not any(kind == 'reader' for kind, _ in lifecycle.calls)


def test_changed_download_is_not_redownloaded_or_rebound(lifecycle, monkeypatch):
    pilot.submit(lifecycle.root)

    def fail(*args, **kwargs):
        raise ValueError('identity mismatch')

    monkeypatch.setattr(pilot.tmt, 'get_provider_output', fail)
    with pytest.raises(ValueError, match='identity mismatch'):
        pilot.collect(lifecycle.root)
    (lifecycle.root / 'result.zip').write_bytes(b'changed')
    with pytest.raises(ValueError, match='hash'):
        pilot.collect(lifecycle.root)
    assert [kind for kind, _ in lifecycle.calls].count('GET') == 1


@pytest.mark.parametrize('value', [None, {'../source.h5msm': 'bad'}])
def test_artifact_manifest_cannot_override_paths(prepared, value):
    path = prepared / 'preflight.json'
    receipt = json.loads(path.read_text())
    receipt['artifacts'] = value
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='artifact'):
        pilot.submit(prepared)


def test_symlink_prepared_artifact_is_rejected(prepared):
    path = prepared / 'input.pdb'
    original = prepared / 'original-input.pdb'
    path.rename(original)
    path.symlink_to(original)
    with pytest.raises(ValueError, match='artifact'):
        pilot.submit(prepared)


def test_failed_transport_marker_prevents_blind_retry(lifecycle, monkeypatch):
    calls = []

    class FailedClient:
        def submit(self, path, **kwargs):
            calls.append(path)
            kwargs['submission_file'].write_text('{"state":"failed"}')
            raise TimeoutError('Remote creation is unknown.')

    monkeypatch.setattr(pilot, 'CastpFoldClient', FailedClient)
    with pytest.raises(TimeoutError):
        pilot.submit(lifecycle.root)
    with pytest.raises(FileExistsError):
        pilot.submit(lifecycle.root)
    assert len(calls) == 1


@pytest.mark.parametrize('value', [True, 2.0, None])
def test_changed_or_malformed_probe_never_reaches_get(lifecycle, value):
    pilot.submit(lifecycle.root)
    path = lifecycle.root / 'submission.json'
    receipt = json.loads(path.read_text())
    receipt['parameters']['probe_radius']['value'] = value
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='submission'):
        pilot.collect(lifecycle.root)
    assert not any(kind == 'GET' for kind, _ in lifecycle.calls)


def test_boolean_state_count_is_not_an_integer_profile(prepared):
    path = prepared / 'preflight.json'
    receipt = json.loads(path.read_text())
    receipt['chemical_state']['count'] = True
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='preflight'):
        pilot.submit(prepared)


@pytest.mark.parametrize(
    'field,value', [('http', None), ('endpoint', 'https://example.org/other')]
)
def test_ack_receipt_route_and_shape_are_checked(lifecycle, field, value):
    pilot.submit(lifecycle.root)
    path = lifecycle.root / 'submission.json'
    receipt = json.loads(path.read_text())
    receipt[field] = value
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='submission|acknowledgement'):
        pilot.collect(lifecycle.root)
    assert not any(kind == 'GET' for kind, _ in lifecycle.calls)


@pytest.mark.parametrize(
    'field,value', [('response_base64', '!invalid'), ('response_sha256', '0' * 64)]
)
def test_raw_ack_integrity_is_checked_before_get(lifecycle, field, value):
    pilot.submit(lifecycle.root)
    path = lifecycle.root / 'submission.json'
    receipt = json.loads(path.read_text())
    receipt['http'][field] = value
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='submission|acknowledgement'):
        pilot.collect(lifecycle.root)
    assert not any(kind == 'GET' for kind, _ in lifecycle.calls)


def test_edited_acknowledgement_must_match_raw_response(lifecycle):
    pilot.submit(lifecycle.root)
    path = lifecycle.root / 'submission.json'
    receipt = json.loads(path.read_text())
    receipt['jobid'] = receipt['acknowledgement']['jobid'] = 'j_other'
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='submission|acknowledgement'):
        pilot.collect(lifecycle.root)


def test_receipt_write_failure_resumes_same_bundle_without_get(lifecycle, monkeypatch):
    pilot.submit(lifecycle.root)
    writer = pilot._write

    def interrupted(path, value):
        if path.name == 'receipt.json':
            raise OSError('Interrupted final receipt write.')
        writer(path, value)

    monkeypatch.setattr(pilot, '_write', interrupted)
    with pytest.raises(OSError, match='Interrupted'):
        pilot.collect(lifecycle.root)
    bundle = lifecycle.root / 'original.zip'
    before = bundle.read_bytes()
    monkeypatch.setattr(pilot, '_write', writer)
    receipt = pilot.collect(lifecycle.root)
    assert bundle.read_bytes() == before
    assert ProviderRun.load(bundle).run_id == receipt['run_id']
    assert [kind for kind, _ in lifecycle.calls].count('GET') == 1
    assert [kind for kind, _ in lifecycle.calls].count('POST') == 1


def test_recovery_uses_an_independent_source_read(lifecycle, monkeypatch):
    pilot.submit(lifecycle.root)
    monkeypatch.setattr(
        pilot.msm,
        'convert',
        lambda *a, **k: SimpleNamespace(
            chemical_states=SimpleNamespace(
                n_chemical_states=1, reference_chemical_state_index=0
            )
        ),
    )
    pilot.collect(lifecycle.root)
    assert lifecycle.sources[0] is not lifecycle.sources[1]


def test_in_memory_source_mutation_is_not_hidden_by_unchanged_file(
    lifecycle, monkeypatch
):
    pilot.submit(lifecycle.root)
    reader = pilot.tmt.get_provider_output

    def mutate(source, **kwargs):
        result = reader(source, **kwargs)
        if 'zip_file' in kwargs:
            source.stamp = 1
        return result

    monkeypatch.setattr(pilot.tmt, 'get_provider_output', mutate)
    with pytest.raises(ValueError, match='checks failed'):
        pilot.collect(lifecycle.root)
    assert not (lifecycle.root / 'receipt.json').exists()
