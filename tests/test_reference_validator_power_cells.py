"""Complete multi-ball regions require checked cells, edges and incidences."""

import copy
import json
import subprocess
import sys
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path

import pytest

from devtools.reference_validator.model import (
    Box,
    Model,
    decode_point,
    encode_point,
    point,
    record_digest,
)
from devtools.reference_validator.power_cells import topology_certificate
from devtools.reference_validator.power_contracts import PowerLimits
from devtools.reference_validator.verify import verify
from devtools.reference_validator.verify.power_cells import locate, path_between


def _barriers(probe=F(1), unequal=False):
    return Model.from_spheres(
        [(-8, 0, 0), (8, 0, 0)],
        [4, 5 if unequal else 4],
        probe,
        domain=Box(point((-20, -3, -4)), point((20, 3, 4))),
    )


@pytest.mark.parametrize(
    'probe,count', [(F(1) - F(1, 2**80), 1), (F(1), 3), (F(1) + F(1, 2**80), 3)]
)
def test_two_complete_barriers_have_an_exact_one_three_three_throat_transition(
    probe, count
):
    model = _barriers(probe)
    checked = verify(model, topology_certificate(model))
    assert checked['topology_complete'] is True
    assert checked['n_components'] == count
    assert checked['n_boundary_patches'] == count
    assert checked['per_region_volume_status'] == 'not_computed'


def test_unequal_radii_and_all_source_cells_remain_present():
    model = _barriers(unequal=True)
    cert = topology_certificate(model)
    assert len(cert['cells']) == 2
    assert verify(model, cert)['n_components'] == 3


@pytest.mark.parametrize(
    'probe,count', [(F(1) - F(1, 2**80), 1), (F(1), 0), (F(1) + F(1, 2**80), 0)]
)
def test_eight_corner_balls_keep_tiny_void_then_certify_complete_union_coverage(
    probe, count
):
    seed = Model.from_spheres(
        list(product((-1, 1), (-2, 2), (-2, 2))),
        [2] * 8,
        probe,
        domain=Box(point((-2, -3, -3)), point((2, 3, 3))),
    )
    model = seed.with_center_hull()
    checked = verify(model, topology_certificate(model))
    assert checked['n_components'] == count
    assert checked['n_boundary_patches'] == 0
    if count == 0:
        assert checked['volume_upper'] == ['0', '1']


@pytest.mark.parametrize(
    'radius,count,patches', [(F(3, 2), 1, 4), (F(5, 3), 1, 0), (F(7, 4), 0, 0)]
)
def test_regular_tetrahedron_separates_region_count_from_boundary_patch_count(
    radius, count, patches
):
    seed = Model.from_spheres(
        [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)],
        [radius] * 4,
        0,
        domain=Box(point((-2, -2, -2)), point((2, 2, 2))),
    )
    model = seed.with_center_hull()
    checked = verify(model, topology_certificate(model))
    assert checked['n_components'] == count
    assert checked['n_boundary_patches'] == patches
    assert all(
        len(
            {
                p['region_id']
                for p in checked['boundary_patches']
                if p['patch_id'] in r['boundary_patch_ids']
            }
        )
        <= 1
        for r in checked['regions']
    )


def test_boundary_patch_supports_and_anchor_membership_preserve_four_patches_one_region():
    seed = Model.from_spheres(
        [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)],
        [F(3, 2)] * 4,
        0,
        domain=Box(point((-2, -2, -2)), point((2, 2, 2))),
    )
    model = seed.with_center_hull()
    cert = topology_certificate(model)
    checked = verify(model, cert)
    assert len(checked['regions']) == 1 and len(checked['boundary_patches']) == 4
    for patch in checked['boundary_patches']:
        assert patch['face_supports']
        x = decode_point(checked['nodes'][patch['node_ids'][0]])
        located = locate(model, cert, x)
        assert located['region_id'] == patch['region_id']
        assert located['boundary_patch_id'] == patch['patch_id']


def test_identical_and_strictly_dominated_coincident_balls_are_not_dropped_or_double_counted():
    model = Model.from_spheres(
        [(-8, 0, 0), (8, 0, 0), (-8, 0, 0)], [4] * 3, 1, domain=_barriers().domain
    )
    cert = topology_certificate(model)
    assert len(cert['cells']) == 3
    assert verify(model, cert)['n_components'] == 3
    nested = Model.from_spheres(
        [(0, 0, 0)] * 2, [1, 2], 0, domain=Box(point((-1, -1, -1)), point((1, 1, 1)))
    )
    proof = topology_certificate(nested)
    assert any('coincident_dominator' in c for c in proof['cells'])
    assert verify(nested, proof)['n_components'] == 0


@pytest.mark.parametrize(
    'dimension,centers,radii,domain,count',
    [
        (
            2,
            [(-3, 0, 0), (3, 0, 0), (0, 0, 0)],
            [5, 5, 4],
            Box(point((-1, -10, -10)), point((1, 10, 10))),
            1,
        ),
        (
            1,
            [(-3, 0, 0), (3, 0, 0), (0, -3, 0), (0, 3, 0), (0, 0, 0)],
            [5, 5, 5, 5, 4],
            Box(point((-1, -1, -10)), point((1, 1, 10))),
            2,
        ),
        (
            0,
            [
                (-3, 0, 0),
                (3, 0, 0),
                (0, -3, 0),
                (0, 3, 0),
                (0, 0, -3),
                (0, 0, 3),
                (0, 0, 0),
            ],
            [5] * 6 + [4],
            Box(point((-10, -10, -10)), point((10, 10, 10))),
            1,
        ),
    ],
)
def test_lower_dimensional_power_cells_keep_their_incidence(
    dimension, centers, radii, domain, count
):
    model = Model.from_spheres(centers, radii, 0, domain=domain)
    cert = topology_certificate(model)
    cell = cert['cells'][-1]
    assert len(cell['vertices']) >= 1
    assert verify(model, cert)['n_components'] == count
    if dimension == 0:
        assert cell['vertices'] == [encode_point(point((0, 0, 0)))]
    elif dimension == 1:
        assert len(cell['vertices']) == 2


def test_noncoincident_empty_power_cell_is_proved_not_omitted():
    model = Model.from_spheres(
        [(-3, 0, 0), (0, 0, 0)],
        [1, 10],
        0,
        domain=Box(point((-1, -1, -1)), point((1, 1, 1))),
    )
    cert = topology_certificate(model)
    assert cert['cells'][0]['vertices'] == []
    assert verify(model, cert)['n_components'] == 0


def test_empty_obstacle_set_has_one_region_and_one_boundary_patch():
    model = Model.from_spheres(
        [], [], 0, domain=Box(point((-1, -1, -1)), point((1, 1, 1)))
    )
    checked = verify(model, topology_certificate(model))
    assert checked['n_components'] == checked['n_boundary_patches'] == 1


def test_power_construction_enforces_vertex_and_atom_work_budgets():
    empty = Model.from_spheres(
        [], [], 0, domain=Box(point((-1, -1, -1)), point((1, 1, 1)))
    )
    with pytest.raises(ValueError, match='vertex'):
        topology_certificate(empty, limits=PowerLimits(max_vertices_per_cell=1))
    with pytest.raises(ValueError, match='atom'):
        topology_certificate(_barriers(), limits=PowerLimits(max_atoms=1))
    with pytest.raises(ValueError):
        PowerLimits(max_atoms=True)


def test_power_construction_agrees_with_every_saved_complete_one_ball_box_control():
    base = (
        Path(__file__).resolve().parents[1]
        / 'devguide/evidence/reference_validator_box_topology_v1/receiving'
    )
    receipt = json.loads((base / 'receipt.json').read_text())
    files = list(base.glob('*.model.json'))
    assert len(files) == len(receipt['cases']) == 13
    for model_file in files:
        model = Model.from_record(json.loads(model_file.read_text()))
        old = base / (model_file.name.replace('.model.json', '.verification.json'))
        expected = json.loads(old.read_text())
        assert (
            verify(model, topology_certificate(model))['n_components']
            == expected['n_components']
        )


def test_producer_preserves_every_frozen_exact_cell_and_complete_partition():
    base = (
        Path(__file__).resolve().parents[1]
        / 'devguide/evidence/reference_validator_power_cells_v1'
    )
    spec = json.loads((base / 'protocol.json').read_text())
    assert len(spec['cases']) == 20
    for row in spec['cases']:
        model = Model.from_record(row['model'])
        old = json.loads(
            (base / 'receiving' / row['name'] / 'certificate.json').read_text()
        )
        # Exact proof equality protects all cells/vertices/edges and the final
        # incidence, not merely an unchanged count after a producer optimization.
        assert topology_certificate(model) == old


def test_complete_region_assignment_proves_separation_and_returns_continuous_paths():
    model = _barriers()
    cert = topology_certificate(model)
    left, mid, right = [point((x, 0, 0)) for x in [-15, 0, 15]]
    regions = {locate(model, cert, x)['region_id'] for x in [left, mid, right]}
    assert len(regions) == 3
    assert path_between(model, cert, left, mid)['connected'] is False
    connected = path_between(model, cert, left, point((-14, 1, 0)))
    assert connected['connected'] is True
    assert connected['model_sha256'] == model.digest
    assert connected['start'] == encode_point(left)
    assert verify(model, connected['path_certificate'])['path_validated'] is True
    assert locate(model, cert, point((-8, 0, 0)))['point_state'] == 'blocked'
    assert locate(model, cert, point((30, 0, 0)))['point_state'] == 'outside_domain'


def test_anchor_batch_checks_complete_topology_once_and_detaches_its_evidence(
    monkeypatch,
):
    import devtools.reference_validator.verify as module
    from devtools.reference_validator.verify.power_cells import query_anchors

    model = _barriers()
    proof = topology_certificate(model)
    saved = copy.deepcopy(proof)
    kinds = []
    original = module.verify

    def checked(model, cert, **kwargs):
        kinds.append(cert['kind'])
        result = original(model, cert, **kwargs)
        if cert['kind'] == 'power_cell_topology':
            # The caller's mutable object must not alter the verified batch.
            proof['nodes'].clear()
        return result

    monkeypatch.setattr(module, 'verify', checked)
    result = query_anchors(
        model,
        proof,
        anchors={
            'left': point((-15, 0, 0)),
            'same': point((-14, 1, 0)),
            'middle': point((0, 0, 0)),
            'blocked': point((-8, 0, 0)),
        },
        pairs=[('left', 'same'), ('left', 'middle')],
    )
    assert kinds.count('power_cell_topology') == 1
    assert result['pairs'][0]['connected'] is True
    assert result['pairs'][1]['connected'] is False
    assert result['length_unit'] == 'nm'
    assert result['model_sha256'] == model.digest
    assert result['locations']['blocked']['point_state'] == 'blocked'
    assert result['pairs'][0]['topology_certificate_sha256'] == record_digest(saved)


def test_anchor_batch_rejects_unknown_pairs_and_blocked_connection_anchors():
    from devtools.reference_validator.verify.power_cells import query_anchors

    model = _barriers()
    proof = topology_certificate(model)
    with pytest.raises(ValueError):
        query_anchors(
            model,
            proof,
            anchors={'free': point((-15, 0, 0))},
            pairs=[('free', 'missing')],
        )
    with pytest.raises(ValueError, match='both be free'):
        query_anchors(
            model,
            proof,
            anchors={'free': point((-15, 0, 0)), 'blocked': point((-8, 0, 0))},
            pairs=[('free', 'blocked')],
        )


def test_missing_cell_false_partition_and_bad_incidence_are_rejected():
    model = _barriers()
    cert = topology_certificate(model)
    mutations = []
    missing = copy.deepcopy(cert)
    missing['cells'].pop()
    mutations.append(missing)
    merged = copy.deepcopy(cert)
    merged['components'] = [sorted(sum(merged['components'], []))]
    mutations.append(merged)
    edge = copy.deepcopy(cert)
    target = next(c for c in edge['cells'] if c['edges'])
    target['edges'].pop()
    mutations.append(edge)
    free = copy.deepcopy(cert)
    target = next(c for c in free['cells'] if c['free_edges'])
    target['free_edges'].pop()
    mutations.append(free)
    for bad in mutations:
        with pytest.raises(ValueError):
            verify(model, bad)
    with pytest.raises(ValueError):
        verify(replace(model, probe=F(2)), cert)


def test_false_boundary_merge_and_boolean_source_identity_are_rejected():
    seed = Model.from_spheres(
        [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)],
        [F(3, 2)] * 4,
        0,
        domain=Box(point((-2, -2, -2)), point((2, 2, 2))),
    )
    model = seed.with_center_hull()
    cert = topology_certificate(model)
    merged = copy.deepcopy(cert)
    merged['boundary_components'] = [sorted(sum(merged['boundary_components'], []))]
    with pytest.raises(ValueError, match='partition'):
        verify(model, merged)
    corrupt = copy.deepcopy(cert)
    corrupt['cells'][0]['atom_id'] = False
    with pytest.raises(ValueError, match='identity'):
        verify(model, corrupt)


def test_exact_rational_rotation_translation_and_scale_preserve_topology():
    model = Model.from_spheres(
        [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)],
        [F(3, 2)] * 4,
        0,
        domain=Box(point((-2, -2, -2)), point((2, 2, 2))),
    ).with_center_hull()
    shift = (F(2**60), F(-(2**59)), F(7, 11))

    def transform(x):
        a, b, c = x
        # Rational orthogonal rotation, then positive scaling and translation.
        y = ((3 * a - 4 * b) / 5, (4 * a + 3 * b) / 5, c)
        return tuple(7 * v + s for v, s in zip(y, shift))

    moved = Model.from_spheres(
        [transform(a.center) for a in model.atoms],
        [7 * a.radius for a in model.atoms],
        7 * model.probe,
        domain=Box(point((-(2**70), -(2**70), -(2**70))), point((2**70, 2**70, 2**70))),
    ).with_center_hull()
    checked = verify(moved, topology_certificate(moved))
    assert checked['n_components'] == 1
    assert checked['n_boundary_patches'] == 4


def test_power_cli_produces_and_independently_checks_saved_evidence(tmp_path):
    model_file = tmp_path / 'model.json'
    model_file.write_text(json.dumps(_barriers().to_record()))
    proof_file = tmp_path / 'proof.json'
    command = [sys.executable, '-m', 'devtools.reference_validator']
    produced = subprocess.run(
        command + ['power-topology', str(model_file), str(proof_file)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert produced.returncode == 0, produced.stderr
    checked = subprocess.run(
        command + ['verify', str(model_file), str(proof_file)],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert json.loads(checked.stdout)['n_components'] == 3


@pytest.mark.parametrize('use_hull', [False, True])
def test_saved_complete_checker_imports_no_producer_dfnd_or_numerical_libraries(
    tmp_path,
    use_hull,
):
    model = _barriers()
    if use_hull:
        model = Model.from_spheres(
            [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)],
            [F(3, 2)] * 4,
            0,
            domain=Box(point((-2, -2, -2)), point((2, 2, 2))),
        ).with_center_hull()
    proof = topology_certificate(model)
    (tmp_path / 'model.json').write_text(json.dumps(model.to_record()))
    (tmp_path / 'proof.json').write_text(json.dumps(proof))
    script = """
import sys,json
from pathlib import Path
for name in ['topomt','numpy','scipy','pyunitwizard','devtools.reference_validator.producer','devtools.reference_validator.power_cells','devtools.reference_validator.center_hull']:
 sys.modules[name]=None
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify import verify
m=Model.from_record(json.loads(Path(sys.argv[1]).read_text()))
print(json.dumps(verify(m,json.loads(Path(sys.argv[2]).read_text()))))
"""
    result = subprocess.run(
        [
            sys.executable,
            '-c',
            script,
            str(tmp_path / 'model.json'),
            str(tmp_path / 'proof.json'),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert json.loads(result.stdout)['n_components'] == (1 if use_hull else 3)
