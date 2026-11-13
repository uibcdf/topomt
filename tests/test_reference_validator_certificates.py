"""Proof coverage and model identity are checked independently of search."""

import copy
import json
import subprocess
import sys
from fractions import Fraction

import pytest

from devtools.reference_validator.model import (
    Atom,
    Box,
    Model,
    decode_scalar,
    encode_point,
    point,
    scalar,
)
from devtools.reference_validator.producer import partition
from devtools.reference_validator.verify import Limits, verify


def make_model(radius=1):
    return Model(
        (Atom(8, point((0, 0, 0)), scalar(radius)),),
        scalar(0),
        Box(point((-2, -2, -2)), point((2, 2, 2))),
        'a' * 64,
    )


def test_partial_partition_bounds_are_not_a_complete_component_count():
    model = make_model()
    shallow = verify(model, partition(model, max_depth=0, max_leaves=8))
    refined_cert = partition(model, max_depth=3, max_leaves=512)
    refined = verify(model, refined_cert)
    assert shallow['volume_lower'] == ['0', '1']
    assert shallow['volume_upper'] == ['64', '1']
    assert 0 < decode_scalar(refined['volume_lower'])
    assert decode_scalar(refined['volume_upper']) < 64
    assert refined['topology_complete'] is False
    assert refined['n_components'] is None
    assert refined['trusted_arithmetic'] == 'stdlib-fraction/1'
    assert refined['certificate_sha256']


def test_full_exclusion_and_full_free_convex_domain_have_proofs():
    model = make_model(radius=4)
    report = verify(model, partition(model, max_depth=0))
    assert report['topology_complete'] and report['n_components'] == 0
    assert report['volume_lower'] == report['volume_upper'] == ['0', '1']
    free = Model((), scalar(0), model.domain, 'b' * 64)
    report = verify(free, partition(free, max_depth=0))
    assert report['topology_complete'] and report['n_components'] == 1
    assert report['volume_lower'] == report['volume_upper'] == ['64', '1']


def test_corrupted_partition_and_changed_model_are_rejected():
    model = make_model()
    cert = partition(model, max_depth=1)
    for mutate in (
        'missing',
        'duplicate',
        'ancestor',
        'false_free',
        'false_cover',
        'wrong_model',
        'wrong_schema',
        'unknown_claim',
    ):
        bad = copy.deepcopy(cert)
        if mutate == 'missing':
            bad['leaves'].pop()
        elif mutate == 'duplicate':
            bad['leaves'].append(bad['leaves'][0])
        elif mutate == 'ancestor':
            bad['leaves'].append({'path': '', 'state': 'unknown'})
        elif mutate == 'false_free':
            bad['leaves'][0] = {'path': '0', 'state': 'free'}
        elif mutate == 'false_cover':
            bad['leaves'][0] = {'path': '0', 'state': 'blocked', 'atom_id': 8}
        elif mutate == 'wrong_model':
            bad['model_sha256'] = 'f' * 64
        elif mutate == 'wrong_schema':
            bad['schema'] = 'unknown'
        else:
            bad['topology_complete'] = True
        with pytest.raises(ValueError):
            verify(model, bad)
    with pytest.raises(ValueError):
        verify(make_model(radius=2), cert)


def test_point_blockage_never_implies_empty_region():
    model = make_model()
    cert = {
        'schema': 'topomt.reference-validator.certificate/1',
        'kind': 'point',
        'model_sha256': model.digest,
        'arithmetic': 'rational-exact/1',
        'point': encode_point(point((0, 0, 0))),
        'claim': 'blocked',
    }
    result = verify(model, cert)
    assert result['point_state'] == 'blocked'
    assert not result['topology_complete'] and result['n_components'] is None
    cert['point'] = encode_point(point((3, 0, 0)))
    with pytest.raises(ValueError):
        verify(model, cert)
    cert['claim'] = 'outside_domain'
    assert verify(model, cert)['point_state'] == 'outside_domain'


def test_wrong_arithmetic_and_checker_budgets_reject_instead_of_guessing():
    model = make_model()
    cert = partition(model, max_depth=1)
    with pytest.raises(ValueError):
        verify(model, cert, limits=Limits(max_leaves=1))
    cert['arithmetic'] = 'float64'
    with pytest.raises(ValueError):
        verify(model, cert)


def test_independent_refinement_bounds_are_nested():
    model = make_model()
    last_lower, last_upper = Fraction(), Fraction(64)
    for depth in range(4):
        report = verify(model, partition(model, max_depth=depth))
        lower, upper = map(
            decode_scalar, (report['volume_lower'], report['volume_upper'])
        )
        assert last_lower <= lower <= upper <= last_upper
        last_lower, last_upper = lower, upper


def test_resource_ceiling_retains_a_complete_unknown_partition():
    model = make_model()
    cert = partition(model, max_depth=12, max_leaves=1)
    assert len(cert['leaves']) == 1
    result = verify(model, cert)
    assert not result['topology_complete']
    with pytest.raises(ValueError):
        partition(model, max_depth=-1)


def test_saved_path_check_runs_without_topomt_or_producer(tmp_path):
    model = make_model()
    cert = {
        'schema': 'topomt.reference-validator.certificate/1',
        'kind': 'path',
        'model_sha256': model.digest,
        'arithmetic': 'rational-exact/1',
        'points': [
            [['-2', '1'], ['2', '1'], ['0', '1']],
            [['2', '1'], ['2', '1'], ['0', '1']],
        ],
    }
    model_file, cert_file = tmp_path / 'model.json', tmp_path / 'certificate.json'
    model_file.write_text(json.dumps(model.to_record()))
    cert_file.write_text(json.dumps(cert))
    command = """
import json, sys
sys.modules['topomt'] = None
sys.modules['devtools.reference_validator.producer'] = None
from devtools.reference_validator.verify import verify
from devtools.reference_validator.model import Model
from pathlib import Path
model = Model.from_record(json.loads(Path(sys.argv[1]).read_text()))
print(json.dumps(verify(model, json.loads(Path(sys.argv[2]).read_text()))))
"""
    result = subprocess.run(
        [sys.executable, '-c', command, str(model_file), str(cert_file)],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['path_validated'] is True
    bad = copy.deepcopy(cert)
    bad['points'][0][1] = ['0', '1']
    bad['points'][1][1] = ['0', '1']
    with pytest.raises(ValueError):
        verify(model, bad)


def test_cli_verification_rejects_fabrication_and_never_overwrites(tmp_path):
    model = make_model(4)
    model_file = tmp_path / 'model.json'
    cert_file = tmp_path / 'certificate.json'
    model_file.write_text(json.dumps(model.to_record()))
    command = [sys.executable, '-m', 'devtools.reference_validator']
    run = subprocess.run(
        command + ['produce', str(model_file), str(cert_file)],
        text=True,
        capture_output=True,
    )
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)['n_components'] == 0
    before = cert_file.read_bytes()
    run = subprocess.run(
        command + ['produce', str(model_file), str(cert_file)],
        text=True,
        capture_output=True,
    )
    assert run.returncode == 2 and cert_file.read_bytes() == before
    bad = json.loads(before)
    bad['leaves'] = []
    cert_file.write_text(json.dumps(bad))
    run = subprocess.run(
        command + ['verify', str(model_file), str(cert_file)],
        text=True,
        capture_output=True,
    )
    assert run.returncode == 2 and not run.stdout
