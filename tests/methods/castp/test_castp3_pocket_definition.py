"""Explicit pocket definitions, independent of the radius profile."""

from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from topomt.third_party.castp3 import _native_impl
from topomt.third_party.castp3.core.castp_core import components
from topomt.third_party.castp3.core.castp_core.mouths import MouthFaceRecord


def test_castp3_depth_keeps_finite_sink_when_exterior_is_also_reachable(monkeypatch):
    geometry = SimpleNamespace(
        mesh=SimpleNamespace(
            n_simplices=2,
            neighbors=np.asarray([[1, -1, -1, -1], [-1, -1, -1, -1]]),
        ),
        simplex_rho_ranks=np.asarray([1, 2]),
        face_is_on_hull=np.asarray([[False, True, False, False], [False] * 4]),
    )
    monkeypatch.setattr(components, '_hidden_triangle', lambda *args: True)
    monkeypatch.setattr(components, '_triangle_is_attached', lambda *args: True)
    monkeypatch.setattr(
        components, '_iter_master_tetra_rho_indices', lambda *args, **kwargs: [1, 0]
    )
    np.testing.assert_array_equal(components._compute_pocket_depths(geometry), [2, 1])
    np.testing.assert_array_equal(
        components._compute_castp3_pocket_depths(geometry), [1, 1]
    )


@pytest.mark.parametrize('definition', ['unknown', None, 3])
def test_invalid_pocket_definition_fails_before_geometry_build(monkeypatch, definition):
    def unexpected_build(*args, **kwargs):
        pytest.fail('Invalid policy must be rejected before molecular preparation.')

    monkeypatch.setattr(_native_impl, 'build_castp_geometry', unexpected_build)
    with pytest.raises(ValueError, match='pocket_definition'):
        _native_impl.castp(None, pocket_definition=definition)


def test_castp3_policy_rejects_probe_limited_literature_diagnostic():
    with pytest.raises(ValueError, match='probe_limited_depth'):
        components.build_castp_feature_records(
            None, probe_radius=1.4, pocket_definition='castp3', probe_limited_depth=True
        )


@pytest.mark.parametrize('definition', ['literature', 'castp3'])
@pytest.mark.parametrize('radii_model', ['protor', 'castp3_protor'])
def test_native_policy_and_radii_are_independent_and_recorded(
    monkeypatch, definition, radii_model
):
    captured = {}

    def build_geometry(*args, **kwargs):
        captured['radii_model'] = kwargs['radii_model']
        return SimpleNamespace(base_rank=1, mesh=object())

    def build_records(geometry, **kwargs):
        captured['pocket_definition'] = kwargs['pocket_definition']
        return [{'id': 1, 'feature_type': 'pocket', 'atom_indices': [0]}]

    monkeypatch.setattr(_native_impl, 'build_castp_geometry', build_geometry)
    monkeypatch.setattr(_native_impl, 'build_castp_feature_records', build_records)
    monkeypatch.setattr(
        _native_impl, 'get_physicochemical_properties', lambda *args: {}
    )
    records, _mesh = _native_impl.castp(
        None, pocket_definition=definition, radii_model=radii_model
    )
    assert captured == {'radii_model': radii_model, 'pocket_definition': definition}
    assert (
        records[0]['properties']['castp3_execution']['pocket_definition'] == definition
    )
    assert records[0]['properties']['castp3_execution']['radii_model'] == radii_model


def test_mouth_reports_triangle_vertices_even_for_attached_faces():
    face = MouthFaceRecord(
        face_atoms=(0, 1, 2), simplex_index=0, face_index=0, triangle_index=0
    )
    geometry = SimpleNamespace(
        mesh=SimpleNamespace(
            neighbors=np.asarray([[1, -1, -1, -1]]),
            simplex_atom_indices=np.asarray([[0, 1, 2, 3], [0, 1, 2, 9]]),
        ),
        face_rho_ranks=np.asarray([[0, 1, 1, 1]]),
    )
    assert components._mouth_cluster_atom_indices_for_reporting(
        geometry, [face], {0}
    ) == {0, 1, 2}


def test_castp3_definition_recovers_separate_1cdo_channel_and_branched_channel(
    monkeypatch,
):
    from devtools.castp.compare_castp3_oracles import audit_castp3_oracle_zip

    monkeypatch.setattr(
        _native_impl, 'get_physicochemical_properties', lambda *args: {}
    )
    archive = (
        Path(__file__).resolve().parents[3] / 'topomt/data/CASTpFold_server/1cdo.zip'
    )
    result = audit_castp3_oracle_zip(
        archive, pocket_definition='castp3', radii_model='castp3_protor'
    )
    assert result['policy']['pocket_definition'] == 'castp3'
    assert result['passed']
    assert result['features']['channel']['exact_count'] == 3
    assert result['features']['branched_channel']['exact_count'] == 3


def test_topography_preserves_explicit_execution_choices(monkeypatch):
    from topomt.third_party.castp3 import native

    execution = {'pocket_definition': 'castp3', 'radii_model': 'protor'}
    record = {
        'id': 1,
        'feature_type': 'pocket',
        'atom_indices': [0, 1],
        'properties': {'castp3_execution': execution},
    }
    monkeypatch.setattr(
        native, '_native_castp', lambda *args, **kwargs: ([record], None)
    )
    topography = native.get_topography(None)
    feature = next(iter(topography.features.values()))
    assert feature.properties['castp3_execution'] == execution
