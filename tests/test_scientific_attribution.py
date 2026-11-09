"""Completion, ownership and optional-provider contracts for attribution."""

import json
import subprocess
import sys
import zipfile
from dataclasses import replace

import numpy as np
import pytest

import topomt as tmt
from topomt import _ackredit
from topomt.provider_output import ProviderRun


def _ids(payload):
    return {entry['item']['id'] for entry in payload['references']}


def test_real_provider_repeated_results_and_enclosing_workflow():
    ackredit = pytest.importorskip('ackredit')

    @_ackredit.attributed('fpocket', route='native')
    def calculation():
        return {}

    with ackredit.session('workflow'), ackredit.capture('outer') as outer:
        first, second = calculation(), calculation()
        for result in (first, second):
            saved = result['scientific_attribution']
            assert saved['status'] == 'recorded'
            assert 'doi:10.1186/1471-2105-10-168' in _ids(saved)
            assert saved['ackredit']['items']
            assert not any(
                use['context'].get('software') == 'fpocket'
                and 'executed_software' in use['roles']
                for use in saved['ackredit']['uses']
            )
        assert _ids(first['scientific_attribution']) <= {
            item['id'] for item in outer.attribution.to_dict()['items']
        }
    first['scientific_attribution']['references'].clear()
    assert second['scientific_attribution']['references']


def test_absent_backend_preserves_empty_science_and_host_bibliography(monkeypatch):
    monkeypatch.setattr(_ackredit, 'backend', lambda: None)

    @_ackredit.attributed('mole', route='original')
    def calculation():
        return {'channels': []}

    result = calculation()
    assert result['channels'] == []
    assert result['scientific_attribution']['status'] == 'unavailable'
    assert 'doi:10.1186/1758-2946-5-39' in _ids(result['scientific_attribution'])


def test_recording_failure_does_not_replace_science_or_exception(monkeypatch):
    ackredit = pytest.importorskip('ackredit')
    monkeypatch.setattr(ackredit, 'track_item', lambda *a, **k: 1 / 0)

    @_ackredit.attributed('fpocket', route='original')
    def successful():
        return {}

    @_ackredit.attributed('fpocket', route='original')
    def failing():
        raise ValueError('scientific failure')

    with ackredit.session('failure'), pytest.warns(Warning):
        assert successful()['scientific_attribution']['status'] == 'failed'
    with ackredit.session('science'):
        with pytest.raises(ValueError, match='scientific failure'):
            failing()
        assert not ackredit.get_attribution().to_dict()['items']


def test_completed_child_credit_survives_failed_parent():
    ackredit = pytest.importorskip('ackredit')

    @_ackredit.attributed('qhull', route='original')
    def child():
        return 1

    @_ackredit.attributed('dfnd')
    def parent():
        child()
        raise ValueError('later failure')

    with ackredit.session('partial'):
        with pytest.raises(ValueError, match='later failure'):
            parent()
        ids = {item['id'] for item in ackredit.get_attribution().to_dict()['items']}
        assert 'doi:10.1145/235815.235821' in ids
        assert not any(
            use['context']['method'] == 'dfnd'
            for use in ackredit.get_attribution().to_dict()['uses']
        )


def test_original_version_is_taken_from_the_result_not_current_installation(tmp_path):
    ackredit = pytest.importorskip('ackredit')
    from topomt.third_party.fpocket.output import FpocketOutput

    input_file = tmp_path / 'input.pdb'
    input_file.write_text('original')
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    run = ProviderRun.capture(
        'fpocket',
        'cli',
        input_file,
        output_dir,
        metadata={'version': 'original-build-4.2'},
    )

    @_ackredit.attributed('fpocket', route='original')
    def calculation():
        return FpocketOutput(run=run, records=())

    with ackredit.session('original'):
        result = calculation()
    assert result.run.run_id == run.run_id
    assert any(
        entry['item'].get('version') == 'original-build-4.2'
        and entry['roles'] == ['executed_software']
        for entry in result.attribution['references']
    )


def test_every_original_dispatch_provider_has_an_explicit_attribution_policy():
    from topomt._private.arg_digestion.provider_dispatch import DEFAULT_BACKENDS

    assert set(DEFAULT_BACKENDS) <= set(_ackredit._METHODS)


def test_fpocket_druggability_is_a_separate_reached_criterion():
    from types import SimpleNamespace

    ackredit = pytest.importorskip('ackredit')
    from topomt.third_party.fpocket._native_impl import _drug_score_native_pocket

    descriptor = SimpleNamespace(
        mean_loc_hyd_dens_norm=0.5,
        as_max_dst_angstrom=8.0,
        surf_pol_vdw22_angstrom2=10.0,
    )
    with ackredit.session('native score'):
        score = _ackredit.scientific_call(
            'fpocket_druggability', _drug_score_native_pocket, descriptor
        )
        assert 0.0 < score < 1.0
        saved = ackredit.get_attribution().to_dict()
        assert 'doi:10.1021/jm100574m' in {item['id'] for item in saved['items']}
        assert not any(
            use['context'].get('software') == 'fpocket'
            and 'executed_software' in use['roles']
            for use in saved['uses']
        )


def test_original_fpocket_cli_retains_detected_method_and_score_references(
    tmp_path, monkeypatch
):
    """Exercise the adapter with analytical original-format bytes, no detector."""
    from tests.methods.fpocket4.test_input_preparation import _pdb_frame
    from topomt.third_party.fpocket import cli

    ackredit = pytest.importorskip('ackredit')
    source = tmp_path / 'source.pdb'
    source.write_text(_pdb_frame() + 'END\n')

    def analytical_run(pdb, **options):
        output = pdb.parent / (pdb.stem + '_out')
        (output / 'pockets').mkdir(parents=True)
        rows = [
            line
            for line in pdb.read_text().splitlines(keepends=True)
            if line.startswith(('ATOM  ', 'HETATM'))
        ]
        (output / (pdb.stem + '_info.txt')).write_text(
            'Pocket 1 :\nScore : 2.5\nDruggability Score : 0.3\n'
            'Volume : 12.5\nNumber of Alpha Spheres : 2\n'
        )
        (output / 'pockets/pocket1_atm.pdb').write_text(''.join(rows))
        (output / 'pockets/pocket1_vert.pqr').write_text(
            ''.join(line[:54] + ' 0.0 1.5\n' for line in rows[:2])
        )
        return output

    monkeypatch.setattr(cli, 'run_fpocket', analytical_run)
    monkeypatch.setattr(cli.shutil, 'which', lambda cmd: None)
    with ackredit.session('original adapter'):
        result = tmt.get_provider_output(source, method='fpocket')
        assert len(result.pockets) == 1
        references = result.attribution
        assert references is not None
        assert {'doi:10.1186/1471-2105-10-168', 'doi:10.1021/jm100574m'} <= _ids(
            references
        )
        assert any(
            entry['context']['software'] == 'fpocket'
            and entry['roles'] == ['executed_software']
            for entry in references['references']
        )
    bundle = tmp_path / 'original.zip'
    result.save(bundle)
    with ackredit.session('reader'):
        restored = tmt.load_provider_output(bundle, molecular_system=source)
        assert restored.attribution == result.attribution
        assert not ackredit.get_attribution().to_dict()['items']


def test_actual_mdtraj_sasa_is_recorded_alongside_its_calling_method(tmp_path):
    ackredit = pytest.importorskip('ackredit')
    pytest.importorskip('mdtraj')
    import molsysmt as msm

    from tests.methods.fpocket4.test_input_preparation import _pdb_frame

    source = tmp_path / 'sasa.pdb'
    source.write_text(_pdb_frame() + 'END\n')

    @_ackredit.attributed('alphaspace2')
    def calculation():
        sasa = _ackredit.scientific_call(
            'mdtraj_sasa',
            msm.physchem.get_sasa,
            source,
            element='atom',
            engine='mdtraj',
        )
        return {'sasa': sasa}

    with ackredit.session('joined scientific methods'):
        result = calculation()
        saved = result['scientific_attribution']
        assert saved['status'] == 'recorded'
        assert result['sasa'].shape == (1, 4)
        assert {
            'doi:10.1016/j.bpj.2015.08.015',
            'doi:10.1016/0022-2836(73)90011-9',
        } <= _ids(saved)


def test_provider_bundle_keeps_attribution_separate_from_run_identity(tmp_path):
    input_file = tmp_path / 'input.pdb'
    input_file.write_text('original')
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    run = ProviderRun.capture('fpocket', 'cli', input_file, output_dir)
    original = tmp_path / 'legacy.zip'
    run.save(original)
    assert ProviderRun.load(original).attribution is None

    @_ackredit.attributed('fpocket', route='original')
    def calculation():
        return {}

    saved = calculation()['scientific_attribution']
    attributed = replace(run, attribution_json=json.dumps(saved))
    bundle = tmp_path / 'attributed.zip'
    attributed.save(bundle)
    restored = ProviderRun.load(bundle)
    assert restored.run_id == run.run_id
    assert restored.metadata == run.metadata
    assert restored.artifacts == run.artifacts
    assert restored.attribution == saved
    detached = restored.attribution
    assert detached is not None
    detached['references'].clear()
    fresh = restored.attribution
    assert fresh is not None and fresh['references']
    with zipfile.ZipFile(bundle) as archive:
        assert json.loads(archive.read('manifest.json'))['schema_version'] == 2

    altered = tmp_path / 'altered.zip'
    with zipfile.ZipFile(bundle) as source, zipfile.ZipFile(altered, 'w') as target:
        for name in source.namelist():
            content = source.read(name)
            if name == 'manifest.json':
                manifest = json.loads(content)
                manifest['attribution']['producer']['version'] = 'tampered'
                content = json.dumps(manifest).encode()
            target.writestr(name, content)
    with pytest.raises(ValueError, match='attribution checksum'):
        ProviderRun.load(altered)


def test_import_and_saved_reading_do_not_credit_or_import_ackredit(tmp_path):
    script = """
import sys
import topomt
assert 'ackredit' not in sys.modules
from topomt.provider_output import ProviderRun
assert 'ackredit' not in sys.modules
"""
    subprocess.run([sys.executable, '-c', script], check=True, timeout=30)


def test_rendering_saved_and_absent_provider_results_never_credits(monkeypatch):
    ackredit = pytest.importorskip('ackredit')

    @_ackredit.attributed('fpocket', route='native')
    def calculation():
        return {}

    with monkeypatch.context() as patch:
        patch.setattr(_ackredit, 'backend', lambda: None)
        untracked = calculation()
    with ackredit.session('reader'):
        assert 'Fpocket' in tmt.cite(untracked)
        assert not ackredit.get_attribution().to_dict()['items']
        assert tmt.get_attribution(untracked)['status'] == 'unavailable'


def test_rendering_partial_recording_cannot_replace_observed_bibliography():
    ackredit = pytest.importorskip('ackredit')

    @_ackredit.attributed('fpocket', route='native')
    def calculation():
        return {}

    result = calculation()
    saved = result['scientific_attribution']
    saved['status'] = 'failed'
    original_title = saved['ackredit']['items'][0]['title']
    with ackredit.session('partial reader'):
        assert tmt.cite(result)
        assert not ackredit.get_attribution().to_dict()['items']
    saved['references'][0]['item']['title'] = 'Conflicting declaration'
    with ackredit.session('reader'):
        with pytest.raises(ValueError, match='Conflicting saved bibliography'):
            tmt.cite(result)
        assert not ackredit.get_attribution().to_dict()['items']
    assert saved['ackredit']['items'][0]['title'] == original_title


def test_really_unimportable_provider_preserves_host_records_in_fresh_process():
    script = """
import sys
import importlib.abc
class Unavailable(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'ackredit' or fullname.startswith('ackredit.'):
            raise ModuleNotFoundError('ackredit is unavailable in this process', name='ackredit')
sys.meta_path.insert(0, Unavailable())
from topomt._ackredit import attributed
@attributed('dfnd')
def calculation():
    return {'value': 42}
result = calculation()
assert result['value'] == 42
assert result['scientific_attribution']['status'] == 'unavailable'
assert result['scientific_attribution']['references']
assert 'ackredit' not in sys.modules
"""
    subprocess.run([sys.executable, '-c', script], check=True, timeout=30)


def test_saved_bundle_in_fresh_reader_preserves_original_version_without_credit(
    tmp_path,
):
    input_file = tmp_path / 'input.pdb'
    input_file.write_text('original')
    output_dir = tmp_path / 'output'
    output_dir.mkdir()

    @_ackredit.attributed('fpocket', route='original')
    def calculation():
        return {}

    saved = calculation()['scientific_attribution']
    saved['producer']['version'] = 'historical-producer'
    run = ProviderRun.capture('fpocket', 'cli', input_file, output_dir)
    run = replace(run, attribution_json=json.dumps(saved))
    bundle = tmp_path / 'original.zip'
    run.save(bundle)
    script = """
import sys
import ackredit
import topomt
from topomt.provider_output import ProviderRun
with ackredit.session('reader'):
    saved = ProviderRun.load(sys.argv[1])
    assert saved.attribution['producer']['version'] == 'historical-producer'
    assert topomt.cite(saved)
    assert not ackredit.get_attribution().to_dict()['items']
"""
    subprocess.run([sys.executable, '-c', script, str(bundle)], check=True, timeout=30)


def test_unselected_auxiliary_backends_are_not_credited():
    import importlib.util

    ackredit = pytest.importorskip('ackredit')
    from topomt.tools.features.channels.profiles import thickness_profile
    from topomt.tools.geometry.meshes import marching_cubes_union

    with ackredit.session('no marching cubes'):
        if importlib.util.find_spec('skimage') is None:
            from topomt._private.smonitor import LibraryNotFoundError

            with pytest.raises(LibraryNotFoundError):
                marching_cubes_union([], [])
        else:
            marching_cubes_union([], [])
        assert 'doi:10.1080/10867651.2003.10487582' not in {
            item['id'] for item in ackredit.get_attribution().to_dict()['items']
        }
    with ackredit.session('explicit neighbors'):
        thickness_profile(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]], [1.0, 0.0, 0.0], neighbor_pairs=[[0, 1]]
        )
        assert 'sklearn:article:2011' not in {
            item['id'] for item in ackredit.get_attribution().to_dict()['items']
        }


def test_strict_warning_policy_preserves_result(monkeypatch):
    import warnings

    ackredit = pytest.importorskip('ackredit')
    monkeypatch.setattr(ackredit, 'register_item', lambda **kwargs: 1 / 0)

    @_ackredit.attributed('fpocket', route='original')
    def calculation():
        return {'value': 42}

    with warnings.catch_warnings(), ackredit.session('strict'):
        warnings.simplefilter('error')
        result = calculation()
    assert result['value'] == 42
    assert result['scientific_attribution']['status'] == 'failed'


def test_cached_dfnd_query_retains_mesh_references_without_claiming_qhull_execution():
    ackredit = pytest.importorskip('ackredit')
    from topomt.dfnd import DelaunayFlowNetwork, synthetic

    system = synthetic.tetrahedron()
    network = DelaunayFlowNetwork.from_coordinates_and_radii(
        system.coords, system.radii
    )
    with ackredit.session('query'):
        result = network.get_topography()
        saved = result['scientific_attribution']
        uses = [
            entry
            for entry in saved['references']
            if entry['item']['id'] == 'doi:10.1145/235815.235821'
        ]
        assert uses
        assert all(entry['roles'] == ['reused_result'] for entry in uses)
        assert all(
            use['roles'] == ['reused_result']
            for use in ackredit.get_attribution().to_dict()['uses']
            if use['item_id'] == 'doi:10.1145/235815.235821'
        )
        assert not any(
            entry['item'].get('doi') == 'DFND' for entry in saved['references']
        )


def test_tessellation_credits_only_actual_qhull_branch():
    ackredit = pytest.importorskip('ackredit')
    points = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    )
    with ackredit.session('empty'):
        tmt.DelaunayMesh()
        assert not ackredit.get_attribution().to_dict()['items']
    with ackredit.session('weighted-four'):
        tmt.WeightedDelaunayMesh(points=points, weights=np.ones(4))
        assert 'doi:10.1145/235815.235821' not in {
            item['id'] for item in ackredit.get_attribution().to_dict()['items']
        }
    with ackredit.session('qhull'):
        mesh = tmt.DelaunayMesh(points=points)
        assert 'doi:10.1145/235815.235821' in {
            item['id'] for item in ackredit.get_attribution().to_dict()['items']
        }
    assert mesh.attribution['producer']['version'] == tmt.__version__


@pytest.mark.parametrize(
    'provider',
    [
        'fpocket',
        'pocketeer',
        'alphaspace2',
        'pycasta',
        'castp3',
        'castpfold',
        'pykvfinder',
        'ghecom',
        'caver',
        'p2rank',
        'mole',
        'dfnd',
    ],
)
def test_inventory_records_are_valid_and_only_selected_method_is_credited(provider):
    ackredit = pytest.importorskip('ackredit')

    @_ackredit.attributed(
        provider, route='native' if provider == 'dfnd' else 'original'
    )
    def calculation():
        return {}

    with ackredit.session(provider):
        result = calculation()['scientific_attribution']
        assert result['status'] == 'recorded'
        assert result['references']
        assert 'doi:10.1021/jm100574m' not in _ids(result)
        ackredit.Attribution.from_dict(result['ackredit'])
        assert not any('Zeo' in item['title'] for item in result['ackredit']['items'])
