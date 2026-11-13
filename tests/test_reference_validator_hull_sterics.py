"""Certified hulls constrain all-atom sterics and continuous paths exactly."""

import copy
import json
import subprocess
import sys
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path

import pytest

from devtools.reference_validator.center_hull import clip_certificate, hull_certificate
from devtools.reference_validator.hull_model import CenterSource
from devtools.reference_validator.model import (
    Box,
    HullDomain,
    Model,
    decode_scalar,
    encode_point,
    point,
)
from devtools.reference_validator.producer import domain_certificate, partition
from devtools.reference_validator.runs import resume_run, start_run
from devtools.reference_validator.verify import verify
from devtools.reference_validator.verify.geometry import (
    contains,
    point_is_free,
    segment_is_free,
    split,
    volume,
)
from devtools.reference_validator.verify.records import verify_checkpoint


def _seed(interior=False):
    centers = list(product((-1, 1), repeat=3))
    radii = [F(1, 10)] * len(centers)
    if interior:
        centers.append((0, 0, 0))
        radii.append(F(1, 3))
    return Model.from_spheres(
        centers, radii, F(1, 10), domain=Box(point((-2, -2, -2)), point((2, 2, 2)))
    )


def _proof(model, kind, **extra):
    return {
        'schema': 'topomt.reference-validator.certificate/1',
        'arithmetic': 'rational-exact/1',
        'kind': kind,
        'model_sha256': model.digest,
        **extra,
    }


def test_hull_domain_is_detached_verified_and_roundtrips_with_all_spheres():
    seed = _seed(True)
    source = CenterSource.from_model(seed)
    source_record = source.to_record()
    certificate = hull_certificate(source)
    domain = HullDomain(source_record, certificate)
    model = replace(seed, domain=domain)
    original = model.to_record()
    source_record['centers'].clear()
    certificate['facets'].clear()
    assert model.to_record() == original
    detached = domain.to_record()
    detached['certificate']['facets'].clear()
    assert model.to_record() == original
    assert Model.from_record(json.loads(json.dumps(original))) == model
    assert model.atoms == seed.atoms
    assert len(model.atoms) == 9
    assert len(model.domain.vertices) == 8
    assert model.digest != seed.digest
    assert domain.geometric_volume == volume(domain) == 8
    with pytest.raises(FrozenInstanceError):
        domain.geometric_volume = F(99)


def test_explicit_domain_change_reuses_hull_across_probes_without_mutating_seed():
    seed = _seed()
    saved = seed.to_record()
    cert = hull_certificate(CenterSource.from_model(seed))
    first = seed.with_center_hull(certificate=cert)
    second = replace(seed, probe=F(1, 2)).with_center_hull(certificate=cert)
    assert seed.to_record() == saved
    assert first.domain == second.domain
    assert first.digest != second.digest
    assert first == seed.with_center_hull()


@pytest.mark.parametrize(
    'field', ['centers', 'ids', 'frame', 'source', 'interpretation']
)
def test_a_verified_hull_cannot_be_attached_to_different_atomic_source_context(field):
    seed = Model.from_spheres(
        list(product((-1, 1), repeat=3)),
        [0] * 8,
        0,
        domain=Box(point((-2, -2, -2)), point((2, 2, 2))),
    )
    domain = seed.with_center_hull().domain
    if field == 'centers':
        seed = replace(
            seed,
            atoms=(replace(seed.atoms[0], center=point((0, 0, 0))), *seed.atoms[1:]),
        )
    elif field == 'ids':
        seed = replace(
            seed, atoms=(replace(seed.atoms[0], source_id=100), *seed.atoms[1:])
        )
    elif field == 'frame':
        seed = replace(seed, frame_index=1)
    elif field == 'source':
        seed = replace(seed, source_sha256='b' * 64)
    else:
        seed = replace(seed, interpretation='received_binary64_nm')
    with pytest.raises(ValueError, match='source'):
        replace(seed, domain=domain)


def test_wrong_or_altered_hull_proofs_are_rejected_during_model_reading():
    model = _seed().with_center_hull()
    record = model.to_record()
    record['domain']['certificate']['facets'].pop()
    with pytest.raises(ValueError):
        Model.from_record(record)
    source = CenterSource.from_model(_seed())
    cert = hull_certificate(source)
    clipped = clip_certificate(source, cert, Box(point((0, -2, -2)), point((2, 2, 2))))
    with pytest.raises(ValueError, match='center_hull'):
        HullDomain(source.to_record(), clipped)


def test_exact_hull_membership_cannot_be_replaced_by_bounding_box_membership():
    seed = Model.from_spheres(
        [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)],
        [0] * 4,
        0,
        domain=Box(point((-2, -2, -2)), point((2, 2, 2))),
    )
    model = seed.with_center_hull()
    x = point((F(4, 5), F(4, 5), 0))
    assert point_is_free(seed, x)
    assert not contains(model.domain, x)
    checked = verify(
        model, _proof(model, 'point', point=encode_point(x), claim='outside_domain')
    )
    assert checked['point_state'] == 'outside_domain'
    assert not segment_is_free(model, point((F(1, 4),) * 3), x)
    assert volume(model.domain) == F(1, 6)


def test_interior_atom_blocks_a_segment_with_free_endpoints_but_allows_a_bent_path():
    model = _seed(True).with_center_hull()
    start, end = point((-F(4, 5), 0, 0)), point((F(4, 5), 0, 0))
    assert point_is_free(model, start) and point_is_free(model, end)
    assert not segment_is_free(model, start, end)
    with pytest.raises(ValueError, match='collides'):
        verify(
            model,
            _proof(model, 'path', points=[encode_point(start), encode_point(end)]),
        )
    bent = [start, point((-F(4, 5), F(1, 2), 0)), point((F(4, 5), F(1, 2), 0)), end]
    checked = verify(
        model, _proof(model, 'path', points=[encode_point(x) for x in bent])
    )
    assert checked['connected'] is True
    assert checked['topology_complete'] is False
    assert checked['n_components'] is None
    assert {
        'hull_model.py',
        'contracts.py',
        'verify/center_hull.py',
        'verify/polytope.py',
    } <= set(checked['verifier_files_sha256'])


def test_closed_hull_boundary_is_admitted_but_exact_atomic_contact_is_excluded():
    model = _seed(True).with_center_hull()
    assert point_is_free(model, point((1, 0, 0)))
    contact = F(1, 3) + model.probe
    for delta, claim in [
        (-F(1, 2**80), 'blocked'),
        (F(0), 'blocked'),
        (F(1, 2**80), 'free'),
    ]:
        x = point((contact + delta, 0, 0))
        assert (
            verify(model, _proof(model, 'point', point=encode_point(x), claim=claim))[
                'point_state'
            ]
            == claim
        )
    assert not point_is_free(replace(model, probe=F(2)), point((0, 0, 0)))
    changed_radius = replace(
        model, atoms=(*model.atoms[:-1], replace(model.atoms[-1], radius=F(0)))
    )
    x = point((F(2, 5), 0, 0))
    assert not point_is_free(model, x)
    assert point_is_free(changed_radius, x)
    assert changed_radius.domain == model.domain


def test_complete_convex_hull_cover_and_unknown_domain_have_distinct_counts():
    model = _seed().with_center_hull()
    unknown = verify(model, domain_certificate(model))
    assert unknown['domain_state'] == 'unknown'
    assert decode_scalar(unknown['volume_lower']) == 0
    assert decode_scalar(unknown['volume_upper']) == 8
    assert unknown['n_components'] is None
    assert unknown['topology_complete'] is False
    covered = replace(
        model, atoms=(replace(model.atoms[0], radius=F(4)), *model.atoms[1:])
    )
    checked = verify(covered, domain_certificate(covered))
    assert checked['domain_state'] == 'blocked'
    assert checked['n_components'] == 0
    assert checked['topology_complete'] is True
    assert decode_scalar(checked['volume_upper']) == 0
    with pytest.raises(ValueError):
        verify(model, _proof(model, 'convex_domain', claim='blocked', atom_id=0))
    with pytest.raises(ValueError):
        verify(
            covered, _proof(covered, 'convex_domain', claim='blocked', atom_id=False)
        )
    with pytest.raises(ValueError):
        verify(model, _proof(model, 'convex_domain', claim='free'))
    empty_obstacles = Model.from_spheres(
        [], [], 0, domain=Box(point((-1, -1, -1)), point((1, 1, 1)))
    )
    assert (
        verify(empty_obstacles, domain_certificate(empty_obstacles))['n_components']
        == 1
    )


def test_partition_and_run_routes_reject_hulls_before_using_tetrahedron_rules():
    model = _seed().with_center_hull()
    cert = _proof(
        model,
        'partition',
        leaves=[{'path': '', 'state': 'unknown'}],
        refinement={'max_depth': 0, 'max_leaves': 1},
    )
    for action in [
        lambda: partition(model),
        lambda: start_run(model),
        lambda: split(model.domain),
        lambda: verify(model, cert),
        lambda: verify_checkpoint(model, {}),
        lambda: resume_run(model, {}),
    ]:
        with pytest.raises(ValueError, match='box|tetrahedr'):
            action()


def test_saved_hull_steric_model_checks_without_search_dfnd_or_quantity_libraries(
    tmp_path,
):
    model = _seed(True).with_center_hull()
    cert = _proof(
        model, 'point', point=encode_point(point((F(4, 5), 0, 0))), claim='free'
    )
    model_file, cert_file = tmp_path / 'model.json', tmp_path / 'cert.json'
    model_file.write_text(json.dumps(model.to_record()))
    cert_file.write_text(json.dumps(cert))
    script = """
import json,sys
from pathlib import Path
for name in ['topomt','numpy','scipy','pyunitwizard','devtools.reference_validator.producer','devtools.reference_validator.center_hull','devtools.reference_validator.runs']:
    sys.modules[name]=None
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify import verify
m=Model.from_record(json.loads(Path(sys.argv[1]).read_text()))
print(json.dumps(verify(m,json.loads(Path(sys.argv[2]).read_text()))))
"""
    done = subprocess.run(
        [sys.executable, '-c', script, str(model_file), str(cert_file)],
        text=True,
        capture_output=True,
        check=True,
        timeout=10,
    )
    assert json.loads(done.stdout)['point_state'] == 'free'


def test_full_sphere_receiving_matches_original_tetrahedron_and_public_unit_policy():
    import pyunitwizard as puw

    from devtools.reference_validator.receiving import (
        freeze_hull_model,
        freeze_tetrahedron,
    )

    path = (
        Path(__file__).resolve().parents[1]
        / 'docs/content/benchlab/synthetic/regular_tetrahedron/artifacts/regular_tetrahedron_v1/input.json'
    )
    old = freeze_tetrahedron(path, probe_angstroms=1.4)
    model = freeze_hull_model(path, probe_angstroms=1.4)
    assert model.atoms == old.atoms
    assert model.probe == old.probe
    assert model.source_sha256 == old.source_sha256
    assert model.domain == old.with_center_hull().domain
    with puw.context(standard_units=['pm', 'fs', 'radians']):
        before = puw.configure.report()
        assert freeze_hull_model(path, probe_angstroms=1.4) == model
        assert puw.configure.report()['standard_units'] == before['standard_units']


def test_full_sphere_receiving_rejects_corrupt_atomic_radii(tmp_path):
    from pyunitwizard.record import RecordError

    from devtools.reference_validator.receiving import freeze_hull_model

    source = (
        Path(__file__).resolve().parents[1]
        / 'docs/content/benchlab/synthetic/regular_tetrahedron/artifacts/regular_tetrahedron_v1/input.json'
    )
    record = copy.deepcopy(json.loads(source.read_text()))
    record['atom_radii']['values'][0] += 1
    damaged = tmp_path / 'damaged.json'
    damaged.write_text(json.dumps(record))
    with pytest.raises(RecordError):
        freeze_hull_model(damaged, probe_angstroms=1.4)


def test_cli_full_hull_receiving_and_domain_proof_keep_new_outputs(tmp_path):
    root = Path(__file__).resolve().parents[1]
    original = (
        root
        / 'docs/content/benchlab/synthetic/regular_tetrahedron/artifacts/regular_tetrahedron_v1/input.json'
    )
    hull = (
        root
        / 'devguide/evidence/reference_validator_hulls_v1/local_receiving/originals/regular_tetrahedron/certificate.json'
    )
    model_path, proof_path = tmp_path / 'model.json', tmp_path / 'proof.json'
    base = [sys.executable, '-m', 'devtools.reference_validator']
    receive = [
        'freeze-hull-model',
        str(original),
        str(model_path),
        '--probe-angstroms',
        '1.4',
        '--hull-certificate',
        str(hull),
    ]
    for command in [
        receive,
        ['domain-proof', str(model_path), str(proof_path)],
        ['verify', str(model_path), str(proof_path)],
    ]:
        done = subprocess.run(
            base + command, capture_output=True, text=True, check=True, timeout=10
        )
    report = json.loads(done.stdout)
    assert report['domain_state'] == 'unknown'
    assert report['n_components'] is None
    repeated = subprocess.run(
        base + receive, capture_output=True, text=True, timeout=10
    )
    assert repeated.returncode == 2


def test_steric_capture_defaults_to_small_controls_and_retains_rejected_candidates(
    tmp_path,
):
    from devtools.reference_validator.capture_hull_sterics import capture

    protocol = (
        Path(__file__).resolve().parents[1]
        / 'devguide/evidence/reference_validator_hull_sterics_v1/protocol.json'
    )
    output = tmp_path / 'receiving'
    capture(protocol, output)
    receipt = json.loads((output / 'receipt.json').read_text())
    assert len(receipt['profiles']) == 4
    assert receipt['originals_selected'] is False
    row = next(
        row for row in receipt['profiles'] if row['name'] == 'cube_interior_obstacle'
    )
    assert (
        row['queries']['colliding_straight']['verification_status']
        == 'rejected_candidate'
    )
    assert row['queries']['bent_clearance']['connected'] is True
    assert row['queries']['whole_domain']['n_components'] is None
    model = Model.from_record(
        json.loads((output / 'cube_interior_obstacle/model.json').read_text())
    )
    assert isinstance(model.domain, HullDomain)
    assert len(model.atoms) == 9
    with pytest.raises(FileExistsError):
        capture(protocol, output)
