import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import molsysviewer
import numpy as np
import pytest
import topomt as tmt
from molsysviewer.shapes import ShapesManager
from topomt import pyunitwizard as puw

from molsysviewer_topomt import get_addon
from molsysviewer_topomt.addon import lifecycle
from molsysviewer_topomt.integration import (
    attach_features,
    attach_pockets,
    attach_topography,
    build_view_with_topography,
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

    lifecycle.on_context_action(view, 'focus-topography-feature', {'feature_id': 'POC-1'})
    assert view._topomt_addon_runtime.last_context_action['action_id'] == 'focus-topography-feature'

    lifecycle.on_disable(view)
    assert view._topomt_addon_runtime.enabled is False


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

    def load(self, molecular_system, *, selection='all', structure_indices='all', syntax='MolSysMT', skip_digestion=False, **kwargs):
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


def test_build_view_with_topography_uses_molsysviewer_factory(monkeypatch):
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

    def fake_new_view(molecular_system, **kwargs):
        view.load(molecular_system, **kwargs)
        return view

    monkeypatch.setattr(molsysviewer, 'new_view', fake_new_view)

    result_view = build_view_with_topography('system', topo, selection='all')

    assert result_view is view
    assert view.load_calls[0]['molecular_system'] == 'system'
    assert view.messages[0]['op'] == 'add_sphere'


def test_subset_topography_keeps_only_requested_features():
    topo = tmt.Topography()
    topo.add_new_feature(feature_type='pocket', feature_id='POC-1', atom_indices=[1], center=[0.0, 0.0, 0.0])
    topo.add_new_feature(feature_type='pocket', feature_id='POC-2', atom_indices=[2], center=[1.0, 1.0, 1.0])

    subset = subset_topography(topo, ['POC-2'])

    assert list(subset.features.keys()) == ['POC-2']


def test_attach_features_renders_only_selected_feature_ids():
    topo = tmt.Topography()
    topo.add_new_feature(feature_type='pocket', feature_id='POC-1', atom_indices=[1], center=[0.0, 0.0, 0.0])
    topo.add_new_feature(feature_type='pocket', feature_id='POC-2', atom_indices=[2], center=[1.0, 1.0, 1.0])

    view = DummyView()
    register_with_molsysviewer()
    result = attach_features(view, topo, feature_ids=['POC-2'])

    assert result['rendered']['n_rendered'] == 1
    assert result['selected_feature_ids'] == ['POC-2']
    assert result['rendered']['rendered'][0]['feature_id'] == 'POC-2'


def test_attach_pockets_is_a_pocket_named_wrapper():
    topo = tmt.Topography()
    topo.add_new_feature(feature_type='pocket', feature_id='POC-1', atom_indices=[1], center=[0.0, 0.0, 0.0])
    topo.add_new_feature(feature_type='pocket', feature_id='POC-2', atom_indices=[2], center=[1.0, 1.0, 1.0])

    view = DummyView()
    register_with_molsysviewer()
    result = attach_pockets(view, topo, pocket_ids=['POC-1'])

    assert result['rendered']['n_rendered'] == 1
    assert result['selected_feature_ids'] == ['POC-1']
    assert result['rendered']['rendered'][0]['feature_id'] == 'POC-1'


def test_build_topography_standalone0_html_uses_viewer_host_and_registers_addon(monkeypatch, tmp_path):
    topo = tmt.Topography()
    topo.add_new_feature(feature_type='pocket', feature_id='POC-1', atom_indices=[1], center=[0.0, 0.0, 0.0])

    view = DummyView()
    captured = {}

    def fake_build_view_with_topography(molecular_system, topography, **kwargs):
        captured['build_view'] = {
            'molecular_system': molecular_system,
            'topography': topography,
            'kwargs': kwargs,
        }
        view.load(molecular_system, **kwargs)
        return view

    def fake_build_standalone0_html(view_arg, output_filename, **kwargs):
        captured['build_html'] = {
            'view': view_arg,
            'output_filename': output_filename,
            'kwargs': kwargs,
        }
        return str(Path(output_filename).resolve())

    monkeypatch.setattr('molsysviewer_topomt.standalone.build_view_with_topography', fake_build_view_with_topography)
    monkeypatch.setattr(molsysviewer, 'build_standalone0_html', fake_build_standalone0_html)

    outfile = tmp_path / 'topomt-standalone.html'
    result = build_topography_standalone0_html('system', str(outfile), topography=topo)

    assert result == str(outfile.resolve())
    assert captured['build_view']['molecular_system'] == 'system'
    assert captured['build_view']['kwargs']['render'] is True
    assert captured['build_html']['view'] is view
    assert captured['build_html']['kwargs']['addon_modules'][0] == 'molsysviewer_topomt'


def test_build_topography_standalone0_html_can_render_only_selected_features(monkeypatch, tmp_path):
    topo = tmt.Topography()
    topo.add_new_feature(feature_type='pocket', feature_id='POC-1', atom_indices=[1], center=[0.0, 0.0, 0.0])
    topo.add_new_feature(feature_type='pocket', feature_id='POC-2', atom_indices=[2], center=[1.0, 1.0, 1.0])

    view = DummyView()
    captured = {}

    def fake_build_view_with_topography(molecular_system, topography, **kwargs):
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

    monkeypatch.setattr('molsysviewer_topomt.standalone.build_view_with_topography', fake_build_view_with_topography)
    monkeypatch.setattr('molsysviewer_topomt.standalone.attach_features', fake_attach_features)
    monkeypatch.setattr(molsysviewer, 'build_standalone0_html', fake_build_standalone0_html)

    outfile = tmp_path / 'topomt-selected.html'
    result = build_topography_standalone0_html('system', str(outfile), topography=topo, feature_ids=['POC-2'])

    assert result == str(outfile.resolve())
    assert captured['build_view']['render'] is False
    assert captured['attach_features']['view'] is view
    assert captured['attach_features']['feature_ids'] == ['POC-2']


def test_launch_topography_standalone0_can_compute_topography_and_open_host(monkeypatch):
    topo = tmt.Topography()
    topo.add_new_feature(feature_type='pocket', feature_id='POC-1', atom_indices=[1], center=[0.0, 0.0, 0.0])

    view = DummyView()
    captured = {}

    def fake_get_topography(molecular_system, **kwargs):
        captured['get_topography'] = {
            'molecular_system': molecular_system,
            'kwargs': kwargs,
        }
        return topo

    def fake_build_view_with_topography(molecular_system, topography, **kwargs):
        captured['build_view'] = {
            'molecular_system': molecular_system,
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
    monkeypatch.setattr('molsysviewer_topomt.standalone.build_view_with_topography', fake_build_view_with_topography)
    monkeypatch.setattr(molsysviewer, 'launch_standalone0', fake_launch_standalone0)

    result = launch_topography_standalone0('system', method='pocketeer', open_browser=False)

    assert result == '/tmp/topomt-launch.html'
    assert captured['get_topography']['molecular_system'] == 'system'
    assert captured['get_topography']['kwargs']['method'] == 'pocketeer'
    assert captured['launch']['view'] is view
    assert captured['launch']['kwargs']['addon_modules'][0] == 'molsysviewer_topomt'
    assert captured['launch']['kwargs']['open_browser'] is False
