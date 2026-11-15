"""Acceleration preserves checked geometry and hostile-input boundaries."""

from copy import deepcopy
from dataclasses import FrozenInstanceError
from fractions import Fraction as F

import pytest

from devtools.reference_validator.model import Box, Model, point
from devtools.reference_validator.power_cells import topology_certificate
from devtools.reference_validator.volume_request import VolumeRequest


def model():
    return Model.from_spheres(
        [(0, 0, 0)],
        [F(3, 2)],
        0,
        domain=Box(point((-1, -1, -1)), point((1, 1, 1))),
    )


def test_checked_queries_reuse_real_validation_without_mutable_aliases(monkeypatch):
    from devtools.reference_validator.verify import context
    from devtools.reference_validator.verify.power_cells import query_anchors

    m = model()
    proof = topology_certificate(m)
    original = deepcopy(proof)
    anchors = {'corner': point((1, 1, 1)), 'blocked': point((0, 0, 0))}
    expected = query_anchors(m, original, anchors=anchors, pairs=[])
    calls = []
    import devtools.reference_validator.verify as checker

    real = checker.verify

    def counted(*args, **kwargs):
        calls.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr(checker, 'verify', counted)
    checked = context.CheckedTopology(m, proof)
    proof['cells'].clear()
    checked.result['regions'].clear()
    for _ in range(2):
        answer = checked.query_anchors(anchors=anchors, pairs=[])
        assert answer == expected
        assert answer['locations']['corner']['point_state'] == 'free'
    assert len(calls) == 1
    with pytest.raises((FrozenInstanceError, AttributeError)):
        checked.model = m
    with pytest.raises(ValueError):
        context.CheckedTopology(m, proof)


def test_incremental_refinement_does_not_reclassify_unchanged_leaves(monkeypatch):
    from devtools.reference_validator import region_volume as producer
    from devtools.reference_validator.verify import verify

    m = model()
    calls = []
    real = producer._leaf_state

    def counted(*args, **kwargs):
        calls.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr(producer, '_leaf_state', counted)
    from devtools.reference_validator.verify import region_volume as reader

    monkeypatch.setattr(reader, '_leaf_state', counted)
    cert = producer.region_volume_certificate(
        m, topology_certificate(m), VolumeRequest(F(0), F(0)), max_leaves=64
    )
    # One root plus exactly eight new classifications per performed split.
    assert len(calls) == 1 + 8 * ((len(cert['leaves']) - 1) // 7)
    assert verify(m, cert)['precision_status'] == 'unresolved'


def test_power_session_checks_each_cell_once_before_final_verification(monkeypatch):
    from devtools.reference_validator import power_runs
    from devtools.reference_validator.verify import verify

    m = Model.from_spheres(
        [(-1, 0, 0), (1, 0, 0)],
        [F(1, 4)] * 2,
        0,
        domain=Box(point((-2, -2, -2)), point((2, 2, 2))),
    )
    session = power_runs.PowerSession(m)
    session.advance(cell_budget=1)
    snapshot = session.snapshot
    snapshot['cells'].clear()
    assert len(session.snapshot['cells']) == 1
    with pytest.raises(ValueError):
        session.finish()
    session.advance(cell_budget=1)
    assert session.finish() == topology_certificate(m)
    assert verify(m, session.finish())['topology_complete']
    bad = session.snapshot
    bad['cells'].clear()
    with pytest.raises(ValueError):
        power_runs.PowerSession(m, progress=bad)


def test_phase_measurements_distinguish_profiled_calls_and_nested_time():
    from devtools.reference_validator.performance import Measurements

    measurements = Measurements(profile=True)
    assert measurements.run('sum', lambda: sum(range(20))) == 190
    record = measurements.to_record()
    assert record['phases']['sum']['wall_seconds'] >= 0
    assert record['phases']['sum']['cpu_seconds'] >= 0
    assert record['profiled'] is True
    assert record['phases']['sum']['calls']
    with pytest.raises(ValueError):
        measurements.run('sum', lambda: None)


def test_boundary_flux_encloses_analytic_volume_and_rejects_missing_faces():
    from devtools.reference_validator.boundary_volume import boundary_volume_certificate
    from devtools.reference_validator.model import decode_scalar
    from devtools.reference_validator.region_volume import region_volume_certificate
    from devtools.reference_validator.verify import verify

    m = Model.from_spheres(
        [(0, 0, 0)], [F(1, 2)], 0, domain=Box(point((-1, -1, -1)), point((1, 1, 1)))
    )
    topology = topology_certificate(m)
    request = VolumeRequest(F(1, 100))
    a = boundary_volume_certificate(m, topology, request, max_leaves=96)
    b = verify(m, a)
    analytic = verify(
        m,
        region_volume_certificate(
            m, topology, request, method='analytic_single_region'
        ),
    )
    assert decode_scalar(b['volume_lower']) <= decode_scalar(analytic['volume_lower'])
    assert decode_scalar(b['volume_upper']) >= decode_scalar(analytic['volume_upper'])
    bad = deepcopy(a)
    bad['leaves'].pop()
    with pytest.raises(ValueError):
        verify(m, bad)


def test_boundary_flux_keeps_all_tiny_regions_and_duplicate_atoms():
    from devtools.reference_validator.boundary_volume import boundary_volume_certificate
    from devtools.reference_validator.verify import verify

    results = []
    for radii in [[F(3, 2)], [F(3, 2), F(3, 2)]]:
        m = Model.from_spheres(
            [(0, 0, 0)] * len(radii),
            radii,
            0,
            domain=Box(point((-1, -1, -1)), point((1, 1, 1))),
        )
        proof = boundary_volume_certificate(
            m, topology_certificate(m), VolumeRequest(F(0), F(0)), max_leaves=48
        )
        result = verify(m, proof)
        assert result['n_components'] == 8
        assert result['precision_status'] == 'unresolved'
        results.append(result)
    assert results[0]['regions'] == results[1]['regions']


def _bounded_process(script):
    import subprocess
    import sys

    if sys.platform != 'linux':
        pytest.skip('Local process prototype currently uses Linux resource contracts')
    limits = 'import resource, os\nos.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:2]))\nresource.setrlimit(resource.RLIMIT_AS, (2*1024**3,2*1024**3))\nresource.setrlimit(resource.RLIMIT_CPU,(30,35))\n'
    subprocess.run([sys.executable, '-c', limits + script], check=True, timeout=40)


def test_bounded_parallel_cells_reproduce_serial_proof_and_check_resources():
    _bounded_process("""
from fractions import Fraction as F
from devtools.reference_validator.model import Model, Box, point
from devtools.reference_validator.parallel import LocalPolicy, parallel_power_topology
from devtools.reference_validator.power_cells import topology_certificate
m=Model.from_spheres([(-1,0,0),(1,0,0)],[F(1,4)]*2,0,domain=Box(point((-2,-2,-2)),point((2,2,2))))
proof,receipt=parallel_power_topology(m,policy=LocalPolicy(workers=2))
assert proof==topology_certificate(m)
assert receipt['worker_count']==2 and receipt['worker_records']
assert all(r['address_space_bytes']<=256*1024**2 for r in receipt['worker_records'])
for count in [0,100,True]:
 try: LocalPolicy(workers=count)
 except ValueError: pass
 else: raise AssertionError('Invalid count accepted')
""")


def test_parallel_boundary_uses_the_same_canonical_partition_and_final_checker():
    _bounded_process("""
from fractions import Fraction as F
from devtools.reference_validator.model import Model, Box, point
from devtools.reference_validator.parallel import LocalPolicy, parallel_boundary_volume
from devtools.reference_validator.boundary_volume import boundary_volume_certificate
from devtools.reference_validator.power_cells import topology_certificate
from devtools.reference_validator.volume_request import VolumeRequest
from devtools.reference_validator.verify import verify
m=Model.from_spheres([(0,0,0)],[F(3,2)],0,domain=Box(point((-1,-1,-1)),point((1,1,1))))
topology=topology_certificate(m)
request=VolumeRequest(F(0),F(0))
expected=boundary_volume_certificate(m,topology,request,max_leaves=48)
actual,receipt=parallel_boundary_volume(m,topology,request,max_leaves=48,policy=LocalPolicy(workers=2))
assert actual==expected and verify(m,actual)['n_components']==8
assert receipt['worker_count']==2
""")


def test_outward_reduction_preserves_negative_endpoints_and_bounds_operand_size():
    from devtools.reference_validator.verify._interval import _Interval, _outward

    for a, b in [(F(-7, 3), F(-1, 7)), (F(1, 101), F(19, 211)), (F(0), F(0))]:
        result = _outward(_Interval(a, b), 64)
        assert result.lower <= a <= b <= result.upper
        assert result.lower.denominator <= 2**64
        assert result.upper.denominator <= 2**64
        assert a - result.lower < F(1, 2**64)
        assert result.upper - b < F(1, 2**64)
    with pytest.raises(ValueError):
        _outward(_Interval(F(0), F(1)), True)


def test_boundary_signed_faces_agree_with_an_independent_contained_ball_union():
    from devtools.reference_validator.boundary_volume import boundary_volume_certificate
    from devtools.reference_validator.model import decode_scalar
    from devtools.reference_validator.region_volume import region_volume_certificate
    from devtools.reference_validator.verify import verify

    # The first owner's center lies outside its own power cell. Its oriented
    # face flux includes negative coefficients; discarding them biases volume.
    m = Model.from_spheres(
        [(0, 0, 0), (F(3, 5), 0, 0)],
        [1, F(7, 5)],
        0,
        domain=Box(point((-3, -3, -3)), point((3, 3, 3))),
    )
    topo = topology_certificate(m)
    request = VolumeRequest(F(1, 100))
    a = verify(m, boundary_volume_certificate(m, topo, request, max_leaves=96))
    b = verify(
        m, region_volume_certificate(m, topo, request, method='analytic_single_region')
    )
    assert decode_scalar(a['volume_lower']) <= decode_scalar(b['volume_lower'])
    assert decode_scalar(b['volume_upper']) <= decode_scalar(a['volume_upper'])


@pytest.mark.parametrize('radii,expected', [([], 8), ([0], 8), ([2], 0)])
def test_boundary_full_zero_measure_and_empty_controls_are_exact(radii, expected):
    from devtools.reference_validator.boundary_volume import boundary_volume_certificate
    from devtools.reference_validator.model import decode_scalar
    from devtools.reference_validator.verify import verify

    m = Model.from_spheres(
        [(0, 0, 0)] * len(radii),
        radii,
        0,
        domain=Box(point((-1, -1, -1)), point((1, 1, 1))),
    )
    proof = boundary_volume_certificate(
        m, topology_certificate(m), VolumeRequest(F(0), F(0)), max_leaves=48
    )
    result = verify(m, proof)
    assert (
        decode_scalar(result['volume_lower'])
        == decode_scalar(result['volume_upper'])
        == expected
    )
    assert result['precision_status'] == 'resolved'


def test_session_save_rechecks_on_fresh_load_and_rejects_kernel_change(
    tmp_path, monkeypatch
):
    from devtools.reference_validator import power_runs

    m = model()
    session = power_runs.PowerSession(m)
    session.advance()
    session.save(tmp_path / 'bundle')
    assert power_runs.load_power_bundle(tmp_path / 'bundle', m) == session.snapshot
    monkeypatch.setattr(power_runs, 'kernel_identity', lambda: {})
    with pytest.raises(ValueError):
        session.snapshot


def test_measurement_failure_is_retained_and_nested_phases_are_rejected():
    from devtools.reference_validator.performance import Measurements

    measured = Measurements()
    with pytest.raises(ValueError):
        measured.run('outer', lambda: measured.run('inner', lambda: None))
    assert measured.to_record()['phases']['outer']['failed'] is True


def test_checked_state_cannot_cross_serialization_or_process_boundaries(monkeypatch):
    import os
    import pickle

    from devtools.reference_validator.power_runs import PowerSession
    from devtools.reference_validator.verify.context import CheckedTopology

    m = model()
    topology = CheckedTopology(m, topology_certificate(m))
    session = PowerSession(m)
    for value in (topology, session):
        with pytest.raises(TypeError):
            pickle.dumps(value)
    pid = os.getpid()
    monkeypatch.setattr(os, 'getpid', lambda: pid + 1)
    with pytest.raises(ValueError):
        topology.result
    with pytest.raises(ValueError):
        session.snapshot
