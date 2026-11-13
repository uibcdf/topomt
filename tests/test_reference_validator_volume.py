"""Certified analytic controls must meet explicit tolerances or retain bounds."""

import copy
import json
import subprocess
import sys
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path

import pytest

from devtools.reference_validator.analytic_volume import volume_certificate
from devtools.reference_validator.model import (
    Atom,
    Box,
    Model,
    decode_scalar,
    encode_scalar,
    point,
)
from devtools.reference_validator.verify import verify
from devtools.reference_validator.volume_request import VolumeRequest

PI_LO = F(314159265358979323846264338327950288419716939937510, 10**50)
PI_HI = PI_LO + F(1, 10**50)
DOMAIN = Box(point((-4, -4, -4)), point((4, 4, 4)))


def _model(centers, radii, *, probe=0, domain=DOMAIN):
    return Model.from_spheres(centers, radii, probe, domain=domain)


def _bounds(result):
    return decode_scalar(result['volume_lower']), decode_scalar(result['volume_upper'])


@pytest.mark.parametrize('k', [8, 16, 24, 32])
def test_contained_unit_ball_reaches_both_requested_precisions(k):
    model = _model([(0, 0, 0)], [1])
    request = VolumeRequest(F(512, 2**k), F(1, 2**k))
    cert = volume_certificate(model, request)
    result = verify(model, cert)
    lo, hi = _bounds(result)
    assert lo <= 512 - F(4, 3) * PI_HI <= hi
    assert lo <= 512 - F(4, 3) * PI_LO <= hi
    assert hi - lo <= request.absolute_nm3
    assert (hi - lo) / lo <= request.relative
    assert result['precision_status'] == 'resolved'
    assert result['volume_unit'] == 'nm**3'
    assert result['volume_target'] == 'total_probe_center_free_set'
    assert result['topology_status'] == 'not_computed'
    assert result['n_components'] is None


@pytest.mark.parametrize(
    'centers,radii,coefficient',
    [
        ([], [], F(0)),
        ([(0, 0, 0)], [0], F(0)),
        ([(-2, 0, 0), (2, 0, 0)], [1, 1], F(8, 3)),
        ([(-1, 0, 0), (1, 0, 0)], [1, 1], F(8, 3)),
        ([(0, 0, 0), (0, 0, 0)], [2, 1], F(32, 3)),
        ([(0, 0, 0), (0, 0, 0)], [1, 1], F(4, 3)),
        ([(0, 0, 0), (1, 0, 0)], [2, 1], F(32, 3)),
        ([(0, 0, 0), (1, 0, 0)], [1, 1], F(9, 4)),
        ([(0, 0, 0), (2, 0, 0)], [2, 1], F(275, 24)),
    ],
)
def test_empty_disjoint_tangent_nested_coincident_and_pair_lens_formulas(
    centers, radii, coefficient
):
    model = _model(centers, radii)
    result = verify(model, volume_certificate(model, VolumeRequest(F(1, 2**40))))
    lo, hi = _bounds(result)
    assert lo <= 512 - coefficient * PI_HI <= hi
    assert lo <= 512 - coefficient * PI_LO <= hi
    assert result['precision_status'] == 'resolved'
    assert hi - lo <= F(1, 2**40)


def test_irrational_distance_pair_is_bounded_without_float_geometry():
    model = _model([(0, 0, 0), (1, 1, 0)], [1, 1])
    request = VolumeRequest(F(1, 2**32))
    cert = volume_certificate(model, request)
    result = verify(model, cert)
    lo, hi = _bounds(result)
    # For equal unit balls, lens/pi = 4/3-d+d^3/12; at d=sqrt(2),
    # union/pi = 4/3+5*sqrt(2)/6. Independent rational sqrt bounds.
    root_lo = F(141421356237309504880168872420969807856967187537694, 10**50)
    root_hi = root_lo + F(1, 10**50)
    assert root_lo**2 < 2 < root_hi**2
    coefficient_lo = F(4, 3) + F(5, 6) * root_lo
    coefficient_hi = F(4, 3) + F(5, 6) * root_hi
    assert lo <= 512 - coefficient_hi * PI_HI <= hi
    assert lo <= 512 - coefficient_lo * PI_LO <= hi
    assert result['precision_status'] == 'resolved'
    assert cert['refinement']['distance_bits'] > 0


def test_insufficient_budget_and_zero_error_do_not_fabricate_precision():
    model = _model([(0, 0, 0), (1, 1, 0)], [1, 1])
    request = VolumeRequest(F(1, 2**80), F(1, 2**80))
    coarse = volume_certificate(model, request, max_atan_terms=0, max_distance_bits=0)
    result = verify(model, coarse)
    assert result['volume_enclosure_status'] == 'resolved'
    assert result['precision_status'] == 'unresolved'
    assert result['stop_reason'] == 'refinement_limit'
    zero = verify(
        model,
        volume_certificate(
            model, VolumeRequest(F(0)), max_atan_terms=4, max_distance_bits=4
        ),
    )
    assert zero['precision_status'] == 'unresolved'
    exact_model = _model([], [])
    exact = verify(
        exact_model,
        volume_certificate(
            exact_model, VolumeRequest(F(0)), max_atan_terms=0, max_distance_bits=0
        ),
    )
    assert _bounds(exact) == (512, 512)
    assert exact['precision_status'] == 'resolved'


def test_maximum_admitted_refinement_keeps_a_portable_unresolved_certificate():
    model = _model([(0, 0, 0), (1, 1, 0)], [1, 1])
    certificate = volume_certificate(
        model, VolumeRequest(F(0)), max_atan_terms=512, max_distance_bits=4096
    )
    serialized = json.dumps(certificate)
    checked = verify(model, json.loads(serialized))
    assert checked['precision_status'] == 'unresolved'
    assert checked['stop_reason'] == 'refinement_limit'
    assert len(certificate['volume_lower'][0]) > 4300


def test_refinement_retains_nested_volume_bounds_for_same_request():
    model = _model([(0, 0, 0), (1, 1, 0)], [1, 1])
    request = VolumeRequest(F(0))
    previous = (F(0), F(512))
    for level in [0, 1, 2, 4, 8, 16]:
        result = verify(
            model,
            volume_certificate(
                model, request, max_atan_terms=level, max_distance_bits=level
            ),
        )
        lo, hi = _bounds(result)
        assert previous[0] <= lo <= hi <= previous[1]
        previous = (lo, hi)


def test_strictly_contained_distinct_pair_clusters_and_source_maps():
    model = _model(
        [(-2, 0, 0), (-1, 0, 0), (2, 0, 0), (2, 0, 0)], [1, 1, F(1, 2), F(1, 4)]
    )
    cert = volume_certificate(model, VolumeRequest(F(1, 2**24)))
    assert cert['clusters'] == [[0, 1], [2]]
    assert cert['dominated'] == [{'source_id': 3, 'covering_id': 2}]
    result = verify(model, cert)
    assert result['precision_status'] == 'resolved'
    assert model.to_record()['atoms'][3]['source_id'] == 3


@pytest.mark.parametrize(
    'bad', ['domain_contact', 'triple_overlap', 'three_ball_chain']
)
def test_unsupported_geometry_is_rejected_instead_of_silently_approximated(bad):
    if bad == 'domain_contact':
        model = _model([(3, 0, 0)], [1])
    elif bad == 'triple_overlap':
        model = _model([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [1, 1, 1])
    else:
        model = _model([(-1, 0, 0), (0, 0, 0), (1, 0, 0)], [F(3, 4)] * 3)
    with pytest.raises(ValueError):
        volume_certificate(model, VolumeRequest(F(1, 100)))


@pytest.mark.parametrize(
    'change',
    [
        'atom',
        'cluster',
        'dominated',
        'bound',
        'unit',
        'relative_unit',
        'budget',
        'extra',
    ],
)
def test_saved_checker_rejects_corrupt_geometric_and_precision_claims(change):
    model = _model([(0, 0, 0), (1, 0, 0), (0, 0, 0)], [1, 1, F(1, 4)])
    cert = copy.deepcopy(volume_certificate(model, VolumeRequest(F(1, 2**24))))
    if change == 'atom':
        model = replace(model, atoms=(*model.atoms, Atom(17, point((0, 1, 0)), F(1))))
    elif change == 'cluster':
        cert['clusters'] = [[0], [1]]
    elif change == 'dominated':
        cert['dominated'][0]['covering_id'] = 1
    elif change == 'bound':
        cert['volume_upper'] = cert['volume_lower']
    elif change == 'unit':
        cert['request']['volume_unit'] = 'angstrom**3'
    elif change == 'relative_unit':
        cert['request']['relative_unit'] = 'nm'
    elif change == 'budget':
        cert['refinement']['atan_terms'] = True
    else:
        cert['precision_status'] = 'resolved'
    with pytest.raises(ValueError):
        verify(model, cert)


def test_dominance_cannot_hide_an_uncovered_atom():
    model = _model([(0, 0, 0), (1, 0, 0)], [1, 1])
    cert = volume_certificate(model, VolumeRequest(F(1, 100)))
    cert['clusters'] = [[0]]
    cert['dominated'] = [{'source_id': 1, 'covering_id': 0}]
    with pytest.raises(ValueError, match='contain'):
        verify(model, cert)


@pytest.mark.parametrize(
    'absolute,relative',
    [(None, None), (-1, None), (None, -1), (float('inf'), None), (True, None)],
)
def test_invalid_or_missing_tolerances_are_rejected(absolute, relative):
    with pytest.raises((ValueError, TypeError)):
        VolumeRequest(absolute, relative)


def test_requests_round_trip_units_and_optional_precision_without_global_policy():
    request = VolumeRequest(F(3, 10**8), F(1, 2**24))
    record = request.to_record()
    assert VolumeRequest.from_record(record) == request
    assert record['absolute_tolerance'] == encode_scalar(request.absolute_nm3)
    assert record['volume_unit'] == 'nm**3'
    relative = VolumeRequest(None, F(1, 2**16))
    model = _model([(0, 0, 0)], [1])
    assert (
        verify(model, volume_certificate(model, relative))['precision_status']
        == 'resolved'
    )


@pytest.mark.parametrize('lo,hi', [(-1, 2), (2, 1)])
def test_precision_check_rejects_nonphysical_bounds(lo, hi):
    with pytest.raises(ValueError):
        VolumeRequest(F(1)).satisfied(F(lo), F(hi))


def test_common_probe_expansion_and_exact_transformed_models_preserve_volume():
    model = _model([(0, 0, 0), (1, 0, 0)], [F(1, 2), F(1, 2)], probe=F(1, 2))
    original = verify(model, volume_certificate(model, VolumeRequest(F(1, 2**24))))
    expected = F(512) - F(9, 4) * PI_LO
    assert _bounds(original)[0] <= expected <= _bounds(original)[1]
    scale, shift = F(1, 2**30), 10**35
    changed = Model(
        tuple(
            Atom(
                a.source_id,
                point(tuple(shift + scale * v for v in a.center)),
                a.radius * scale,
            )
            for a in reversed(model.atoms)
        ),
        model.probe * scale,
        Box(point((shift - 4 * scale,) * 3), point((shift + 4 * scale,) * 3)),
        'b' * 64,
    )
    result = verify(
        changed, volume_certificate(changed, VolumeRequest(F(1, 2**24) * scale**3))
    )
    lo, hi = _bounds(result)
    assert lo <= expected * scale**3 <= hi
    assert result['precision_status'] == 'resolved'


def test_exact_near_tangency_and_coincidence_do_not_lose_atoms_or_divide_by_zero():
    delta = F(1, 2**80)
    for distance in (delta, 2 - delta, 2 + delta):
        model = _model([(0, 0, 0), (distance, 0, 0)], [1, 1])
        cert = volume_certificate(model, VolumeRequest(F(1, 2**32)))
        assert cert['dominated'] == []
        assert cert['clusters'] == ([[0, 1]] if distance < 2 else [[0], [1]])
        checked = verify(model, cert)
        assert checked['precision_status'] == 'resolved'
    tiny = _model([(0, 0, 0), (delta, 0, 0)], [1, 1])
    stopped = verify(
        tiny,
        volume_certificate(
            tiny, VolumeRequest(F(0)), max_atan_terms=2, max_distance_bits=2
        ),
    )
    assert stopped['precision_status'] == 'unresolved'


def test_rational_constant_bounds_against_optional_directed_mpfr():
    g = pytest.importorskip('gmpy2')
    from devtools.reference_validator.verify._interval import _pi, _sqrt

    original_policy = (g.get_context().precision, g.get_context().round)

    def rational(value):
        numerator, denominator = value.as_integer_ratio()
        return F(int(numerator), int(denominator))

    with g.context(precision=1024, round=g.RoundDown):
        pi_low, root_low = rational(g.const_pi()), rational(g.sqrt(g.mpfr(2)))
    with g.context(precision=1024, round=g.RoundUp):
        pi_high, root_high = rational(g.const_pi()), rational(g.sqrt(g.mpfr(2)))
    assert PI_LO <= pi_low < pi_high <= PI_HI
    for n in [0, 1, 2, 4, 8, 16, 64]:
        bounds = _pi(n)
        assert bounds.lower <= pi_low <= pi_high <= bounds.upper
    for bits in [0, 1, 16, 64, 128]:
        bounds = _sqrt(F(2), bits)
        assert bounds.lower <= root_low <= root_high <= bounds.upper
    assert (g.get_context().precision, g.get_context().round) == original_policy


def test_fresh_reader_does_not_import_volume_producer_or_numerical_engines(tmp_path):
    model = _model([(0, 0, 0), (1, 1, 0)], [1, 1])
    certificate = volume_certificate(model, VolumeRequest(F(1, 2**24)))
    source = tmp_path / 'model.json'
    proof = tmp_path / 'certificate.json'
    source.write_text(json.dumps(model.to_record()))
    proof.write_text(json.dumps(certificate))
    code = """
import json,sys
from pathlib import Path
for name in ['topomt','numpy','gmpy2','mpmath','sympy','devtools.reference_validator.analytic_volume']:
    sys.modules[name] = None
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify import verify
model = Model.from_record(json.loads(Path(sys.argv[1]).read_text()))
print(json.dumps(verify(model,json.loads(Path(sys.argv[2]).read_text()))))
"""
    result = subprocess.run(
        [sys.executable, '-c', code, str(source), str(proof)],
        text=True,
        capture_output=True,
        check=True,
        timeout=10,
    )
    assert json.loads(result.stdout)['precision_status'] == 'resolved'


def test_volume_cli_preserves_exact_requests_saved_results_and_existing_files(tmp_path):
    model = _model([(0, 0, 0), (1, 1, 0)], [1, 1])
    source, proof = tmp_path / 'model.json', tmp_path / 'proof.json'
    source.write_text(json.dumps(model.to_record()))
    base = [sys.executable, '-m', 'devtools.reference_validator']
    command = [
        'volume',
        str(source),
        str(proof),
        '--absolute-nm3',
        '1/16777216',
        '--relative',
        '1/16777216',
    ]
    computed = subprocess.run(
        base + command, text=True, capture_output=True, check=True, timeout=10
    )
    saved = subprocess.run(
        base + ['verify', str(source), str(proof)],
        text=True,
        capture_output=True,
        check=True,
        timeout=10,
    )
    assert json.loads(computed.stdout)['precision_status'] == 'resolved'
    assert json.loads(saved.stdout)['precision_request']['absolute_tolerance'] == [
        '1',
        '16777216',
    ]
    repeated = subprocess.run(base + command, capture_output=True, timeout=10)
    assert repeated.returncode == 2


@pytest.mark.parametrize(
    'terms,bits', [(-1, 0), (True, 0), (513, 0), (0, -1), (0, True), (0, 4097)]
)
def test_invalid_work_limits_are_rejected(terms, bits):
    with pytest.raises(ValueError, match='budgets'):
        volume_certificate(
            _model([], []),
            VolumeRequest(F(0)),
            max_atan_terms=terms,
            max_distance_bits=bits,
        )


def test_invalid_cli_fraction_is_diagnosed_without_output_or_traceback(tmp_path):
    source = tmp_path / 'model.json'
    output = tmp_path / 'proof.json'
    source.write_text(json.dumps(_model([], []).to_record()))
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'devtools.reference_validator',
            'volume',
            str(source),
            str(output),
            '--absolute-nm3',
            '1/0',
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert 'Reference validation failed' in result.stderr
    assert 'Traceback' not in result.stderr
    assert not output.exists()


def test_frozen_volume_protocol_retains_precision_success_and_explicit_budget_stops(
    tmp_path,
):
    from devtools.reference_validator.capture_volume import capture

    protocol = (
        Path(__file__).resolve().parents[1]
        / 'devguide/evidence/reference_validator_analytic_volume_v1/protocol.json'
    )
    output = tmp_path / 'receiving'
    capture(protocol, output)
    receipt = json.loads((output / 'receipt.json').read_text())
    assert len(receipt['profiles']) == 23
    assert receipt['profiles']['unit_ball_k24']['precision_status'] == 'resolved'
    assert receipt['profiles']['irrational_pair_k32']['precision_status'] == 'resolved'
    assert (
        receipt['profiles']['stopped_irrational_pair']['precision_status']
        == 'unresolved'
    )
    assert (
        receipt['profiles']['unit_ball_zero_error']['precision_status'] == 'unresolved'
    )
    assert (
        receipt['profiles']['empty_exact_zero_error']['precision_status'] == 'resolved'
    )
    assert receipt['general_topology_status'] == 'not_qualified'
    assert receipt['mpfr_crosscheck'] is None
    with pytest.raises(FileExistsError):
        capture(protocol, output)


def test_optional_capture_audit_preserves_independent_constant_versions():
    pytest.importorskip('gmpy2')
    from devtools.reference_validator.capture_volume import _mpfr_audit

    record = _mpfr_audit()
    assert record['gmpy2_version']
    assert record['mpfr_version']
    assert record['mpfr_precision_bits'] == 1024
    for entry in record['constants'].values():
        assert decode_scalar(entry['rational_lower']) <= decode_scalar(
            entry['mpfr_lower']
        )
        assert decode_scalar(entry['mpfr_upper']) <= decode_scalar(
            entry['rational_upper']
        )
