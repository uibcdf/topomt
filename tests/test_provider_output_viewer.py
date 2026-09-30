"""Observable viewer adoption of original provider pocket evidence."""

import copy
import importlib
import shutil
import zipfile
from pathlib import Path

import molsysviewer
import numpy as np
import pytest

import molsysviewer_topomt as addon
import topomt as tmt
from molsysviewer_topomt.panels import TopoMTPocketsPanel, TopoMTTopographyPanel
from molsysviewer_topomt.runtime import ensure_runtime
from topomt import pyunitwizard as puw
from topomt.third_party.output import PocketGeometry, ProviderRecord

ROOT = Path(tmt.__file__).parent
PDB = ROOT / 'data/fpocket4/sample/3LKF.pdb'
OUT = ROOT / 'data/fpocket4/sample/3LKF_out'


@pytest.fixture
def view(monkeypatch):
    viewer = molsysviewer.MolSysView()
    messages = []
    original_send = viewer._send

    def capture(message):
        messages.append(copy.deepcopy(message))
        return original_send(message)

    monkeypatch.setattr(viewer, '_send', capture)
    viewer.test_messages = messages
    return viewer


@pytest.fixture(scope='module')
def fpocket_output():
    return tmt.get_provider_output(
        PDB, method='fpocket', backend='files', pdb_file=PDB, output_dir=OUT
    )


def test_fpocket_viewer_preserves_original_spheres_and_identity(view, fpocket_output):
    attached = addon.attach_provider_output(view, fpocket_output)
    runtime = ensure_runtime(view)
    assert runtime.provider_outputs[fpocket_output.run.run_id] is fpocket_output
    assert runtime.topography is None
    assert getattr(view, 'topography', None) is None
    rendered = attached['rendered']
    assert rendered.rendered_ids == tuple(p.source_id for p in fpocket_output.pockets)
    assert len(rendered.layers) == 7
    assert all(view.shapes.contains(tag) for tag in rendered.tags)
    messages = [m for m in view.test_messages if m['op'] == 'add_alpha_sphere_set']
    assert len(messages) == 7
    geometry = fpocket_output.pockets[0].geometries['alpha_spheres']
    assert np.allclose(
        messages[0]['options']['alpha_spheres']['centers'],
        puw.get_value(geometry.coordinates, to_unit='angstroms'),
    )
    assert np.allclose(
        messages[0]['options']['alpha_spheres']['radii'],
        puw.get_value(geometry.radii, to_unit='angstroms'),
    )
    first = rendered.details['rendered'][0]
    assert first['provider'] == 'fpocket'
    assert first['run_id'] == fpocket_output.run.run_id
    assert first['source_id'] == 'fpocket:1'
    assert first['geometry_kind'] == 'alpha_spheres'
    assert first['definition'] == geometry.definition


def test_repeated_provider_render_and_clear_preserve_unrelated_shape(
    view, fpocket_output
):
    unrelated = view.shapes.spheres.add_sphere(
        center=puw.quantity([0.0, 0.0, 0.0], 'nm'),
        radius=puw.quantity(0.1, 'nm'),
        tag='unrelated',
        skip_digestion=True,
    )
    first = addon.show_provider_pockets(view, fpocket_output)
    second = addon.show_provider_pockets(view, fpocket_output, pocket_ids=['fpocket:2'])
    assert second.rendered_ids == ('fpocket:2',)
    assert not view.shapes.contains(first.tags[0])
    assert view.shapes.get('unrelated') is unrelated
    assert addon.clear_provider_pockets(view, fpocket_output)
    assert view.shapes.tags() == ['unrelated']
    assert not addon.clear_provider_pockets(view, fpocket_output)


def test_provider_runs_coexist_without_overwriting_topography(view, fpocket_output):
    castp = tmt.get_provider_output(
        method='castp',
        backend='files',
        zip_file=ROOT / 'data/CASTp_3.0_server/1tcd.zip',
    )
    topography = tmt.Topography()
    addon.attach_topography(view, topography, show=False)
    first = addon.attach_provider_output(view, fpocket_output)['rendered']
    second = addon.attach_provider_output(view, castp)['rendered']
    runtime = ensure_runtime(view)
    assert runtime.topography is topography and view.topography is topography
    assert len(runtime.provider_outputs) == 2
    assert runtime.active_provider_run_id == castp.run.run_id
    assert len(second.selected_ids) == 78
    assert len(second.layers) == 78
    assert all(
        item['geometry_kind'] == 'member_atoms' for item in second.details['rendered']
    )
    assert set(first.tags).isdisjoint(second.tags)
    addon.clear_provider_pockets(view, castp)
    assert all(view.shapes.contains(tag) for tag in first.tags)


@pytest.mark.parametrize(
    'panel_class,action',
    [
        (TopoMTPocketsPanel, 'show_all_pockets'),
        (TopoMTTopographyPanel, 'render_pockets'),
    ],
)
def test_provider_panel_show_select_and_clear(
    view, fpocket_output, monkeypatch, panel_class, action
):
    addon.attach_provider_output(view, fpocket_output, show=False)
    panel = panel_class()
    states = []
    monkeypatch.setattr(panel, 'push_state', states.append)
    panel.on_mount(view)
    assert states[-1]['source_kind'] == 'provider_output'
    assert states[-1]['provider'] == 'fpocket'
    assert states[-1]['run_id'] == fpocket_output.run.run_id
    assert len(states[-1]['pockets']) == 7
    assert states[-1]['has_dfnd'] is False
    panel.handle_action(view, action, {})
    assert states[-1]['status'] == 'done' and len(view.shapes.tags()) == 7
    panel.handle_action(view, 'show_pocket', {'feature_id': 'fpocket:2'})
    assert states[-1]['status'] == 'done' and len(view.shapes.tags()) == 1
    panel.handle_action(view, 'clear_pockets', {})
    assert states[-1]['status'] == 'idle' and not view.shapes.tags()
    assert fpocket_output.pockets[0].measurements


def test_castp_panel_lists_pocket_rows_not_auxiliary_mouths(view):
    output = tmt.get_provider_output(
        method='castp',
        backend='files',
        zip_file=ROOT / 'data/CASTp_3.0_server/1tcd.zip',
    )
    addon.attach_provider_output(view, output, show=False)
    state = TopoMTPocketsPanel._build_state(ensure_runtime(view))
    assert len(state['pockets']) == 78
    assert all(p['source_id'].startswith('Pocket ') for p in state['pockets'])


def test_missing_geometry_is_reported_without_fabricated_marker(view, fpocket_output):
    record = ProviderRecord(
        'empty',
        'pocket',
        fpocket_output.run,
        _fields={'volume': 1000.0, 'center': [1.0, 2.0, 3.0]},
    )
    output = type(fpocket_output)(fpocket_output.run, (record,))
    rendered = addon.show_provider_pockets(view, output)
    assert rendered.selected_ids == ('empty',)
    assert rendered.is_empty and rendered.warnings
    assert rendered.details['unavailable_ids'] == ('empty',)
    assert not view.shapes.tags()


def test_invalid_selection_preserves_existing_render(view, fpocket_output):
    rendered = addon.show_provider_pockets(view, fpocket_output)
    with pytest.raises(ValueError, match='Unknown provider pocket'):
        addon.show_provider_pockets(view, fpocket_output, pocket_ids=['missing'])
    assert all(view.shapes.contains(tag) for tag in rendered.tags)
    with pytest.raises(ValueError, match='representation'):
        addon.show_provider_pockets(view, fpocket_output, representation='exact_region')
    assert all(view.shapes.contains(tag) for tag in rendered.tags)


def test_empty_selection_clears_previous_provider_render(view, fpocket_output):
    addon.attach_provider_output(view, fpocket_output)
    result = addon.show_provider_pockets(view, pocket_ids=[])
    assert result.is_empty and result.selected_ids == ()
    assert not view.shapes.tags()


def test_real_fpocket_cli_output_renders_in_viewer(view):
    if shutil.which('fpocket') is None:
        pytest.skip('Optional fpocket executable unavailable')
    output = tmt.get_provider_output(PDB, method='fpocket')
    result = addon.attach_provider_output(view, output)['rendered']
    assert result.rendered_ids == tuple(p.source_id for p in output.pockets)
    assert output.run.backend == 'cli'
    assert result.layers and output.run.artifacts


@pytest.mark.parametrize('provider', ['pocketeer', 'alphaspace2', 'pycasta'])
def test_installed_original_library_output_renders_in_viewer(view, provider, tmp_path):
    if importlib.util.find_spec(provider) is None:
        pytest.skip(f'Optional original {provider} engine unavailable')
    pdb = tmp_path / '2pk4.pdb'
    with zipfile.ZipFile(ROOT / 'data/CASTpFold_server/2pk4.zip') as archive:
        pdb.write_bytes(archive.read('2pk4.pdb'))
    output = tmt.get_provider_output(pdb, method=provider)
    result = addon.attach_provider_output(view, output)['rendered']
    assert output.run.backend == 'library'
    assert result.rendered_ids == tuple(p.source_id for p in output.pockets)
    assert result.layers and not result.warnings


def test_existing_direct_render_cleanup_uses_public_shapes(view):
    topography = tmt.Topography()
    topography.add_new_feature(
        feature_type='pocket', feature_id='POC-1', center=[0.0, 0.0, 0.0]
    )
    first = addon.show_topography_pockets(view, topography)
    second = addon.show_topography_pockets(view, topography)
    assert first.tags == second.tags
    assert len(view.shapes.tags()) == 1


def test_clear_preserves_replacement_shape_reusing_an_old_owned_tag(
    view, fpocket_output
):
    rendered = addon.show_provider_pockets(
        view, fpocket_output, pocket_ids=['fpocket:1']
    )
    tag = rendered.tags[0]
    view.shapes.clear(tag=tag)
    replacement = view.shapes.spheres.add_sphere(
        center=puw.quantity([0.0, 0.0, 0.0], 'nm'),
        radius=puw.quantity(0.1, 'nm'),
        tag=tag,
        skip_digestion=True,
    )
    addon.clear_provider_pockets(view, fpocket_output)
    assert view.shapes.get(tag) is replacement


@pytest.mark.parametrize('panel_class', [TopoMTPocketsPanel, TopoMTTopographyPanel])
def test_panel_state_query_and_already_mounted_refresh(
    view, fpocket_output, panel_class, monkeypatch
):
    panel = panel_class(view=view)
    sent = []
    monkeypatch.setattr(panel, 'send', sent.append)
    panel.on_mount(view)
    sent.clear()
    addon.attach_provider_output(view, fpocket_output, show=False)
    assert sent[-1]['type'] == 'state'
    assert sent[-1]['state']['run_id'] == fpocket_output.run.run_id
    sent.clear()
    panel._route_topomt_query(panel, {'type': 'query', 'id': 'topomt.state'}, [])
    assert sent[-1]['state']['provider'] == 'fpocket'
    panel.on_unmount(view)
    sent.clear()
    addon.attach_provider_output(view, fpocket_output, show=False)
    assert not sent


def test_computed_empty_geometry_is_distinct_from_unavailable_geometry(
    view, fpocket_output
):
    record = ProviderRecord(
        'empty',
        'pocket',
        fpocket_output.run,
        _geometries=(
            PocketGeometry('alpha_spheres', (), 'Reported empty sphere set', ()),
        ),
    )
    output = type(fpocket_output)(fpocket_output.run, (record,))
    result = addon.show_provider_pockets(view, output, representation='alpha_spheres')
    assert result.is_empty and not result.warnings
    assert result.details['empty_ids'] == ('empty',)
    assert result.details['unavailable_ids'] == ()


def test_point_markers_preserve_member_coordinates_and_declared_display_radius(
    view, fpocket_output
):
    result = addon.show_provider_pockets(
        view,
        fpocket_output,
        pocket_ids=['fpocket:1'],
        representation='member_atoms',
        point_radius_nm=0.04,
    )
    geometry = fpocket_output.pockets[0].geometries['member_atoms']
    message = next(m for m in view.test_messages if m['op'] == 'add_alpha_sphere_set')
    assert np.allclose(
        message['options']['alpha_spheres']['centers'],
        puw.get_value(geometry.coordinates, to_unit='angstroms'),
    )
    assert message['options']['alpha_spheres']['radii'] == pytest.approx(
        [0.4] * len(geometry.points_nm)
    )
    assert result.details['rendered'][0]['mode'] == 'point_markers'
    assert geometry.radii is None


def test_failed_render_does_not_leave_partial_owned_layers(
    view, fpocket_output, monkeypatch
):
    original_add = view.shapes.spheres.add_set_alpha_spheres
    calls = []

    def add(**kwargs):
        calls.append(kwargs)
        if len(calls) == 2:
            raise RuntimeError('Injected second pocket failure')
        return original_add(**kwargs)

    monkeypatch.setattr(view.shapes.spheres, 'add_set_alpha_spheres', add)
    with pytest.raises(RuntimeError, match='second pocket'):
        addon.show_provider_pockets(view, fpocket_output)
    assert not view.shapes.tags()


def test_topography_attachment_switches_panel_source_without_losing_provider(
    view, fpocket_output
):
    addon.attach_provider_output(view, fpocket_output, show=False)
    topography = tmt.Topography()
    addon.attach_topography(view, topography, show=False)
    runtime = ensure_runtime(view)
    assert runtime.active_provider_run_id is None
    assert runtime.provider_outputs[fpocket_output.run.run_id] is fpocket_output
    state = TopoMTTopographyPanel._build_state(runtime)
    assert state['source_kind'] == 'topography' and state['provider'] is None


def test_provider_only_panel_rejects_tetrahedra_without_changing_scene(
    view, fpocket_output, monkeypatch
):
    attached = addon.attach_provider_output(view, fpocket_output)
    panel = TopoMTTopographyPanel()
    states = []
    monkeypatch.setattr(panel, 'push_state', states.append)
    panel.handle_action(view, 'render_tetrahedra', {})
    assert states[-1]['status'] == 'error'
    assert 'no DFND' in states[-1]['error']
    assert all(view.shapes.contains(tag) for tag in attached['rendered'].tags)


def test_loaded_receptor_and_original_cli_pockets_share_source_frame():
    if shutil.which('fpocket') is None:
        pytest.skip('Optional fpocket executable unavailable')
    view = molsysviewer.new_view(PDB, structure_indices=0)
    output = tmt.get_provider_output(PDB, method='fpocket', structure_indices=0)
    attached = addon.attach_provider_output(view, output)
    assert len(attached['rendered'].layers) == len(output.pockets) > 0
    assert all(view.shapes.contains(tag) for tag in attached['rendered'].tags)
    assert output.run.get_artifact('input/3LKF.pdb') == PDB.read_bytes()
    assert view.addons.topomt.provider_outputs[output.run.run_id] is output
