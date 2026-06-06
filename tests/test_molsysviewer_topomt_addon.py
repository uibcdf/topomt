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
                'shape_name': 'Face id 1: tetrahedra 0-1; permeability=permeable',
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

    assert result['n_rendered'] == 2
    assert result['rendered'][0]['mode'] == 'blob'
    assert result['rendered'][1]['mode'] == 'marker'
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
            self.dfnd = types.SimpleNamespace(
                mesh=MockMesh(), dfn=MockDFN(), raw={'faces': [], 'tetrahedra': []}
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
    topo = types.SimpleNamespace(
        dfnd=types.SimpleNamespace(
            mesh=MockMesh(),
            dfn=types.SimpleNamespace(
                components=types.SimpleNamespace(wet=[component], dry=[])
            ),
            raw={'faces': [], 'tetrahedra': []},
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
    assert getattr(spheres_layer, 'tag') == 'dfnd-comp:WET-2'


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

    face_meta = _dfnd_face_meta(raw, {1}, colors_by_tetrahedron={1: 0x123456})

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
            raw={'faces': [], 'tetrahedra': []},
        )
    )
    from molsysviewer_topomt.render import show_dfnd_components

    residence_view = DummyView()
    show_dfnd_components(residence_view, topo, representation='residence_spheres')
    assert residence_view.messages[-1]['options']['alpha_spheres'][
        'radii'
    ] == pytest.approx([2.5])

    alpha_view = DummyView()
    show_dfnd_components(alpha_view, topo, representation='alpha_spheres')
    assert alpha_view.messages[-1]['options']['alpha_spheres'][
        'radii'
    ] == pytest.approx([7.5])

    probe_view = DummyView()
    show_dfnd_components(
        probe_view,
        topo,
        representation='probe_centers',
        use_resident_nodes=False,
    )
    assert probe_view.messages[-1]['op'] == 'add_sphere'
    assert probe_view.messages[-1]['options']['radius'] == pytest.approx(1.4)
    assert probe_view.messages[-1]['options']['center'] == pytest.approx(
        [0.25, 0.25, 0.25]
    )

    graph = show_dfnd_components(DummyView(), topo, representation='graph')
    skeleton = show_dfnd_components(DummyView(), topo, representation='skeleton')
    assert graph['n_nodes'] == skeleton['n_nodes'] == 1


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
        / 'topomt' / 'data' / 'synthetic' / 'tube_channel_clean.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_arrays(coords, np.full(len(coords), 1.88), epsilon=1e-7)
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
        / 'topomt' / 'data' / 'synthetic' / 'two_blocks_interface.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_arrays(coords, np.full(len(coords), 1.88), epsilon=1e-7)
    result = net.get_topography(probe_radius=1.4, min_size=0)
    dfnd = DFNDData(net, result)
    topo = SimpleNamespace(dfnd=dfnd)

    # there must be an interface wet component lined by two dry bodies
    assert dfnd.dfn.components.wet_interfaces

    view = DummyView()
    layer = show_dfnd_components(
        view, topo, representation='contact_sheet', interfaces_only=True,
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
        / 'topomt' / 'data' / 'synthetic' / 'tube_channel_clean.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_arrays(coords, np.full(len(coords), 1.88), epsilon=1e-7)
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
    assert [c.component_id for c in comp_mod._rank_by_volume(comps, None)] == ['A', 'B', 'C']
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
        / 'topomt' / 'data' / 'synthetic' / 'tube_channel_clean.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_arrays(coords, np.full(len(coords), 1.88), epsilon=1e-7)
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
        / 'topomt' / 'data' / 'synthetic' / 'two_blocks_interface.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_arrays(coords, np.full(len(coords), 1.88), epsilon=1e-7)
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
        / 'topomt' / 'data' / 'synthetic' / 'tube_channel_clean.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_arrays(coords, np.full(len(coords), 1.88), epsilon=1e-7)
    result = net.get_topography(probe_radius=1.4, min_size=0)
    topo = SimpleNamespace(dfnd=DFNDData(net, result))

    view = DummyView()
    layer = show_dfnd_components(view, topo, representation='rings', component_types=('channel',))
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
    assert comp_mod._hole_clearance_color(0.9) == comp_mod._HOLE_CLOSED  # < 1.15
    assert comp_mod._hole_clearance_color(1.3) == comp_mod._HOLE_TIGHT   # 1.15..1.5
    assert comp_mod._hole_clearance_color(2.0) == comp_mod._HOLE_OPEN    # >= 1.5


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
        / 'topomt' / 'data' / 'synthetic' / 'hollow_sphere_void.pdb'
    )
    coords = np.array(
        [
            [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            for line in pdb.read_text().splitlines()
            if line.startswith(('ATOM', 'HETATM'))
        ]
    )
    net = DelaunayFlowNetwork.from_arrays(coords, np.full(len(coords), 1.88), epsilon=1e-7)
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


def test_show_dfnd_components_rejects_unknown_representation():
    from molsysviewer_topomt.render import show_dfnd_components

    component = types.SimpleNamespace(
        component_id="WET-1", family="void", side="wet", node_indices=[0]
    )
    topography = types.SimpleNamespace(
        dfnd=types.SimpleNamespace(
            dfn=types.SimpleNamespace(
                components=types.SimpleNamespace(wet=[component], dry=[])
            )
        )
    )

    with pytest.raises(ValueError, match="Unknown representation"):
        show_dfnd_components(DummyView(), topography, representation="unknown")


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
    network = DelaunayFlowNetwork.from_arrays(coords, np.full(4, 1.88), epsilon=1e-7)
    result = network.get_topography(probe_radius=1.0, min_size=0)
    topography = SimpleNamespace(dfnd=DFNDData(network, result))

    view = DummyView()
    layer = show_dfnd_components(
        view, topography, representation="probe_centers", component_types=None
    )

    assert layer is not None
    assert view.messages[-1]["options"]["radius"] == pytest.approx(1.0)


def _graph_render_topography():
    tetrahedron_ids = [0, 1, 3, 10]
    coords = []
    tetrahedra = []
    for tetrahedron_id in tetrahedron_ids:
        start = len(coords)
        coords.extend([[float(tetrahedron_id), 0.0, 0.0]] * 4)
        tetrahedra.append(
            {
                "tetrahedron_id": tetrahedron_id,
                "local_atom_indices": list(range(start, start + 4)),
            }
        )
    component = types.SimpleNamespace(
        component_id="WET-1",
        family="void",
        side="wet",
        node_indices=tetrahedron_ids,
        resident_node_indices=tetrahedron_ids,
        volume=1.0,
    )
    nodes = [
        {
            "tetrahedron_id": tetrahedron_id,
            "residence_state": "resident",
            "n_permeable_contacts": 0,
            "combined_class": "wet_sealed",
        }
        for tetrahedron_id in tetrahedron_ids
    ]
    return types.SimpleNamespace(
        dfnd=types.SimpleNamespace(
            mesh=types.SimpleNamespace(
                atoms=types.SimpleNamespace(coords=np.asarray(coords)),
                tetrahedra=tetrahedra,
                faces=[],
            ),
            dfn=types.SimpleNamespace(
                components=types.SimpleNamespace(wet=[component], dry=[]),
                graph=types.SimpleNamespace(nodes=nodes, faces=[]),
            ),
            raw={"faces": [], "tetrahedra": []},
        )
    )


def test_component_graph_emits_nodes_in_tetrahedron_id_order():
    from molsysviewer_topomt.render import show_dfnd_components

    view = DummyView()
    show_dfnd_components(view, _graph_render_topography(), representation="graph")

    centers = [
        message["options"]["center"]
        for message in view.messages
        if message["op"] == "add_sphere"
    ]
    assert np.asarray(centers)[:, 0].tolist() == [0.0, 1.0, 3.0, 10.0]


def test_show_dfn_graph_can_render_twice_with_same_tag_prefix():
    from molsysviewer_topomt.render import show_dfn_graph

    view = DummyView()
    topography = _graph_render_topography()

    first = show_dfn_graph(view, topography, tag_prefix="repeat-graph")
    second = show_dfn_graph(view, topography, tag_prefix="repeat-graph")

    assert first["n_nodes"] == second["n_nodes"] == 4
    cleared_tags = {
        message["tag"]
        for message in view.messages
        if message["op"] == "clear_shapes_by_tag"
    }
    assert {"repeat-graph-node", "repeat-graph-edges", "repeat-graph-mouths"} <= cleared_tags


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
    net = DelaunayFlowNetwork.from_arrays(coords, np.full(len(coords), 1.88), epsilon=1e-7)
    result = net.get_topography(probe_radius=probe, min_size=0)
    return SimpleNamespace(dfnd=DFNDData(net, result))


def test_envelope_pocket_has_blob_and_one_mouth_ring():
    """Phase 1: a pocket renders a blob + one gate ring; a void only the blob."""
    from molsysviewer_topomt.render import show_dfnd_components

    pocket_topo = _build_dfnd_topo('hollow_sphere_pocket.pdb')
    view = DummyView()
    show_dfnd_components(view, pocket_topo, representation='envelope',
                         component_types=('pocket',))
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
    show_dfnd_components(view, void_topo, representation='envelope',
                         component_types=('void',))
    ops = [m['op'] for m in view.messages]
    assert 'add_pocket_blob' in ops  # the volume
    assert 'add_rings' not in ops  # a void has no mouths
