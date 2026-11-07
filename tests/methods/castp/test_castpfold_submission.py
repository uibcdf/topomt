"""Persist one original-server submission without permitting duplicate POSTs."""

import base64
import hashlib
import json
from datetime import datetime
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError

import pytest

from topomt import pyunitwizard as puw
from topomt.third_party.castp.servers import castpfold


class Response(BytesIO):
    def __init__(self, payload, *, status=200, content_type='application/json'):
        super().__init__(payload)
        self.status = status
        self.headers = {'Content-Type': content_type}
        self.url = castpfold.SUBMIT_URL

    def geturl(self):
        return self.url


@pytest.fixture
def pdb(tmp_path):
    path = tmp_path / 'submitted.pdb'
    path.write_bytes(b'ATOM      1  CA  ALA A   1       0.000   0.000   0.000\nEND\n')
    return path


def test_legacy_submit_keeps_string_return_without_recording(pdb, monkeypatch):
    monkeypatch.setattr(
        castpfold,
        'urlopen',
        lambda *a, **k: Response(b'{"success":true,"jobid":"j_legacy"}'),
    )
    assert castpfold.CastpFoldClient().submit(pdb) == 'j_legacy'


def test_receipt_exists_before_post_and_exact_ack_is_saved_before_parsing(
    pdb, tmp_path, monkeypatch
):
    receipt = tmp_path / 'new' / 'submission.json'
    raw = b'{\n "success": true, "jobid": "j_recorded_1", "probe": "1.4"\n}\n'
    requests = []

    def post(request, *, timeout):
        saved = json.loads(receipt.read_text())
        assert saved['state'] == 'submitting'
        assert saved['provider'] == 'castp' and saved['server'] == 'castpfold'
        assert saved['endpoint'] == castpfold.SUBMIT_URL
        assert saved['input_pdb'] == {
            'filename': pdb.name,
            'bytes': pdb.stat().st_size,
            'sha256': hashlib.sha256(pdb.read_bytes()).hexdigest(),
        }
        assert saved['parameters'] == {
            'probe_radius': {'value': pytest.approx(1.4), 'unit': 'angstroms'},
            'email': 'N/A',
        }
        assert (
            datetime.fromisoformat(saved['started_utc']).utcoffset().total_seconds()
            == 0
        )
        assert (
            request.get_method() == 'POST' and request.data.count(pdb.read_bytes()) == 1
        )
        requests.append(request)
        return Response(raw)

    def parse(data, *, provider):
        saved = json.loads(receipt.read_text())
        assert base64.b64decode(saved['http']['response_base64']) == raw == data
        assert saved['http']['response_sha256'] == hashlib.sha256(raw).hexdigest()
        assert saved['http']['status'] == 200
        assert saved['http']['final_url'] == castpfold.SUBMIT_URL
        assert saved['http']['content_type'] == 'application/json'
        assert saved['state'] == 'submitting' and saved['acknowledgement'] is None
        return json.loads(data)

    monkeypatch.setattr(castpfold, 'urlopen', post)
    monkeypatch.setattr(castpfold, 'read_json', parse, raising=False)
    jobid = castpfold.CastpFoldClient(timeout=7).submit(
        pdb, probe_radius=puw.quantity(0.14, 'nm'), submission_file=receipt
    )
    saved = json.loads(receipt.read_text())
    assert jobid == saved['jobid'] == 'j_recorded_1'
    assert saved['state'] == 'submitted_pending' and saved['schema_version'] == 1
    assert saved['acknowledgement'] == json.loads(raw)
    assert saved['updated_utc'] >= saved['started_utc']
    assert len(requests) == 1
    assert sorted(p.name for p in receipt.parent.iterdir()) == ['submission.json']


@pytest.mark.parametrize('state', ['submitting', 'submitted_pending', 'failed'])
def test_existing_receipt_blocks_post_and_is_never_overwritten(
    pdb, tmp_path, monkeypatch, state
):
    receipt = tmp_path / 'submission.json'
    before = json.dumps({'state': state, 'jobid': 'j_existing'}).encode()
    receipt.write_bytes(before)

    def forbidden(*args, **kwargs):
        pytest.fail('A receipt must prevent another POST, including after failure.')

    monkeypatch.setattr(castpfold, 'urlopen', forbidden)
    with pytest.raises(FileExistsError):
        castpfold.CastpFoldClient().submit(pdb, submission_file=receipt)
    assert receipt.read_bytes() == before


@pytest.mark.parametrize(
    'payload',
    [
        b'not-json',
        b'{"success":true,',
        b'\xff',
        b'{"success":false,"success":true,"jobid":"j_duplicate"}',
    ],
)
def test_malformed_ack_keeps_raw_bytes_and_failed_state(
    pdb, tmp_path, monkeypatch, payload
):
    receipt = tmp_path / 'submission.json'
    monkeypatch.setattr(castpfold, 'urlopen', lambda *a, **k: Response(payload))
    with pytest.raises(ValueError):
        castpfold.CastpFoldClient().submit(pdb, submission_file=receipt)
    saved = json.loads(receipt.read_text())
    assert saved['state'] == 'failed' and saved['jobid'] is None
    assert base64.b64decode(saved['http']['response_base64']) == payload
    assert saved['http']['response_sha256'] == hashlib.sha256(payload).hexdigest()


@pytest.mark.parametrize(
    'ack',
    [
        {'success': False, 'jobid': 'j_rejected'},
        {'success': 1, 'jobid': 'j_rejected'},
        {'jobid': 'j_rejected'},
        {'success': True, 'jobid': ''},
        {'success': True, 'jobid': '../job'},
        {'success': True, 'jobid': 'j_bad/path'},
        {'success': True, 'jobid': 'j_bad\n'},
        {'success': True, 'jobid': 1},
        ['success', 'j_not_object'],
    ],
)
def test_unaccepted_ack_is_retained_without_a_resumable_job(
    pdb, tmp_path, monkeypatch, ack
):
    receipt = tmp_path / 'submission.json'
    payload = json.dumps(ack).encode()
    monkeypatch.setattr(castpfold, 'urlopen', lambda *a, **k: Response(payload))
    with pytest.raises(RuntimeError):
        castpfold.CastpFoldClient().submit(pdb, submission_file=receipt)
    saved = json.loads(receipt.read_text())
    assert saved['state'] == 'failed' and saved['jobid'] is None
    assert saved['acknowledgement'] == ack
    assert base64.b64decode(saved['http']['response_base64']) == payload


@pytest.mark.parametrize(
    'error',
    [TimeoutError('submission timed out'), ConnectionError('transport unavailable')],
)
def test_transport_failure_is_recorded_and_original_exception_propagates(
    pdb, tmp_path, monkeypatch, error
):
    receipt = tmp_path / 'submission.json'

    def failing(*args, **kwargs):
        assert json.loads(receipt.read_text())['state'] == 'submitting'
        raise error

    monkeypatch.setattr(castpfold, 'urlopen', failing)
    with pytest.raises(type(error)) as caught:
        castpfold.CastpFoldClient().submit(pdb, submission_file=receipt)
    assert caught.value is error
    saved = json.loads(receipt.read_text())
    assert saved['state'] == 'failed' and saved['http'] is None
    assert saved['jobid'] is None and saved['acknowledgement'] is None
    assert saved['error']['type'] == type(error).__name__


def test_parser_exception_identity_is_preserved_when_failure_is_recorded(
    pdb, tmp_path, monkeypatch
):
    receipt = tmp_path / 'submission.json'
    error = ValueError('sentinel parse failure')

    def parser(*args, **kwargs):
        raise error

    monkeypatch.setattr(castpfold, 'read_json', parser, raising=False)
    monkeypatch.setattr(
        castpfold,
        'urlopen',
        lambda *a, **k: Response(b'{"success":true,"jobid":"j_unit"}'),
    )
    with pytest.raises(ValueError) as caught:
        castpfold.CastpFoldClient().submit(pdb, submission_file=receipt)
    assert caught.value is error
    saved = json.loads(receipt.read_text())
    assert saved['state'] == 'failed'
    assert saved['error']['type'] == 'ValueError'


@pytest.mark.parametrize('success', [False, 1])
def test_success_flag_is_required_even_without_a_receipt(pdb, monkeypatch, success):
    payload = json.dumps({'success': success, 'jobid': 'j_not_accepted'}).encode()
    monkeypatch.setattr(castpfold, 'urlopen', lambda *a, **k: Response(payload))
    with pytest.raises(RuntimeError):
        castpfold.CastpFoldClient().submit(pdb)


def test_exclusive_reservation_wins_a_race_without_touching_the_other_receipt(
    pdb, tmp_path, monkeypatch
):
    receipt = tmp_path / 'submission.json'
    other = b'{"state":"submitted_pending","jobid":"j_other"}'
    encode = castpfold._encode_multipart_form_data

    def race(**kwargs):
        receipt.write_bytes(other)
        return encode(**kwargs)

    def forbidden(*args, **kwargs):
        pytest.fail('A competing reservation must prevent the POST.')

    monkeypatch.setattr(castpfold, '_encode_multipart_form_data', race)
    monkeypatch.setattr(castpfold, 'urlopen', forbidden)
    with pytest.raises(FileExistsError):
        castpfold.CastpFoldClient().submit(pdb, submission_file=receipt)
    assert receipt.read_bytes() == other


def test_failure_recording_error_does_not_replace_original_transport_exception(
    pdb, tmp_path, monkeypatch
):
    receipt = tmp_path / 'submission.json'
    original = TimeoutError('remote outcome is unknown')
    write = castpfold._write_submission_file

    def broken_update(path, value, *, exclusive=False):
        if value['state'] == 'failed':
            raise OSError('storage unavailable')
        return write(path, value, exclusive=exclusive)

    def timeout(*args, **kwargs):
        raise original

    monkeypatch.setattr(castpfold, '_write_submission_file', broken_update)
    monkeypatch.setattr(castpfold, 'urlopen', timeout)
    with pytest.raises(TimeoutError) as caught:
        castpfold.CastpFoldClient().submit(pdb, submission_file=receipt)
    assert caught.value is original
    assert any('OSError' in note for note in original.__notes__)
    assert json.loads(receipt.read_text())['state'] == 'submitting'
    with pytest.raises(FileExistsError):
        castpfold.CastpFoldClient().submit(pdb, submission_file=receipt)


def test_receipt_updates_replace_complete_json_on_the_same_filesystem(
    pdb, tmp_path, monkeypatch
):
    receipt = tmp_path / 'submission.json'
    replace = castpfold.os.replace
    transitions = []

    def observe(source, destination):
        if Path(destination) == receipt:
            assert Path(source).parent == receipt.parent
            before = json.loads(receipt.read_text())
            after = json.loads(Path(source).read_text())
            transitions.append((before['state'], after['state']))
        return replace(source, destination)

    monkeypatch.setattr(castpfold.os, 'replace', observe)
    monkeypatch.setattr(
        castpfold,
        'urlopen',
        lambda *a, **k: Response(b'{"success":true,"jobid":"j_atomic"}'),
    )
    castpfold.CastpFoldClient().submit(pdb, submission_file=receipt)
    assert transitions and transitions[-1][1] == 'submitted_pending'
    assert all(left == 'submitting' for left, right in transitions)
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        'submission.json',
        'submitted.pdb',
    ]


def test_receipt_hash_and_multipart_use_the_same_input_snapshot(
    pdb, tmp_path, monkeypatch
):
    receipt = tmp_path / 'submission.json'
    original = pdb.read_bytes()
    encode = castpfold._encode_multipart_form_data

    def mutate_after_snapshot(**kwargs):
        pdb.write_bytes(b'changed after admission')
        return encode(**kwargs)

    def post(request, **kwargs):
        assert request.data.count(original) == 1
        assert b'changed after admission' not in request.data
        return Response(b'{"success":true,"jobid":"j_snapshot"}')

    monkeypatch.setattr(castpfold, '_encode_multipart_form_data', mutate_after_snapshot)
    monkeypatch.setattr(castpfold, 'urlopen', post)
    castpfold.CastpFoldClient().submit(pdb, submission_file=receipt)
    saved = json.loads(receipt.read_text())
    assert saved['input_pdb']['bytes'] == len(original)
    assert saved['input_pdb']['sha256'] == hashlib.sha256(original).hexdigest()


def test_http_error_response_is_retained_without_replacing_the_original_error(
    pdb, tmp_path, monkeypatch
):
    receipt = tmp_path / 'submission.json'
    raw = b'upstream unavailable\n'
    original = HTTPError(
        castpfold.SUBMIT_URL,
        503,
        'unavailable',
        {'Content-Type': 'text/plain'},
        BytesIO(raw),
    )

    def fail(*args, **kwargs):
        raise original

    monkeypatch.setattr(castpfold, 'urlopen', fail)
    with pytest.raises(HTTPError) as caught:
        castpfold.CastpFoldClient().submit(pdb, submission_file=receipt)
    assert caught.value is original
    saved = json.loads(receipt.read_text())
    assert saved['state'] == 'failed' and saved['jobid'] is None
    assert saved['http']['status'] == 503
    assert saved['http']['content_type'] == 'text/plain'
    assert base64.b64decode(saved['http']['response_base64']) == raw
    assert saved['http']['response_sha256'] == hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize('name_bytes', [242, 255])
def test_valid_long_receipt_name_persists_ack_and_final_state(
    pdb, tmp_path, monkeypatch, name_bytes
):
    receipt = tmp_path / ('s' * (name_bytes - 5) + '.json')
    raw = b'{"success":true,"jobid":"j_long_receipt"}'
    posts = []

    def post(request, **kwargs):
        assert json.loads(receipt.read_text())['state'] == 'submitting'
        posts.append(request.get_method())
        return Response(raw)

    monkeypatch.setattr(castpfold, 'urlopen', post)
    assert (
        castpfold.CastpFoldClient().submit(pdb, submission_file=receipt)
        == 'j_long_receipt'
    )
    saved = json.loads(receipt.read_text())
    assert saved['state'] == 'submitted_pending' and saved['jobid'] == 'j_long_receipt'
    assert base64.b64decode(saved['http']['response_base64']) == raw
    assert saved['http']['response_sha256'] == hashlib.sha256(raw).hexdigest()
    assert posts == ['POST']
    assert {path.name for path in tmp_path.iterdir()} == {pdb.name, receipt.name}
