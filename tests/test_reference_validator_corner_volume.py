"""Boundary integration on a proved eight-region clipped-ball control."""

from copy import deepcopy
from fractions import Fraction as F
from math import isqrt

import pytest

from devtools.reference_validator.model import Box, Model, decode_scalar, point
from devtools.reference_validator.power_cells import topology_certificate
from devtools.reference_validator.region_volume import region_volume_certificate
from devtools.reference_validator.verify import verify
from devtools.reference_validator.verify._interval import _exact, _Interval, _pi, _sqrt
from devtools.reference_validator.verify.corner_volume import _atan, corner_bounds
from devtools.reference_validator.volume_request import VolumeRequest


def _model(radius=F(3, 2), half=F(1), center=(0, 0, 0)):
    return Model.from_spheres(
        [center],
        [radius],
        0,
        domain=Box(
            point([c - half for c in center]), point([c + half for c in center])
        ),
    )


@pytest.mark.parametrize('value', [F(0), F(1, 3), F(1, 2), F(1), F(2), F(3)])
def test_outward_atan_bounds_respect_oddness_and_reciprocal_identity(value):
    positive = _atan(_exact(value), 128)
    negative = _atan(_exact(-value), 128)
    assert positive.lower == -negative.upper
    assert positive.upper == -negative.lower
    assert positive.upper - positive.lower < F(1, 2**100)
    if value:
        total = positive + _atan(_exact(1 / value), 128)
        reference = _pi(128) / _exact(2)
        assert total.lower <= reference.upper and reference.lower <= total.upper
    else:
        assert positive.lower == positive.upper == 0


def test_atan_interval_encloses_a_known_addition_identity():
    value = _atan(_exact(F(1, 2)), 128) + _atan(_exact(F(1, 3)), 128)
    reference = _pi(128) / _exact(4)
    assert value.lower <= reference.upper and reference.lower <= value.upper
    interval = _atan(_Interval(F(-1, 2), F(1, 3)), 128)
    assert interval.lower < 0 < interval.upper


@pytest.mark.parametrize('radius', [F(3, 2), F(17, 10), F(isqrt(3 << 160), 1 << 80)])
def test_boundary_route_meets_precision_for_each_of_eight_even_tiny_regions(radius):
    model = _model(radius)
    request = VolumeRequest(F(8, 2**32), F(1, 2**32))
    cert = region_volume_certificate(
        model, topology_certificate(model), request, method='analytic_corner_regions'
    )
    checked = verify(model, cert)
    assert checked['precision_status'] == 'resolved'
    assert checked['total_precision_status'] == 'resolved'
    assert len(checked['regions']) == 8
    # Independent elementary sandwich. With u_i=1-x_i and delta=3-R²,
    # sum(u)<delta/2 implies free; free implies sum(u)<delta. Both
    # bounding simplexes fit in an orthant cube, giving these volume bounds.
    delta = 3 - radius**2
    low, high = delta**3 / 48, (delta / (2 - delta)) ** 3 / 6
    if delta < F(1, 2**40):
        # A second high-precision enclosure from polynomial inequalities alone.
        assert request.satisfied(low, high)
    for row in checked['regions']:
        lower, upper = map(decode_scalar, [row['lower'], row['upper']])
        assert low <= lower <= upper <= high
        assert request.satisfied(lower, upper)
        assert row['precision_status'] == 'resolved'
    assert sum(decode_scalar(r['lower']) for r in checked['regions']) == decode_scalar(
        checked['volume_lower']
    )
    assert sum(decode_scalar(r['upper']) for r in checked['regions']) == decode_scalar(
        checked['volume_upper']
    )


def test_clipped_boundary_bounds_are_translation_invariant_and_scale_cubically():
    original = corner_bounds(_model(), {'scheme': 'cube-cap-wedge/1', 'bits': 128})
    moved = corner_bounds(
        _model(center=(10**9, -(10**9), 17)),
        {'scheme': 'cube-cap-wedge/1', 'bits': 128},
    )
    assert original == moved
    scaled = corner_bounds(
        _model(F(9, 2), F(3)), {'scheme': 'cube-cap-wedge/1', 'bits': 128}
    )
    assert scaled.lower <= 27 * original.upper
    assert 27 * original.lower <= scaled.upper


@pytest.mark.parametrize(
    'corruption', ['scheme', 'bits', 'omitted', 'geometry', 'topology']
)
def test_boundary_certificates_reject_changed_geometry_and_arithmetic(corruption):
    model = _model()
    cert = region_volume_certificate(
        model,
        topology_certificate(model),
        VolumeRequest(F(8, 2**24), F(1, 2**24)),
        method='analytic_corner_regions',
    )
    changed = deepcopy(cert)
    if corruption == 'scheme':
        changed['analytic_certificate']['scheme'] = 'unbounded-rounding'
    elif corruption == 'bits':
        changed['analytic_certificate']['bits'] = True
    elif corruption == 'omitted':
        changed['analytic_certificate'].pop('bits')
    elif corruption == 'geometry':
        model = _model(center=(1, 0, 0))
    else:
        changed['topology_certificate']['cells'] = []
    with pytest.raises(ValueError):
        verify(model, changed)


def test_boundary_route_refuses_unadmitted_spheres_and_does_not_fake_zero_error():
    for radius in [1, 2]:
        model = _model(radius)
        with pytest.raises(ValueError):
            region_volume_certificate(
                model,
                topology_certificate(model),
                VolumeRequest(F(1)),
                method='analytic_corner_regions',
            )
    model = _model()
    cert = region_volume_certificate(
        model,
        topology_certificate(model),
        VolumeRequest(F(0), F(0)),
        method='analytic_corner_regions',
    )
    checked = verify(model, cert)
    assert checked['precision_status'] == 'unresolved'
    assert checked['stop_reason'] == 'analytic_precision_envelope'


@pytest.mark.parametrize(
    'volume_request', [VolumeRequest(F(1, 10**20)), VolumeRequest(None, F(1, 10**20))]
)
def test_boundary_absolute_only_and_relative_only_requests_are_preserved(
    volume_request,
):
    model = _model()
    cert = region_volume_certificate(
        model,
        topology_certificate(model),
        volume_request,
        method='analytic_corner_regions',
    )
    assert cert['request'] == volume_request.to_record()
    checked = verify(model, cert)
    assert checked['precision_status'] == 'resolved'
    assert 'verify/corner_volume.py' in checked['verifier_files_sha256']


def test_boundary_admission_requires_the_exact_symmetric_model():
    domain = Box(point((-1, -1, -1)), point((1, 1, 1)))
    for centers, radii in [
        ([(F(1, 10), 0, 0)], [F(3, 2)]),
        ([(0, 0, 0)] * 2, [F(3, 2)] * 2),
    ]:
        model = Model.from_spheres(centers, radii, 0, domain=domain)
        with pytest.raises(ValueError):
            corner_bounds(model, {'scheme': 'cube-cap-wedge/1', 'bits': 128})
    with pytest.raises(ValueError):
        corner_bounds(
            _model(), {'scheme': 'cube-cap-wedge/1', 'bits': 128, 'volume': 0}
        )


def test_saved_boundary_checking_needs_no_producer_or_scientific_packages(tmp_path):
    import json
    import subprocess
    import sys

    model = _model()
    cert = region_volume_certificate(
        model,
        topology_certificate(model),
        VolumeRequest(F(8, 2**32), F(1, 2**32)),
        method='analytic_corner_regions',
    )
    (tmp_path / 'model.json').write_text(json.dumps(model.to_record()))
    (tmp_path / 'certificate.json').write_text(json.dumps(cert))
    script = """
import json,sys
from pathlib import Path
for name in ['topomt','numpy','scipy','pyunitwizard','devtools.reference_validator.region_volume','devtools.reference_validator.power_cells','devtools.reference_validator.producer']:
 sys.modules[name]=None
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify import verify
model=Model.from_record(json.loads(Path(sys.argv[1]).read_text()))
result=verify(model,json.loads(Path(sys.argv[2]).read_text()))
assert len(result['regions'])==8 and result['precision_status']=='resolved'
"""
    subprocess.run(
        [
            sys.executable,
            '-c',
            script,
            str(tmp_path / 'model.json'),
            str(tmp_path / 'certificate.json'),
        ],
        check=True,
        timeout=15,
    )


def test_near_edge_transition_agrees_with_independent_cap_and_annulus_bounds():
    radius = F(isqrt(2 << 200) + 1, 1 << 100)
    assert 2 < radius**2 < 3
    model = _model(radius)
    cert = region_volume_certificate(
        model,
        topology_certificate(model),
        VolumeRequest(F(8, 2**96), F(1, 2**96)),
        method='analytic_corner_regions',
    )
    result = verify(model, cert)
    assert result['precision_status'] == 'resolved'
    # At R0=sqrt(2), face caps have zero pair-overlap. Integrating only
    # the six caps gives V0=8+(16*sqrt(2)/3-10)*pi. Increasing R can
    # remove no more than the complete sphere's annular volume.
    root = _sqrt(F(2), 256)
    pi = _pi(128)
    reference = _exact(8) + (_exact(F(16, 3)) * root - _exact(10)) * pi
    annulus = _exact(F(4, 3)) * pi * (_exact(radius**3) - _exact(2) * root)
    lower = decode_scalar(result['volume_lower'])
    upper = decode_scalar(result['volume_upper'])
    assert reference.lower - annulus.upper <= lower <= upper <= reference.upper
