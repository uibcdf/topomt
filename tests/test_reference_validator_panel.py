"""The six-case observational panel keeps exact proofs and honest resources."""

import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path

import pytest

from devtools.reference_validator.model import Box, Model, decode_point, point

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    ROOT
    / 'docs/content/benchlab/synthetic/artifacts/reference_validator_panel_v1/protocol.json'
)


def test_axis_candidates_hit_exact_hull_boundaries_without_claiming_apertures():
    from devtools.reference_validator.benchlab_panel import _rays

    model = Model.from_spheres(
        list(product((-1, 1), repeat=3)),
        [F(1, 10)] * 8,
        F(1, 10),
        domain=Box(point((-2, -2, -2)), point((2, 2, 2))),
    ).with_center_hull()
    rays = _rays(model)
    assert len(rays) == 6
    assert {decode_point(row['target']) for row in rays} == {
        point(x)
        for x in [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    }
    assert all(row['active_planes'] for row in rays)
    assert all('n_patches' not in row for row in rays)


def test_fresh_case_worker_retains_three_profiles_and_the_stronger_tetrahedron_route(
    tmp_path,
):
    from devtools.reference_validator.benchlab_panel import capture

    out = tmp_path / 'panel'
    capture(PROTOCOL, out, cases=('regular_tetrahedron',))
    receipt = json.loads((out / 'receipt.json').read_text())
    case = receipt['cases']['regular_tetrahedron']
    assert case['status'] == 'completed'
    assert len(case['profiles']) == 3
    assert case['worker_wall_seconds'] > 0
    assert case['worker_cpu_seconds'] > 0
    assert case['peak_rss_kib_linux'] > 0
    for row in case['profiles']:
        assert row['whole_hull']['n_components'] is None
        assert row['whole_hull']['topology_complete'] is False
        assert row['phases']['saved_model_check']['wall_seconds'] > 0
    negative = case['profiles'][-1]['tetrahedron_partition']
    assert negative['topology_complete'] is True
    assert negative['n_components'] == 0
    assert negative['volume_upper'] == ['0', '1']
    with pytest.raises(FileExistsError):
        capture(PROTOCOL, out, cases=('regular_tetrahedron',))


def test_resource_deferral_preserves_unknown_instead_of_zero(tmp_path, monkeypatch):
    import devtools.reference_validator.benchlab_panel as panel

    monkeypatch.setattr(
        panel, '_host', lambda: {'safe': False, 'reason': 'controlled_memory_pressure'}
    )
    out = tmp_path / 'deferred'
    panel.capture(PROTOCOL, out, cases=('regular_tetrahedron',))
    row = json.loads((out / 'receipt.json').read_text())['cases']['regular_tetrahedron']
    assert row['status'] == 'deferred_resources'
    assert row['n_components'] is None
    assert 'profiles' not in row


def test_stopped_worker_is_unresolved_not_an_empty_physical_result(
    tmp_path, monkeypatch
):
    import devtools.reference_validator.benchlab_panel as panel

    monkeypatch.setattr(
        panel,
        '_launch',
        lambda *args, **kwargs: {
            'status': 'unresolved',
            'reason': 'wall_limit',
            'n_components': None,
        },
    )
    out = tmp_path / 'stopped'
    panel.capture(PROTOCOL, out, cases=('regular_tetrahedron',))
    row = json.loads((out / 'receipt.json').read_text())['cases']['regular_tetrahedron']
    assert row['status'] == 'unresolved'
    assert row['n_components'] is None
    assert 'profiles' not in row
