"""Volume enclosures retain exact topology, shared uncertainty and requests."""

from fractions import Fraction as F

import pytest

from devtools.reference_validator.model import Box, Model, decode_scalar, point
from devtools.reference_validator.power_cells import topology_certificate
from devtools.reference_validator.region_volume import (
    refine_region_volume,
    region_volume_certificate,
)
from devtools.reference_validator.verify.region_volume import check_region_volume
from devtools.reference_validator.volume_request import VolumeRequest


def _model(radii):
    return Model.from_spheres(
        [(0, 0, 0)] * len(radii),
        radii,
        0,
        domain=Box(point((-1, -1, -1)), point((1, 1, 1))),
    )


@pytest.mark.parametrize('radii,count,volume', [([], 1, 8), ([3], 0, 0)])
def test_exact_full_and_empty_volumes_satisfy_literal_zero_error(radii, count, volume):
    model = _model(radii)
    cert = region_volume_certificate(
        model, topology_certificate(model), VolumeRequest(F(0), F(0))
    )
    result = check_region_volume(model, cert)
    assert result['n_components'] == count
    assert (
        decode_scalar(result['volume_lower'])
        == decode_scalar(result['volume_upper'])
        == volume
    )
    assert result['precision_status'] == 'resolved'


def test_eight_regions_share_uncertainty_without_duplicate_total_mass():
    model = _model([F(3, 2), F(3, 2)])
    cert = region_volume_certificate(
        model, topology_certificate(model), VolumeRequest(F(1, 100)), max_leaves=1
    )
    result = check_region_volume(model, cert)
    assert result['n_components'] == 8
    assert decode_scalar(result['volume_upper']) == 8
    assert sum(decode_scalar(r['upper']) for r in result['regions']) == 64
    assert result['precision_status'] == 'unresolved'


def test_refinement_preserves_topology_and_nested_bounds():
    model = _model([F(3, 2)])
    request = VolumeRequest(F(1, 2**24), F(1, 2**24))
    old = region_volume_certificate(
        model, topology_certificate(model), request, max_leaves=8
    )
    new = refine_region_volume(model, old, max_leaves=64)
    a, b = (check_region_volume(model, c) for c in [old, new])
    assert a['n_components'] == b['n_components'] == 8
    assert decode_scalar(a['volume_lower']) <= decode_scalar(b['volume_lower'])
    assert decode_scalar(b['volume_upper']) <= decode_scalar(a['volume_upper'])
    assert all(
        decode_scalar(x['lower']) <= decode_scalar(y['lower'])
        and decode_scalar(y['upper']) <= decode_scalar(x['upper'])
        for x, y in zip(a['regions'], b['regions'])
    )
    altered = dict(new)
    altered['leaves'] = new['leaves'][1:]
    with pytest.raises(ValueError):
        check_region_volume(model, altered)


def test_analytic_volume_can_be_assigned_only_to_a_proved_single_region():
    model = Model.from_spheres(
        [(0, 0, 0)], [1], 0, domain=Box(point((-2, -2, -2)), point((2, 2, 2)))
    )
    cert = region_volume_certificate(
        model,
        topology_certificate(model),
        VolumeRequest(F(64, 2**32), F(1, 2**32)),
        method='analytic_single_region',
    )
    result = check_region_volume(model, cert)
    assert result['precision_status'] == 'resolved'
    assert result['regions'][0]['lower'] == result['volume_lower']
    model = _model([F(3, 2)])
    with pytest.raises(ValueError):
        region_volume_certificate(
            model,
            topology_certificate(model),
            VolumeRequest(F(1, 100)),
            method='analytic_single_region',
        )


def test_changed_request_cannot_be_presented_as_a_same_run_refinement():
    from copy import deepcopy

    from devtools.reference_validator.verify.region_volume import (
        check_volume_transition,
    )

    model = _model([F(3, 2)])
    old = region_volume_certificate(
        model, topology_certificate(model), VolumeRequest(F(1, 100)), max_leaves=8
    )
    new = refine_region_volume(model, old, max_leaves=64)
    assert check_volume_transition(model, old, new)['lineage_status'] == 'checked'
    changed = deepcopy(new)
    changed['request'] = VolumeRequest(F(1, 10)).to_record()
    with pytest.raises(ValueError):
        check_volume_transition(model, old, changed)
    changed = deepcopy(new)
    changed['request']['volume_unit'] = 'angstrom**3'
    with pytest.raises(ValueError):
        check_region_volume(model, changed)


def test_duplicate_obstacles_do_not_duplicate_integrated_volume():
    results = []
    for radii in [[F(3, 2)], [F(3, 2), F(3, 2)]]:
        model = _model(radii)
        cert = region_volume_certificate(
            model, topology_certificate(model), VolumeRequest(F(1, 100)), max_leaves=64
        )
        results.append(check_region_volume(model, cert))
    for key in ['volume_lower', 'volume_upper', 'regions', 'precision_status']:
        assert results[0][key] == results[1][key]


def test_saved_volume_bundle_rechecks_before_same_kernel_refinement(tmp_path):
    from devtools.reference_validator.region_volume import (
        load_region_bundle,
        save_region_bundle,
    )
    from devtools.reference_validator.verify.region_volume import (
        check_volume_transition,
    )

    model = _model([F(3, 2)])
    old = region_volume_certificate(
        model, topology_certificate(model), VolumeRequest(F(1, 100)), max_leaves=8
    )
    save_region_bundle(tmp_path / 'first', model, old)
    saved = load_region_bundle(tmp_path / 'first', model)
    new = refine_region_volume(model, saved, max_leaves=64)
    assert check_volume_transition(model, old, new)['lineage_status'] == 'checked'
    with pytest.raises(FileExistsError):
        save_region_bundle(tmp_path / 'first', model, old)
    (tmp_path / 'torn').mkdir()
    (tmp_path / 'torn/certificate.json').write_text('{}')
    with pytest.raises(ValueError):
        load_region_bundle(tmp_path / 'torn', model)
    (tmp_path / 'first/certificate.json').write_text('{}')
    with pytest.raises(ValueError):
        load_region_bundle(tmp_path / 'first', model)


def test_a_wholly_free_nontessellated_hull_has_exact_volume():
    from devtools.reference_validator.model import Tetrahedron
    from devtools.reference_validator.verify.geometry import volume

    domain = Tetrahedron(
        tuple(point(v) for v in [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)])
    )
    model = Model.from_spheres([], [], 0, domain=domain)
    cert = region_volume_certificate(
        model, topology_certificate(model), VolumeRequest(F(0), F(0)), max_leaves=1
    )
    result = check_region_volume(model, cert)
    assert (
        decode_scalar(result['volume_lower'])
        == decode_scalar(result['volume_upper'])
        == volume(domain)
    )
    assert result['precision_status'] == 'resolved'


def test_generic_reader_honors_a_smaller_leaf_work_envelope():
    from devtools.reference_validator.verify import Limits, verify

    model = _model([F(3, 2)])
    cert = region_volume_certificate(
        model, topology_certificate(model), VolumeRequest(F(1, 100)), max_leaves=64
    )
    with pytest.raises(ValueError, match='leaf envelope'):
        verify(model, cert, limits=Limits(max_leaves=1))


def test_saved_volume_checker_runs_without_producer_or_scientific_packages(tmp_path):
    import json
    import subprocess
    import sys

    model = _model([F(3, 2)])
    cert = region_volume_certificate(
        model, topology_certificate(model), VolumeRequest(F(1, 100)), max_leaves=8
    )
    (tmp_path / 'model.json').write_text(json.dumps(model.to_record()))
    (tmp_path / 'certificate.json').write_text(json.dumps(cert))
    script = """
import sys,json
from pathlib import Path
for name in ['topomt','numpy','scipy','pyunitwizard','devtools.reference_validator.region_volume','devtools.reference_validator.power_cells','devtools.reference_validator.producer']:
 sys.modules[name]=None
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify import verify
model=Model.from_record(json.loads(Path(sys.argv[1]).read_text()))
result=verify(model,json.loads(Path(sys.argv[2]).read_text()))
assert result['n_components']==8 and result['precision_status']=='unresolved'
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


def test_asymmetric_barriers_keep_three_independently_named_regions():
    from devtools.reference_validator.verify.power_cells import query_anchors

    model = Model.from_spheres(
        [(-8, 0, 0), (8, 0, 0)],
        [4, 5],
        1,
        domain=Box(point((-20, -3, -4)), point((20, 3, 4))),
    )
    topology = topology_certificate(model)
    anchors = query_anchors(
        model,
        topology,
        anchors={
            name: point((x, 0, 0))
            for name, x in [('left', -20), ('middle', 0), ('right', 20)]
        },
        pairs=[],
    )
    cert = region_volume_certificate(
        model, topology, VolumeRequest(F(1920, 2**24), F(1, 2**24)), max_leaves=512
    )
    result = check_region_volume(model, cert)
    bounds = {r['region_id']: r for r in result['regions']}
    assert len(bounds) == 3
    assert len({p['region_id'] for p in anchors['locations'].values()}) == 3
    # Independent column formula: I_R=integral_rectangle sqrt(R²-y²-z²).
    # Left=576-I_5, right=576-I_6, middle=768-I_5-I_6. Pointwise
    # 0<=I_5<=240 and 144<I_6<=288 give these conservative bounds.
    independent = {'left': (336, 576), 'middle': (240, 624), 'right': (288, 432)}
    for name, (lower, upper) in independent.items():
        row = bounds[anchors['locations'][name]['region_id']]
        assert decode_scalar(row['lower']) <= upper
        assert decode_scalar(row['upper']) >= lower
    for name in ['left', 'right']:
        assert (
            decode_scalar(bounds[anchors['locations'][name]['region_id']]['lower']) > 0
        )
    assert result['precision_status'] == 'unresolved'
