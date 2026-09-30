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


def test_installed_pycasta_matches_direct_process(protein_pdb, tmp_path):
    _require_distribution('pycasta')
    script = """
import importlib.util
import json
from pathlib import Path
import sys
spec = importlib.util.find_spec('pycasta')
sys.path.insert(0, next(iter(spec.submodule_search_locations)))
import run_analysis
result = run_analysis.process_pdb(sys.argv[1])
Path(sys.argv[2]).write_text(json.dumps(result, allow_nan=True))
"""
    result_path = tmp_path / 'direct.json'
    execution = subprocess.run(
        [sys.executable, '-c', script, str(protein_pdb), str(result_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert execution.returncode == 0, execution.stderr
    expected = json.loads(result_path.read_text())
    before = set(sys.modules)
    topography = tmt.third_party.pycasta.get_topography(
        str(protein_pdb), backend='library'
    )
    assert not {'run_analysis', 'config', 'pocket_detection'} & (
        set(sys.modules) - before
    )
    pockets = list(topography.get_features(by='type', value='pocket'))
    assert len(pockets) == len(expected['ranked_pockets'])
    assert pockets
    for pocket in pockets:
        index = int(pocket.source_id.split(':')[-1])
        assert pocket.score == pytest.approx(expected['ranking_scores'][index])
        assert puw.get_value(pocket.volume, to_unit='angstroms**3') == pytest.approx(
            expected['pocket_volumes'][index]
        )
    run = next(iter(topography.provider_runs.values()))
    recorded = json.loads(run.get_artifact('output/topomt_returned_result.json'))
    assert recorded['ranked_pockets'] == expected['ranked_pockets']
    assert run.get_artifact('input/2pk4.pdb') == protein_pdb.read_bytes()
