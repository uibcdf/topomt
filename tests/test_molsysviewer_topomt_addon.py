import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import molsysviewer
import numpy as np
import pytest
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
from molsysviewer_topomt.render import render_topography_pockets
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

    lifecycle.on_context_action(view, 'dfnd-tetrahedron-info', {'context': {}})

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
                'shape_name': 'Face 1: tetrahedra 0-1; permeability=permeable',
            }
        ]
    )

    lifecycle.on_context_action(view, 'dfnd-tetrahedron-info', {'context': {}})

    assert calls == [[0, 1]]


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
        self._layer_counter = 0
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


def test_render_topography_pockets_uses_blob_and_marker_modes():
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
    result = render_topography_pockets(view, topo)

    assert result['n_rendered'] == 2
    assert result['rendered'][0]['mode'] == 'blob'
    assert result['rendered'][1]['mode'] == 'marker'
    assert view.messages[0]['op'] == 'add_pocket_blob'
    assert view.messages[1]['op'] == 'add_sphere'


def test_render_topography_pockets_accepts_quantity_backed_features():
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
    result = render_topography_pockets(view, topo)

    assert result['n_rendered'] == 1
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
    assert result['rendered']['n_rendered'] == 1
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
    assert result['rendered']['n_rendered'] == 1
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

    assert result['rendered']['n_rendered'] == 1
    assert result['selected_feature_ids'] == ['POC-2']
    assert result['rendered']['rendered'][0]['feature_id'] == 'POC-2'


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

    assert result['rendered']['n_rendered'] == 1
    assert result['selected_feature_ids'] == ['POC-1']
    assert result['rendered']['rendered'][0]['feature_id'] == 'POC-1'


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
    assert captured['build_view']['kwargs']['render'] is True
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
    assert captured['build_view']['render'] is False
    assert captured['attach_features']['view'] is view
    assert captured['attach_features']['feature_ids'] == ['POC-2']


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


def test_render_dfnd_tetrahedra_creates_shapes():
    # Build simulated dfnd_records
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
        ]
    }

    view = DummyView()

    # Test default mode (combined_class)
    from molsysviewer_topomt.render import render_dfnd_tetrahedra

    layer = render_dfnd_tetrahedra(view, dfnd_records)

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


def test_render_dfnd_tetrahedra_with_custom_indices():
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
    from molsysviewer_topomt.render import render_dfnd_tetrahedra

    layer = render_dfnd_tetrahedra(view, dfnd_records, tetrahedra_indices=[0, 2])

    assert layer is not None
    assert len(view.messages) == 2
    msg = view.messages[1]
    assert msg['op'] == 'add_tetrahedra'
    # Should only contain 2 tetrahedra, not 3
    assert len(msg['options']['atom_quads']) == 2
    assert msg['options']['atom_quads'] == [[10, 11, 12, 13], [30, 31, 32, 33]]


def test_attach_dfnd_tetrahedra_with_click_callback():
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

        def on_click(self, cb):
            self.click_callbacks.append(cb)

        def off_click(self, cb):
            if cb in self.click_callbacks:
                self.click_callbacks.remove(cb)

    view = ClickableDummyView()
    from molsysviewer_topomt.integration import attach_dfnd_tetrahedra

    result = attach_dfnd_tetrahedra(view, dfnd_records, tetrahedra_indices=[0])

    assert result['layer'] is not None
    assert len(view.click_callbacks) == 1
    cb = view.click_callbacks[0]

    # Verify that calling attach_dfnd_tetrahedra again does not double-register the callback
    attach_dfnd_tetrahedra(view, dfnd_records, tetrahedra_indices=[0])
    assert len(view.click_callbacks) == 1

    # Simulate triggering of click callback
    # Triggers with mismatched event -> ignored
    cb({'kind': 'structure'})
    # Triggers with matched event, but no topography -> ignored
    cb(
        {
            'kind': 'shape',
            'tag': 'dfnd-tetra',
            'shape_name': 'Tetrahedron 0: combined_class=wet_sealed, role=resident_transit, R_res=2.15 Å',
        }
    )


def test_render_dfn_dry_components_filters_dry_faces_by_permeability():
    dfnd_records = {
        'tetrahedra': [
            {
                'tetrahedron_id': 0,
                'local_atom_indices': [10, 11, 12, 13],
                'residence_state': 'non_resident',
            },
            {
                'tetrahedron_id': 1,
                'local_atom_indices': [20, 21, 22, 23],
                'residence_state': 'resident',
            },
        ],
        'faces': [
            {
                'face_id': 1,
                'owner_tetrahedron_id': 0,
                'neighbor_tetrahedron_id': 1,
                'face_index': 2,
                'face_atoms_local': [10, 11, 12],
                'permeability_state': 'permeable',
                'R_gate': 1.8,
            },
            {
                'face_id': 2,
                'owner_tetrahedron_id': 0,
                'face_atoms_local': [10, 11, 13],
                'permeability_state': 'non_permeable',
                'R_gate': 0.8,
            },
            {
                'face_id': 3,
                'owner_tetrahedron_id': 1,
                'face_atoms_local': [20, 21, 22],
                'permeability_state': 'permeable',
                'R_gate': 2.0,
            },
        ],
    }

    view = DummyView()
    from molsysviewer_topomt.render import render_dfn_dry_components

    result = render_dfn_dry_components(
        view,
        dfnd_records,
        draw_faces=True,
        draw_edges=True,
        draw_impermeable_faces=False,
        draw_permeable_faces=True,
    )

    assert result['n_tetrahedra'] == 1
    assert result['n_faces'] == 1
    assert [msg['op'] for msg in view.messages] == [
        'clear_shapes_by_tag',
        'clear_shapes_by_tag',
        'clear_shapes_by_tag',
        'add_tetrahedra',
        'add_triangle_faces',
    ]
    assert [msg['tag'] for msg in view.messages[:3]] == [
        'dfn-dry',
        'dfn-dry-edges',
        'dfn-dry-faces',
    ]

    edge_msg = view.messages[3]
    assert edge_msg['options']['atom_quads'] == [[10, 11, 12, 13]]
    assert edge_msg['options']['draw_faces'] is False
    assert edge_msg['options']['draw_edges'] is True
    assert 'Tetrahedron 0' in edge_msg['options']['labels'][0]

    face_msg = view.messages[4]
    assert face_msg['options']['atom_triplets'] == [[10, 11, 12]]
    label = face_msg['options']['labels'][0]
    assert 'Face 1' in label
    assert 'tetrahedra 0-1' in label
    assert 'owner_face_index=2' in label
    assert 'permeability=permeable' in label
    assert 'R_gate=1.80 Å' in label


def test_render_dfn_dry_components_uses_explicit_face_vertices_when_available():
    raw = {
        'tetrahedra': [
            {
                'tetrahedron_id': 0,
                'local_atom_indices': [0, 1, 2, 3],
                'residence_state': 'non_resident',
            },
        ],
        'faces': [
            {
                'face_id': 1,
                'owner_tetrahedron_id': 0,
                'neighbor_tetrahedron_id': -1,
                'face_index': 0,
                'face_atoms_local': [0, 1, 2],
                'permeability_state': 'permeable',
                'R_gate': 1.8,
            },
        ],
    }
    dfnd = types.SimpleNamespace(
        raw=raw,
        mesh=types.SimpleNamespace(
            atoms=types.SimpleNamespace(
                coords=np.asarray(
                    [
                        [0.0, 0.0, 0.0],
                        [1.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0],
                        [0.0, 0.0, 1.0],
                    ],
                    dtype=float,
                )
            )
        ),
    )
    topography = types.SimpleNamespace(dfnd=dfnd)

    view = DummyView()
    from molsysviewer_topomt.render import render_dfn_dry_components

    result = render_dfn_dry_components(
        view,
        topography,
        draw_faces=True,
        draw_edges=False,
        draw_permeable_faces=True,
        draw_impermeable_faces=False,
    )

    assert result is not None
    face_msg = view.messages[3]
    assert face_msg['op'] == 'add_triangle_faces'
    assert 'vertices' in face_msg['options']
    assert 'atom_triplets' not in face_msg['options']
    assert face_msg['options']['vertices'] == [
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    ]
    assert 'tetrahedra 0-OCEAN' in face_msg['options']['labels'][0]


def test_render_dfn_dry_components_can_select_dry_components():
    dfnd_result = {
        'raw': {
            'tetrahedra': [
                {
                    'tetrahedron_id': 0,
                    'local_atom_indices': [10, 11, 12, 13],
                    'residence_state': 'non_resident',
                },
                {
                    'tetrahedron_id': 1,
                    'local_atom_indices': [20, 21, 22, 23],
                    'residence_state': 'non_resident',
                },
            ],
            'faces': [
                {
                    'face_id': 1,
                    'owner_tetrahedron_id': 0,
                    'face_atoms_local': [10, 11, 12],
                    'permeability_state': 'permeable',
                    'R_gate': 1.8,
                },
                {
                    'face_id': 2,
                    'owner_tetrahedron_id': 1,
                    'face_atoms_local': [20, 21, 22],
                    'permeability_state': 'permeable',
                    'R_gate': 2.0,
                },
            ],
        },
        'dry': {
            'components': [
                {
                    'id': 1,
                    'tetrahedron_indices': [0],
                    'atom_indices': [10, 11, 12, 13],
                },
                {
                    'id': 2,
                    'tetrahedron_indices': [1],
                    'atom_indices': [20, 21, 22, 23],
                },
            ],
        },
    }

    view = DummyView()
    from molsysviewer_topomt.render import render_dfn_dry_components

    result = render_dfn_dry_components(
        view,
        dfnd_result,
        component_ids='DRY-2',
        draw_faces=True,
        draw_edges=True,
        draw_permeable_faces=True,
    )

    assert result['n_tetrahedra'] == 1
    assert result['n_faces'] == 1
    assert view.messages[3]['options']['atom_quads'] == [[20, 21, 22, 23]]
    assert view.messages[4]['options']['atom_triplets'] == [[20, 21, 22]]


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

    # Renders BOTH pockets and tetrahedra when render_tetrahedra=True
    view = DummyView()
    res = attach_topography(view, topo, render_tetrahedra=True)
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

    # 2. Action: render_tetrahedra
    panel.handle_action(view, 'render_tetrahedra', {})
    assert len(view.messages) == 3
    assert view.messages[1]['op'] == 'clear_shapes_by_tag'
    assert view.messages[2]['op'] == 'add_tetrahedra'

    # 3. Action: clear_pockets (clears both pockets and tetrahedra)
    panel.handle_action(view, 'clear_pockets', {})
    clear_ops = [msg for msg in view.messages if msg.get('op') == 'clear_shapes_by_tag']
    # There should be clear operations for pocket tag and dfnd-tetra tag
    assert len(clear_ops) == 3
    tags_cleared = {msg['tag'] for msg in clear_ops}
    assert 'topomt-pocket:POC-1' in tags_cleared
    assert 'dfnd-tetra' in tags_cleared


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
        ValueError, match="topography does not have a '_molsys' attribute"
    ):
        new_view(BadTopography())
