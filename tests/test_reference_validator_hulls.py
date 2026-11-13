"""Hull equality and exact clipping cannot be inferred from point containment."""

import copy
import hashlib
import json
import subprocess
import sys
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path

import pytest

from devtools.reference_validator.center_hull import clip_certificate, hull_certificate
from devtools.reference_validator.hull_model import CenterSource, HullLimits
from devtools.reference_validator.model import (
    Box,
    Model,
    _determinant,
    decode_point,
    decode_scalar,
    point,
    record_digest,
)
from devtools.reference_validator.verify.center_hull import verify_hull


def _source(points):
    return CenterSource(
        tuple(point(p) for p in points), tuple(range(len(points))), 'a' * 64
    )


CUBE = _source(list(product((-1, 1), repeat=3)))
TETRAHEDRON = _source([(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)])
OCTAHEDRON = _source(
    [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
)


@pytest.mark.parametrize(
    'source,vertices,facets,volume',
    [(CUBE, 8, 6, F(8)), (TETRAHEDRON, 4, 4, F(1, 6)), (OCTAHEDRON, 6, 8, F(4, 3))],
)
def test_complete_source_hull_is_proved_with_exact_volume(
    source, vertices, facets, volume
):
    cert = hull_certificate(source)
    result = verify_hull(source, cert)
    assert result['hull_equality_status'] == 'resolved'
    assert len(result['vertices']) == vertices
    assert len(result['facets']) == facets
    assert result['geometric_dimension'] == 3
    assert decode_scalar(result['geometric_volume']) == volume
    assert result['volume_unit'] == 'nm**3'
    assert result['free_volume_status'] == 'not_computed'
    assert result['free_topology_status'] == 'not_computed'
    for facet in result['facets']:
        a, b, c = (
            decode_point(result['vertices'][i]) for i in facet['vertex_indices'][:3]
        )
        first, second = (
            point([b[i] - a[i] for i in range(3)]),
            point([c[i] - a[i] for i in range(3)]),
        )
        normal = point([int(v) for v in facet['coefficients'][:3]])
        assert _determinant(first, second, normal) > 0


def test_redundant_coplanar_interior_and_duplicate_centers_keep_source_identity():
    source = _source([*CUBE.centers, (0, 0, 0), (1, 0, 0), (-1, -1, -1)])
    cert = hull_certificate(source)
    result = verify_hull(source, cert)
    assert len(result['vertices']) == 8
    assert len(result['facets']) == 6
    assert set(cert['vertex_source_ids']) == set(range(8))
    assert len(source.to_record()['centers']) == 11
    assert decode_scalar(result['geometric_volume']) == 8


@pytest.mark.parametrize(
    'lower,upper,dimension,volume',
    [
        ((-2, -2, -2), (2, 2, 2), 3, F(8)),
        ((F(-1, 2),) * 3, (F(1, 2),) * 3, 3, F(1)),
        ((0, -2, -2), (2, 2, 2), 3, F(4)),
        ((2, 2, 2), (3, 3, 3), -1, F(0)),
        ((1, -2, -2), (2, 2, 2), 2, F(0)),
        ((1, 1, -2), (2, 2, 2), 1, F(0)),
        ((1, 1, 1), (2, 2, 2), 0, F(0)),
        ((1 - F(1, 2**80), -2, -2), (2, 2, 2), 3, F(4, 2**80)),
    ],
)
def test_clipping_preserves_empty_positive_and_lower_dimensional_intersections(
    lower, upper, dimension, volume
):
    cert = clip_certificate(
        CUBE, hull_certificate(CUBE), Box(point(lower), point(upper))
    )
    result = verify_hull(CUBE, cert)
    assert result['geometric_dimension'] == dimension
    assert decode_scalar(result['geometric_volume']) == volume
    if dimension >= 0:
        assert result['vertices']
    else:
        assert result['vertices'] == []
    assert result['free_topology_status'] == 'not_computed'


def test_non_axis_hull_faces_clip_the_box_instead_of_using_its_volume():
    box = Box(point((F(1, 2), -1, -1)), point((2, 2, 2)))
    result = verify_hull(
        TETRAHEDRON, clip_certificate(TETRAHEDRON, hull_certificate(TETRAHEDRON), box)
    )
    assert decode_scalar(result['geometric_volume']) == F(1, 48)
    assert result['geometric_dimension'] == 3


def test_exact_translation_scaling_and_source_order_keep_geometric_hull():
    shift, scale = 10**35, F(1, 2**70)
    source = replace(
        CUBE,
        centers=tuple(
            point([shift + scale * x for x in p]) for p in reversed(CUBE.centers)
        ),
        source_ids=tuple(reversed(CUBE.source_ids)),
    )
    result = verify_hull(source, hull_certificate(source))
    assert decode_scalar(result['geometric_volume']) == 8 * scale**3


@pytest.mark.parametrize(
    'change',
    [
        'missing_plane',
        'enlarged_plane',
        'weight',
        'vertex',
        'witness',
        'source',
        'extra',
    ],
)
def test_checker_rejects_unbounded_larger_or_incomplete_hulls(change):
    source = CUBE
    cert = copy.deepcopy(hull_certificate(source))
    if change == 'missing_plane':
        cert['facets'].pop()
        cert['positive_weights'].pop()
    elif change == 'enlarged_plane':
        cert['facets'][0]['coefficients'][3] = '2'
    elif change == 'weight':
        cert['positive_weights'][0] = ['0', '1']
    elif change == 'vertex':
        cert['vertex_source_ids'].pop()
    elif change == 'witness':
        cert['affine_witness'] = [0, 1, 2, 3]
    elif change == 'source':
        source = replace(source, centers=(*source.centers[:-1], point((2, 2, 2))))
    else:
        cert['volume'] = 8
    with pytest.raises(ValueError):
        verify_hull(source, cert)


def test_containing_box_is_not_accepted_as_source_hull():
    # Every tetrahedron center lies inside this cube; hull equality still fails.
    larger = _source(list(product((0, 1), repeat=3)))
    cert = hull_certificate(larger)
    cert['source_sha256'] = TETRAHEDRON.digest
    with pytest.raises(ValueError):
        verify_hull(TETRAHEDRON, cert)


def test_omitted_source_vertex_cannot_be_hidden_by_rebinding_a_smaller_hull():
    expanded = _source([*TETRAHEDRON.centers, (2, 2, 2)])
    cert = hull_certificate(TETRAHEDRON)
    cert['source_sha256'] = expanded.digest
    with pytest.raises(ValueError):
        verify_hull(expanded, cert)


@pytest.mark.parametrize(
    'points',
    [
        [],
        [(0, 0, 0)],
        [(0, 0, 0), (1, 0, 0), (2, 0, 0)],
        [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)],
    ],
)
def test_degenerate_sources_are_explicitly_rejected_as_three_dimensional_hulls(points):
    with pytest.raises(ValueError, match='full.dimension'):
        hull_certificate(_source(points))


def test_source_records_retain_units_maps_and_do_not_depend_on_probe():
    m = Model.from_spheres(
        TETRAHEDRON.centers,
        [F(1, 10)] * 4,
        F(1, 10),
        domain=Box(point((-1, -1, -1)), point((2, 2, 2))),
    )
    first, second = (
        CenterSource.from_model(m),
        CenterSource.from_model(replace(m, probe=F(1, 2))),
    )
    assert first.digest == second.digest
    assert CenterSource.from_record(json.loads(json.dumps(first.to_record()))) == first
    bad = first.to_record()
    bad['length_unit'] = 'angstrom'
    with pytest.raises(ValueError):
        CenterSource.from_record(bad)


def test_work_limits_reject_expensive_or_invalid_requests_before_claiming_geometry():
    with pytest.raises(ValueError):
        HullLimits(max_facets=True)
    with pytest.raises(ValueError):
        hull_certificate(CUBE, limits=HullLimits(max_plane_triples=1))
    with pytest.raises(ValueError):
        verify_hull(CUBE, hull_certificate(CUBE), limits=HullLimits(max_centers=4))


def test_saved_hull_checker_imports_no_producer_or_floating_geometry(tmp_path):
    source = tmp_path / 'source.json'
    cert = tmp_path / 'hull.json'
    source.write_text(json.dumps(CUBE.to_record()))
    cert.write_text(json.dumps(hull_certificate(CUBE)))
    script = """
import sys,json
from pathlib import Path
for name in ['topomt','numpy','scipy','devtools.reference_validator.center_hull']:
    sys.modules[name]=None
from devtools.reference_validator.hull_model import CenterSource
from devtools.reference_validator.verify.center_hull import verify_hull
s=CenterSource.from_record(json.loads(Path(sys.argv[1]).read_text()))
print(json.dumps(verify_hull(s,json.loads(Path(sys.argv[2]).read_text()))))
"""
    result = subprocess.run(
        [sys.executable, '-c', script, str(source), str(cert)],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert decode_scalar(json.loads(result.stdout)['geometric_volume']) == 8


def test_containment_and_boundedness_alone_do_not_prove_hull_equality():
    cert = copy.deepcopy(hull_certificate(OCTAHEDRON))
    cert['facets'] = [
        f for f in cert['facets'] if f['coefficients'][:3] != ['1', '1', '1']
    ]
    cert['positive_weights'] = [
        ['1', '10'] if sum(map(int, f['coefficients'][:3])) < 0 else ['1', '5']
        for f in cert['facets']
    ]
    cert['normal_rank_witness'] = [0, 1, 2]
    # Seven supporting planes still bound a polytope and contain all source
    # centers, but create the non-source vertex (1,1,1). Completeness catches it.
    with pytest.raises(ValueError, match='larger'):
        verify_hull(OCTAHEDRON, cert)


def test_center_receiving_uses_the_original_quantity_codec_and_rejects_corruption(
    tmp_path,
):
    from pyunitwizard.record import RecordError

    from devtools.reference_validator.receiving import (
        freeze_centers,
        freeze_tetrahedron,
    )

    source = (
        Path(__file__).resolve().parents[1]
        / 'docs/content/benchlab/synthetic/regular_tetrahedron/artifacts/regular_tetrahedron_v1/input.json'
    )
    centers = freeze_centers(source)
    assert centers == CenterSource.from_model(
        freeze_tetrahedron(source, probe_angstroms=1.4)
    )
    damaged = json.loads(source.read_text())
    damaged['coordinates']['values'][0][0] += 1
    path = tmp_path / 'bad.json'
    path.write_text(json.dumps(damaged))
    with pytest.raises(RecordError):
        freeze_centers(path)


def test_cli_hull_and_clipping_preserve_new_outputs_and_support_saved_reading(tmp_path):
    source = tmp_path / 'source.json'
    source.write_text(json.dumps(CUBE.to_record()))
    hull = tmp_path / 'hull.json'
    clip = tmp_path / 'clip.json'
    base = [sys.executable, '-m', 'devtools.reference_validator']
    for command in [
        ['hull', str(source), str(hull)],
        [
            'clip-hull',
            str(source),
            str(hull),
            str(clip),
            '--lower-nm',
            '1',
            '-2',
            '-2',
            '--upper-nm',
            '2',
            '2',
            '2',
        ],
        ['verify-hull', str(source), str(clip)],
    ]:
        done = subprocess.run(
            base + command, capture_output=True, text=True, check=True, timeout=10
        )
        result = json.loads(done.stdout)
    assert result['geometric_dimension'] == 2
    assert decode_scalar(result['geometric_volume']) == 0
    repeated = subprocess.run(
        base + ['hull', str(source), str(hull)], capture_output=True, timeout=10
    )
    assert repeated.returncode == 2


def test_boolean_vertex_ids_are_not_canonical_source_maps():
    cert = hull_certificate(CUBE)
    cert['vertex_source_ids'][0] = False
    with pytest.raises(ValueError):
        verify_hull(CUBE, cert)


def test_clip_proof_is_detached_and_rejects_forged_intersection_claims():
    original = hull_certificate(CUBE)
    clipped = clip_certificate(
        CUBE, original, Box(point((0, -2, -2)), point((2, 2, 2)))
    )
    saved = copy.deepcopy(clipped)
    original['vertex_source_ids'].clear()
    assert clipped == saved
    for key, value in [
        ('claimed_volume', ['8', '1']),
        ('claimed_dimension', True),
        ('claimed_vertices', []),
    ]:
        bad = copy.deepcopy(saved)
        bad[key] = value
        with pytest.raises(ValueError):
            verify_hull(CUBE, bad)


def test_center_receiving_is_explicit_under_nondefault_unit_policy():
    import pyunitwizard as puw

    from devtools.reference_validator.receiving import freeze_centers

    path = (
        Path(__file__).resolve().parents[1]
        / 'docs/content/benchlab/synthetic/regular_tetrahedron/artifacts/regular_tetrahedron_v1/input.json'
    )
    baseline = freeze_centers(path)
    with puw.context(standard_units=['pm', 'fs', 'radians']):
        before = puw.configure.report()
        received = freeze_centers(path)
        assert received == baseline
        after = puw.configure.report()
        assert after['standard_units'] == before['standard_units']
        assert after['provenance'] == before['provenance']


def test_hull_capture_records_fixture_clips_without_scheduling_original_inputs(
    tmp_path,
):
    from devtools.reference_validator.capture_hulls import capture

    protocol = (
        Path(__file__).resolve().parents[1]
        / 'devguide/evidence/reference_validator_hulls_v1/protocol.json'
    )
    output = tmp_path / 'fixture_receiving'
    capture(protocol, output)
    receipt = json.loads((output / 'receipt.json').read_text())
    assert len(receipt['fixtures']) == 3
    assert len(receipt['clips']) == 6
    assert receipt['original_selection'] == []
    assert receipt['originals'] == {}
    assert receipt['free_volume_status'] == 'not_computed'
    with pytest.raises(FileExistsError):
        capture(protocol, output)


def test_hull_capture_worker_checks_one_real_source_with_finite_resources(tmp_path):
    from devtools.reference_validator.capture_hulls import capture

    protocol = (
        Path(__file__).resolve().parents[1]
        / 'devguide/evidence/reference_validator_hulls_v1/protocol.json'
    )
    output = tmp_path / 'one_receiving'
    capture(protocol, output, original_cases=('regular_tetrahedron',))
    receipt = json.loads((output / 'receipt.json').read_text())
    row = receipt['originals']['regular_tetrahedron']
    assert row['status'] == 'accepted'
    assert row['n_centers'] == 4
    assert row['address_space_limit_bytes'] == 2 * 1024**3
    assert len(row['cpu_affinity']) == 1


def test_hull_worker_timeout_is_not_reported_as_a_geometric_empty_result(
    tmp_path, monkeypatch
):
    import devtools.reference_validator.capture_hulls as helper

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired('controlled worker', 40)

    monkeypatch.setattr(helper, '_run_worker', timeout)
    protocol = (
        Path(__file__).resolve().parents[1]
        / 'devguide/evidence/reference_validator_hulls_v1/protocol.json'
    )
    output = tmp_path / 'stopped_receiving'
    helper.capture(protocol, output, original_cases=('regular_tetrahedron',))
    row = json.loads((output / 'receipt.json').read_text())['originals'][
        'regular_tetrahedron'
    ]
    assert row['status'] == 'unresolved'
    assert row['reason'] == 'wall_limit'
    assert 'geometric_volume' not in row


def test_capture_cli_rejects_ambiguous_original_selection_before_reading_or_work(
    tmp_path,
):
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'devtools.reference_validator.capture_hulls',
            str(tmp_path / 'absent.json'),
            str(tmp_path / 'out'),
            '--all-originals',
            '--original-case',
            'regular_tetrahedron',
        ],
        text=True,
        capture_output=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert 'not allowed with' in result.stderr
    assert not (tmp_path / 'out').exists()


def test_retained_hull_controls_preserve_geometric_proofs_and_unexecuted_scope():
    base = (
        Path(__file__).resolve().parents[1]
        / 'devguide/evidence/reference_validator_hulls_v1'
    )
    saved = base / 'receiving'
    receipt = json.loads((saved / 'receipt.json').read_text())
    assert (
        hashlib.sha256((base / 'protocol.json').read_bytes()).hexdigest()
        == receipt['protocol_sha256']
    )
    assert receipt['original_selection'] == []
    assert receipt['originals'] == {}
    expected = {
        f'{category}/{name}/{kind}.json'
        for category in ['fixtures', 'clips']
        for name in receipt[category]
        for kind in ['source', 'certificate', 'verification']
    }
    assert set(receipt['files']) == expected
    for name, digest in receipt['files'].items():
        assert hashlib.sha256((saved / name).read_bytes()).hexdigest() == digest
    for category in ['fixtures', 'clips']:
        for name, row in receipt[category].items():
            directory = saved / category / name
            source = CenterSource.from_record(
                json.loads((directory / 'source.json').read_text())
            )
            cert = json.loads((directory / 'certificate.json').read_text())
            original = json.loads((directory / 'verification.json').read_text())
            assert record_digest(original) == row['verification_sha256']
            assert record_digest(cert) == row['certificate_sha256']
            checked = verify_hull(source, cert)
            for key in [
                'vertices',
                'facets',
                'geometric_dimension',
                'geometric_volume',
                'free_volume_status',
                'free_topology_status',
            ]:
                assert checked[key] == original[key]
    attempt = json.loads((base / 'scheduler_attempt.json').read_text())
    assert attempt['execution_started'] is False
    assert attempt['allocation_status'] == 'not_allocated'
    assert attempt['queue_readback_after_failure'] == []
