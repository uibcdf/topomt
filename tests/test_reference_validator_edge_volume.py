"""Analytic edge reduction retains exact cuts, signed faces and all regions."""

from copy import deepcopy
from fractions import Fraction as F

import pytest

from devtools.reference_validator.model import Box, Model, decode_scalar, point
from devtools.reference_validator.power_cells import topology_certificate
from devtools.reference_validator.verify import verify
from devtools.reference_validator.volume_request import VolumeRequest


def cube(radius):
    return Model.from_spheres(
        [(0, 0, 0)], [radius], 0, domain=Box(point((-1, -1, -1)), point((1, 1, 1)))
    )


@pytest.mark.parametrize('radius,count', [(F(1, 2), 1), (F(3, 2), 8)])
def test_edge_formula_passes_k32_and_matches_independent_analytic_controls(
    radius, count
):
    from devtools.reference_validator.edge_volume import edge_volume_certificate
    from devtools.reference_validator.region_volume import region_volume_certificate

    m = cube(radius)
    proof = topology_certificate(m)
    req = VolumeRequest(F(8, 2**32), F(1, 2**32))
    a = verify(m, edge_volume_certificate(m, proof, req))
    method = 'analytic_corner_regions' if count == 8 else 'analytic_single_region'
    b = verify(m, region_volume_certificate(m, proof, req, method=method))
    assert a['precision_status'] == 'resolved'
    assert len(a['regions']) == count
    assert max(
        decode_scalar(a['volume_lower']), decode_scalar(b['volume_lower'])
    ) <= min(decode_scalar(a['volume_upper']), decode_scalar(b['volume_upper']))
    assert all(r['precision_status'] == 'resolved' for r in a['regions'])


def test_oriented_triangle_flux_reverses_sign_and_has_exact_zero_radius_limit():
    from devtools.reference_validator.verify.edge_volume import triangle_flux

    t = tuple(map(point, [(0, 0, 1), (2, 0, 1), (0, 2, 1)]))
    a = triangle_flux(point((0, 0, 0)), F(3, 2), t, 128)
    b = triangle_flux(point((0, 0, 0)), F(3, 2), (t[0], t[2], t[1]), 128)
    assert a.lower <= -b.upper <= -b.lower <= a.upper
    zero = triangle_flux(point((0, 0, 0)), F(0), t, 64)
    assert zero.lower == zero.upper == F(2, 3)


def test_edge_certificate_rejects_modified_scheme_units_and_topology():
    from devtools.reference_validator.edge_volume import edge_volume_certificate

    m = cube(F(3, 2))
    p = edge_volume_certificate(m, topology_certificate(m), VolumeRequest(F(1, 2**24)))
    for field, value in [('scheme', 'incorrect'), ('bits', True), ('bits', 1)]:
        bad = deepcopy(p)
        bad[field] = value
        with pytest.raises(ValueError):
            verify(m, bad)
    bad = deepcopy(p)
    bad['topology_certificate']['cells'].clear()
    with pytest.raises(ValueError):
        verify(m, bad)

    bad = deepcopy(p)
    bad['request']['volume_unit'] = 'angstrom**3'
    with pytest.raises(ValueError):
        verify(m, bad)


def test_extremely_tiny_eight_regions_need_more_bits_and_keep_independent_sandwich():
    from math import isqrt

    from devtools.reference_validator.edge_volume import edge_volume_certificate

    m = cube(F(isqrt(3 << 160), 1 << 80))
    proof = topology_certificate(m)
    req = VolumeRequest(F(8, 2**32), F(1, 2**32))
    coarse = verify(m, edge_volume_certificate(m, proof, req, max_bits=64))
    assert coarse['precision_status'] == 'unresolved'
    cert = edge_volume_certificate(m, proof, req)
    result = verify(m, cert)
    assert cert['bits'] > 64 and result['precision_status'] == 'resolved'
    delta = 3 - m.atoms[0].radius ** 2
    low, high = delta**3 / 48, (delta / (2 - delta)) ** 3 / 6
    assert len(result['regions']) == 8
    for region in result['regions']:
        assert (
            low
            <= decode_scalar(region['lower'])
            <= decode_scalar(region['upper'])
            <= high
        )


def test_asymmetric_barriers_have_precise_three_region_accounting():
    from devtools.reference_validator.edge_volume import edge_volume_certificate
    from devtools.reference_validator.verify.power_cells import query_anchors

    m = Model.from_spheres(
        [(-8, 0, 0), (8, 0, 0)],
        [4, 5],
        1,
        domain=Box(point((-20, -3, -4)), point((20, 3, 4))),
    )
    topology = topology_certificate(m)
    anchors = query_anchors(
        m,
        topology,
        anchors={
            name: point((x, 0, 0))
            for name, x in [('left', -20), ('middle', 0), ('right', 20)]
        },
        pairs=[],
    )
    result = verify(
        m,
        edge_volume_certificate(
            m, topology, VolumeRequest(F(1920, 2**32), F(1, 2**32))
        ),
    )
    assert result['precision_status'] == 'resolved'
    assert len(result['regions']) == 3
    rows = {r['region_id']: r for r in result['regions']}
    for name, (low, high) in {
        'left': (336, 576),
        'middle': (240, 624),
        'right': (288, 432),
    }.items():
        region = rows[anchors['locations'][name]['region_id']]
        assert (
            low
            <= decode_scalar(region['lower'])
            <= decode_scalar(region['upper'])
            <= high
        )
    assert sum(decode_scalar(r['lower']) for r in rows.values()) == decode_scalar(
        result['volume_lower']
    )
    assert sum(decode_scalar(r['upper']) for r in rows.values()) == decode_scalar(
        result['volume_upper']
    )


def test_signed_owner_faces_match_contained_unequal_ball_union():
    from devtools.reference_validator.edge_volume import edge_volume_certificate
    from devtools.reference_validator.region_volume import region_volume_certificate

    m = Model.from_spheres(
        [(0, 0, 0), (F(3, 5), 0, 0)],
        [1, F(7, 5)],
        0,
        domain=Box(point((-3, -3, -3)), point((3, 3, 3))),
    )
    p = topology_certificate(m)
    req = VolumeRequest(F(216, 2**32), F(1, 2**32))
    a = verify(m, edge_volume_certificate(m, p, req))
    b = verify(m, region_volume_certificate(m, p, req, method='analytic_single_region'))
    assert a['precision_status'] == 'resolved'
    assert max(
        decode_scalar(a['volume_lower']), decode_scalar(b['volume_lower'])
    ) <= min(decode_scalar(a['volume_upper']), decode_scalar(b['volume_upper']))


@pytest.mark.parametrize('radii,expected', [([], 8), ([0], 8), ([2], 0)])
def test_literal_zero_requests_preserve_full_zero_measure_and_empty(radii, expected):
    from devtools.reference_validator.edge_volume import edge_volume_certificate

    m = Model.from_spheres(
        [(0, 0, 0)] * len(radii),
        radii,
        0,
        domain=Box(point((-1, -1, -1)), point((1, 1, 1))),
    )
    r = verify(
        m,
        edge_volume_certificate(m, topology_certificate(m), VolumeRequest(F(0), F(0))),
    )
    assert r['precision_status'] == 'resolved'
    assert (
        decode_scalar(r['volume_lower']) == decode_scalar(r['volume_upper']) == expected
    )


def test_exact_three_four_five_contacts_match_independent_cap_formula():
    from devtools.reference_validator.edge_volume import edge_volume_certificate
    from devtools.reference_validator.verify._interval import _exact, _pi

    m = Model.from_spheres(
        [(0, 0, 0)], [5], 0, domain=Box(point((-5, -4, -3)), point((5, 4, 3)))
    )
    result = verify(
        m,
        edge_volume_certificate(
            m, topology_certificate(m), VolumeRequest(F(480, 2**32), F(1, 2**32))
        ),
    )
    assert result['precision_status'] == 'resolved' and len(result['regions']) == 2
    # y/z caps meet at points: 4²+3²=5²; cap overlap volume is exactly zero.
    reference = (_exact(480) - _exact(F(368, 3)) * _pi(128)) / _exact(2)
    for region in result['regions']:
        assert max(reference.lower, decode_scalar(region['lower'])) <= min(
            reference.upper, decode_scalar(region['upper'])
        )


def test_rational_rotation_translation_and_scaling_preserve_triangle_flux():
    from devtools.reference_validator.verify.edge_volume import triangle_flux

    tri = tuple(map(point, [(-1, 0, 1), (1, 0, 1), (0, 2, 1)]))
    origin = point((0, 0, 0))
    a = triangle_flux(origin, F(3, 2), tri, 128)

    def transform(p):
        return point(
            (
                3 * (F(3, 5) * p[0] - F(4, 5) * p[1]) + 10**9,
                3 * (F(4, 5) * p[0] + F(3, 5) * p[1]) - 10**9,
                3 * p[2] + 17,
            )
        )

    b = triangle_flux(transform(origin), F(9, 2), tuple(map(transform, tri)), 128)
    assert max(27 * a.lower, b.lower) <= min(27 * a.upper, b.upper)


def test_literal_zero_full_free_shortcut_is_still_independently_proved():
    from devtools.reference_validator.edge_volume import edge_volume_certificate

    m = Model.from_spheres(
        [(10, 10, 10)], [1], 0, domain=Box(point((-1, -1, -1)), point((1, 1, 1)))
    )
    result = verify(
        m,
        edge_volume_certificate(m, topology_certificate(m), VolumeRequest(F(0), F(0))),
    )
    assert result['precision_status'] == 'resolved'
    assert (
        decode_scalar(result['volume_lower'])
        == decode_scalar(result['volume_upper'])
        == 8
    )


@pytest.mark.parametrize(
    'value', [F(0), F(1, 3), F(1), F(2), F(3), F(10**50), F(1, 10**50), F(-2)]
)
def test_dyadic_atan_preserves_independent_series_enclosures(value):
    from devtools.reference_validator.verify._interval import _exact
    from devtools.reference_validator.verify.corner_volume import _atan
    from devtools.reference_validator.verify.edge_math import atan_dyadic

    fast = atan_dyadic(value, 128)
    reference = _atan(_exact(value), 128)
    assert max(fast.lower, reference.lower) <= min(fast.upper, reference.upper)
    assert fast.upper - fast.lower < F(1, 2**120)
    neg = atan_dyadic(-value, 128)
    assert fast.lower == -neg.upper and fast.upper == -neg.lower


def test_dyadic_atan_addition_identity_and_rejected_precision():
    from devtools.reference_validator.verify._interval import _exact, _pi
    from devtools.reference_validator.verify.edge_math import atan_dyadic

    actual = atan_dyadic(F(1, 2), 128) + atan_dyadic(F(1, 3), 128)
    reference = _pi(128) / _exact(4)
    assert max(actual.lower, reference.lower) <= min(actual.upper, reference.upper)
    with pytest.raises(ValueError):
        atan_dyadic(F(1), True)


def test_dyadic_atan_keeps_integer_arguments_exact_and_admits_maximum_bits():
    from devtools.reference_validator.verify.edge_math import atan_dyadic

    assert atan_dyadic(3, 128) == atan_dyadic(F(3), 128)
    result = atan_dyadic(F(2), 2048)
    assert 0 < result.lower < result.upper
    assert result.upper - result.lower < F(1, 2**2040)


def test_declarative_proposal_does_not_claim_or_skip_independent_checking(monkeypatch):
    from devtools.reference_validator import edge_volume as producer

    m = cube(F(3, 2))
    topology = topology_certificate(m)

    def forbidden(*args, **kwargs):
        raise AssertionError(
            'Preparing a symbolic proposal must not execute verification'
        )

    monkeypatch.setattr(producer, 'verify', forbidden)
    request = VolumeRequest(F(8, 2**32), F(1, 2**32))
    proposal = producer.edge_volume_proposal(m, topology, request, bits=128)
    assert 'verification_status' not in proposal and 'precision_status' not in proposal
    assert verify(m, proposal)['precision_status'] == 'resolved'
    topology['cells'].clear()
    assert verify(m, proposal)['precision_status'] == 'resolved'
    bad = producer.edge_volume_proposal(m, topology, request, bits=128)
    with pytest.raises(ValueError):
        verify(m, bad)
