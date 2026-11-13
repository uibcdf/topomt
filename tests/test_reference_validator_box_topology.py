"""Exact corner/gate controls require complete regions, not sampled counts."""

import copy
import hashlib
import json
import subprocess
import sys
from dataclasses import replace
from fractions import Fraction
from itertools import permutations, product
from pathlib import Path

import pytest

from devtools.reference_validator.box_topology import single_ball_box
from devtools.reference_validator.model import (
    Atom,
    Box,
    Model,
    Tetrahedron,
    decode_point,
    point,
    record_digest,
)
from devtools.reference_validator.verify import verify
from devtools.reference_validator.verify.geometry import point_is_free, segment_is_free


def _model(radius, *, probe=0, lower=(-1, -1, -1), upper=(1, 1, 1), center=(0, 0, 0)):
    return Model.from_spheres(
        [center], [radius], probe, domain=Box(point(lower), point(upper))
    )


@pytest.mark.parametrize('radius', [Fraction(3, 2), Fraction(173205, 100000)])
def test_all_eight_corner_components_are_exhaustively_recovered(radius):
    model = _model(radius)
    cert = single_ball_box(model)
    result = verify(model, cert)
    assert result['topology_complete']
    assert result['n_components'] == 8
    assert result['topology_scope'] == 'single-ball-axis-box/1'
    assert result['boundary_incidence_status'] == 'not_computed'
    assert result['volume_status'] == 'not_computed'
    assert len(result['regions']) == 8
    representatives = {decode_point(r['representative']) for r in result['regions']}
    assert representatives == {point(c) for c in product((-1, 1), repeat=3)}
    assert all(point_is_free(model, p) for p in representatives)
    assert all(len(r['piece_ids']) == 1 for r in result['regions'])


@pytest.mark.parametrize('offset,expected', [(-1, 1), (0, 2), (1, 2)])
def test_throat_closes_exactly_at_contact(offset, expected):
    model = _model(
        4, probe=1 + offset * Fraction(1, 2**80), lower=(-10, -3, -4), upper=(10, 3, 4)
    )
    cert = single_ball_box(model)
    result = verify(model, cert)
    assert result['n_components'] == expected
    assert result['topology_complete']
    assert segment_is_free(model, point((-10, 3, 4)), point((10, 3, 4))) == (offset < 0)
    if expected == 2:
        assert all(
            len({piece[0] for piece in region['piece_ids']}) == 1
            for region in result['regions']
        )
    for join in cert['joins']:
        if join['free_set_state'] == 'nonempty':
            roots = {p['id']: decode_point(p['corner']) for p in cert['pieces']}
            witness = decode_point(join['witness'])
            assert all(
                segment_is_free(model, roots[p], witness) for p in join['pieces']
            )


@pytest.mark.parametrize(
    'model,expected',
    [
        (_model(4), 0),
        (_model(1, lower=(-2, -2, -2), upper=(2, 2, 2)), 1),
        (_model(0), 1),
        (_model(Fraction(1, 4), center=(3, 0, 0)), 1),
        (_model(Fraction(8, 5), center=(1, 0, 0)), 1),
        (_model(7, lower=(0, 0, 0), upper=(2, 3, 6)), 0),
        (_model(7 - Fraction(1, 2**80), lower=(0, 0, 0), upper=(2, 3, 6)), 1),
    ],
)
def test_empty_internal_external_boundary_and_zero_radius_models(model, expected):
    result = verify(model, single_ball_box(model))
    assert result['n_components'] == expected
    assert len(result['regions']) == expected


def test_exact_translations_scaling_and_axis_permutations_preserve_components():
    shift = 10**40
    scale = Fraction(1, 2**80)
    for axes in permutations(range(3)):
        lower = tuple(shift + scale * (-10, -3, -4)[i] for i in axes)
        upper = tuple(shift + scale * (10, 3, 4)[i] for i in axes)
        model = _model(5 * scale, lower=lower, upper=upper, center=(shift,) * 3)
        assert verify(model, single_ball_box(model))['n_components'] == 2


def test_nonempty_sector_is_not_mislabeled_as_a_wholly_free_cell():
    model = _model(1, lower=(-2, -2, -2), upper=(2, 2, 2))
    cert = single_ball_box(model)
    assert all(p['free_set_state'] == 'nonempty' for p in cert['pieces'])
    assert all('state' not in p for p in cert['pieces'])
    # The sectors contain blocked points as well as a nonempty free part.
    assert not point_is_free(model, point((0, 0, 0)))
    assert verify(model, cert)['volume_status'] == 'not_computed'


@pytest.mark.parametrize(
    'change', ['piece', 'corner', 'state', 'join', 'witness', 'merge', 'extra']
)
def test_checker_rejects_incomplete_or_false_topology(change):
    model = _model(Fraction(3, 2))
    cert = copy.deepcopy(single_ball_box(model))
    if change == 'piece':
        cert['pieces'].pop()
    elif change == 'corner':
        cert['pieces'][0]['corner'][0] = ['0', '1']
    elif change == 'state':
        cert['pieces'][0]['free_set_state'] = 'empty'
    elif change == 'join':
        cert['joins'].pop()
    elif change == 'witness':
        cert['joins'][0]['witness'][0] = ['17', '1']
    elif change == 'merge':
        cert['components'] = [[p['id'] for p in cert['pieces']]]
    else:
        cert['n_components'] = 8
    with pytest.raises(ValueError):
        verify(model, cert)


def test_checker_rejects_fictitious_separation_and_forgotten_free_join():
    model = _model(1)
    cert = single_ball_box(model)
    cert['components'] = [[p['id']] for p in cert['pieces']]
    with pytest.raises(ValueError, match='component'):
        verify(model, cert)
    cert = single_ball_box(model)
    next(j for j in cert['joins'] if j['free_set_state'] == 'nonempty')[
        'free_set_state'
    ] = 'empty'
    with pytest.raises(ValueError, match='intersection'):
        verify(model, cert)


def test_model_binding_and_scope_cannot_drop_additional_obstacles():
    model = _model(Fraction(3, 2))
    certificate = single_ball_box(model)
    with pytest.raises(ValueError, match='binding'):
        verify(replace(model, probe=Fraction(1, 100)), certificate)
    for unsupported in (
        replace(model, atoms=()),
        replace(model, atoms=(*model.atoms, Atom(7, point((0, 0, 0)), Fraction(1)))),
        replace(
            model,
            domain=Tetrahedron(
                tuple(point(c) for c in [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)])
            ),
        ),
    ):
        with pytest.raises(ValueError, match='one ball.*box'):
            single_ball_box(unsupported)
        rebound = copy.deepcopy(certificate)
        rebound['model_sha256'] = unsupported.digest
        with pytest.raises(ValueError, match='one ball.*box'):
            verify(unsupported, rebound)


def test_saved_checker_runs_without_producer_or_molecular_imports(tmp_path):
    model = _model(Fraction(173205, 100000))
    model_path = tmp_path / 'model.json'
    proof_path = tmp_path / 'proof.json'
    model_path.write_text(json.dumps(model.to_record()))
    proof_path.write_text(json.dumps(single_ball_box(model)))
    script = """
import json,sys
from pathlib import Path
sys.modules['topomt'] = None
sys.modules['numpy'] = None
sys.modules['devtools.reference_validator.box_topology'] = None
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify import verify
model = Model.from_record(json.loads(Path(sys.argv[1]).read_text()))
proof = json.loads(Path(sys.argv[2]).read_text())
print(json.dumps(verify(model, proof)))
"""
    completed = subprocess.run(
        [sys.executable, '-c', script, str(model_path), str(proof_path)],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    result = json.loads(completed.stdout)
    assert result['n_components'] == 8
    assert 'verify/box_topology.py' in result['verifier_files_sha256']


def test_topology_cli_produces_and_independently_reads_new_evidence(tmp_path):
    model = _model(5, lower=(-10, -3, -4), upper=(10, 3, 4))
    source = tmp_path / 'model.json'
    source.write_text(json.dumps(model.to_record()))
    output = tmp_path / 'proof.json'
    base = [sys.executable, '-m', 'devtools.reference_validator']
    for args in (
        ['box-topology', str(source), str(output)],
        ['verify', str(source), str(output)],
    ):
        completed = subprocess.run(
            base + args, text=True, capture_output=True, check=True, timeout=10
        )
        assert json.loads(completed.stdout)['n_components'] == 2
    repeated = subprocess.run(
        base + ['box-topology', str(source), str(output)],
        capture_output=True,
        timeout=10,
    )
    assert repeated.returncode == 2


def test_frozen_topology_protocol_captures_replayable_qualified_scope(tmp_path):
    from devtools.reference_validator.capture_box_topology import capture

    protocol = (
        Path(__file__).resolve().parents[1]
        / 'devguide/evidence/reference_validator_box_topology_v1/protocol.json'
    )
    output = tmp_path / 'receiving'
    capture(protocol, output)
    receipt = json.loads((output / 'receipt.json').read_text())
    assert len(receipt['cases']) == 13
    assert receipt['cases']['tiny_eight_corners']['n_components'] == 8
    assert receipt['cases']['throat_before']['n_components'] == 1
    assert receipt['cases']['throat_contact']['n_components'] == 2
    assert receipt['cases']['throat_after']['n_components'] == 2
    assert receipt['general_multi_ball_status'] == 'unresolved'
    assert receipt['requested_precision_status'] == 'not_computed'
    for name, row in receipt['cases'].items():
        model = Model.from_record(
            json.loads((output / f'{name}.model.json').read_text())
        )
        certificate = json.loads((output / f'{name}.certificate.json').read_text())
        checked = verify(model, certificate)
        assert checked['n_components'] == row['n_components']
        assert checked['topology_complete']
    with pytest.raises(FileExistsError):
        capture(protocol, output)


def test_retained_topology_evidence_keeps_original_bytes_and_exact_regions():
    base = (
        Path(__file__).resolve().parents[1]
        / 'devguide/evidence/reference_validator_box_topology_v1'
    )
    protocol = json.loads((base / 'protocol.json').read_text())
    saved = base / 'receiving'
    receipt = json.loads((saved / 'receipt.json').read_text())
    assert (
        hashlib.sha256((base / 'protocol.json').read_bytes()).hexdigest()
        == receipt['protocol_sha256']
    )
    expected_files = {
        f'{case["name"]}.{suffix}.json'
        for case in protocol['cases']
        for suffix in ['model', 'certificate', 'verification']
    }
    assert set(receipt['files']) == expected_files
    for name, digest in receipt['files'].items():
        assert hashlib.sha256((saved / name).read_bytes()).hexdigest() == digest
    for case in protocol['cases']:
        name = case['name']
        model = Model.from_record(
            json.loads((saved / f'{name}.model.json').read_text())
        )
        assert model.to_record() == case['model']
        cert = json.loads((saved / f'{name}.certificate.json').read_text())
        original = json.loads((saved / f'{name}.verification.json').read_text())
        row = receipt['cases'][name]
        assert model.digest == row['model_sha256']
        assert record_digest(cert) == row['certificate_sha256']
        assert record_digest(original) == row['verification_sha256']
        checked = verify(model, cert)
        assert checked['topology_complete']
        assert (
            checked['n_components']
            == original['n_components']
            == case['expected_components']
        )
        if case['method'] == 'single_ball_box':
            assert checked['regions'] == original['regions']
            assert checked['boundary_incidence_status'] == 'not_computed'
            assert checked['volume_status'] == 'not_computed'
