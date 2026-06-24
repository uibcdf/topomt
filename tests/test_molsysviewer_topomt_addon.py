import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import molsysviewer
import numpy as np
import pytest
from molsysviewer.scene import SceneManager
from molsysviewer.shapes import ShapesManager

import topomt as tmt
from molsysviewer_topomt import get_addon
from molsysviewer_topomt.addon import lifecycle
from molsysviewer_topomt.integration import (
    attach_features,
    attach_pockets,
    attach_topography,
    new_view,
    register_with_molsysviewer,
    subset_topography,
)
from molsysviewer_topomt.payloads import feature_record_from_feature, topography_payload
from molsysviewer_topomt.render import show_topography_pockets
from molsysviewer_topomt.shapes import pocket_blob_provider
from molsysviewer_topomt.standalone import (
    build_topography_standalone0_html,
    launch_topography_standalone0,
)
from topomt import pyunitwizard as puw


def test_addon_spec_matches_current_molsysviewer_contract():
    addon = get_addon()

    assert addon.name == 'topomt'
    assert addon.package == 'molsysviewer-topomt'
    assert addon.workspaces[0].id == 'topomt'
    assert addon.workspaces[0].entry_panel == 'topography'
    assert [panel.id for panel in addon.panels] == ['topography', 'pockets']
    assert addon.context_actions[0].id == 'focus-topography-feature'
    assert addon.context_actions[1].id == 'dfnd-tetrahedron-info'
    assert (
        addon.context_actions[1].entry
        == 'molsysviewer_topomt.context.inspect_dfnd_tetrahedra'
    )
    assert addon.workbench_sections[0].id == 'topography-summary'
    assert addon.shape_providers[0].id == 'topography-pocket-blob'
    assert addon.export_helpers[0].id == 'topography-summary-export'


def test_lifecycle_records_runtime_on_view():
    view = molsysviewer.MolSysView()

    lifecycle.on_enable(view)
    assert view._topomt_addon_runtime.enabled is True
    assert view._topomt_addon_runtime.workspace == 'topomt'

    lifecycle.on_context_action(
        view, 'focus-topography-feature', {'feature_id': 'POC-1'}
    )
    assert (
        view._topomt_addon_runtime.last_context_action['action_id']
        == 'focus-topography-feature'
    )

    lifecycle.on_disable(view)
    assert view._topomt_addon_runtime.enabled is False


def test_tetrahedron_context_action_accepts_dry_domain_shape_selection():
    calls = []
    dfnd = types.SimpleNamespace(info=lambda tetra_ids: calls.append(list(tetra_ids)))
    topography = types.SimpleNamespace(dfnd=dfnd)
    view = types.SimpleNamespace(active_selection=None)

    lifecycle.on_enable(view)
    view._topomt_addon_runtime.topography = topography
    view.active_selection = types.SimpleNamespace(
        items=[
            {
                'source_kind': 'shape',
                'tag': 'dfn-dry-edges',
                'shape_name': 'Tetrahedron 104: combined_class=dry_sealed',
            }
        ]
    )

    lifecycle.on_context_action(
        view,
        'dfnd-tetrahedron-info',
        {'entity_refs': [{'kind': 'tetrahedron', 'tetrahedron_ids': [104]}]},
    )

    assert calls == [[104]]


def test_tetrahedron_context_action_accepts_dry_face_shape_selection():
    calls = []
    dfnd = types.SimpleNamespace(info=lambda tetra_ids: calls.append(list(tetra_ids)))
    topography = types.SimpleNamespace(dfnd=dfnd)
    view = types.SimpleNamespace(active_selection=None)

    lifecycle.on_enable(view)
    view._topomt_addon_runtime.topography = topography
    view.active_selection = types.SimpleNamespace(
        items=[
            {
                'source_kind': 'shape',
                'tag': 'dfn-dry-faces',
                'shape_name': 'Face id 1: tetrahedra 0-1; permeability=permeable',
            }
        ]
    )

    lifecycle.on_context_action(
        view,
        'dfnd-tetrahedron-info',
        {'entity_refs': [{'kind': 'face', 'tetrahedron_ids': [0, 1]}]},
    )

    assert calls == [[0, 1]]


def test_tetrahedron_context_entry_is_directly_executable():
    from molsysviewer_topomt.context import inspect_dfnd_tetrahedra

    calls = []
    dfnd = types.SimpleNamespace(info=lambda tetra_ids: calls.append(list(tetra_ids)))
    view = types.SimpleNamespace(active_selection=None)
    lifecycle.on_enable(view)
    view._topomt_addon_runtime.topography = types.SimpleNamespace(dfnd=dfnd)

    result = inspect_dfnd_tetrahedra(
        view,
        {'entity_refs': [{'kind': 'face', 'tetrahedron_ids': [4, 7]}]},
    )

    assert calls == [[4, 7]]
    assert result == {'action': 'dfnd-tetrahedron-info', 'tetrahedron_ids': [4, 7]}


def test_addon_registers_with_molsysviewer_host_registry():
    molsysviewer.addons.clear()
    molsysviewer.addons.register(get_addon(), lifecycle=lifecycle)

    assert molsysviewer.addons.contains('topomt') is True
    assert molsysviewer.addons.workspace_specs()[0]['id'] == 'topomt'
    assert molsysviewer.addons.panel_specs()[0]['addon'] == 'topomt'
    assert molsysviewer.addons.lifecycle_for('topomt') is lifecycle


def test_topography_payload_normalizes_current_topomt_features():
    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1, 2, 3],
        center=[0.1, 0.2, 0.3],
        volume=0.5,
        score=1.2,
        source='pocketeer',
        source_id='pocketeer:1',
        alpha_sphere_centers=[[0.1, 0.2, 0.3]],
        alpha_sphere_radii=[0.4],
    )

    feature = topo['POC-1']
    record = feature_record_from_feature(feature)
    assert record['feature_id'] == 'POC-1'
    assert record['feature_type'] == 'pocket'
    assert record['atom_indices'] == [1, 2, 3]
    assert record['sphere_radii'] == [0.4]

    payload = topography_payload(topo)
    assert payload['n_features'] == 1
    assert payload['feature_counts'] == {'pocket': 1}
    assert payload['features'][0]['source'] == 'pocketeer'


def test_topography_payload_converts_quantities_to_canonical_magnitudes():
    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1, 2, 3],
        center=puw.quantity([1.0, 2.0, 3.0], 'angstrom'),
        volume=puw.quantity(1000.0, 'angstrom**3'),
        alpha_sphere_centers=puw.quantity([[1.0, 2.0, 3.0]], 'angstrom'),
        alpha_sphere_radii=puw.quantity([2.0], 'angstrom'),
    )

    payload = topography_payload(topo)
    feature = payload['features'][0]

    assert feature['center'] == pytest.approx([0.1, 0.2, 0.3])
    assert feature['volume'] == pytest.approx(1.0)
    assert np.allclose(feature['sphere_centers'], [[0.1, 0.2, 0.3]])
    assert feature['sphere_radii'] == pytest.approx([0.2])


class DummyView:
    def __init__(self):
        self.messages = []
        self._layers = {}
        self._scene_objects = {}
        self._section_history = []
        self._section_counter = 0
        self._layer_counter = 0
        self.scene = SceneManager(self)
        self.shapes = ShapesManager(self)
        self.addons = molsysviewer.MolSysView().addons
        self.load_calls = []

    def _send(self, message):
        self.messages.append(message)

    def _next_layer_tag(self):
        self._layer_counter += 1
        return f'layer-{self._layer_counter}'

    def load(
        self,
        molecular_system,
        *,
        selection='all',
        structure_indices='all',
        syntax='MolSysMT',
        skip_digestion=False,
        **kwargs,
    ):
        self.load_calls.append(
            {
                'molecular_system': molecular_system,
                'selection': selection,
                'structure_indices': structure_indices,
                'syntax': syntax,
                'skip_digestion': skip_digestion,
            }
        )


def test_show_topography_pockets_uses_blob_and_marker_modes():
    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1, 2, 3],
        center=[0.1, 0.2, 0.3],
        volume=0.5,
        score=1.2,
        source='pocketeer',
        source_id='pocketeer:1',
        alpha_sphere_centers=[[0.1, 0.2, 0.3], [0.2, 0.3, 0.4]],
        alpha_sphere_radii=[0.4, 0.5],
    )
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-2',
        atom_indices=[4, 5, 6],
        center=[1.0, 1.1, 1.2],
        volume=0.1,
        source='manual',
        source_id='manual:2',
    )

    view = DummyView()
    result = show_topography_pockets(view, topo)

    assert result.counts['n_rendered'] == 2
    assert result.details['rendered'][0]['mode'] == 'blob'
    assert result.details['rendered'][1]['mode'] == 'marker'
    assert view.messages[0]['op'] == 'add_pocket_blob'
    assert view.messages[1]['op'] == 'add_sphere'


def test_show_topography_pockets_accepts_quantity_backed_features():
    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1, 2, 3],
        center=puw.quantity([1.0, 2.0, 3.0], 'angstrom'),
        volume=puw.quantity(1000.0, 'angstrom**3'),
        alpha_sphere_centers=puw.quantity([[1.0, 2.0, 3.0]], 'angstrom'),
        alpha_sphere_radii=puw.quantity([2.0], 'angstrom'),
    )

    view = DummyView()
    result = show_topography_pockets(view, topo)

    assert result.counts['n_rendered'] == 1
    assert view.messages[0]['op'] == 'add_pocket_blob'
    assert np.allclose(view.messages[0]['options']['centers'], [[1.0, 2.0, 3.0]])
    assert view.messages[0]['options']['radii'] == pytest.approx([2.0])


def test_pocket_blob_provider_renders_when_view_is_available():
    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1, 2, 3],
        center=[0.1, 0.2, 0.3],
        volume=0.5,
        score=1.2,
        source='pocketeer',
        source_id='pocketeer:1',
        alpha_sphere_centers=[[0.1, 0.2, 0.3]],
        alpha_sphere_radii=[0.4],
    )

    view = DummyView()
    result = pocket_blob_provider(view=view, topography=topo)

    assert result['has_view'] is True
    assert result['rendered'].counts['n_rendered'] == 1
    assert view.messages[0]['op'] == 'add_pocket_blob'


def test_attach_topography_enables_addon_and_renders():
    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1, 2, 3],
        center=[0.1, 0.2, 0.3],
        volume=0.5,
        source='manual',
        source_id='manual:1',
    )

    view = DummyView()
    register_with_molsysviewer()
    result = attach_topography(view, topo)

    assert result['addon_enabled'] is True
    assert result['rendered'].counts['n_rendered'] == 1
    assert view._topomt_addon_runtime.enabled is True


def test_new_view_uses_molsysviewer_factory(monkeypatch):
    topo = tmt.Topography()
    topo._molsys = 'system'
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1, 2, 3],
        center=[0.1, 0.2, 0.3],
        volume=0.5,
        source='manual',
        source_id='manual:1',
    )

    view = DummyView()

    def fake_new_view(molecular_system, **kwargs):
        view.load(molecular_system, **kwargs)
        return view

    monkeypatch.setattr(molsysviewer, 'new_view', fake_new_view)

    result_view = new_view(topo, selection='all')

    assert result_view is view
    assert view.load_calls[0]['molecular_system'] == 'system'
    assert view.messages[0]['op'] == 'add_sphere'


def test_new_view_feature_filter_keeps_complete_topography_attached(monkeypatch):
    topo = tmt.Topography()
    topo._molsys = 'system'
    topo.dfnd = types.SimpleNamespace(marker='complete-dfnd')
    topo.add_new_feature(
        feature_type='pocket', feature_id='POC-1', center=[0.0, 0.0, 0.0]
    )
    topo.add_new_feature(
        feature_type='pocket', feature_id='POC-2', center=[1.0, 1.0, 1.0]
    )
    view = DummyView()

    monkeypatch.setattr(molsysviewer, 'new_view', lambda _system, **_kwargs: view)

    result_view = new_view(topo, feature_ids=['POC-2'])
    runtime = result_view._topomt_addon_runtime

    assert runtime.topography is topo
    assert result_view.topography is topo
    assert runtime.active_feature_ids == ('POC-2',)
    assert runtime.topography.dfnd.marker == 'complete-dfnd'
    rendered_tags = [
        message.get('options', {}).get('tag')
        for message in view.messages
        if message.get('op') in {'add_sphere', 'add_pocket_blob'}
    ]
    assert rendered_tags == ['topomt-pocket:POC-2']


def test_subset_topography_keeps_only_requested_features():
    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1],
        center=[0.0, 0.0, 0.0],
    )
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-2',
        atom_indices=[2],
        center=[1.0, 1.0, 1.0],
    )

    subset = subset_topography(topo, ['POC-2'])

    assert list(subset.features.keys()) == ['POC-2']


def test_attach_features_renders_only_selected_feature_ids():
    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1],
        center=[0.0, 0.0, 0.0],
    )
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-2',
        atom_indices=[2],
        center=[1.0, 1.0, 1.0],
    )

    view = DummyView()
    register_with_molsysviewer()
    result = attach_features(view, topo, feature_ids=['POC-2'])

    assert result['rendered'].counts['n_rendered'] == 1
    assert result['selected_feature_ids'] == ['POC-2']
    assert result['rendered'].details['rendered'][0]['feature_id'] == 'POC-2'


def test_subset_topography_preserves_selected_relations_and_dfnd_semantics():
    topo = tmt.Topography()
    topo.dfnd = types.SimpleNamespace(marker='complete-dfnd')
    topo.add_new_feature(feature_type='pocket', feature_id='POC-1')
    topo.add_new_feature(feature_type='mouth', feature_id='MOU-1')
    topo.add_new_feature(feature_type='pocket', feature_id='POC-2')
    topo.connect_features('MOU-1', 'POC-1')

    subset = subset_topography(topo, ['POC-1', 'MOU-1'])

    assert list(subset) == ['POC-1', 'MOU-1']
    assert subset.parents_of('MOU-1', as_feature_ids=True) == {'POC-1'}
    assert subset.dfnd.marker == 'complete-dfnd'
    assert subset.dfnd is not topo.dfnd
    assert subset['POC-1'] is not topo['POC-1']


def test_subset_topography_preserves_real_dfnd_analysis(tmp_path):
    pdb = tmp_path / 'minimal_dfnd.pdb'
    pdb.write_text(
        '\n'.join(
            [
                'ATOM      1  C1  GLY A   1       1.874   1.874   1.874  1.00  0.00           C',
                'ATOM      2  C2  GLY A   1       1.874  -1.874  -1.874  1.00  0.00           C',
                'ATOM      3  C3  GLY A   1      -1.874   1.874  -1.874  1.00  0.00           C',
                'ATOM      4  C4  GLY A   1      -1.874  -1.874   1.874  1.00  0.00           C',
                'END',
                '',
            ]
        )
    )
    topo = tmt.get_topography(
        str(pdb),
        method='dfnd',
        probe_radius=1.4,
        min_size=0,
        transit_policy='resident_only',
    )
    selected_id = next(iter(topo))

    subset = subset_topography(topo, [selected_id])

    assert list(subset) == [selected_id]
    assert subset.dfnd is not topo.dfnd
    assert subset.dfnd.raw == topo.dfnd.raw
    assert subset.dfnd.dfn.components.wet


def test_attach_features_keeps_complete_source_and_tracks_feature_filter():
    topo = tmt.Topography()
    topo.dfnd = types.SimpleNamespace(marker='complete-dfnd')
    topo.add_new_feature(
        feature_type='pocket', feature_id='POC-1', center=[0.0, 0.0, 0.0]
    )
    topo.add_new_feature(
        feature_type='pocket', feature_id='POC-2', center=[1.0, 1.0, 1.0]
    )

    view = DummyView()
    register_with_molsysviewer()
    first = attach_features(view, topo, feature_ids=['POC-2'])
    second = attach_features(view, topo, feature_ids=['POC-1'])
    runtime = view._topomt_addon_runtime

    assert runtime.topography is topo
    assert view.topography is topo
    assert runtime.topography.dfnd.marker == 'complete-dfnd'
    assert runtime.active_feature_ids == ('POC-1',)
    assert second['selected_feature_ids'] == ['POC-1']
    assert second['rendered'].details['rendered'][0]['feature_id'] == 'POC-1'
    group = runtime.render_groups['features:topomt-pocket']
    assert group['feature_ids'] == ('POC-1',)
    assert group['tags'] == ('topomt-pocket:POC-1',)
    assert first['render_group_key'] == second['render_group_key']
    assert any(
        message.get('op') == 'clear_shapes_by_tag'
        and message.get('tag') == 'topomt-pocket:POC-2'
        for message in view.messages
    )


def test_attach_topography_clears_feature_filter_without_touching_other_groups():
    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket', feature_id='POC-1', center=[0.0, 0.0, 0.0]
    )
    topo.add_new_feature(
        feature_type='pocket', feature_id='POC-2', center=[1.0, 1.0, 1.0]
    )
    view = DummyView()
    register_with_molsysviewer()
    attach_features(view, topo, feature_ids=['POC-1'])
    runtime = view._topomt_addon_runtime
    runtime.render_groups['tetrahedra:dfnd-tetra'] = {'tags': ('dfnd-tetra',)}

    result = attach_topography(view, topo)

    assert runtime.active_feature_ids is None
    assert 'tetrahedra:dfnd-tetra' in runtime.render_groups
    assert runtime.render_groups['features:topomt-pocket']['feature_ids'] is None
    assert result['render_group_key'] == 'features:topomt-pocket'


def test_attach_pockets_is_a_pocket_named_wrapper():
    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1],
        center=[0.0, 0.0, 0.0],
    )
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-2',
        atom_indices=[2],
        center=[1.0, 1.0, 1.0],
    )

    view = DummyView()
    register_with_molsysviewer()
    result = attach_pockets(view, topo, pocket_ids=['POC-1'])

    assert result['rendered'].counts['n_rendered'] == 1
    assert result['selected_feature_ids'] == ['POC-1']
    assert result['rendered'].details['rendered'][0]['feature_id'] == 'POC-1'


def test_build_topography_standalone0_html_uses_viewer_host_and_registers_addon(
    monkeypatch, tmp_path
):
    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1],
        center=[0.0, 0.0, 0.0],
    )

    view = DummyView()
    captured = {}

    def fake_new_view(topography, **kwargs):
        captured['build_view'] = {
            'molecular_system': getattr(topography, '_molsys', 'system'),
            'topography': topography,
            'kwargs': kwargs,
        }
        view.load(getattr(topography, '_molsys', 'system'), **kwargs)
        return view

    def fake_build_standalone0_html(view_arg, output_filename, **kwargs):
        captured['build_html'] = {
            'view': view_arg,
            'output_filename': output_filename,
            'kwargs': kwargs,
        }
        return str(Path(output_filename).resolve())

    monkeypatch.setattr('molsysviewer_topomt.standalone.new_view', fake_new_view)
    monkeypatch.setattr(
        molsysviewer, 'build_standalone0_html', fake_build_standalone0_html
    )

    outfile = tmp_path / 'topomt-standalone.html'
    result = build_topography_standalone0_html('system', str(outfile), topography=topo)

    assert result == str(outfile.resolve())
    assert captured['build_view']['molecular_system'] == 'system'
    assert captured['build_view']['kwargs']['show'] is True
    assert captured['build_html']['view'] is view
    assert captured['build_html']['kwargs']['addon_modules'][0] == 'molsysviewer_topomt'


def test_build_topography_standalone0_html_can_render_only_selected_features(
    monkeypatch, tmp_path
):
    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1],
        center=[0.0, 0.0, 0.0],
    )
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-2',
        atom_indices=[2],
        center=[1.0, 1.0, 1.0],
    )

    view = DummyView()
    captured = {}

    def fake_new_view(topography, **kwargs):
        captured['build_view'] = kwargs
        return view

    def fake_attach_features(view_arg, topography, *, feature_ids, **kwargs):
        captured['attach_features'] = {
            'view': view_arg,
            'topography': topography,
            'feature_ids': list(feature_ids),
            'kwargs': kwargs,
        }
        return {'rendered': {'n_rendered': 1}}

    def fake_build_standalone0_html(view_arg, output_filename, **kwargs):
        captured['build_html'] = kwargs
        return str(Path(output_filename).resolve())

    monkeypatch.setattr('molsysviewer_topomt.standalone.new_view', fake_new_view)
    monkeypatch.setattr(
        'molsysviewer_topomt.standalone.attach_features', fake_attach_features
    )
    monkeypatch.setattr(
        molsysviewer, 'build_standalone0_html', fake_build_standalone0_html
    )

    outfile = tmp_path / 'topomt-selected.html'
    result = build_topography_standalone0_html(
        'system', str(outfile), topography=topo, feature_ids=['POC-2']
    )

    assert result == str(outfile.resolve())
    assert captured['build_view']['show'] is False
    assert captured['attach_features']['view'] is view
    assert captured['attach_features']['feature_ids'] == ['POC-2']


def test_build_topography_standalone0_selected_features_emit_real_render_operations(
    monkeypatch, tmp_path
):
    topo = tmt.Topography()
    topo._molsys = 'system'
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1],
        center=[0.0, 0.0, 0.0],
    )
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-2',
        atom_indices=[2],
        center=[1.0, 1.0, 1.0],
    )
    view = DummyView()

    monkeypatch.setattr(molsysviewer, 'new_view', lambda *args, **kwargs: view)
    monkeypatch.setattr(
        molsysviewer,
        'build_standalone0_html',
        lambda view_arg, output_filename, **kwargs: str(
            Path(output_filename).resolve()
        ),
    )

    build_topography_standalone0_html(
        'system',
        str(tmp_path / 'selected.html'),
        topography=topo,
        feature_ids=['POC-2'],
    )

    rendered = [
        message for message in view.messages if message.get('op') == 'add_sphere'
    ]
    assert len(rendered) == 1
    assert rendered[0]['options']['tag'] == 'topomt-pocket:POC-2'
    assert view._topomt_addon_runtime.active_feature_ids == ('POC-2',)


def test_launch_topography_standalone0_can_compute_topography_and_open_host(
    monkeypatch,
):
    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1],
        center=[0.0, 0.0, 0.0],
    )

    view = DummyView()
    captured = {}

    def fake_get_topography(molecular_system, **kwargs):
        captured['get_topography'] = {
            'molecular_system': molecular_system,
            'kwargs': kwargs,
        }
        return topo

    def fake_new_view(topography, **kwargs):
        captured['build_view'] = {
            'molecular_system': getattr(topography, '_molsys', None),
            'topography': topography,
            'kwargs': kwargs,
        }
        return view

    def fake_launch_standalone0(view_arg, output_filename=None, **kwargs):
        captured['launch'] = {
            'view': view_arg,
            'output_filename': output_filename,
            'kwargs': kwargs,
        }
        return '/tmp/topomt-launch.html'

    monkeypatch.setattr(tmt, 'get_topography', fake_get_topography)
    monkeypatch.setattr('molsysviewer_topomt.standalone.new_view', fake_new_view)
    monkeypatch.setattr(molsysviewer, 'launch_standalone0', fake_launch_standalone0)

    result = launch_topography_standalone0(
        'system', method='pocketeer', open_browser=False
    )

    assert result == '/tmp/topomt-launch.html'
    assert captured['get_topography']['molecular_system'] == 'system'
    assert captured['get_topography']['kwargs']['method'] == 'pocketeer'
    assert captured['launch']['view'] is view
    assert captured['launch']['kwargs']['addon_modules'][0] == 'molsysviewer_topomt'
    assert captured['launch']['kwargs']['open_browser'] is False


def test_show_dfnd_tetrahedra_creates_shapes():
    # Build simulated dfnd_records
    dfnd_records = {
        'tetrahedra': [
            {
                'tetrahedron_id': 0,
                'local_atom_indices': [10, 11, 12, 13],
                'combined_class': 'wet_sealed',
                'transit_role': 'resident_transit',
                'R_residence': 0.215,
                'residence_state': 'resident',
            },
            {
                'tetrahedron_id': 1,
                'local_atom_indices': [20, 21, 22, 23],
                'combined_class': 'dry_open',
                'transit_role': 'non_transit',
                'R_residence': 0.0,
                'residence_state': 'non_resident',
            },
        ]
    }

    view = DummyView()

    # Test default mode (combined_class)
    from molsysviewer_topomt.render import show_dfnd_tetrahedra

    layer = show_dfnd_tetrahedra(view, dfnd_records)

    assert layer is not None
    assert len(view.messages) == 2
    assert view.messages[0]['op'] == 'clear_shapes_by_tag'
    assert view.messages[0]['tag'] == 'dfnd-tetra'
    msg = view.messages[1]
    assert msg['op'] == 'add_tetrahedra'
    assert msg['options']['atom_quads'] == [[10, 11, 12, 13], [20, 21, 22, 23]]
    # wet_sealed is 0x14B8A6, dry_open is 0x64748B
    assert msg['options']['colors'] == [0x14B8A6, 0x64748B]
    assert msg['options']['alphas'] == [0.5, 0.1]
    assert 'combined_class=wet_sealed' in msg['options']['labels'][0]
    assert 'R_res=2.15 Å' in msg['options']['labels'][0]


def test_simplex_menu_selection_sets_native_selection_and_is_inspectable():
    from molsysviewer_topomt.addon import on_context_action, on_enable
    from molsysviewer_topomt.simplex_selection import ACTION_ID, simplex_selection_info
    from topomt.dfnd.graph import DelaunayFlowNetwork

    net = DelaunayFlowNetwork(
        'topomt/data/synthetic/tetrahedron_void.pdb', selection='all'
    )
    result = net.get_topography(probe_radius=1.4, min_size=0)

    view = DummyView()
    on_enable(view)
    view._topomt_addon_runtime.topography = result

    # Click on the "face" dynamic menu item -> should set the native atom selection
    # to the face's atoms (same highlight as clicking the face) and be inspectable.
    on_context_action(
        view,
        ACTION_ID,
        {
            'addon_action_payload': {
                'kind': 'face',
                'face_id': 1,
                'atom_indices': [0, 1, 2],
                'tetrahedron_ids': [0],
            }
        },
    )

    sel = [m for m in view.messages if m.get('op') == 'set_active_selection']
    assert sel and sel[-1]['atom_indices'] == [0, 1, 2]
    info = simplex_selection_info(view)
    assert info['kind'] == 'face'
    assert info['atom_indices'] == [0, 1, 2]


def test_show_dfnd_tetrahedra_edges_carry_edge_metadata():
    from molsysviewer_topomt.render import show_dfnd_tetrahedra
    from topomt.dfnd.graph import DelaunayFlowNetwork

    net = DelaunayFlowNetwork(
        'topomt/data/synthetic/tetrahedron_void.pdb', selection='all'
    )
    result = net.get_topography(probe_radius=1.4, min_size=0)

    view = DummyView()
    # edges-only mode forces the wireframe; edge_meta must accompany it.
    show_dfnd_tetrahedra(view, result, draw_faces=False)

    msg = view.messages[-1]
    assert msg['op'] == 'add_tetrahedra'
    assert msg['options']['draw_edges'] is True
    edge_meta = msg['options']['edge_meta']
    assert len(edge_meta) == 6  # single tetra -> 6 edges
    entry = edge_meta[0]
    assert 'edge_id' in entry and len(entry['atoms']) == 2


def test_resolve_simplices_maps_atom_selection_to_dfnd_simplices():
    from molsysviewer_topomt.simplex_selection import resolve_simplices
    from topomt.dfnd.graph import DelaunayFlowNetwork

    net = DelaunayFlowNetwork(
        'topomt/data/synthetic/tetrahedron_void.pdb', selection='all'
    )
    result = net.get_topography(probe_radius=1.4, min_size=0)

    # 2 atoms forming an edge -> a single edge item.
    edge_items = resolve_simplices(result, [0, 1])
    edge = next(i for i in edge_items if i['payload']['kind'] == 'edge')
    assert edge['payload']['atom_indices'] == [0, 1]
    assert 'arista id' in edge['title']
    assert edge['group'] == 'Selección actual'

    # 3 atoms forming a face -> a single face item.
    face_items = resolve_simplices(result, [0, 1, 2])
    assert any(i['payload']['kind'] == 'face' for i in face_items)

    # 4 atoms forming the tetrahedron -> a single tetrahedron item.
    tet_items = resolve_simplices(result, [0, 1, 2, 3])
    tet = next(i for i in tet_items if i['payload']['kind'] == 'tetrahedron')
    assert tet['payload']['tetrahedron_id'] == 0

    # Fewer than 2 atoms -> nothing.
    assert resolve_simplices(result, [0]) == []


def test_show_dfnd_tetrahedra_faces_are_pickable_with_metadata():
    # Two tetrahedra sharing one internal face plus face records: the emitted
    # add_tetrahedra message must request face-addressed picking (faces_pickable)
    # and carry per-face metadata so the frontend can label each face with its id,
    # permeability and both owning tetrahedra.
    dfnd_records = {
        'tetrahedra': [
            {
                'tetrahedron_id': 0,
                'local_atom_indices': [10, 11, 12, 13],
                'combined_class': 'wet_sealed',
                'transit_role': 'resident_transit',
                'R_residence': 2.15,
                'residence_state': 'resident',
            },
            {
                'tetrahedron_id': 1,
                'local_atom_indices': [11, 12, 13, 14],
                'combined_class': 'dry_open',
                'transit_role': 'non_transit',
                'R_residence': 0.0,
                'residence_state': 'non_resident',
            },
        ],
        'faces': [
            {
                'face_id': 7,
                'owner_tetrahedron_id': 0,
                'neighbor_tetrahedron_id': 1,
                'face_atoms_local': [11, 12, 13],
                'permeability_state': 'permeable',
            },
            {
                'face_id': 8,
                'owner_tetrahedron_id': 0,
                'neighbor_tetrahedron_id': -1,
                'face_atoms_local': [10, 11, 12],
                'permeability_state': 'non_permeable',
            },
        ],
    }

    view = DummyView()
    from molsysviewer_topomt.render import show_dfnd_tetrahedra

    show_dfnd_tetrahedra(view, dfnd_records)

    msg = view.messages[-1]
    assert msg['op'] == 'add_tetrahedra'
    assert msg['options']['faces_pickable'] is True
    meta = {entry['face_id']: entry for entry in msg['options']['face_meta']}
    assert meta[7]['atoms'] == [11, 12, 13]
    assert meta[7]['permeability'] == 'permeable'
    assert meta[7]['owner_id'] == 0
    assert meta[7]['neighbor_id'] == 1
    assert meta[7]['role'] == 'coast_face'
    assert meta[7]['side_relation'] == 'wet-dry'
    # exterior face -> neighbor reported as OCEAN
    assert meta[8]['neighbor_id'] == 'OCEAN'


def test_attach_dfnd_tetrahedra_integration():
    dfnd_records = {
        'tetrahedra': [
            {
                'tetrahedron_id': 0,
                'local_atom_indices': [10, 11, 12, 13],
                'combined_class': 'wet_sealed',
                'transit_role': 'resident_transit',
                'R_residence': 2.15,
                'residence_state': 'resident',
            }
        ]
    }

    view = DummyView()
    register_with_molsysviewer()

    from molsysviewer_topomt.integration import attach_dfnd_tetrahedra

    result = attach_dfnd_tetrahedra(view, dfnd_records, color_mode='transit_role')

    assert result['addon_enabled'] is True
    assert result['layer'] is not None
    assert result['tag'] == 'dfnd-tetra'
    assert view._topomt_addon_runtime.enabled is True

    assert len(view.messages) == 2
    assert view.messages[0]['op'] == 'clear_shapes_by_tag'
    assert view.messages[0]['tag'] == 'dfnd-tetra'
    msg = view.messages[1]
    # resident_transit is 0x6366F1
    assert msg['options']['colors'] == [0x6366F1]


def test_show_dfnd_tetrahedra_with_custom_indices():
    # Build simulated dfnd_records with three tetrahedra
    dfnd_records = {
        'tetrahedra': [
            {
                'tetrahedron_id': 0,
                'local_atom_indices': [10, 11, 12, 13],
                'combined_class': 'wet_sealed',
                'transit_role': 'resident_transit',
                'R_residence': 2.15,
                'residence_state': 'resident',
            },
            {
                'tetrahedron_id': 1,
                'local_atom_indices': [20, 21, 22, 23],
                'combined_class': 'dry_open',
                'transit_role': 'non_transit',
                'R_residence': 0.0,
                'residence_state': 'non_resident',
            },
            {
                'tetrahedron_id': 2,
                'local_atom_indices': [30, 31, 32, 33],
                'combined_class': 'dry_coast',
                'transit_role': 'transit_connector',
                'R_residence': 1.5,
                'residence_state': 'non_resident',
            },
        ]
    }

    view = DummyView()

    # Test filtering to keep only tetrahedron 0 and 2
    from molsysviewer_topomt.render import show_dfnd_tetrahedra

    layer = show_dfnd_tetrahedra(view, dfnd_records, tetrahedra_indices=[0, 2])

    assert layer is not None
    assert len(view.messages) == 2
    msg = view.messages[1]
    assert msg['op'] == 'add_tetrahedra'
    # Should only contain 2 tetrahedra, not 3
    assert len(msg['options']['atom_quads']) == 2
    assert msg['options']['atom_quads'] == [[10, 11, 12, 13], [30, 31, 32, 33]]


def test_attach_dfnd_tetrahedra_relies_on_native_selection_without_click_callback():
    dfnd_records = {
        'tetrahedra': [
            {
                'tetrahedron_id': 0,
                'local_atom_indices': [10, 11, 12, 13],
                'combined_class': 'wet_sealed',
                'transit_role': 'resident_transit',
                'R_residence': 2.15,
                'residence_state': 'resident',
            }
        ]
    }

    class ClickableDummyView(DummyView):
        def __init__(self):
            super().__init__()
            self.click_callbacks = []

        def on_click(self, callback):
            self.click_callbacks.append(callback)

    view = ClickableDummyView()
    from molsysviewer_topomt.integration import attach_dfnd_tetrahedra

    result = attach_dfnd_tetrahedra(view, dfnd_records, tetrahedra_indices=[0])

    assert result['layer'] is not None
    assert view.click_callbacks == []


def test_attach_topography_with_tetrahedra():
    # A complete topography with pockets and tetrahedra
    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1, 2, 3],
        center=[0.1, 0.2, 0.3],
        volume=0.5,
        source='manual',
        source_id='manual:1',
    )
    topo.dfnd = types.SimpleNamespace(
        raw={
            'tetrahedra': [
                {
                    'tetrahedron_id': 0,
                    'local_atom_indices': [10, 11, 12, 13],
                    'combined_class': 'wet_sealed',
                    'transit_role': 'resident_transit',
                    'R_residence': 2.15,
                    'residence_state': 'resident',
                }
            ]
        }
    )

    view = DummyView()
    register_with_molsysviewer()

    # Renders pockets but NOT tetrahedra by default
    res = attach_topography(view, topo)
    assert res['rendered'] is not None
    assert res['rendered_tetrahedra'] is None

    # Renders BOTH pockets and tetrahedra when show_tetrahedra=True
    view = DummyView()
    res = attach_topography(view, topo, show_tetrahedra=True)
    assert res['rendered'] is not None
    assert res['rendered_tetrahedra'] is not None
    assert len(view.messages) == 3
    # First is pocket sphere
    assert view.messages[0]['op'] == 'add_sphere'
    # Second is clear tetrahedra tag
    assert view.messages[1]['op'] == 'clear_shapes_by_tag'
    assert view.messages[1]['tag'] == 'dfnd-tetra'
    # Third is tetrahedra
    assert view.messages[2]['op'] == 'add_tetrahedra'


def test_topography_panel_actions_with_tetrahedra():
    from molsysviewer_topomt.panels.topography import TopoMTTopographyPanel

    topo = tmt.Topography()
    topo.add_new_feature(
        feature_type='pocket',
        feature_id='POC-1',
        atom_indices=[1, 2, 3],
        center=[0.1, 0.2, 0.3],
        volume=0.5,
        source='manual',
        source_id='manual:1',
    )
    topo.dfnd = types.SimpleNamespace(
        raw={
            'tetrahedra': [
                {
                    'tetrahedron_id': 0,
                    'local_atom_indices': [10, 11, 12, 13],
                    'combined_class': 'wet_sealed',
                    'transit_role': 'resident_transit',
                    'R_residence': 2.15,
                    'residence_state': 'resident',
                }
            ]
        }
    )

    view = DummyView()
    register_with_molsysviewer()

    # Enable addon lifecycle to initialize runtime
    view.addons.enable('topomt')
    lifecycle.on_enable(view)

    panel = TopoMTTopographyPanel()
    panel.on_mount(view)

    # Attach topography first
    view._topomt_addon_runtime.topography = topo

    # 1. Action: render_pockets
    panel.handle_action(view, 'render_pockets', {})
    assert len(view.messages) == 1
    assert view.messages[0]['op'] == 'add_sphere'
    assert view._topomt_addon_runtime.active_feature_ids is None
    assert 'features:topomt-pocket' in view._topomt_addon_runtime.render_groups

    # 2. Action: render_tetrahedra
    panel.handle_action(view, 'render_tetrahedra', {})
    assert len(view.messages) == 3
    assert view.messages[1]['op'] == 'clear_shapes_by_tag'
    assert view.messages[2]['op'] == 'add_tetrahedra'
    assert 'tetrahedra:dfnd-tetra' in view._topomt_addon_runtime.render_groups

    # 3. Action: clear_pockets (clears both pockets and tetrahedra)
    panel.handle_action(view, 'clear_pockets', {})
    clear_ops = [msg for msg in view.messages if msg.get('op') == 'clear_shapes_by_tag']
    # There should be clear operations for pocket tag and dfnd-tetra tag
    assert len(clear_ops) == 3
    tags_cleared = {msg['tag'] for msg in clear_ops}
    assert 'topomt-pocket:POC-1' in tags_cleared
    assert 'dfnd-tetra' in tags_cleared
    assert view._topomt_addon_runtime.active_feature_ids == ()
    assert view._topomt_addon_runtime.render_groups == {}


def test_new_view_resolves_molsys(monkeypatch):
    class MockTopography:
        def __init__(self, molsys):
            self._molsys = molsys
            self.features = {}

        def __iter__(self):
            return iter(self.features)

    view = DummyView()

    def fake_molsysviewer_new_view(molecular_system, **kwargs):
        view.load(molecular_system, **kwargs)
        return view

    monkeypatch.setattr(molsysviewer, 'new_view', fake_molsysviewer_new_view)
    monkeypatch.setattr(
        'molsysviewer_topomt.integration.attach_topography',
        lambda *args, **kwargs: {'rendered': None},
    )

    topo = MockTopography('real-molsys')

    res_view = new_view(topo)
    assert res_view is view
    assert view.load_calls[-1]['molecular_system'] == 'real-molsys'

    # Topography with no _molsys raises ValueError
    class BadTopography:
        pass

    with pytest.raises(
        ValueError, match='topography does not expose a molecular_system'
    ):
        new_view(BadTopography())


def test_show_dfnd_components_creates_shapes():
    class MockMesh:
        def __init__(self):
            self.atoms = types.SimpleNamespace(
                coords=np.array(
                    [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0], [3.0, 3.0, 3.0]]
                )
            )
            self.tetrahedra = [
                {
                    'tetrahedron_id': 0,
                    'local_atom_indices': [0, 1, 2, 3],
                    'center': [0.5, 0.5, 0.5],
                    'R_residence': 1.5,
                }
            ]
            self.faces = []

            class FakeDelaunay:
                def __init__(self):
                    self.alpha_sphere_centers = np.array([[0.0, 0.0, 0.0]])
                    self.alpha_sphere_radii = np.array([1.5])

            self.delaunay = FakeDelaunay()

    class MockComponent:
        def __init__(
            self,
            component_id,
            family,
            side,
            node_indices,
            resident_node_indices,
            atom_indices,
        ):
            self.component_id = component_id
            self.family = family
            self.side = side
            self.node_indices = node_indices
            self.resident_node_indices = resident_node_indices
            self.atom_indices = atom_indices
            self.volume = 10.0

    class MockDFN:
        def __init__(self):
            self.components = types.SimpleNamespace(
                wet=[MockComponent('WET-1', 'pocket', 'wet', [0], [0], [0, 1, 2, 3])],
                dry=[],
            )
            self.faces = []

    class MockTopography:
        def __init__(self):
            mesh = MockMesh()
            self.dfnd = types.SimpleNamespace(
                mesh=mesh,
                dfn=MockDFN(),
                raw={'faces': [], 'tetrahedra': mesh.tetrahedra},
            )

            self.features = {}

        def __getitem__(self, item):
            return self.features[item]

        def __iter__(self):
            return iter(self.features)

        def __len__(self):
            return len(self.features)

    topo = MockTopography()
    from molsysviewer_topomt.render import show_dfnd_components

    # Test tetrahedra mode
    view = DummyView()
    layer = show_dfnd_components(view, topo, representation='tetrahedra')
    assert layer is not None
    assert any(msg['op'] == 'add_tetrahedra' for msg in view.messages)

    # Test spheres mode
    view = DummyView()
    layer = show_dfnd_components(view, topo, representation='spheres')
    assert layer is not None
    assert any(msg['op'] == 'add_alpha_sphere_set' for msg in view.messages)

    # Test cloud mode
    view = DummyView()
    layer = show_dfnd_components(view, topo, representation='cloud')
    assert layer is not None
    blob_messages = [msg for msg in view.messages if msg['op'] == 'add_pocket_blob']
    assert blob_messages
    assert blob_messages[0]['options']['layer_tag'] == 'dfnd-comp'
    assert 'color_map' not in blob_messages[0]['options']
    assert blob_messages[0]['options']['iso_level'] == 0.5
    assert blob_messages[0]['options']['smoothing'] == 0.5
    assert blob_messages[0]['options']['resolution'] == 0.5
    assert blob_messages[0]['options']['radius_scale'] == 0.6

    # Test surface mode
    view = DummyView()
    layer = show_dfnd_components(view, topo, representation='surface')
    assert layer is not None
    assert any(msg['op'] == 'add_pocket_surface' for msg in view.messages)


def test_dfnd_component_palette_is_okabe_ito_colour_blind_safe():
    """Phase 0: the family palette is the fixed Okabe-Ito assignment.

    See devguide/DFND/component_visualization.md §11 and
    component_visualization_implementation.md (Phase 0).
    """
    from topomt.dfnd import families as fam
    from molsysviewer_topomt.render import _components as comp

    # Fixed family -> Okabe-Ito hexes (no arbitrary choices).
    assert comp._TYPE_PALETTE[fam.POCKET] == 0x0072B2  # blue
    assert comp._TYPE_PALETTE[fam.VOID] == 0x56B4E9  # sky blue
    assert comp._TYPE_PALETTE[fam.CHANNEL] == 0xE69F00  # orange
    assert comp._TYPE_PALETTE[fam.PERCOLATING] == 0xCC79A7  # reddish purple
    assert comp._TYPE_PALETTE[fam.DRY_BANK] == 0x999999  # grey

    # pocket (blue) and void (sky blue) are deliberately two blues: a pocket is a
    # void with one opening, separated by luminance + the mouth primitive.
    assert comp._TYPE_PALETTE[fam.POCKET] != comp._TYPE_PALETTE[fam.VOID]

    # Mouth/gate accent is the reserved yellow, used by no family.
    assert comp._MOUTH_ACCENT == 0xF0E442
    assert comp._MOUTH_ACCENT not in comp._TYPE_PALETTE.values()

    # Interface bodies: bipartite pair is vermillion + bluish green.
    assert comp._INTERFACE_BODY_COLORS[0] == 0xD55E00
    assert comp._INTERFACE_BODY_COLORS[1] == 0x009E73

    # Every palette colour comes from the Okabe-Ito catalog.
    okabe = set(comp._OKABE_ITO.values())
    assert set(comp._TYPE_PALETTE.values()) <= okabe
    assert comp._MOUTH_ACCENT in okabe
    assert set(comp._INTERFACE_BODY_COLORS) <= okabe
    assert set(comp._DISTINCT_PALETTE_LIST) <= okabe


def test_show_dfnd_components_replaces_component_tag_between_representations():
    class MockMesh:
        def __init__(self):
            self.atoms = types.SimpleNamespace(
                coords=np.array(
                    [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0], [3.0, 3.0, 3.0]]
                )
            )
            self.tetrahedra = [
                {
                    'tetrahedron_id': 0,
                    'local_atom_indices': [0, 1, 2, 3],
                    'center': [0.5, 0.5, 0.5],
                    'R_residence': 1.5,
                }
            ]
            self.faces = []

            class FakeDelaunay:
                alpha_sphere_centers = np.array([[0.5, 0.5, 0.5]])
                alpha_sphere_radii = np.array([1.5])

            self.delaunay = FakeDelaunay()

    component = types.SimpleNamespace(
        component_id='WET-2',
        family='pocket',
        side='wet',
        node_indices=[0],
        resident_node_indices=[0],
        atom_indices=[0, 1, 2, 3],
        volume=10.0,
    )
    mesh = MockMesh()
    topo = types.SimpleNamespace(
        dfnd=types.SimpleNamespace(
            mesh=mesh,
            dfn=types.SimpleNamespace(
                components=types.SimpleNamespace(wet=[component], dry=[])
            ),
            raw={'faces': [], 'tetrahedra': mesh.tetrahedra},
        )
    )

    from molsysviewer_topomt.render import show_dfnd_components

    view = DummyView()
    cloud_layer = show_dfnd_components(
        view, topo, representation='cloud', component_ids=['WET-2']
    )
    assert cloud_layer is not None

    spheres_layer = show_dfnd_components(
        view, topo, representation='spheres', component_ids=['WET-2']
    )
    assert spheres_layer is not None
    assert 'dfnd-comp:WET-2' in spheres_layer.tags


def test_dfnd_face_meta_includes_faces_touching_selected_tetrahedra():
    from molsysviewer_topomt.render._common import _dfnd_face_meta

    raw = {
        'faces': [
            {
                'face_id': 7,
                'owner_tetrahedron_id': 0,
                'neighbor_tetrahedron_id': 1,
                'face_atoms_local': [10, 11, 12],
                'permeability_state': 'permeable',
            },
            {
                'face_id': 8,
                'owner_tetrahedron_id': 2,
                'neighbor_tetrahedron_id': 1,
                'face_atoms_local': [11, 12, 13],
                'permeability_state': 'non_permeable',
            },
        ]
    }

    face_meta = _dfnd_face_meta(
        raw,
        {1},
        colors_by_tetrahedron={1: 0x123456},
        face_color_mode='component',
    )

    assert [entry['face_id'] for entry in face_meta] == [7, 8]
    assert face_meta[0]['color'] == 0x123456
    assert face_meta[1]['permeability'] == 'non_permeable'


def test_show_dfnd_components_explicit_sphere_modes_and_graph_alias():
    class MockMesh:
        atoms = types.SimpleNamespace(
            coords=np.array(
                [
                    [0.0, 0.0, 0.0],
                    [1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [0.0, 0.0, 1.0],
                ]
            )
        )
        tetrahedra = [
            {
                'tetrahedron_id': 0,
                'local_atom_indices': [0, 1, 2, 3],
                'center': [0.25, 0.25, 0.25],
                'R_residence': 2.5,
            },
            {
                'tetrahedron_id': 1,
                'local_atom_indices': [0, 1, 2, 3],
                'center': [0.75, 0.75, 0.75],
                'R_residence': 1.0,
            },
        ]
        faces = []
        delaunay = types.SimpleNamespace(
            alpha_sphere_centers=np.array([[0.5, 0.5, 0.5]]),
            alpha_sphere_radii=np.array([7.5]),
        )

    component = types.SimpleNamespace(
        component_id='WET-1',
        family='pocket',
        side='wet',
        node_indices=[0, 1],
        resident_node_indices=[0],
        atom_indices=[0, 1, 2, 3],
        volume=10.0,
    )
    topo = types.SimpleNamespace(
        dfnd=types.SimpleNamespace(
            mesh=MockMesh(),
            dfn=types.SimpleNamespace(
                components=types.SimpleNamespace(wet=[component], dry=[]),
                graph=types.SimpleNamespace(faces=[]),
                parameters={'probe_radius': 1.4},
            ),
            raw={'faces': [], 'tetrahedra': MockMesh.tetrahedra},
        )
    )
    from molsysviewer_topomt.render import show_dfnd_components

    # MockMesh values are nm (kernel units); emitted on the Mol* canvas (angstroms, x10).
    residence_view = DummyView()
    show_dfnd_components(residence_view, topo, representation='residence_spheres')
    assert residence_view.messages[-1]['options']['alpha_spheres'][
        'radii'
    ] == pytest.approx([25.0])

    alpha_view = DummyView()
    show_dfnd_components(alpha_view, topo, representation='alpha_spheres')
    assert alpha_view.messages[-1]['options']['alpha_spheres'][
        'radii'
    ] == pytest.approx([75.0])

    probe_view = DummyView()
    show_dfnd_components(
        probe_view,
        topo,
        representation='probe_centers',
        use_resident_nodes=False,
    )
    assert probe_view.messages[-1]['op'] == 'add_sphere'
    assert probe_view.messages[-1]['options']['radius'] == pytest.approx(14.0)
    assert probe_view.messages[-1]['options']['center'] == pytest.approx(
        [2.5, 2.5, 2.5]  # [0.25]*3 nm on the Mol* canvas (angstroms)
    )

    graph = show_dfnd_components(DummyView(), topo, representation='graph')
    skeleton = show_dfnd_components(DummyView(), topo, representation='skeleton')
    assert graph.counts['n_nodes'] == skeleton.counts['n_nodes'] == 1


def test_pipe_renders_channel_as_variable_radius_tube():
    """Phase 2: a channel renders as add_channel_tube + a bottleneck marker.

    Uses a real DFND substrate from the committed two-mouth-channel fixture (no
    synthetic.py dependency). See topomt/dfnd/centerline.py and
    devguide/DFND/component_visualization_implementation.md (Phase 2).
    """
    from pathlib import Path
    from types import SimpleNamespace

    from topomt.dfnd.graph import DelaunayFlowNetwork
    from topomt.dfnd.data import DFNDData
    from molsysviewer_topomt.render import show_dfnd_components

    pdb = (
        Path(__file__).resolve().parents[1]
        / 'topomt'
        / 'data'
        / 'synthetic'
        / 'tube_channel_clean.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_coordinates_and_radii(
        coords, np.full(len(coords), 1.88), epsilon=1e-7
    )
    result = net.get_topography(probe_radius=1.4, min_size=0)
    topo = SimpleNamespace(dfnd=DFNDData(net, result))

    view = DummyView()
    layer = show_dfnd_components(
        view, topo, representation='pipe', component_types=('channel',)
    )
    assert layer is not None
    ops = [m['op'] for m in view.messages]
    assert 'add_channel_tube' in ops  # the tube
    assert 'add_rings' in ops  # the bottleneck ring
    ring_msg = next(m for m in view.messages if m['op'] == 'add_rings')
    assert len(ring_msg['options']['centers']) == 1
    assert len(ring_msg['options']['normals']) == 1


def test_pipe_renders_secondary_branches_for_three_mouth_channel():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('branched_tube_y.pdb')
    component = next(
        comp for comp in topo.dfnd.dfn.components.wet if comp.family == 'channel'
    )
    assert component.n_mouths >= 3

    view = DummyView()
    show_dfnd_components(
        view,
        topo,
        representation='pipe',
        component_ids=[component.component_id],
    )

    branch_msgs = [
        message
        for message in view.messages
        if message['op'] == 'add_channel_tube'
        and '-branch-' in message['options']['tag']
    ]
    assert len(branch_msgs) == component.n_mouths - 2
    assert all(message['options']['alpha'] < 0.5 for message in branch_msgs)


def test_channel_representation_aliases_emit_expected_shapes():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('branched_tube_y.pdb')
    component = next(
        comp for comp in topo.dfnd.dfn.components.wet if comp.family == 'channel'
    )

    tube_view = DummyView()
    show_dfnd_components(
        tube_view,
        topo,
        representation='channel_tube',
        component_ids=[component.component_id],
    )
    primary_tube = next(
        message
        for message in tube_view.messages
        if message['op'] == 'add_channel_tube'
        and message['options']['tag'] == f'dfnd-comp:{component.component_id}'
    )
    assert primary_tube['options']['tube_style'] == 'smooth'
    assert len(set(primary_tube['options']['colors'])) == 1
    assert primary_tube['options']['alpha'] >= 0.85

    profile_view = DummyView()
    show_dfnd_components(
        profile_view,
        topo,
        representation='channel_profile',
        component_ids=[component.component_id],
    )
    profile_tube = next(
        message
        for message in profile_view.messages
        if message['op'] == 'add_channel_tube'
        and message['options']['tag'] == f'dfnd-comp:{component.component_id}'
    )
    assert profile_tube['options']['tube_style'] == 'segments'
    assert len(set(profile_tube['options']['colors'])) >= 1

    blob_view = DummyView()
    show_dfnd_components(
        blob_view,
        topo,
        representation='channel_blob',
        component_ids=[component.component_id],
    )
    assert any(message['op'] == 'add_pocket_blob' for message in blob_view.messages)
    assert not any(message['op'] == 'add_channel_tube' for message in blob_view.messages)

    wire_view = DummyView()
    show_dfnd_components(
        wire_view,
        topo,
        representation='channel_wire_blob',
        component_ids=[component.component_id],
    )
    wire_blob = next(
        message for message in wire_view.messages if message['op'] == 'add_pocket_blob'
    )
    assert wire_blob['options']['wireframe'] is True

    lumen_view = DummyView()
    show_dfnd_components(
        lumen_view,
        topo,
        representation='channel_lumen',
        component_ids=[component.component_id],
    )
    lumen_tube = next(
        message
        for message in lumen_view.messages
        if message['op'] == 'add_channel_tube'
        and message['options']['tag'] == f'dfnd-comp:{component.component_id}'
    )
    assert lumen_tube['options']['tube_style'] == 'surface'
    assert lumen_tube['options']['surface_resolution'] == pytest.approx(0.5)
    assert lumen_tube['options']['surface_iso_level'] == pytest.approx(0.5)

    ribbon_view = DummyView()
    show_dfnd_components(
        ribbon_view,
        topo,
        representation='channel_ribbon',
        component_ids=[component.component_id],
    )
    ribbon_tube = next(
        message
        for message in ribbon_view.messages
        if message['op'] == 'add_channel_tube'
        and message['options']['tag'] == f'dfnd-comp:{component.component_id}'
    )
    assert ribbon_tube['options']['tube_style'] == 'smooth'
    assert ribbon_tube['options']['tube_aspect_ratio'] == pytest.approx(0.22)


def test_scalar_isosurface_uses_generic_molsysviewer_primitive():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    component = next(comp for comp in topo.dfnd.dfn.components.wet)
    view = DummyView()

    show_dfnd_components(
        view,
        topo,
        representation='scalar_isosurface',
        component_ids=[component.component_id],
    )

    iso = next(
        message for message in view.messages if message['op'] == 'add_scalar_isosurface'
    )
    assert iso['options']['centers']
    assert iso['options']['radii']
    assert iso['options']['values']
    assert iso['options']['color_map'] == 'turbo'


def test_interface_surface_aliases_are_explicit():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('two_blocks_interface.pdb')
    component = next(comp for comp in topo.dfnd.dfn.components.wet if comp.is_interface)

    surface_view = DummyView()
    show_dfnd_components(
        surface_view,
        topo,
        representation='interface_lining_surface',
        component_ids=[component.component_id],
    )
    assert any(
        message['op'] == 'add_pocket_surface' for message in surface_view.messages
    )

    faces_view = DummyView()
    show_dfnd_components(
        faces_view,
        topo,
        representation='interface_contact_faces',
        component_ids=[component.component_id],
    )
    face_msg = next(
        message for message in faces_view.messages if message['op'] == 'add_triangle_faces'
    )
    assert face_msg['options']['labels']
    assert all('role=coast_face' in label for label in face_msg['options']['labels'])


def test_interface_links_connect_wet_and_dry_sides():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    component = next(comp for comp in topo.dfnd.dfn.components.wet if comp.n_mouths > 0)
    view = DummyView()

    show_dfnd_components(
        view,
        topo,
        representation='interface_links',
        component_ids=[component.component_id],
    )

    link_msg = next(
        message
        for message in view.messages
        if message['op'] in {'add_network_links', 'add_links'}
    )
    assert link_msg['options']['coordinate_pairs']
    assert link_msg['options']['colors'] == [0xE69F00] * len(
        link_msg['options']['coordinate_pairs']
    )


def test_interface_ribbon_summarizes_coast_face_centroids():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    component = next(comp for comp in topo.dfnd.dfn.components.wet if comp.n_mouths > 0)
    view = DummyView()

    show_dfnd_components(
        view,
        topo,
        representation='interface_ribbon',
        component_ids=[component.component_id],
    )

    ribbon_msg = next(
        message for message in view.messages if message['op'] == 'add_channel_tube'
    )
    assert ribbon_msg['options']['tube_style'] == 'smooth'
    assert ribbon_msg['options']['tube_aspect_ratio'] == pytest.approx(0.18)
    assert len(ribbon_msg['options']['centers']) >= 2
    assert len(ribbon_msg['options']['radii']) == len(ribbon_msg['options']['centers'])


def test_dfnd_cutaway_helpers_add_scene_sections():
    from molsysviewer_topomt.render import (
        show_dfnd_interface_cutaway,
        show_dfnd_pocket_cutaway,
    )

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    component = next(comp for comp in topo.dfnd.dfn.components.wet if comp.n_mouths > 0)

    pocket_view = DummyView()
    pocket_section = show_dfnd_pocket_cutaway(
        pocket_view,
        topo,
        component_ids=[component.component_id],
        tag_prefix='cut',
    )

    assert pocket_section.tag == f'cut:{component.component_id}'
    pocket_msg = next(
        message for message in pocket_view.messages if message['op'] == 'set_sections'
    )
    assert len(pocket_msg['sections']) == 1
    assert pocket_msg['sections'][0]['tag'] == pocket_section.tag
    assert len(pocket_msg['sections'][0]['point']) == 3
    assert np.linalg.norm(pocket_msg['sections'][0]['normal']) == pytest.approx(1.0)

    interface_topo = _build_dfnd_topo('two_blocks_interface.pdb')
    interface_component = next(
        comp for comp in interface_topo.dfnd.dfn.components.wet if comp.is_interface
    )
    interface_view = DummyView()
    interface_section = show_dfnd_interface_cutaway(
        interface_view,
        interface_topo,
        component_ids=[interface_component.component_id],
    )

    assert interface_section is not None
    assert interface_section.tag == f'dfnd-interface-cutaway:{interface_component.component_id}'
    interface_msg = next(
        message for message in interface_view.messages if message['op'] == 'set_sections'
    )
    assert np.linalg.norm(interface_msg['sections'][0]['normal']) == pytest.approx(1.0)


def test_pocket_depth_map_uses_topological_depth_values():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    component = next(comp for comp in topo.dfnd.dfn.components.wet if comp.n_mouths > 0)
    view = DummyView()

    show_dfnd_components(
        view,
        topo,
        representation='pocket_depth_map',
        component_ids=[component.component_id],
    )

    blob = next(
        message
        for message in view.messages
        if message['op'] in {'add_pocket_blob', 'add_scalar_isosurface'}
    )
    assert blob['options']['values']
    assert len(blob['options']['values']) == len(blob['options']['centers'])
    assert blob['options']['color_map'] == 'turbo'


def test_mouth_stubs_render_external_links_as_segments():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    component = next(comp for comp in topo.dfnd.dfn.components.wet if comp.n_mouths > 0)
    view = DummyView()
    layer = show_dfnd_components(
        view,
        topo,
        representation='mouth_stubs',
        component_ids=[component.component_id],
    )

    assert layer is not None
    link_msg = next(
        message
        for message in view.messages
        if message['op'] in {'add_network_links', 'add_links'}
    )
    assert link_msg['options']['coordinate_pairs']
    assert link_msg['options']['colors']
    assert set(link_msg['options']['colors']) == {0xF0E442}
    assert link_msg['options']['tag'] == 'dfnd-comp'
    assert link_msg['options']['layer_tag'] == 'dfnd-comp'


def test_mouth_and_bottleneck_rings_are_explicit():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    component = next(
        comp
        for comp in topo.dfnd.dfn.components.wet
        if comp.family == 'channel' and comp.n_mouths > 0
    )

    mouth_view = DummyView()
    show_dfnd_components(
        mouth_view,
        topo,
        representation='mouth_rings',
        component_ids=[component.component_id],
    )
    mouth_msg = next(message for message in mouth_view.messages if message['op'] == 'add_rings')
    assert mouth_msg['options']['centers']
    assert mouth_msg['options']['colors']
    assert set(mouth_msg['options']['colors']) == {0xF0E442}
    assert mouth_msg['options']['tag'] == f'dfnd-comp:{component.component_id}'

    neck_view = DummyView()
    show_dfnd_components(
        neck_view,
        topo,
        representation='bottleneck_rings',
        component_ids=[component.component_id],
    )
    neck_msg = next(message for message in neck_view.messages if message['op'] == 'add_rings')
    assert len(neck_msg['options']['centers']) == 1
    assert neck_msg['options']['colors'] == [0xF0E442]
    assert neck_msg['options']['tag'] == f'dfnd-comp:{component.component_id}'


def test_shape_ellipsoids_summarize_component_orientation():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    view = DummyView()
    layer = show_dfnd_components(
        view,
        topo,
        representation='shape_ellipsoids',
        show_wet=True,
        show_dry=True,
        component_types=None,
    )

    assert layer is not None
    ellipsoid = next(
        message
        for message in view.messages
        if message['op'] == 'add_anisotropy_ellipsoids'
    )
    options = ellipsoid['options']
    assert options['centers']
    assert len(options['centers']) == len(options['eigenvalues'])
    assert len(options['centers']) == len(options['eigenvectors'])
    assert len(options['centers']) == len(options['values'])
    assert options['color_by'] == 'anisotropy'
    assert options['tag'] == 'dfnd-comp'


def test_dry_face_representations_are_explicit():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    dry_component = topo.dfnd.dfn.components.dry[0]

    interface_view = DummyView()
    show_dfnd_components(
        interface_view,
        topo,
        representation='dry_interface_faces',
        component_ids=[dry_component.component_id],
    )
    interface_msg = next(
        message
        for message in interface_view.messages
        if message['op'] == 'add_triangle_faces'
    )
    assert interface_msg['options']['labels']
    assert all(
        label.startswith('Dry interface face')
        for label in interface_msg['options']['labels']
    )

    blocked_view = DummyView()
    show_dfnd_components(
        blocked_view,
        topo,
        representation='dry_blocked_faces',
        component_ids=[dry_component.component_id],
    )
    blocked_msg = next(
        message for message in blocked_view.messages if message['op'] == 'add_triangle_faces'
    )
    assert blocked_msg['options']['labels']
    assert all('permeability=non_permeable' in label for label in blocked_msg['options']['labels'])

    depth_view = DummyView()
    show_dfnd_components(
        depth_view,
        topo,
        representation='dry_depth_map',
        component_ids=[dry_component.component_id],
    )
    depth_msg = next(
        message for message in depth_view.messages if message['op'] == 'add_triangle_faces'
    )
    assert depth_msg['options']['labels']
    assert all('face_depth=' in label for label in depth_msg['options']['labels'])
    assert len(set(depth_msg['options']['colors'])) >= 1


def test_dry_shell_collects_boundary_faces_without_semantic_coloring():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    dry_component = topo.dfnd.dfn.components.dry[0]
    view = DummyView()

    show_dfnd_components(
        view,
        topo,
        representation='dry_shell',
        component_ids=[dry_component.component_id],
        alpha=0.35,
    )

    shell_msg = next(
        message for message in view.messages if message['op'] == 'add_triangle_faces'
    )
    assert shell_msg['options']['colors']
    assert set(shell_msg['options']['colors']) == {0x999999}
    assert any(
        label.startswith('Dry shell face')
        for label in shell_msg['options']['labels']
    )
    assert shell_msg['options']['alpha'] == pytest.approx(0.35)


def test_dry_cage_draws_edge_only_tetrahedral_scaffold():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    dry_component = topo.dfnd.dfn.components.dry[0]
    view = DummyView()

    show_dfnd_components(
        view,
        topo,
        representation='dry_cage',
        component_ids=[dry_component.component_id],
    )

    cage_msg = next(message for message in view.messages if message['op'] == 'add_tetrahedra')
    assert cage_msg['options']['draw_faces'] is False
    assert cage_msg['options']['draw_edges'] is True
    assert cage_msg['options']['edge_color'] == 0x999999


def test_groove_diagnostics_reuse_component_geometry_primitives():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('branched_tube_y.pdb')
    component = next(comp for comp in topo.dfnd.dfn.components.wet if comp.family == 'channel')

    floor_view = DummyView()
    show_dfnd_components(
        floor_view,
        topo,
        representation='groove_floor',
        component_ids=[component.component_id],
    )
    floor_msg = next(
        message for message in floor_view.messages if message['op'] == 'add_triangle_faces'
    )
    assert floor_msg['options']['labels']
    assert set(floor_msg['options']['colors']) == {0x56B4E9}

    walls_view = DummyView()
    show_dfnd_components(
        walls_view,
        topo,
        representation='groove_walls',
        component_ids=[component.component_id],
    )
    assert any(message['op'] == 'add_pocket_surface' for message in walls_view.messages)

    width_view = DummyView()
    show_dfnd_components(
        width_view,
        topo,
        representation='groove_width_profile',
        component_ids=[component.component_id],
    )
    width_msg = next(message for message in width_view.messages if message['op'] == 'add_rings')
    assert width_msg['options']['centers']
    assert width_msg['options']['colors']

    depth_view = DummyView()
    show_dfnd_components(
        depth_view,
        topo,
        representation='groove_depth_profile',
        component_ids=[component.component_id],
    )
    depth_msg = next(
        message for message in depth_view.messages if message['op'] == 'add_pocket_blob'
    )
    assert depth_msg['options']['values']
    assert depth_msg['options']['color_map'] == 'turbo'


def test_clearance_map_colours_envelope_by_residence_radius():
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    component = next(
        comp for comp in topo.dfnd.dfn.components.wet if comp.family in ('pocket', 'channel')
    )

    view = DummyView()
    show_dfnd_components(
        view,
        topo,
        representation='clearance_map',
        component_ids=[component.component_id],
    )
    blob = next(message for message in view.messages if message['op'] == 'add_pocket_blob')
    assert blob['options']['values']
    assert len(blob['options']['values']) == len(blob['options']['centers'])
    assert blob['options']['color_map'] == 'turbo'
    assert 'wireframe' not in blob['options']

    wire_view = DummyView()
    show_dfnd_components(
        wire_view,
        topo,
        representation='clearance_wire',
        component_ids=[component.component_id],
    )
    wire_blob = next(
        message for message in wire_view.messages if message['op'] == 'add_pocket_blob'
    )
    assert wire_blob['options']['values']
    assert wire_blob['options']['wireframe'] is True


def test_semantic_face_representations_emit_filtered_triangle_faces():
    from molsysviewer_topomt.render import show_dfnd_components

    pocket_topography = _build_dfnd_topo('tube_channel_clean.pdb')
    pocket_component = next(
        comp for comp in pocket_topography.dfnd.dfn.components.wet if comp.n_mouths > 0
    )
    mouth_view = DummyView()
    show_dfnd_components(
        mouth_view,
        pocket_topography,
        representation='mouth_faces',
        component_ids=[pocket_component.component_id],
    )
    mouth_msg = next(
        message for message in mouth_view.messages if message['op'] == 'add_triangle_faces'
    )
    assert mouth_msg['options']['labels']
    assert all('role=mouth_face' in label for label in mouth_msg['options']['labels'])

    interface_topography = _build_dfnd_topo('two_blocks_interface.pdb')
    interface_component = next(
        comp for comp in interface_topography.dfnd.dfn.components.wet if comp.is_interface
    )
    interface_view = DummyView()
    show_dfnd_components(
        interface_view,
        interface_topography,
        representation='interface_faces',
        component_ids=[interface_component.component_id],
    )
    interface_msg = next(
        message
        for message in interface_view.messages
        if message['op'] == 'add_triangle_faces'
    )
    assert interface_msg['options']['labels']
    assert all(
        'role=coast_face' in label for label in interface_msg['options']['labels']
    )


def test_contact_sheet_splits_interface_lining_by_body():
    """Phase 3: an interface renders its lining surface split per body.

    Uses the committed two-block interface fixture (two dry banks + a wet
    interface lined by both). See devguide/DFND/component_visualization_implementation.md
    (Phase 3).
    """
    from pathlib import Path
    from types import SimpleNamespace

    from topomt.dfnd.graph import DelaunayFlowNetwork
    from topomt.dfnd.data import DFNDData
    from molsysviewer_topomt.render import show_dfnd_components
    from molsysviewer_topomt.render import _components as comp_mod

    pdb = (
        Path(__file__).resolve().parents[1]
        / 'topomt'
        / 'data'
        / 'synthetic'
        / 'two_blocks_interface.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_coordinates_and_radii(
        coords, np.full(len(coords), 1.88), epsilon=1e-7
    )
    result = net.get_topography(probe_radius=1.4, min_size=0)
    dfnd = DFNDData(net, result)
    topo = SimpleNamespace(dfnd=dfnd)

    # there must be an interface wet component lined by two dry bodies
    assert dfnd.dfn.components.wet_interfaces

    view = DummyView()
    layer = show_dfnd_components(
        view,
        topo,
        representation='contact_sheet',
        interfaces_only=True,
        component_types=None,
    )
    assert layer is not None
    surfaces = [m for m in view.messages if m['op'] == 'add_pocket_surface']
    # at least two body surfaces, coloured from the interface body palette
    assert len(surfaces) >= 2
    used_colors = set()
    for m in surfaces:
        cmap = m['options'].get('color_map') or []
        used_colors.update(cmap)
    assert used_colors & set(comp_mod._INTERFACE_BODY_COLORS)
    # the two leading body colours (vermillion, bluish green) both appear
    assert comp_mod._INTERFACE_BODY_COLORS[0] in used_colors
    assert comp_mod._INTERFACE_BODY_COLORS[1] in used_colors


def test_auto_renders_each_family_with_its_mode():
    """Phase 0/2: representation='auto' draws each family with its default mode.

    tube_channel_clean has a channel (-> pipe / add_channel_tube) and a pocket
    (-> cloud / add_pocket_blob); both must appear in one 'auto' call.
    """
    from pathlib import Path
    from types import SimpleNamespace

    from topomt.dfnd.graph import DelaunayFlowNetwork
    from topomt.dfnd.data import DFNDData
    from molsysviewer_topomt.render import show_dfnd_components

    pdb = (
        Path(__file__).resolve().parents[1]
        / 'topomt'
        / 'data'
        / 'synthetic'
        / 'tube_channel_clean.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_coordinates_and_radii(
        coords, np.full(len(coords), 1.88), epsilon=1e-7
    )
    result = net.get_topography(probe_radius=1.4, min_size=0)
    topo = SimpleNamespace(dfnd=DFNDData(net, result))

    view = DummyView()
    layer = show_dfnd_components(view, topo, representation='auto')
    assert layer is not None
    ops = [m['op'] for m in view.messages]
    assert 'add_channel_tube' in ops  # channel -> pipe
    assert 'add_pocket_blob' in ops  # pocket -> cloud


def test_rank_by_volume_keeps_largest_components():
    """Phase 5: default-visibility-by-relevance keeps the top_n largest."""
    from types import SimpleNamespace
    from molsysviewer_topomt.render import _components as comp_mod

    comps = [
        SimpleNamespace(component_id='A', volume_solvent_estimate=1.0),
        SimpleNamespace(component_id='B', volume_solvent_estimate=3.0),
        SimpleNamespace(component_id='C', volume_solvent_estimate=2.0),
    ]
    assert [c.component_id for c in comp_mod._rank_by_volume(comps, None)] == [
        'A',
        'B',
        'C',
    ]
    assert [c.component_id for c in comp_mod._rank_by_volume(comps, 2)] == ['B', 'C']
    assert [c.component_id for c in comp_mod._rank_by_volume(comps, 1)] == ['B']

    # None volume sorts as zero (does not crash, ranked last)
    mixed = [
        SimpleNamespace(component_id='X', volume_solvent_estimate=None),
        SimpleNamespace(component_id='Y', volume_solvent_estimate=5.0),
    ]
    assert [c.component_id for c in comp_mod._rank_by_volume(mixed, 1)] == ['Y']


def test_top_n_limits_rendered_components():
    """Phase 5: top_n renders only the most voluminous components."""
    from pathlib import Path
    from types import SimpleNamespace

    from topomt.dfnd.graph import DelaunayFlowNetwork
    from topomt.dfnd.data import DFNDData
    from molsysviewer_topomt.render import show_dfnd_components

    pdb = (
        Path(__file__).resolve().parents[1]
        / 'topomt'
        / 'data'
        / 'synthetic'
        / 'tube_channel_clean.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_coordinates_and_radii(
        coords, np.full(len(coords), 1.88), epsilon=1e-7
    )
    result = net.get_topography(probe_radius=1.4, min_size=0)
    topo = SimpleNamespace(dfnd=DFNDData(net, result))

    # surface draws one layer per component; top_n=1 keeps a single one
    view_all = DummyView()
    show_dfnd_components(view_all, topo, representation='surface')
    n_all = sum(1 for m in view_all.messages if m['op'] == 'add_pocket_surface')

    view_top = DummyView()
    show_dfnd_components(view_top, topo, representation='surface', top_n=1)
    n_top = sum(1 for m in view_top.messages if m['op'] == 'add_pocket_surface')

    assert n_all >= 2
    assert n_top == 1


def test_auto_renders_interfaces_as_contact_sheet():
    """auto recognizes the interface axis: an interface wet component renders as
    a body-split contact_sheet (add_pocket_surface), not a plain blob.
    """
    from pathlib import Path
    from types import SimpleNamespace

    from topomt.dfnd.graph import DelaunayFlowNetwork
    from topomt.dfnd.data import DFNDData
    from molsysviewer_topomt.render import show_dfnd_components

    pdb = (
        Path(__file__).resolve().parents[1]
        / 'topomt'
        / 'data'
        / 'synthetic'
        / 'two_blocks_interface.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_coordinates_and_radii(
        coords, np.full(len(coords), 1.88), epsilon=1e-7
    )
    result = net.get_topography(probe_radius=1.4, min_size=0)
    dfnd = DFNDData(net, result)
    assert dfnd.dfn.components.wet_interfaces  # the fixture has an interface
    topo = SimpleNamespace(dfnd=dfnd)

    view = DummyView()
    show_dfnd_components(view, topo, representation='auto')
    # the interface lining is drawn as a (body-split) surface
    assert any(m['op'] == 'add_pocket_surface' for m in view.messages)


def test_rings_renders_hole_clearance_profile():
    """Phase 4: a channel renders as a HOLE-style ring profile coloured by clearance."""
    from pathlib import Path
    from types import SimpleNamespace

    from topomt.dfnd.graph import DelaunayFlowNetwork
    from topomt.dfnd.data import DFNDData
    from molsysviewer_topomt.render import show_dfnd_components
    from molsysviewer_topomt.render import _components as comp_mod

    pdb = (
        Path(__file__).resolve().parents[1]
        / 'topomt'
        / 'data'
        / 'synthetic'
        / 'tube_channel_clean.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_coordinates_and_radii(
        coords, np.full(len(coords), 1.88), epsilon=1e-7
    )
    result = net.get_topography(probe_radius=1.4, min_size=0)
    topo = SimpleNamespace(dfnd=DFNDData(net, result))

    view = DummyView()
    layer = show_dfnd_components(
        view, topo, representation='rings', component_types=('channel',)
    )
    assert layer is not None
    ring_msgs = [m for m in view.messages if m['op'] == 'add_rings']
    assert ring_msgs
    opts = ring_msgs[0]['options']
    # a ring per centerline station: centers, normals, radii, colors aligned
    n = len(opts['centers'])
    assert n >= 2
    assert len(opts['normals']) == n
    assert len(opts['radii']) == n
    assert len(opts['colors']) == n
    # colours come from the HOLE traffic-light set
    hole = {comp_mod._HOLE_OPEN, comp_mod._HOLE_TIGHT, comp_mod._HOLE_CLOSED}
    assert set(opts['colors']) <= hole


def test_hole_clearance_color_thresholds():
    from molsysviewer_topomt.render import _components as comp_mod

    # clearance radii are nm: thresholds are 0.115 nm (water) and 0.15 nm
    assert comp_mod._hole_clearance_color(0.09) == comp_mod._HOLE_CLOSED  # < 1.15 Å
    assert comp_mod._hole_clearance_color(0.13) == comp_mod._HOLE_TIGHT  # 1.15..1.5 Å
    assert comp_mod._hole_clearance_color(0.20) == comp_mod._HOLE_OPEN  # >= 1.5 Å


def test_carve_voids_focuses_on_void_lining():
    """Phase 5: carve_voids fades the protein outside a void's lining via
    view.focus_with_fade (the new molsysviewer focus-with-fade primitive)."""
    from pathlib import Path
    from types import SimpleNamespace

    from topomt.dfnd.graph import DelaunayFlowNetwork
    from topomt.dfnd.data import DFNDData
    from molsysviewer_topomt.render import carve_voids

    pdb = (
        Path(__file__).resolve().parents[1]
        / 'topomt'
        / 'data'
        / 'synthetic'
        / 'hollow_sphere_void.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_coordinates_and_radii(
        coords, np.full(len(coords), 1.88), epsilon=1e-7
    )
    result = net.get_topography(probe_radius=1.4, min_size=0)
    dfnd = DFNDData(net, result)
    # the fixture has a void
    assert any(c.family == 'void' for c in dfnd.dfn.components.wet)

    captured = {}

    def fake_focus_with_fade(atom_indices, fade=0.85):
        captured['atoms'] = atom_indices
        captured['fade'] = fade

    view = SimpleNamespace(focus_with_fade=fake_focus_with_fade)
    topo = SimpleNamespace(dfnd=dfnd)

    kept = carve_voids(view, topo, fade=0.8)
    assert kept  # some lining atoms
    assert captured['atoms'] == kept  # passed straight to focus_with_fade
    assert captured['fade'] == 0.8
    # the kept atoms are exactly the void components' lining atoms
    void_atoms = set()
    for c in dfnd.dfn.components.wet:
        if c.family == 'void':
            void_atoms.update(c.atom_indices)
    assert set(kept) == void_atoms


def test_wire_contour_uses_pocket_blob_wireframe():
    from molsysviewer_topomt.render import show_dfnd_components

    topography = _build_dfnd_topo('tube_channel_clean.pdb')
    view = DummyView()
    result = show_dfnd_components(view, topography, representation='wire_contour')

    assert result is not None
    blob_messages = [message for message in view.messages if message['op'] == 'add_pocket_blob']
    assert blob_messages
    assert all(message['options']['wireframe'] is True for message in blob_messages)


def test_show_dfnd_components_rejects_unknown_representation():
    from molsysviewer_topomt.render import show_dfnd_components

    component = types.SimpleNamespace(
        component_id='WET-1', family='void', side='wet', node_indices=[0]
    )
    topography = types.SimpleNamespace(
        dfnd=types.SimpleNamespace(
            dfn=types.SimpleNamespace(
                components=types.SimpleNamespace(wet=[component], dry=[])
            )
        )
    )

    with pytest.raises(ValueError, match='Unknown representation'):
        show_dfnd_components(DummyView(), topography, representation='unknown')


def test_probe_centers_uses_parameters_from_real_dfnd_data():
    from types import SimpleNamespace

    from molsysviewer_topomt.render import show_dfnd_components
    from topomt.dfnd.data import DFNDData
    from topomt.dfnd.graph import DelaunayFlowNetwork

    coords = np.array(
        [
            [1.874, 1.874, 1.874],
            [1.874, -1.874, -1.874],
            [-1.874, 1.874, -1.874],
            [-1.874, -1.874, 1.874],
        ]
    )
    network = DelaunayFlowNetwork.from_coordinates_and_radii(coords, np.full(4, 1.88), epsilon=1e-7)
    result = network.get_topography(probe_radius=1.0, min_size=0)
    topography = SimpleNamespace(dfnd=DFNDData(network, result))

    view = DummyView()
    layer = show_dfnd_components(
        view, topography, representation='probe_centers', component_types=None
    )

    assert layer is not None
    assert view.messages[-1]['options']['radius'] == pytest.approx(1.0)


def _graph_render_topography():
    tetrahedron_ids = [0, 1, 3, 10]
    coords = []
    tetrahedra = []
    for tetrahedron_id in tetrahedron_ids:
        start = len(coords)
        x = float(tetrahedron_id)
        coords.extend(
            [[x + 1.0, 0.0, 0.0], [x, 1.0, 0.0], [x, 0.0, 1.0], [x - 1.0, -1.0, -1.0]]
        )
        tetrahedra.append(
            {
                'tetrahedron_id': tetrahedron_id,
                'local_atom_indices': list(range(start, start + 4)),
            }
        )
    faces = [
        {
            'face_id': 101,
            'owner_tetrahedron_id': 0,
            'neighbor_tetrahedron_id': 1,
            'permeability_state': 'permeable',
            'transit_edge': True,
            'face_atoms_local': [0, 1, 2],
        },
        {
            'face_id': 102,
            'owner_tetrahedron_id': 1,
            'neighbor_tetrahedron_id': 3,
            'permeability_state': 'permeable',
            'transit_edge': True,
            'face_atoms_local': [4, 5, 6],
        },
        {
            'face_id': 110,
            'owner_tetrahedron_id': 10,
            'neighbor_tetrahedron_id': -1,
            'permeability_state': 'permeable',
            'transit_edge': False,
            'face_atoms_local': [12, 13, 14],
        },
    ]
    component = types.SimpleNamespace(
        component_id='WET-1',
        family='void',
        side='wet',
        support_key='support:WET-1',
        component_key='component:WET-1',
        node_indices=tetrahedron_ids,
        resident_node_indices=tetrahedron_ids,
        volume=1.0,
    )
    nodes = [
        {
            'tetrahedron_id': tetrahedron_id,
            'residence_state': 'resident',
            'n_permeable_contacts': 0,
            'combined_class': 'wet_sealed',
        }
        for tetrahedron_id in tetrahedron_ids
    ]
    return types.SimpleNamespace(
        dfnd=types.SimpleNamespace(
            mesh=types.SimpleNamespace(
                atoms=types.SimpleNamespace(coords=np.asarray(coords)),
                tetrahedra=tetrahedra,
                faces=faces,
            ),
            dfn=types.SimpleNamespace(
                components=types.SimpleNamespace(wet=[component], dry=[]),
                graph=types.SimpleNamespace(nodes=nodes, faces=faces),
            ),
            raw={'faces': faces, 'tetrahedra': tetrahedra},
        )
    )


def test_component_graph_emits_nodes_in_tetrahedron_id_order():
    from molsysviewer_topomt.render import show_dfnd_components

    view = DummyView()
    show_dfnd_components(view, _graph_render_topography(), representation='graph')

    centers = [
        message['options']['center']
        for message in view.messages
        if message['op'] == 'add_sphere'
    ]
    # nm geometry emitted on the Mol* canvas (angstroms) -> stub coords x10
    assert np.asarray(centers)[:, 0].tolist() == [0.0, 10.0, 30.0, 100.0]


def test_show_dfn_graph_can_render_twice_with_same_tag_prefix():
    from molsysviewer_topomt.render import show_dfn_graph

    view = DummyView()
    topography = _graph_render_topography()

    first = show_dfn_graph(view, topography, tag_prefix='repeat-graph')
    second = show_dfn_graph(view, topography, tag_prefix='repeat-graph')

    assert first.counts['n_nodes'] == second.counts['n_nodes'] == 4
    cleared_tags = {
        message['tag']
        for message in view.messages
        if message['op'] == 'clear_shapes_by_tag'
    }
    assert {
        'repeat-graph-node',
        'repeat-graph-edges',
        'repeat-graph-mouths',
    } <= cleared_tags


def _build_dfnd_topo(pdb_name, probe=1.4):
    from pathlib import Path
    from types import SimpleNamespace
    from topomt.dfnd.graph import DelaunayFlowNetwork
    from topomt.dfnd.data import DFNDData

    pdb = (
        Path(__file__).resolve().parents[1] / 'topomt' / 'data' / 'synthetic' / pdb_name
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_coordinates_and_radii(
        coords, np.full(len(coords), 1.88), epsilon=1e-7
    )
    result = net.get_topography(probe_radius=probe, min_size=0)
    return SimpleNamespace(dfnd=DFNDData(net, result))


def test_envelope_pocket_has_blob_and_one_mouth_ring():
    """Phase 1: a pocket renders a blob + one gate ring; a void only the blob."""
    from molsysviewer_topomt.render import show_dfnd_components

    pocket_topo = _build_dfnd_topo('hollow_sphere_pocket.pdb')
    view = DummyView()
    show_dfnd_components(
        view, pocket_topo, representation='envelope', component_types=('pocket',)
    )
    ops = [m['op'] for m in view.messages]
    assert 'add_pocket_blob' in ops  # the volume
    ring_msgs = [m for m in view.messages if m['op'] == 'add_rings']
    assert ring_msgs  # the pocket's mouth ring
    assert len(ring_msgs[0]['options']['centers']) == 1  # exactly one mouth
    assert 'add_triangle_faces' in ops  # the translucent mouth cap


def test_envelope_void_has_blob_and_no_mouth_ring():
    from molsysviewer_topomt.render import show_dfnd_components

    void_topo = _build_dfnd_topo('hollow_sphere_void.pdb')
    view = DummyView()
    show_dfnd_components(
        view, void_topo, representation='envelope', component_types=('void',)
    )
    ops = [m['op'] for m in view.messages]
    assert 'add_pocket_blob' in ops  # the volume
    assert 'add_rings' not in ops  # a void has no mouths


def test_show_dfnd_labels_annotates_each_component():
    """Phase 5: show_dfnd_labels puts an id/family/mouths/volume label per
    component via view.annotations.add_annotation."""
    from types import SimpleNamespace
    from molsysviewer_topomt.render import show_dfnd_labels

    topo = _build_dfnd_topo('tube_channel_clean.pdb')

    captured = []

    class FakeAnnotations:
        def add_annotation(
            self, *, text, kind, atom_indices, tag, layer_tag, skip_digestion=False
        ):
            layer = SimpleNamespace(tag=tag)
            captured.append(
                {
                    'text': text,
                    'kind': kind,
                    'atom_indices': atom_indices,
                    'tag': tag,
                    'layer_tag': layer_tag,
                }
            )
            return layer

        def delete(self, *a, **k):
            pass

    view = SimpleNamespace(annotations=FakeAnnotations())
    layer = show_dfnd_labels(view, topo)
    assert layer is not None

    # one label per primary wet component, anchored to its lining atoms
    wet = [
        c
        for c in topo.dfnd.dfn.components.wet
        if c.family in ('pocket', 'void', 'channel')
    ]
    assert len(captured) == len(wet)
    for ann in captured:
        assert ann['kind'] == 'label'
        assert ann['layer_tag'] == 'dfnd-label'
        assert ann['atom_indices']  # anchored to atoms
    # the channel label mentions its family and mouth count
    channel = next(c for c in wet if c.family == 'channel')
    chan_label = next(a for a in captured if a['tag'].endswith(channel.component_id))
    assert 'channel' in chan_label['text']
    assert 'mouth' in chan_label['text']


def test_scaffold_draws_dry_core_spine():
    """§7: scaffold renders each dry component's MST as links (the dry spine)."""
    from molsysviewer_topomt.render import show_dfnd_components

    topo = _build_dfnd_topo('two_blocks_interface.pdb')
    assert len(list(topo.dfnd.dfn.components.dry)) >= 2  # two dry banks

    view = DummyView()
    layer = show_dfnd_components(view, topo, representation='scaffold')
    assert layer is not None
    link_msgs = [
        m for m in view.messages if m['op'] in ('add_network_links', 'add_links')
    ]
    assert link_msgs  # the dry spine cylinders


def test_affinity_color_typing_from_scalars():
    """Phase 5: the affinity classifier maps (hydrophobicity, charge) to colours."""
    from molsysviewer_topomt.render import _components as c

    assert (
        c._affinity_color_for_scalars(2.0, 1.0) == c._AFFINITY_POSITIVE
    )  # +charge wins
    assert (
        c._affinity_color_for_scalars(2.0, -1.0) == c._AFFINITY_NEGATIVE
    )  # -charge wins
    assert c._affinity_color_for_scalars(1.5, 0.0) == c._AFFINITY_HYDROPHOBIC
    assert c._affinity_color_for_scalars(-1.5, 0.0) == c._AFFINITY_POLAR
    assert c._affinity_color_for_scalars(None, None) == c._AFFINITY_NEUTRAL


def test_affinity_spheres_neutral_on_dummy_system():
    """affinity_spheres must not crash on dummy (argon/DUM) systems: physchem has
    no DUM entry, so the lining falls back to the neutral colour."""
    from molsysviewer_topomt.render import show_dfnd_components
    from molsysviewer_topomt.render import _components as c

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    view = DummyView()  # DummyView has no _molsys -> chemistry unavailable
    layer = show_dfnd_components(view, topo, representation='affinity_spheres')
    assert layer is not None
    sphere_msgs = [m for m in view.messages if m['op'] == 'add_alpha_sphere_set']
    assert sphere_msgs
    # no chemistry -> every sphere set is the neutral colour
    for m in sphere_msgs:
        assert m['options']['alpha_spheres']['color'] == c._AFFINITY_NEUTRAL


def test_atom_convexity_spike_is_most_convex():
    """§7: the convexity scalar flags a protrusion as the most convex atom."""
    from pathlib import Path
    from molsysviewer_topomt.render._components import _atom_convexity

    pdb = (
        Path(__file__).resolve().parents[1]
        / 'topomt'
        / 'data'
        / 'synthetic'
        / 'tetrahedron_spike.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    # the spike is the 4th atom at z=10; use a radius large enough to see the base
    conv = _atom_convexity(coords, radius=15.0)
    assert np.argmax(conv) == 3  # the spike atom is the most convex
    assert conv[3] > 0  # it is a protrusion (positive)


def test_peak_patches_and_ridge_lines_use_convex_peak_geometry():
    from types import SimpleNamespace

    from molsysviewer_topomt.render import show_dfnd_peak_patches, show_dfnd_ridge_lines

    coords = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 3.0],
        ]
    )
    atoms = SimpleNamespace(coords=coords, index_map=np.array([10, 11, 12, 13]))
    topography = SimpleNamespace(dfnd=SimpleNamespace(mesh=SimpleNamespace(atoms=atoms)))

    patch_view = DummyView()
    patches = show_dfnd_peak_patches(
        patch_view, topography, radius=4.0, top_n=2, patch_radius=0.2
    )
    assert patches is not None
    patch_msgs = [message for message in patch_view.messages if message['op'] == 'add_sphere']
    assert patch_msgs
    assert patch_msgs[0]['options']['layer_tag'] == 'dfnd-peak-patches'

    ridge_view = DummyView()
    ridge = show_dfnd_ridge_lines(ridge_view, topography, radius=4.0, top_n=3)
    assert ridge is not None
    ridge_msg = next(
        message
        for message in ridge_view.messages
        if message['op'] in {'add_network_links', 'add_links'}
    )
    assert ridge_msg['options']['coordinate_pairs']
    assert ridge_msg['options']['tag'] == 'dfnd-ridge-lines'


def test_show_dfnd_spikes_uses_displacement_vectors_for_convex_peaks():
    from types import SimpleNamespace

    from molsysviewer_topomt.render import show_dfnd_spikes

    coords = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 3.0],
        ]
    )
    atoms = SimpleNamespace(coords=coords, index_map=np.array([10, 11, 12, 13]))
    mesh = SimpleNamespace(atoms=atoms)
    topography = SimpleNamespace(dfnd=SimpleNamespace(mesh=mesh))
    calls = []

    class FakeVectors:
        def add_displacement_vectors(self, **kwargs):
            calls.append(kwargs)
            return 'spike-layer'

    view = SimpleNamespace(shapes=SimpleNamespace(vectors=FakeVectors()))
    layer = show_dfnd_spikes(
        view,
        topography,
        radius=4.0,
        top_n=1,
        vector_length=0.3,
        palette=None,
    )

    assert layer == 'spike-layer'
    assert calls[0]['atom_indices'] == [13]
    assert calls[0]['tag'] == 'dfnd-spikes'
    assert calls[0]['skip_digestion'] is True


def test_show_dfnd_convexity_colours_whole_surface():
    """§7: show_dfnd_convexity feeds per-atom convexity to whole.set_color_by_values."""
    from types import SimpleNamespace
    from molsysviewer_topomt.render import show_dfnd_convexity

    topo = _build_dfnd_topo('hollow_sphere_void.pdb')
    captured = {}

    class FakeWhole:
        def set_color_by_values(
            self,
            values,
            element='atom',
            palette='viridis',
            value_range=None,
            skip_digestion=False,
        ):
            captured['values'] = np.asarray(values)
            captured['element'] = element
            captured['palette'] = palette

    view = SimpleNamespace(whole=FakeWhole())  # no _molsys -> DFND order
    values = show_dfnd_convexity(view, topo, radius=6.0)
    assert captured['element'] == 'atom'
    n_atoms = len(topo.dfnd.mesh.atoms.coords)
    assert len(captured['values']) == n_atoms
    assert np.allclose(captured['values'], values)


def test_show_dfnd_legend_lists_present_families():
    """Phase 5 legend: show_dfnd_legend feeds family->Okabe-Ito items to scene.set_legend."""
    from types import SimpleNamespace
    from molsysviewer_topomt.render import show_dfnd_legend
    from molsysviewer_topomt.render import _components as c

    topo = _build_dfnd_topo('tube_channel_clean.pdb')  # channel + pocket
    captured = {}

    class FakeScene:
        def set_legend(self, items, position='top-right'):
            captured['items'] = items

    view = SimpleNamespace(scene=FakeScene())
    items = show_dfnd_legend(view, topo)
    assert captured['items'] == items
    labels = {it['label'] for it in items}
    assert 'channel' in labels and 'pocket' in labels
    by_label = {it['label']: it['color'] for it in items}
    assert by_label['channel'] == c._TYPE_PALETTE[c.fam.CHANNEL]
    assert by_label['pocket'] == c._TYPE_PALETTE[c.fam.POCKET]


def test_pharmacophore_kind_typing():
    """§9: the pharmacophore classifier maps (hydrophobicity, charge) to kinds."""
    from molsysviewer_topomt.render._components import (
        _pharmacophore_kind_for_scalars as k,
    )

    assert k(2.0, 1.0) == 'positive'
    assert k(2.0, -1.0) == 'negative'
    assert k(1.5, 0.0) == 'hydrophobic'
    assert k(-1.5, 0.0) == 'acceptor'
    assert k(None, None) is None


def test_pharmacophore_map_places_typed_sites(monkeypatch):
    """§9: show_dfnd_pharmacophore places a typed interaction site per cavity."""
    from types import SimpleNamespace
    import numpy as _np
    from molsysviewer_topomt.render import show_dfnd_pharmacophore
    from molsysviewer_topomt.render import _components as c

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    n_atoms = len(topo.dfnd.mesh.atoms.coords)
    # pretend every atom is hydrophobic (chemistry available)
    monkeypatch.setattr(
        c, '_atom_pharmacophore_kinds', lambda molsys: ['hydrophobic'] * n_atoms
    )

    view = DummyView()
    view._molsys = object()  # non-None so the function proceeds
    layer = show_dfnd_pharmacophore(view, topo)
    assert layer is not None
    site_msgs = [m for m in view.messages if m['op'] == 'add_pharmacophore_features']
    assert site_msgs
    opts = site_msgs[0]['options']
    assert len(opts['centers']) == len(opts['kinds'])
    assert all(kind == 'hydrophobic' for kind in opts['kinds'])


def test_pharmacophore_map_none_on_dummy_system():
    """No chemistry (dummy) -> no sites, no crash."""
    from molsysviewer_topomt.render import show_dfnd_pharmacophore

    topo = _build_dfnd_topo('tube_channel_clean.pdb')
    view = DummyView()  # no _molsys
    assert show_dfnd_pharmacophore(view, topo) is None


def test_dfnd_index_space_helpers_and_geometry_conversion_are_explicit():
    from types import SimpleNamespace

    from molsysviewer_topomt.index_spaces import (
        MESH_LOCAL,
        MOLECULAR_SYSTEM,
        atom_index_payload,
        mesh_local_from_molecular_system,
    )
    from molsysviewer_topomt.render._components import _body_labels_from_dry

    index_map = np.array([10, 20, 30, 40])
    comp = SimpleNamespace(
        component_id='DRY-1',
        atom_indices=[10, 30],
        center=[1.0, 0.0, 0.0],
        external_link_ids=[1],
    )

    assert mesh_local_from_molecular_system([30, 10], index_map) == [2, 0]
    assert atom_index_payload([0, 2], MESH_LOCAL)['atom_index_space'] == MESH_LOCAL
    assert (
        atom_index_payload([10, 30], MOLECULAR_SYSTEM)['atom_index_space']
        == MOLECULAR_SYSTEM
    )
    assert _body_labels_from_dry([comp]) == {10: 0, 30: 0}


def test_dfnd_face_label_converts_raw_nm_gate_to_angstroms():
    from molsysviewer_topomt.render._common import _dfnd_face_label

    label = _dfnd_face_label(
        {
            'face_id': 7,
            'owner_tetrahedron_id': 1,
            'neighbor_tetrahedron_id': 2,
            'permeability_state': 'permeable',
            'R_gate': 0.215,
        },
        7,
    )

    assert 'R_gate=2.15 Å' in label


def test_dfnd_face_semantics_reports_role_margin_and_components():
    from molsysviewer_topomt.render._common import _dfnd_face_meta

    topography = {
        'parameters': {'probe_radius': 0.14},
        'tetrahedra': [
            {
                'tetrahedron_id': 0,
                'local_atom_indices': [0, 1, 2, 3],
                'combined_class': 'wet_open',
                'residence_state': 'resident',
            },
            {
                'tetrahedron_id': 1,
                'local_atom_indices': [1, 2, 3, 4],
                'combined_class': 'wet_open',
                'residence_state': 'resident',
            },
            {
                'tetrahedron_id': 2,
                'local_atom_indices': [0, 2, 3, 5],
                'combined_class': 'dry_sealed',
                'residence_state': 'non_resident',
            },
        ],
        'faces': [
            {
                'face_id': 10,
                'owner_tetrahedron_id': 0,
                'neighbor_tetrahedron_id': 1,
                'face_atoms_local': [1, 2, 3],
                'permeability_state': 'permeable',
                'R_gate': 0.215,
            },
            {
                'face_id': 11,
                'owner_tetrahedron_id': 0,
                'neighbor_tetrahedron_id': 2,
                'face_atoms_local': [0, 2, 3],
                'permeability_state': 'non_permeable',
                'R_gate': 0.110,
            },
            {
                'face_id': 12,
                'owner_tetrahedron_id': 0,
                'neighbor_tetrahedron_id': -1,
                'face_atoms_local': [0, 1, 2],
                'permeability_state': 'permeable',
                'R_gate': 0.180,
            },
        ],
    }

    meta = {
        item['face_id']: item
        for item in _dfnd_face_meta(
            topography,
            {0, 1, 2},
            components_by_tetrahedron={0: 'WET-1', 1: 'WET-1', 2: 'DRY-1'},
            face_color_mode='role',
        )
    }

    assert meta[10]['role'] == 'transit_face'
    assert meta[10]['side_relation'] == 'wet-wet'
    assert meta[10]['gate_margin'] == pytest.approx(0.075)
    assert meta[10]['component_ids'] == ['WET-1']
    assert 'gate_margin=0.75 Å' in meta[10]['label']
    assert meta[11]['role'] == 'coast_face'
    assert meta[11]['side_relation'] == 'wet-dry'
    assert meta[11]['component_ids'] == ['WET-1', 'DRY-1']
    assert meta[12]['role'] == 'mouth_face'
    assert meta[12]['side_relation'] == 'wet-OCEAN'


def test_dfnd_face_color_modes_are_semantic():
    from molsysviewer_topomt.render._common import _dfnd_face_meta

    topography = {
        'parameters': {'probe_radius': 0.14},
        'tetrahedra': [
            {'tetrahedron_id': 0, 'local_atom_indices': [0, 1, 2, 3]},
            {'tetrahedron_id': 1, 'local_atom_indices': [1, 2, 3, 4]},
        ],
        'faces': [
            {
                'face_id': 10,
                'owner_tetrahedron_id': 0,
                'neighbor_tetrahedron_id': 1,
                'face_atoms_local': [1, 2, 3],
                'permeability_state': 'permeable',
                'R_gate': 0.215,
            },
        ],
    }

    by_component = _dfnd_face_meta(
        topography,
        {0, 1},
        colors_by_tetrahedron={0: 0x123456},
        face_color_mode='component',
    )[0]
    by_permeability = _dfnd_face_meta(
        topography, {0, 1}, face_color_mode='permeability'
    )[0]
    by_margin = _dfnd_face_meta(
        topography, {0, 1}, face_color_mode='gate_margin'
    )[0]

    assert by_component['color'] == 0x123456
    assert by_permeability['color'] == 0x93C5FD
    assert by_margin['color'] == 0x0072B2


def test_dfnd_owned_payloads_declare_atom_index_space():
    from molsysviewer_topomt.payloads import feature_record_from_feature
    from molsysviewer_topomt.render._common import _dfnd_edge_meta, _dfnd_face_meta
    from molsysviewer_topomt.simplex_selection import resolve_simplices
    from topomt.dfnd.graph import DelaunayFlowNetwork

    net = DelaunayFlowNetwork.from_coordinates_and_radii(
        np.array(
            [
                [0.0, 0.0, 0.0],
                [4.0, 0.0, 0.0],
                [0.0, 4.0, 0.0],
                [0.0, 0.0, 4.0],
            ]
        ),
        np.full(4, 1.5),
        atom_indices=[10, 20, 30, 40],
    )
    result = net.get_topography()

    assert all(
        item['atom_index_space'] == 'mesh_local'
        for item in _dfnd_edge_meta(result, {0})
    )
    assert all(
        item['atom_index_space'] == 'mesh_local'
        for item in _dfnd_face_meta(result, {0})
    )
    tetra_item = next(
        item
        for item in resolve_simplices(result, [10, 20, 30, 40])
        if item['payload']['kind'] == 'tetrahedron'
    )
    assert tetra_item['payload']['atom_index_space'] == 'molecular_system'
    feature = types.SimpleNamespace(atom_indices=[10, 20], feature_id='P-1')
    assert (
        feature_record_from_feature(feature)['atom_index_space'] == 'molecular_system'
    )


def test_partial_mesh_global_selection_hover_click_boundary():
    from molsysviewer_topomt.addon import (
        _handle_simplex_selection,
        on_active_selection_changed,
        on_enable,
    )
    from molsysviewer_topomt.simplex_selection import simplex_selection_info
    from topomt.dfnd.graph import DelaunayFlowNetwork

    net = DelaunayFlowNetwork.from_coordinates_and_radii(
        np.array(
            [
                [0.0, 0.0, 0.0],
                [4.0, 0.0, 0.0],
                [0.0, 4.0, 0.0],
                [0.0, 0.0, 4.0],
            ]
        ),
        np.full(4, 1.5),
        atom_indices=[10, 20, 30, 40],
    )
    result = net.get_topography()
    topography = types.SimpleNamespace(dfnd=tmt.dfnd.data.DFNDData(net, result))
    view = DummyView()
    on_enable(view)
    runtime = view._topomt_addon_runtime
    runtime.topography = topography

    items = on_active_selection_changed(
        view,
        {
            'atom_indices': [10, 20, 30, 40],
            'atom_index_space': 'molecular_system',
        },
    )
    tetra = next(
        item['payload'] for item in items if item['payload']['kind'] == 'tetrahedron'
    )
    assert tetra['atom_indices'] == [10, 20, 30, 40]
    assert tetra['atom_index_space'] == 'molecular_system'

    view._index_mapper = types.SimpleNamespace(
        to_local_atoms=lambda atoms: [1, 3, 5, 7]
    )
    _handle_simplex_selection(view, runtime, tetra)
    message = next(
        msg for msg in reversed(view.messages) if msg['op'] == 'set_active_selection'
    )
    assert message['atom_indices'] == [1, 3, 5, 7]
    assert simplex_selection_info(view)['atom_indices'] == [10, 20, 30, 40]
    assert view._last_active_selection_event['atom_index_space'] == 'molecular_system'


def test_primary_renderers_return_common_render_result_and_render_twice():
    from molsysviewer_topomt.render import RenderResult
    from molsysviewer_topomt.render import show_dfn_graph, show_dfnd_components
    from molsysviewer_topomt.render import show_dfnd_tetrahedra, show_topography_pockets

    pocket_topography = tmt.Topography()
    pocket_topography.add_new_feature(
        feature_type='pocket', feature_id='POC-1', center=[0.0, 0.0, 0.0]
    )
    pocket_view = DummyView()
    pocket_first = show_topography_pockets(pocket_view, pocket_topography)
    pocket_second = show_topography_pockets(pocket_view, pocket_topography)

    tetra_view = DummyView()
    tetra_empty = show_dfnd_tetrahedra(tetra_view, {'tetrahedra': []})

    graph_view = DummyView()
    graph_first = show_dfn_graph(graph_view, _graph_render_topography())
    graph_second = show_dfn_graph(graph_view, _graph_render_topography())

    component_view = DummyView()
    component_topography = _build_dfnd_topo('hollow_sphere_void.pdb')
    component_first = show_dfnd_components(
        component_view, component_topography, representation='surface'
    )
    component_second = show_dfnd_components(
        component_view, component_topography, representation='surface'
    )

    for result in (
        pocket_first,
        pocket_second,
        tetra_empty,
        graph_first,
        graph_second,
        component_first,
        component_second,
    ):
        assert isinstance(result, RenderResult)
        assert isinstance(result.layers, tuple)
        assert isinstance(result.tags, tuple)
        assert isinstance(result.warnings, tuple)

    assert pocket_second.counts['n_rendered'] == 1
    assert pocket_second.layers[0] is pocket_second.layers[0]
    assert tetra_empty.is_empty is True
    assert bool(tetra_empty) is False
    assert graph_second.counts['n_nodes'] == graph_first.counts['n_nodes']
    assert component_second.representation == 'surface'
    assert component_second.selected_ids
    assert any(
        message.get('op') == 'clear_shapes_by_tag'
        and message.get('tag') == 'topomt-pocket:POC-1'
        for message in pocket_view.messages
    )


def test_render_result_uses_explicit_counts_and_details():
    from molsysviewer_topomt.render import RenderResult

    layer = types.SimpleNamespace(tag='layer-tag')
    result = RenderResult(
        representation='test',
        selected_ids=('A',),
        layers=(layer,),
        tags=('layer-tag',),
        counts={'n_items': 1},
        details={'payload': 'value'},
    )

    assert result.counts['n_items'] == 1
    assert result.details['payload'] == 'value'
    assert result.layers == (layer,)
    assert result.tags == ('layer-tag',)
    assert result.counts['n_layers'] == 1
    assert result.counts['n_selected'] == 1
    with pytest.raises(TypeError):
        result.counts['n_items'] = 2
    with pytest.raises(TypeError):
        result.details['payload'] = 'other'
    assert bool(result) is True


@pytest.mark.parametrize(
    'representation',
    [
        'auto',
        'tetrahedra',
        'cloud',
        'envelope',
        'wire_contour',
        'clearance_map',
        'clearance_wire',
        'scalar_isosurface',
        'pocket_depth_map',
        'shape_ellipsoids',
        'pipe',
        'channel_tube',
        'channel_solid',
        'channel_profile',
        'channel_lumen',
        'channel_tunnel',
        'channel_ribbon',
        'groove_ribbon',
        'groove_floor',
        'groove_walls',
        'groove_width_profile',
        'groove_depth_profile',
        'channel_blob',
        'channel_wire_blob',
        'rings',
        'mouth_rings',
        'bottleneck_rings',
        'residence_spheres',
        'alpha_spheres',
        'probe_centers',
        'surface',
        'contact_sheet',
        'scaffold',
        'affinity_spheres',
        'coast_faces',
        'dry_interface_faces',
        'dry_blocked_faces',
        'dry_depth_map',
        'dry_shell',
        'dry_cage',
        'semantic_faces',
        'permeable_faces',
        'impermeable_faces',
        'mouth_faces',
        'interface_faces',
        'interface_contact_faces',
        'interface_links',
        'interface_ribbon',
        'interface_lining_surface',
        'interface_surface',
        'mouth_stubs',
        'graph',
    ],
)
def test_every_component_representation_returns_render_result_and_repeats(
    representation,
):
    from molsysviewer_topomt.render import RenderResult, show_dfnd_components

    topography = _build_dfnd_topo('tube_channel_clean.pdb')
    view = DummyView()
    first = show_dfnd_components(
        view,
        topography,
        representation=representation,
        show_wet=True,
        show_dry=True,
        component_types=None,
        draw_faces=True,
        draw_edges=True,
    )
    second = show_dfnd_components(
        view,
        topography,
        representation=representation,
        show_wet=True,
        show_dry=True,
        component_types=None,
        draw_faces=True,
        draw_edges=True,
    )

    assert isinstance(first, RenderResult)
    assert isinstance(second, RenderResult)
    assert first.representation == representation
    assert second.representation == representation
    assert first.selected_ids == second.selected_ids


def test_empty_render_result_replaces_previous_graph_tetrahedra_and_components():
    from molsysviewer_topomt.render import (
        show_dfn_graph,
        show_dfnd_components,
        show_dfnd_tetrahedra,
    )

    graph_topography = _graph_render_topography()
    graph_view = DummyView()
    assert show_dfn_graph(graph_view, graph_topography)
    for node in graph_topography.dfnd.dfn.graph.nodes:
        node['residence_state'] = 'non_resident'
    empty_graph = show_dfn_graph(graph_view, graph_topography)
    assert empty_graph.is_empty
    assert 'dfn-graph-node' not in getattr(graph_view, '_scene_objects', {})

    tetra_view = DummyView()
    tetra_records = {
        'tetrahedra': [
            {
                'tetrahedron_id': 0,
                'local_atom_indices': [0, 1, 2, 3],
                'combined_class': 'wet_sealed',
                'residence_state': 'resident',
            }
        ]
    }
    assert show_dfnd_tetrahedra(tetra_view, tetra_records)
    empty_tetrahedra = show_dfnd_tetrahedra(
        tetra_view, tetra_records, tetrahedra_indices=[]
    )
    assert empty_tetrahedra.is_empty
    assert 'dfnd-tetra' not in getattr(tetra_view, '_scene_objects', {})

    component_view = DummyView()
    component_topography = _build_dfnd_topo('hollow_sphere_void.pdb')
    assert show_dfnd_components(
        component_view, component_topography, representation='surface'
    )
    empty_components = show_dfnd_components(
        component_view,
        component_topography,
        representation='surface',
        component_ids=['missing'],
    )
    assert empty_components.is_empty
    assert not any(
        tag.startswith('dfnd-comp')
        for tag in getattr(component_view, '_scene_objects', {})
    )


def test_wp18_point_geometry_requires_units_and_structured_refs():
    from molsysviewer_topomt.geometry import EntityRef, PointGeometry

    ref = EntityRef(kind='tetrahedron', entity_id=7, tetrahedron_ids=(7,))
    geometry = PointGeometry(((1.0, 2.0, 3.0),), unit='angstroms', refs=(ref,))

    assert geometry.coordinates == ((1.0, 2.0, 3.0),)
    assert geometry.refs[0].tetrahedron_ids == (7,)
    with pytest.raises(ValueError, match='unit is required'):
        PointGeometry(((1.0, 2.0, 3.0),), unit='', refs=(ref,))


def test_wp18_graph_renderers_share_canonical_tetrahedron_center_geometry():
    from molsysviewer_topomt.render import show_dfn_graph, show_dfnd_components

    topography = _graph_render_topography()
    full = show_dfn_graph(DummyView(), topography)
    component = show_dfnd_components(DummyView(), topography, representation='graph')

    full_geometry = full.details['node_geometry']
    component_geometry = component.details['node_geometry']
    assert full_geometry.unit == component_geometry.unit == 'nm'
    assert full_geometry.coordinates == component_geometry.coordinates
    assert tuple(ref.entity_id for ref in full_geometry.refs) == tuple(
        ref.entity_id for ref in component_geometry.refs
    )
    assert all(ref.component_key for ref in component_geometry.refs)


def test_wp18_point_adapter_always_skips_digestion():
    from molsysviewer_topomt.geometry import EntityRef, PointGeometry
    from molsysviewer_topomt.render.adapters import add_point_spheres

    calls = []
    view = types.SimpleNamespace(
        shapes=types.SimpleNamespace(add_sphere=lambda **kwargs: calls.append(kwargs))
    )
    geometry = PointGeometry(
        ((0.0, 0.0, 0.0),),
        unit='angstroms',
        refs=(EntityRef(kind='tetrahedron', entity_id=0),),
    )

    add_point_spheres(view, geometry, radius=puw.quantity(0.03, 'nm'))

    assert calls[0]['skip_digestion'] is True


def test_wp18_tetrahedron_centers_preserve_requested_order():
    from molsysviewer_topomt.geometry import tetrahedron_centers

    geometry = tetrahedron_centers(_graph_render_topography(), [10, 0, 3])

    assert tuple(ref.entity_id for ref in geometry.refs) == (10, 0, 3)
    assert tuple(point[0] for point in geometry.coordinates) == (10.0, 0.0, 3.0)


def test_wp18_graph_renderers_share_canonical_edge_geometry():
    from molsysviewer_topomt.render import show_dfn_graph, show_dfnd_components

    topography = _graph_render_topography()
    full = show_dfn_graph(DummyView(), topography)
    component = show_dfnd_components(DummyView(), topography, representation='graph')

    full_edges = full.details['edge_geometry']
    component_edges = component.details['edge_geometry']
    assert full_edges.unit == component_edges.unit == 'nm'
    assert full_edges.coordinate_pairs == component_edges.coordinate_pairs
    assert tuple(ref.entity_id for ref in full_edges.refs) == (101, 102)
    assert tuple(ref.entity_id for ref in component_edges.refs) == (101, 102)
    assert all(ref.kind == 'face' for ref in full_edges.refs)


def test_wp18_full_graph_mouth_geometry_keeps_face_reference():
    from molsysviewer_topomt.render import show_dfn_graph

    result = show_dfn_graph(DummyView(), _graph_render_topography())
    mouths = result.details['mouth_geometry']

    assert mouths.unit == 'nm'
    assert len(mouths.refs) == 1
    assert mouths.refs[0].entity_id == 110
    assert mouths.refs[0].tetrahedron_ids == (10,)


def test_wp18_segment_adapter_always_skips_digestion():
    from molsysviewer_topomt.geometry import EntityRef, SegmentGeometry
    from molsysviewer_topomt.render.adapters import add_segments

    calls = []
    view = types.SimpleNamespace(
        shapes=types.SimpleNamespace(add_links=lambda **kwargs: calls.append(kwargs))
    )
    geometry = SegmentGeometry(
        ((0.0, 0.0, 0.0),),
        ((1.0, 0.0, 0.0),),
        unit='angstroms',
        refs=(EntityRef(kind='face', entity_id=1, tetrahedron_ids=(0, 1)),),
    )

    add_segments(view, geometry, radius=puw.quantity(0.015, 'nm'), skip_digestion=False)

    assert calls[0]['skip_digestion'] is True


def test_wp18_tetrahedra_geometry_preserves_coordinates_indices_and_refs():
    from molsysviewer_topomt.geometry import tetrahedra_geometry

    geometry = tetrahedra_geometry(_graph_render_topography(), [10, 0])

    assert geometry.unit == 'nm'
    assert geometry.atom_index_space == 'mesh_local'
    assert tuple(ref.entity_id for ref in geometry.refs) == (10, 0)
    assert len(geometry.coordinates) == len(geometry.atom_quads) == 2
    assert geometry.atom_quads[0] == (12, 13, 14, 15)


def test_wp18_tetrahedron_renderers_emit_identical_canonical_quads():
    from molsysviewer_topomt.render import show_dfnd_components, show_dfnd_tetrahedra

    topography = _graph_render_topography()
    general_view = DummyView()
    component_view = DummyView()
    show_dfnd_tetrahedra(general_view, topography)
    show_dfnd_components(component_view, topography, representation='tetrahedra')

    general = next(
        message
        for message in general_view.messages
        if message['op'] == 'add_tetrahedra'
    )
    component = next(
        message
        for message in component_view.messages
        if message['op'] == 'add_tetrahedra'
    )
    assert general['options']['atom_quads'] == component['options']['atom_quads']


def test_wp18_tetrahedra_adapter_always_skips_digestion():
    from molsysviewer_topomt.geometry import EntityRef, TetrahedraGeometry
    from molsysviewer_topomt.render.adapters import add_tetrahedra

    calls = []
    view = types.SimpleNamespace(
        shapes=types.SimpleNamespace(
            add_tetrahedra=lambda **kwargs: calls.append(kwargs)
        )
    )
    geometry = TetrahedraGeometry(
        (),
        ((0, 1, 2, 3),),
        atom_index_space='mesh_local',
        unit='angstroms',
        refs=(EntityRef(kind='tetrahedron', entity_id=0),),
    )

    add_tetrahedra(view, geometry, skip_digestion=False)

    assert calls[0]['skip_digestion'] is True
    assert calls[0]['atom_quads'] == ((0, 1, 2, 3),)


def test_wp18_face_and_edge_geometry_preserve_pick_indices_and_identity():
    from molsysviewer_topomt.geometry import edge_geometry, face_geometry

    topography = _build_dfnd_topo('tetrahedron_void.pdb')
    faces = face_geometry(topography, [0])
    edges = edge_geometry(topography, [0])

    assert faces.unit == edges.unit == 'nm'
    assert faces.atom_index_space == edges.atom_index_space == 'mesh_local'
    assert all(len(item) == 3 for item in faces.atom_triplets)
    assert all(len(item) == 2 for item in edges.atom_pairs)
    assert all(ref.kind == 'face' for ref in faces.refs)
    assert all(ref.kind == 'edge' for ref in edges.refs)


def test_wp18_pick_metadata_contains_json_structured_entity_refs():
    from molsysviewer_topomt.render._common import _dfnd_edge_meta, _dfnd_face_meta

    topography = _build_dfnd_topo('tetrahedron_void.pdb')
    face = _dfnd_face_meta(topography, {0})[0]
    edge = _dfnd_edge_meta(topography, {0})[0]

    assert isinstance(face['entity_ref'], dict)
    assert face['entity_ref']['kind'] == 'face'
    assert face['entity_ref']['entity_id'] == face['face_id']
    assert isinstance(edge['entity_ref'], dict)
    assert edge['entity_ref']['kind'] == 'edge'
    assert edge['entity_ref']['entity_id'] == edge['edge_id']


def test_wp18_face_geometry_filters_by_stable_face_id():
    from molsysviewer_topomt.geometry import face_geometry

    topography = _graph_render_topography()
    geometry = face_geometry(topography, face_ids=[110, 101])

    assert tuple(ref.entity_id for ref in geometry.refs) == (101, 110)
    assert all(ref.kind == 'face' for ref in geometry.refs)


def test_wp18_indexed_triangle_adapter_preserves_pick_triplets_and_skips_digestion():
    from molsysviewer_topomt.geometry import EntityRef, IndexedTriangleGeometry
    from molsysviewer_topomt.render.adapters import add_indexed_triangles

    calls = []
    view = types.SimpleNamespace(
        shapes=types.SimpleNamespace(
            add_triangle_faces=lambda **kwargs: calls.append(kwargs)
        )
    )
    geometry = IndexedTriangleGeometry(
        (),
        ((0, 1, 2),),
        atom_index_space='mesh_local',
        unit='angstroms',
        refs=(EntityRef(kind='face', entity_id=7, tetrahedron_ids=(0, 1)),),
    )

    add_indexed_triangles(view, geometry, skip_digestion=False)

    assert calls[0]['skip_digestion'] is True
    assert calls[0]['atom_triplets'] == ((0, 1, 2),)


def test_wp18_component_sphere_geometries_share_tetrahedron_identity():
    from molsysviewer_topomt.geometry import (
        component_alpha_sphere_geometry,
        component_residence_sphere_geometry,
        probe_sphere_geometry,
    )

    topography = _build_dfnd_topo('hollow_sphere_void.pdb')
    component = topography.dfnd.dfn.components.wet[0]
    residence = component_residence_sphere_geometry(topography, component)
    alpha = component_alpha_sphere_geometry(topography, component)
    probe = probe_sphere_geometry(residence, 0.14)  # nm (1.4 angstroms)

    assert residence.unit == alpha.unit == probe.unit == 'nm'
    assert tuple(ref.entity_id for ref in residence.refs) == tuple(
        ref.entity_id for ref in alpha.refs
    )
    assert all(ref.component_key == component.component_key for ref in residence.refs)
    assert probe.radii  # the void admits the probe
    assert all(radius == pytest.approx(0.14) for radius in probe.radii)


def test_wp18_sphere_adapters_force_skip_digestion():
    from molsysviewer_topomt.geometry import EntityRef, SphereGeometry
    from molsysviewer_topomt.render.adapters import add_sphere_set, add_uniform_spheres

    alpha_calls = []
    uniform_calls = []
    view = types.SimpleNamespace(
        shapes=types.SimpleNamespace(
            add_set_alpha_spheres=lambda **kwargs: alpha_calls.append(kwargs),
            add_sphere=lambda **kwargs: uniform_calls.append(kwargs),
        )
    )
    geometry = SphereGeometry(
        ((0.0, 0.0, 0.0),),
        (1.4,),
        unit='angstroms',
        refs=(EntityRef(kind='tetrahedron', entity_id=0),),
    )

    add_sphere_set(view, geometry, skip_digestion=False)
    add_uniform_spheres(view, geometry, skip_digestion=False)

    assert alpha_calls[0]['skip_digestion'] is True
    assert uniform_calls[0]['skip_digestion'] is True


def test_wp18_sphere_renderers_emit_canonical_residence_and_alpha_geometry():
    from molsysviewer_topomt.geometry import (
        component_alpha_sphere_geometry,
        component_residence_sphere_geometry,
    )
    from molsysviewer_topomt.render import show_dfnd_components

    topography = _build_dfnd_topo('hollow_sphere_void.pdb')
    component = topography.dfnd.dfn.components.wet[0]

    for representation, extractor in (
        ('residence_spheres', component_residence_sphere_geometry),
        ('alpha_spheres', component_alpha_sphere_geometry),
    ):
        expected = extractor(topography, component)
        view = DummyView()
        show_dfnd_components(
            view,
            topography,
            representation=representation,
            component_ids=[component.component_id],
        )
        emitted = view.messages[-1]['options']['alpha_spheres']
        # canonical geometry is nm; the emitted wire is the Mol* canvas (angstroms)
        expected_centers = puw.get_value(
            puw.quantity(np.asarray(expected.centers), 'nm'), to_unit='angstroms'
        )
        expected_radii = puw.get_value(
            puw.quantity(np.asarray(expected.radii), 'nm'), to_unit='angstroms'
        )
        assert np.allclose(emitted['centers'], expected_centers)
        assert np.allclose(emitted['radii'], expected_radii)


def test_wp18_blob_adapter_forces_skip_digestion_and_preserves_spheres():
    from molsysviewer_topomt.geometry import EntityRef, SphereGeometry
    from molsysviewer_topomt.render.adapters import add_pocket_blob

    calls = []
    view = types.SimpleNamespace(
        shapes=types.SimpleNamespace(
            add_pocket_blob=lambda **kwargs: calls.append(kwargs)
        )
    )
    geometry = SphereGeometry(
        ((0.0, 0.0, 0.0),),
        (2.0,),
        unit='angstroms',
        refs=(EntityRef(kind='tetrahedron', entity_id=0),),
    )

    add_pocket_blob(view, geometry, skip_digestion=False)

    assert calls[0]['skip_digestion'] is True
    assert np.allclose(
        puw.get_value(calls[0]['centers'], to_unit='angstroms'), geometry.centers
    )
    assert np.allclose(
        puw.get_value(calls[0]['radii'], to_unit='angstroms'), geometry.radii
    )


def test_wp18_cloud_emits_canonical_residence_sphere_geometry():
    from molsysviewer_topomt.geometry import component_residence_sphere_geometry
    from molsysviewer_topomt.render import show_dfnd_components

    topography = _build_dfnd_topo('hollow_sphere_void.pdb')
    component = topography.dfnd.dfn.components.wet[0]
    expected = component_residence_sphere_geometry(topography, component)
    view = DummyView()

    show_dfnd_components(
        view,
        topography,
        representation='cloud',
        component_ids=[component.component_id],
    )

    emitted = view.messages[-1]['options']
    # canonical geometry is nm; the emitted wire is the Mol* canvas (angstroms)
    expected_centers = puw.get_value(
        puw.quantity(np.asarray(expected.centers), 'nm'), to_unit='angstroms'
    )
    expected_radii = puw.get_value(
        puw.quantity(np.asarray(expected.radii), 'nm'), to_unit='angstroms'
    )
    assert np.allclose(emitted['centers'], expected_centers)
    assert np.allclose(emitted['radii'], expected_radii)


def test_wp18_envelope_mouth_cap_emits_canonical_face_geometry():
    from molsysviewer_topomt.geometry import face_geometry
    from molsysviewer_topomt.render import show_dfnd_components

    topography = _build_dfnd_topo('tube_channel_clean.pdb')
    component = next(
        comp for comp in topography.dfnd.dfn.components.wet if comp.family == 'pocket'
    )
    links = {
        link['external_link_id']: link for link in topography.dfnd.raw['external_links']
    }
    face_ids = [
        face_id
        for link_id in component.external_link_ids
        for face_id in links[link_id]['face_ids']
    ]
    expected = face_geometry(topography, face_ids=face_ids)
    view = DummyView()

    show_dfnd_components(
        view,
        topography,
        representation='envelope',
        component_ids=[component.component_id],
    )

    cap = next(
        message for message in view.messages if message['op'] == 'add_triangle_faces'
    )
    assert cap['options']['atom_triplets'] == [
        list(item) for item in expected.atom_triplets
    ]


def test_wp18_feature_geometry_carries_stable_feature_identity_and_nm_units():
    from molsysviewer_topomt.geometry import (
        feature_center_geometry,
        feature_sphere_geometry,
    )

    feature = {
        'feature_id': 'POC-7',
        'atom_indices': [1, 2, 3],
        'atom_index_space': 'molecular_system',
        'center': [0.1, 0.2, 0.3],
        'sphere_centers': [[0.1, 0.2, 0.3], [0.2, 0.3, 0.4]],
        'sphere_radii': [0.4, 0.5],
    }

    marker = feature_center_geometry(feature)
    blob = feature_sphere_geometry(feature)

    assert marker.unit == blob.unit == 'nm'
    assert marker.refs[0].kind == 'feature'
    assert marker.refs[0].entity_id == 'POC-7'
    assert tuple(ref.entity_id for ref in blob.refs) == ('POC-7', 'POC-7')
    assert blob.radii == (0.4, 0.5)


def test_wp18_centerline_and_ring_geometry_preserve_structural_identity():
    from molsysviewer_topomt.geometry import (
        component_branch_geometries,
        component_centerline_geometry,
        centerline_ring_geometry,
        mouth_ring_geometry,
    )

    topography = _build_dfnd_topo('tube_channel_clean.pdb')
    component = next(
        comp for comp in topography.dfnd.dfn.components.wet if comp.family == 'channel'
    )
    centerline, bottleneck_index = component_centerline_geometry(topography, component)
    rings = centerline_ring_geometry(topography, component)
    mouths = mouth_ring_geometry(topography, component)

    assert centerline.unit == rings.unit == mouths.unit == 'nm'
    assert len(centerline.centers) >= 2
    assert 0 <= bottleneck_index < len(centerline.centers)
    assert tuple(ref.entity_id for ref in centerline.refs) == tuple(
        ref.entity_id for ref in rings.refs
    )
    assert all(ref.kind == 'centerline_station' for ref in centerline.refs)
    assert all(ref.component_key == component.component_key for ref in centerline.refs)
    assert all(ref.kind == 'external_link' for ref in mouths.refs)
    assert {ref.entity_id for ref in mouths.refs} == set(component.external_link_keys)

    branched = _build_dfnd_topo('branched_tube_y.pdb')
    branched_component = next(
        comp for comp in branched.dfnd.dfn.components.wet if comp.family == 'channel'
    )
    branches = component_branch_geometries(branched, branched_component)
    assert len(branches) == branched_component.n_mouths - 2
    assert all(branch.unit == 'nm' for branch in branches)
    assert all(
        ref.kind == 'centerline_branch_station'
        for branch in branches
        for ref in branch.refs
    )
    assert all(
        ref.metadata and ref.metadata.get('path_kind') == 'secondary_branch_shortest_distance'
        for branch in branches
        for ref in branch.refs
    )


def test_wp18_scaffold_geometry_uses_canonical_global_atom_pairs():
    from molsysviewer_topomt.geometry import scaffold_geometry

    topography = _build_dfnd_topo('two_blocks_interface.pdb')
    component = topography.dfnd.dfn.components.dry[0]
    geometry = scaffold_geometry(topography, component)

    assert geometry.unit == 'nm'
    assert geometry.refs
    assert all(ref.kind == 'scaffold_edge' for ref in geometry.refs)
    assert all(
        tuple(sorted(ref.atom_indices)) == ref.atom_indices for ref in geometry.refs
    )
    assert all(ref.component_key == component.component_key for ref in geometry.refs)


def test_wp18_path_and_ring_adapters_force_skip_digestion():
    from molsysviewer_topomt.geometry import EntityRef, RingGeometry, SphereGeometry
    from molsysviewer_topomt.render.adapters import add_channel_tube, add_rings

    tube_calls = []
    ring_calls = []
    view = types.SimpleNamespace(
        shapes=types.SimpleNamespace(
            add_channel_tube=lambda **kwargs: tube_calls.append(kwargs),
            add_rings=lambda **kwargs: ring_calls.append(kwargs),
        )
    )
    refs = (
        EntityRef(kind='centerline_station', entity_id=1),
        EntityRef(kind='centerline_station', entity_id=2),
    )
    tube = SphereGeometry(
        ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
        (1.0, 0.8),
        unit='angstroms',
        refs=refs,
    )
    rings = RingGeometry(
        tube.centers,
        ((1.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
        tube.radii,
        unit='angstroms',
        refs=refs,
    )

    add_channel_tube(view, tube, skip_digestion=False)
    add_rings(view, rings, skip_digestion=False)

    assert tube_calls[0]['skip_digestion'] is True
    assert ring_calls[0]['skip_digestion'] is True
