"""Integration checks against installed distributions, without source checkouts."""

import importlib
import json
import subprocess
import sys
import zipfile
from importlib.metadata import PackageNotFoundError, distribution
from importlib.util import find_spec
from pathlib import Path

import numpy as np
import pytest

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun


def _require_distribution(name):
    try:
        installed = distribution(name)
    except PackageNotFoundError:
        pytest.skip(f'optional distribution {name} is not installed')
    spec = find_spec(name)
    expected_init = Path(installed.locate_file(f'{name}/__init__.py')).resolve()
    if spec is not None and spec.origin is not None:
        if Path(spec.origin).resolve() != expected_init:
            pytest.skip(
                'source checkout shadows installed engine; run this module in a fresh process'
            )
    return installed.version


@pytest.fixture
def protein_pdb(tmp_path):
    archive = Path(tmt.__file__).parent / 'data' / 'CASTpFold_server' / '2pk4.zip'
    pdb = tmp_path / '2pk4.pdb'
    with zipfile.ZipFile(archive) as files:
        pdb.write_bytes(files.read('2pk4.pdb'))
    return pdb


def test_installed_pocketeer_matches_direct_library(protein_pdb):
    _require_distribution('pocketeer')
    upstream = importlib.import_module('pocketeer')
    expected = upstream.find_pockets(upstream.load_structure(str(protein_pdb)))
    topography = tmt.third_party.pocketeer.get_topography(
        str(protein_pdb), backend='library'
    )
    pockets = list(topography.get_features(by='type', value='pocket'))
    assert len(pockets) == len(expected)
    assert expected
    references = {f'pocketeer:{pocket.pocket_id}': pocket for pocket in expected}
    for actual in pockets:
        reference = references[actual.source_id]
        assert actual.score == pytest.approx(reference.score)
        assert puw.get_value(actual.volume, to_unit='angstroms**3') == pytest.approx(
            reference.volume
        )
        assert actual.atom_indices == np.flatnonzero(reference.mask).tolist()


def test_installed_alphaspace2_matches_direct_snapshot(protein_pdb):
    _require_distribution('alphaspace2')
    import mdtraj

    from topomt.third_party.alphaspace2.library import (
        _patch_alphaspace2_mdtraj_sasa,
        _patch_alphaspace2_numpy_compatibility,
    )

    upstream = importlib.import_module('alphaspace2')
    _patch_alphaspace2_numpy_compatibility()
    _patch_alphaspace2_mdtraj_sasa(upstream)
    snapshot = upstream.Snapshot()
    snapshot.run(mdtraj.load(str(protein_pdb)))
    expected = [pocket for pocket in snapshot.pockets if len(pocket.alpha_index) >= 20]
    topography = tmt.third_party.alphaspace2.get_topography(
        str(protein_pdb), backend='library'
    )
    pockets = list(topography.get_features(by='type', value='pocket'))
    assert len(pockets) == len(expected)
    assert expected
    run = next(iter(topography.provider_runs.values()))
    state = json.loads(run.get_artifact('output/topomt_snapshot.json'))
    assert np.asarray(state['_alpha_xyz']) == pytest.approx(snapshot._alpha_xyz)
    assert np.asarray(state['_beta_scores']) == pytest.approx(snapshot._beta_scores)


@pytest.fixture
def bound_inputs(protein_pdb, tmp_path):
    lines = protein_pdb.read_text().splitlines()
    receptor = tmp_path / 'receptor.pdb'
    binder = tmp_path / 'binder.pdb'
    receptor.write_text(
        '\n'.join(line for line in lines if line.startswith(('ATOM  ', 'TER   ')))
        + '\nEND\n'
    )
    binder.write_text(
        '\n'.join(
            line for line in lines if line.startswith('HETATM') and line[17:20] == 'ACA'
        )
        + '\nEND\n'
    )
    return receptor, binder


@pytest.mark.parametrize('same_complex', [False, True])
def test_installed_alphaspace2_binder_matches_direct_snapshot(
    bound_inputs,
    protein_pdb,
    tmp_path,
    same_complex,
    recwarn,
):
    _require_distribution('alphaspace2')
    import mdtraj

    from topomt.third_party.alphaspace2.library import (
        _patch_alphaspace2_mdtraj_sasa,
        _patch_alphaspace2_numpy_compatibility,
    )

    receptor_path, binder_path = bound_inputs
    upstream = importlib.import_module('alphaspace2')
    _patch_alphaspace2_numpy_compatibility()
    _patch_alphaspace2_mdtraj_sasa(upstream)
    if same_complex:
        topography = tmt.get_topography(
            str(protein_pdb),
            method='alphaspace2',
            implementation='wrapper',
            selection='group_type=="amino acid"',
            binder=str(protein_pdb),
            binder_selection='group_name=="ACA"',
            binder_structure_indices=[0],
            binder_syntax='molsysmt',
            min_vertices=1,
        )
    else:
        topography = tmt.third_party.alphaspace2.get_topography(
            str(receptor_path),
            backend='library',
            binder=str(binder_path),
            min_vertices=1,
        )
    run = next(iter(topography.provider_runs.values()))
    receptor_input = tmp_path / 'submitted_receptor.pdb'
    receptor_input.write_bytes(
        run.get_artifact(run.metadata['receptor_input_artifact'])
    )
    binder_input = tmp_path / 'submitted_binder.pdb'
    binder_input.write_bytes(run.get_artifact(run.metadata['binder']['input_artifact']))
    receptor = mdtraj.load(str(receptor_input))
    binder = mdtraj.load(str(binder_input))
    assert receptor.n_atoms == 630
    assert binder.n_atoms == 9
    assert receptor.xyz == pytest.approx(mdtraj.load(str(receptor_path)).xyz)
    assert binder.xyz == pytest.approx(mdtraj.load(str(binder_path)).xyz)
    snapshot = upstream.Snapshot()
    snapshot.run(receptor, binder)
    assert np.any(snapshot._alpha_contact)
    assert np.any(~snapshot._alpha_contact)
    state = json.loads(run.get_artifact('output/topomt_snapshot.json'))
    for name in (
        '_alpha_xyz',
        '_alpha_contact',
        '_beta_contact',
        '_pocket_contact',
        '_beta_scores',
    ):
        assert np.asarray(state[name]) == pytest.approx(getattr(snapshot, name))
    pockets = list(topography.get_features(by='type', value='pocket'))
    assert len(pockets) == len(list(snapshot.pockets))
    selected_indices = np.asarray(run.metadata['selected_atom_indices'])
    references = list(snapshot.pockets)
    for actual in pockets:
        expected = references[int(actual.source_id.split(':')[-1])]
        assert (
            actual.alpha_contact.tolist()
            == snapshot._alpha_contact[expected.alpha_index].tolist()
        )
        assert (
            actual.beta_contact.tolist()
            == snapshot._beta_contact[
                snapshot._pocket_beta_index_list[expected.index]
            ].tolist()
        )
        assert actual.is_contact == bool(expected.isContact)
        assert actual.atom_indices == sorted(
            selected_indices[expected.lining_atoms_idx].tolist()
        )
        for field, original, unit in (
            ('occupied_space', 'occupiedSpace', 'angstroms**3'),
            ('occupied_nonpolar_space', 'occupiedNonpolarSpace', 'angstroms**3'),
            ('occupancy', 'occupancy', None),
            ('occupancy_nonpolar', 'occupancy_nonpolar', None),
        ):
            reported = float(getattr(expected, original))
            value = getattr(actual, field)
            if unit:
                value = puw.get_value(value, to_unit=unit)
            assert value == pytest.approx(reported, nan_ok=True)
            measurement = actual.external_measurements[field]
            assert measurement.original_value == pytest.approx(reported, nan_ok=True)
            assert measurement.status == 'external_only'
            assert measurement.run_id == run.run_id
    direct_output = tmp_path / 'direct_bound'
    snapshot.save(
        output_dir=str(direct_output),
        receptor=receptor,
        binder=binder,
        chimera_scripts=False,
        contact_only=False,
    )
    assert run.get_artifact('output/pdb_out/lig.pdb')
    for path in direct_output.rglob('*'):
        if path.is_file():
            assert (
                run.get_artifact(f'output/{path.relative_to(direct_output).as_posix()}')
                == path.read_bytes()
            )
    if not same_complex:
        assert receptor_input.read_bytes() == receptor_path.read_bytes()
        assert binder_input.read_bytes() == binder_path.read_bytes()
    else:
        assert run.metadata['selected_atom_indices'] == list(range(630))
        assert run.metadata['binder']['selected_atom_indices'] == list(range(630, 639))
    bundle = tmp_path / 'bound_run.zip'
    run.save(bundle)
    assert ProviderRun.load(bundle) == run
    assert not any(
        warning.category.__name__ == 'DigestNotDigestedWarning' for warning in recwarn
    )


@pytest.mark.parametrize(
    'invalid', ['multiple_frames', 'receptor_multiple_frames', 'empty_selection']
)
def test_installed_alphaspace2_rejects_invalid_binder(bound_inputs, tmp_path, invalid):
    _require_distribution('alphaspace2')
    receptor_path, binder_path = bound_inputs
    options = {}
    if invalid in {'multiple_frames', 'receptor_multiple_frames'}:
        original = (
            receptor_path if invalid == 'receptor_multiple_frames' else binder_path
        )
        records = '\n'.join(
            line
            for line in original.read_text().splitlines()
            if line.startswith(('ATOM  ', 'HETATM'))
        )
        multiple = tmp_path / 'multiple.pdb'
        multiple.write_text(
            f'MODEL        1\n{records}\nENDMDL\nMODEL        2\n{records}\nENDMDL\nEND\n'
        )
        if invalid == 'receptor_multiple_frames':
            receptor_path = multiple
            options['structure_indices'] = [0, 1]
        else:
            binder_path = multiple
            options['binder_structure_indices'] = [0, 1]
    else:
        options['binder_selection'] = 'group_name=="ABSENT"'
    with pytest.raises(ValueError, match='single|empty'):
        tmt.third_party.alphaspace2.get_topography(
            str(receptor_path),
            backend='library',
            binder=str(binder_path),
            **options,
        )


@pytest.mark.parametrize('frame_index', [0, 1])
def test_installed_alphaspace2_selects_binder_frame_without_alignment(
    bound_inputs, tmp_path, frame_index
):
    _require_distribution('alphaspace2')
    import mdtraj

    receptor_path, binder_path = bound_inputs
    binder = mdtraj.load(str(binder_path))
    displaced = binder[:]
    displaced.xyz += (
        10.0  # MDTraj coordinates are in nm; this pose is far from the receptor.
    )
    trajectory_path = tmp_path / 'binder_frames.pdb'
    mdtraj.join([binder, displaced]).save_pdb(str(trajectory_path))
    topography = tmt.get_topography(
        str(receptor_path),
        method='alphaspace2',
        implementation='wrapper',
        binder=str(trajectory_path),
        binder_structure_indices=[frame_index],
    )
    run = next(iter(topography.provider_runs.values()))
    submitted = tmp_path / 'submitted.pdb'
    submitted.write_bytes(run.get_artifact(run.metadata['binder']['input_artifact']))
    expected = binder if frame_index == 0 else displaced
    assert mdtraj.load(str(submitted)).xyz == pytest.approx(expected.xyz)
    state = json.loads(run.get_artifact('output/topomt_snapshot.json'))
    assert any(state['_alpha_contact']) == (frame_index == 0)
    assert not run.metadata['unbound_contacts_initialized']
    assert run.metadata['binder']['structure_indices'] == [frame_index]
    if frame_index == 1:
        assert all(
            pocket['occupied_space'] == 0 for pocket in state['pocket_properties']
        )


@pytest.fixture(params=['2pk4', '1stp', '2ifb', '1hew'])
def installed_pycasta_pdb(request, tmp_path):
    assert _require_distribution('pycasta') == '1.0.8'
    installed = distribution('pycasta')
    spec = find_spec('pycasta')
    assert spec is not None and spec.submodule_search_locations is not None
    package_root = Path(installed.locate_file('pycasta')).resolve()
    assert [Path(p).resolve() for p in spec.submodule_search_locations] == [
        package_root
    ]
    assert (package_root / 'run_analysis.py').is_file()
    archive = (
        Path(tmt.__file__).parent / 'data' / 'CASTpFold_server' / f'{request.param}.zip'
    )
    pdb = tmp_path / f'{request.param}.pdb'
    with zipfile.ZipFile(archive) as files:
        inputs = [name for name in files.namelist() if name.endswith('.pdb')]
        assert len(inputs) == 1
        pdb = tmp_path / Path(inputs[0]).name
        pdb.write_bytes(files.read(inputs[0]))
    return pdb, package_root


def test_installed_pycasta_matches_direct_process(installed_pycasta_pdb, tmp_path):
    import hashlib
    from io import BytesIO

    import molsysmt as msm
    from scipy.spatial import Delaunay

    protein_pdb, package_root = installed_pycasta_pdb
    script = """
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import sys
installed = importlib.metadata.distribution('pycasta')
assert installed.version == '1.0.8'
root = Path(sys.argv[3]).resolve()
assert root == Path(installed.locate_file('pycasta')).resolve()
spec = importlib.util.find_spec('pycasta')
assert [Path(p).resolve() for p in spec.submodule_search_locations] == [root]
sys.path.insert(0, str(root))
import config
import run_analysis
assert Path(config.__file__).resolve() == root / 'config.py'
assert Path(run_analysis.__file__).resolve() == root / 'run_analysis.py'
result = run_analysis.process_pdb(sys.argv[1])
source_modules = {}
for name, module in sorted(sys.modules.items()):
    filename = getattr(module, '__file__', None)
    if filename is None:
        continue
    path = Path(filename).resolve()
    if path.is_relative_to(root):
        source_modules[name] = {
            'path': str(path.relative_to(root)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        }
assert {'config', 'run_analysis', 'pocket_detection'} <= set(source_modules)
Path(sys.argv[2]).write_text(json.dumps({
    'result': result,
    'source_modules': source_modules,
    'configuration': {
        'use_cgal': bool(config.USE_CGAL),
        'filter_alpha_by_sasa': bool(config.FILTER_ALPHA_BY_SASA),
        'save_alpha': bool(config.SAVE_ALPHA),
        'validation_method': config.VALIDATION_METHOD,
        'use_existing_results': bool(config.USE_EXISTING_RESULTS),
        'manual_alpha': config.MANUAL_ALPHA,
        'version_tag': run_analysis.VERSION_TAG,
        'distribution_version': installed.version,
    },
}, sort_keys=True, allow_nan=True))
"""
    direct = tmp_path / 'direct'
    direct.mkdir()
    result_path = tmp_path / 'direct.json'
    execution = subprocess.run(
        [
            sys.executable,
            '-I',
            '-B',
            '-c',
            script,
            str(protein_pdb),
            str(result_path),
            str(package_root),
        ],
        cwd=direct,
        capture_output=True,
        text=True,
        check=False,
    )
    assert execution.returncode == 0, execution.stderr
    direct_run = json.loads(result_path.read_text())
    expected = direct_run['result']
    before = set(sys.modules)
    assert not set(direct_run['source_modules']) & before
    output = tmt.get_provider_output(
        str(protein_pdb), method='pycasta', backend='library'
    )
    assert not set(direct_run['source_modules']) & (set(sys.modules) - before)
    pockets = output.pockets
    assert len(pockets) == len(expected['ranked_pockets'])
    assert pockets
    assert [p.source_id for p in pockets] == [
        f'pycasta:{index}' for index in range(len(pockets))
    ]
    configuration = direct_run['configuration']
    direct_alpha = (
        direct
        / 'results'
        / configuration['version_tag']
        / f'{protein_pdb.stem}.alpha.npz'
    )
    with np.load(direct_alpha, allow_pickle=False) as arrays:
        protein_coords = arrays['protein_coords']
        tetrahedra = arrays['tetrahedra']
    np.testing.assert_array_equal(protein_coords, expected['protein_coords'])
    simplices = Delaunay(protein_coords).simplices
    np.testing.assert_array_equal(tetrahedra, protein_coords[simplices])
    submitted_rows = [
        row
        for row in protein_pdb.read_text().splitlines()
        if row.startswith(('ATOM  ', 'HETATM'))
    ]
    protein_map = np.array(
        [index for index, row in enumerate(submitted_rows) if row.startswith('ATOM  ')]
    )
    all_coordinates = np.array(
        [
            [float(row[start : start + 8]) for start in (30, 38, 46)]
            for row in submitted_rows
        ]
    )
    np.testing.assert_array_equal(protein_coords, all_coordinates[protein_map])
    for index, pocket in enumerate(pockets):
        fields = pocket.fields
        tetra_indices = expected['ranked_pockets'][index]
        assert fields['provider_tetrahedron_indices'] == tetra_indices
        members = np.unique(simplices[tetra_indices].reshape(-1))
        assert pocket.atom_indices == tuple(sorted(protein_map[members].tolist()))
        assert pocket.atom_role == 'region_tetrahedron_vertices'
        assert fields['score'] == pytest.approx(expected['ranking_scores'][index])
        assert (
            fields['provider_validation_method']
            == expected['validation_methods'][index]
        )
        assert puw.get_value(fields['volume'], to_unit='angstroms**3') == pytest.approx(
            expected['pocket_volumes'][index]
        )
        for field, original, unit in (
            ('depth', 'pocket_depths', 'angstroms'),
            ('mouth_area', 'mouth_area', 'angstroms**2'),
            ('mouth_perimeter', 'mouth_perimeter', 'angstroms'),
            ('representative_point', 'representative_points', 'angstroms'),
        ):
            assert puw.get_value(fields[field], to_unit=unit) == pytest.approx(
                expected[original][index]
            )
            assert pocket.measurements[field].original_value == pytest.approx(
                expected[original][index]
            )
        np.testing.assert_allclose(
            puw.get_value(
                pocket.geometries['member_atoms'].coordinates, to_unit='angstroms'
            ),
            all_coordinates[np.array(pocket.atom_indices)],
            rtol=0,
            atol=1e-9,
        )
    run = output.run
    assert run.metadata['distribution_version'] == '1.0.8'
    assert run.metadata['configuration'] == configuration
    assert (
        run.metadata['source_sha256']
        == direct_run['source_modules']['run_analysis']['sha256']
    )
    assert (
        run.metadata['source_sha256']
        == hashlib.sha256((package_root / 'run_analysis.py').read_bytes()).hexdigest()
    )
    assert run.metadata['selected_atom_indices'] == list(range(len(submitted_rows)))
    assert run.metadata['protein_atom_indices'] == protein_map.tolist()
    assert np.atleast_1d(run.metadata['structure_indices']).tolist() == [0]
    assert run.metadata['selection'] == 'all'
    assert run.metadata['syntax'] == 'MolSysMT'
    recorded = json.loads(run.get_artifact('output/topomt_returned_result.json'))

    def json_value(value):
        if isinstance(value, dict):
            return {key: json_value(item) for key, item in value.items()}
        if isinstance(value, list):
            return [json_value(item) for item in value]
        if isinstance(value, float) and not np.isfinite(value):
            return {'nonfinite': str(value)}
        return value

    assert recorded.keys() == expected.keys()
    for name, value in expected.items():
        if name == 'pdb_path':
            # Each independent execution retains its own submitted path.
            assert Path(recorded[name]).name == Path(value).name == protein_pdb.name
        else:
            assert recorded[name] == json_value(value)
    assert run.get_artifact(f'input/{protein_pdb.name}') == protein_pdb.read_bytes()
    with np.load(
        BytesIO(run.get_artifact(run.metadata['alpha_artifact'])), allow_pickle=False
    ) as arrays:
        np.testing.assert_array_equal(arrays['protein_coords'], protein_coords)
        np.testing.assert_array_equal(arrays['tetrahedra'], tetrahedra)
    source_context = json.loads(
        run.get_artifact(run.metadata['source_context_artifact'])
    )
    source = msm.convert(str(protein_pdb), to_form='molsysmt.MolSys')
    assert source_context['schema_version'] == 1
    assert source_context['n_atoms'] == len(submitted_rows)
    assert source_context['coordinates']['unit'] == 'nm'
    np.testing.assert_allclose(
        source_context['coordinates']['value'],
        puw.get_value(
            msm.get(source, structure_indices=0, coordinates=True), to_unit='nm'
        )[0],
        rtol=0,
        atol=1e-12,
    )
    attributes = msm.get(
        source,
        element='atom',
        output_type='dictionary',
        get_missing_bonds=False,
        **{name: True for name in source_context['atom_attributes']},
    )
    for name, values in attributes.items():
        np.testing.assert_equal(source_context['atom_attributes'][name], values)
    worker = json.loads(run.get_artifact(run.metadata['worker_origin_artifact']))
    assert Path(worker['source_root']).resolve() == package_root
    assert worker['distribution_version'] == '1.0.8'
    for name, identity in direct_run['source_modules'].items():
        assert (
            Path(worker['modules'][name]['file']).resolve()
            == package_root / identity['path']
        )
        artifact = 'output/topomt_worker_sources/' + identity['path']
        assert worker['source_files'][artifact]['sha256'] == identity['sha256']
        assert (
            hashlib.sha256(run.get_artifact(artifact)).hexdigest() == identity['sha256']
        )
    portable = tmp_path / f'{protein_pdb.stem}-provider.zip'
    run.save(portable)
    recovered = ProviderRun.load(portable)
    assert recovered.run_id == run.run_id
    assert recovered.artifacts == run.artifacts
    assert recovered.metadata_json == run.metadata_json
