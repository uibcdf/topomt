"""Original fpocket bundles retain source context and acquisition identity."""

import copy
import json
import os
import subprocess
import sys

import molsysmt as msm
import pytest
from argdigest import UnknownArgumentError

import topomt as tmt
from devtools.provider_handoff import pocket_outputs_agree
from tests.methods.fpocket4.test_input_preparation import _pdb_frame
from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError
from topomt.provider_output import ProviderRun
from topomt.third_party.pdb_context import source_input_context


def build_captured(tmp_path):
    """Capture analytical original-format files; no fpocket calculation runs."""
    submitted = tmp_path / 'submitted.pdb'
    submitted.write_text(_pdb_frame() + 'END\n')
    atoms = _pdb_frame().splitlines(keepends=True)
    excluded = atoms[0][:6] + '   99' + atoms[0][11:]
    excluded = (
        excluded[:12]
        + ' HX '
        + excluded[16:30]
        + (f'{4.0:8.3f}{4.0:8.3f}{4.0:8.3f}')
        + excluded[54:76]
        + ' H\n'
    )
    full = atoms[:1] + [excluded] + atoms[1:]
    first = ''.join(
        line[:30] + f'{float(line[30:38]) + 10:8.3f}' + line[38:] for line in full
    )
    source_file = tmp_path / 'full.pdb'
    source_file.write_text(
        'MODEL        1\n'
        + first
        + 'ENDMDL\nMODEL        2\n'
        + ''.join(full)
        + 'ENDMDL\nEND\n'
    )
    source = msm.convert(
        source_file, to_form='molsysmt.MolSys', get_missing_bonds=False
    )
    output_dir = tmp_path / 'submitted_out'
    (output_dir / 'pockets').mkdir(parents=True)
    (output_dir / 'submitted_info.txt').write_text(
        'Pocket 1 :\nScore : 2.5\nDruggability Score : 0.3\n'
        'Volume : 12.5\nTotal SASA : 7.25\nNumber of Alpha Spheres : 2\n'
    )
    (output_dir / 'pockets/pocket1_atm.pdb').write_text(atoms[0] + atoms[2])
    (output_dir / 'pockets/pocket1_vert.pqr').write_text(
        ''.join(line[:54] + ' 0.0 1.5\n' for line in atoms[:2])
    )
    original_files = {
        path.relative_to(output_dir).as_posix(): path.read_bytes()
        for path in output_dir.rglob('*')
        if path.is_file()
    }
    output = tmt.get_provider_output(
        source,
        method='fpocket',
        backend='files',
        pdb_file=submitted,
        output_dir=output_dir,
        selection=[0, 2, 3, 4],
        structure_indices=1,
        submitted_atom_indices=[0, 2, 3, 4],
        chemical_state='reference',
    )
    bundle = tmp_path / 'original.zip'
    output.run.save(bundle)
    return source, output, bundle, submitted, output_dir, original_files


@pytest.fixture
def captured(tmp_path):
    return build_captured(tmp_path)


def _recover(source, bundle, **kwargs):
    return tmt.get_provider_output(
        source, method='fpocket', backend='files', bundle_file=bundle, **kwargs
    )


def _rewrite(
    run, tmp_path, *, metadata=None, changes=None, provider=None, backend=None
):
    root = tmp_path / 'rewritten'
    root.mkdir()
    for name, data in run.artifacts:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((changes or {}).get(name, data))
    input_path = next((root / 'input').iterdir())
    altered = ProviderRun.capture(
        provider or run.provider,
        backend or run.backend,
        input_path,
        root / 'output',
        metadata=run.metadata if metadata is None else metadata,
    )
    bundle = tmp_path / 'rewritten.zip'
    altered.save(bundle)
    assert ProviderRun.load(bundle) == altered
    return bundle


def test_capture_augments_only_owned_snapshot(captured):
    source, output, _, submitted, output_dir, original_files = captured
    metadata = output.run.metadata
    assert metadata['source_binding_protocol'] == 1
    context_path = metadata['source_context_artifact']
    assert context_path == 'output/topomt_source_context.json'
    assert json.loads(output.run.get_artifact(context_path)) == source_input_context(
        source, 1
    )
    assert output.run.get_artifact('input/submitted.pdb') == submitted.read_bytes()
    assert {
        path.relative_to(output_dir).as_posix(): path.read_bytes()
        for path in output_dir.rglob('*')
        if path.is_file()
    } == original_files
    for name, data in original_files.items():
        assert output.run.get_artifact('output/' + name) == data


@pytest.mark.parametrize('units', [['nm', 'ps'], ['pm', 'fs']])
@pytest.mark.parametrize('backend', ['files', 'cli', 'wrapper'])
def test_bundle_roundtrip_preserves_original_run_and_science(
    captured, tmp_path, units, backend
):
    source, original, bundle, _, _, _ = captured
    if backend != 'files':
        bundle = _rewrite(original.run, tmp_path, backend=backend)
    run = ProviderRun.load(bundle)
    before = source_input_context(source, 1)
    with puw.context(standard_units=units):
        recovered = _recover(source, bundle)
    assert recovered.run == run
    assert recovered.run.backend == backend
    assert pocket_outputs_agree(recovered, original)
    pocket = recovered.pockets[0]
    assert pocket.source_id == 'fpocket:1'
    assert pocket.atom_indices == (0, 3)
    assert pocket.fields['score'] == pytest.approx(2.5)
    assert pocket.fields['volume'] == pytest.approx(12.5)
    assert pocket.measurements['total_sasa'].run_id == run.run_id
    assert source_input_context(source, 1) == before
    saved = tmp_path / 'saved-again.zip'
    recovered.run.save(saved)
    assert ProviderRun.load(saved) == run


def test_legacy_raw_import_remains_available_but_is_not_bound(captured, tmp_path):
    source, _, _, submitted, output_dir, _ = captured
    legacy = tmt.get_provider_output(
        source,
        method='fpocket',
        backend='files',
        pdb_file=submitted,
        output_dir=output_dir,
        selection=[0, 2, 3, 4],
        structure_indices=1,
    )
    assert 'source_binding_protocol' not in legacy.run.metadata
    assert 'output/topomt_source_context.json' not in dict(legacy.run.artifacts)
    bundle = tmp_path / 'legacy.zip'
    legacy.run.save(bundle)
    with pytest.raises(ValueError, match='context|bound|protocol'):
        _recover(source, bundle)


@pytest.mark.parametrize(
    'name,value',
    [
        ('selection', 'all'),
        ('structure_indices', 0),
        ('syntax', 'MolSysMT'),
        ('chemical_state', 'reference'),
        ('chemical_state_context', {}),
        ('submitted_atom_indices', [0]),
        ('provider_metadata', {}),
        ('pdb_file', 'other.pdb'),
        ('output_dir', 'other'),
        ('fpocket_cmd', 'false'),
    ],
)
def test_saved_selectors_and_execution_options_cannot_override(captured, name, value):
    source, _, bundle, _, _, _ = captured
    with pytest.raises((UnknownArgumentError, ArgumentError), match=name):
        _recover(source, bundle, **{name: value})


@pytest.mark.parametrize(
    'mutation',
    ['excluded_coordinates', 'excluded_label', 'chemistry', 'selected_coordinates'],
)
def test_full_source_mismatch_is_rejected(captured, mutation):
    source, _, bundle, _, _, _ = captured
    altered = msm.copy(source)
    if mutation.endswith('coordinates'):
        coordinates = puw.get_value(
            msm.get(altered, coordinates=True), to_unit='nm'
        ).copy()
        coordinates[1, 1 if mutation == 'excluded_coordinates' else 0, 0] += 0.1
        msm.set(altered, coordinates=puw.quantity(coordinates, 'nm'))
    elif mutation == 'excluded_label':
        names = list(msm.get(altered, element='atom', atom_name=True))
        names[1] = 'changed'
        msm.set(altered, element='atom', atom_name=names)
    else:
        msm.set(altered, formal_charge=[0, 1, 0, 0, 0], chemical_state=0)
    with pytest.raises(ValueError, match='context|coordinates|chemical'):
        _recover(altered, bundle)


@pytest.mark.parametrize(
    'field,value',
    [
        ('source_binding_protocol', True),
        ('source_binding_protocol', 2),
        ('source_context_artifact', 'input/submitted.pdb'),
        ('submitted_atom_indices', [0, True, 3, 4]),
        ('submitted_atom_indices', [0, 2, 2, 4]),
        ('submitted_atom_indices', [0, 2, 3, 99]),
        ('submitted_atom_indices', [4, 3, 2, 0]),
        ('atom_serial_to_index', {'1': 4, '2': 2, '3': 3, '4': 0}),
        ('structure_indices', 0),
        ('structure_indices', True),
        ('selection', 'all'),
        ('chemical_state_context', {'index': True}),
    ],
)
def test_rehashed_manifest_cannot_change_source_contract(
    captured, tmp_path, field, value
):
    source, output, _, _, _, _ = captured
    metadata = copy.deepcopy(output.run.metadata)
    metadata[field] = value
    bundle = _rewrite(output.run, tmp_path, metadata=metadata)
    with pytest.raises(ValueError):
        _recover(source, bundle)


@pytest.mark.parametrize(
    'provider,backend', [('pocketeer', 'library'), ('fpocket', 'native')]
)
def test_recovery_rejects_other_provider_or_local_backend(
    captured, tmp_path, provider, backend
):
    source, output, _, _, _, _ = captured
    bundle = _rewrite(output.run, tmp_path, provider=provider, backend=backend)
    with pytest.raises(ValueError, match='original|fpocket|backend'):
        _recover(source, bundle)


@pytest.mark.parametrize(
    'missing',
    [
        'source_context_artifact',
        'chemical_state_context',
        'submitted_atom_indices',
    ],
)
def test_insufficient_historical_context_is_not_invented(captured, tmp_path, missing):
    source, output, _, _, _, _ = captured
    metadata = output.run.metadata
    del metadata[missing]
    bundle = _rewrite(output.run, tmp_path, metadata=metadata)
    with pytest.raises(ValueError, match='context|protocol'):
        _recover(source, bundle)


@pytest.mark.parametrize(
    'content',
    [
        b'{"schema_version":1,"schema_version":1}',
        b'[]',
        b'{"coordinates":{"value":[NaN],"unit":"nm"}}',
    ],
)
def test_rehashed_context_artifact_requires_strict_schema(captured, tmp_path, content):
    source, output, _, _, _, _ = captured
    bundle = _rewrite(
        output.run,
        tmp_path,
        changes={
            'output/topomt_source_context.json': content,
        },
    )
    with pytest.raises(ValueError, match='context|saved|JSON'):
        _recover(source, bundle)


@pytest.mark.parametrize('entry', ['supplement_collision', 'symlink'])
def test_augmented_capture_does_not_hide_original_artifact_conflicts(captured, entry):
    source, _, _, submitted, output_dir, _ = captured
    if entry == 'supplement_collision':
        (output_dir / 'topomt_source_context.json').write_text('original evidence')
    else:
        (output_dir / 'original-link').symlink_to(submitted)
    with pytest.raises(ValueError, match='collid|Symbolic'):
        tmt.get_provider_output(
            source,
            method='fpocket',
            backend='files',
            pdb_file=submitted,
            output_dir=output_dir,
            selection=[0, 2, 3, 4],
            structure_indices=1,
            submitted_atom_indices=[0, 2, 3, 4],
            chemical_state='reference',
        )


def test_saved_leaf_rejects_overrides_before_reading(monkeypatch):
    from topomt.third_party.fpocket import files

    def forbidden(*args, **kwargs):
        pytest.fail('Bundle was read before selector override rejection.')

    monkeypatch.setattr(ProviderRun, 'load', forbidden)
    with pytest.raises(UnknownArgumentError, match='selection'):
        files.load_output(object(), bundle_file='absent.zip', selection='all')


@pytest.mark.parametrize('frame', ['all'])
def test_single_frame_legacy_selectors_are_recorded_unambiguously(
    captured, tmp_path, frame
):
    source, _, _, submitted, output_dir, _ = captured
    single_frame = msm.extract(source, structure_indices=1)
    output = tmt.get_provider_output(
        single_frame,
        method='fpocket',
        backend='files',
        pdb_file=submitted,
        output_dir=output_dir,
        selection=[0, 2, 3, 4],
        structure_indices=frame,
        submitted_atom_indices=[0, 2, 3, 4],
        chemical_state='reference',
    )
    assert output.run.metadata['structure_indices'] == 0
    bundle = tmp_path / 'single-frame.zip'
    output.run.save(bundle)
    assert _recover(single_frame, bundle).run == output.run


def test_available_empty_original_output_remains_empty(captured, tmp_path):
    source, _, _, submitted, output_dir, _ = captured
    for path in (output_dir / 'pockets').iterdir():
        path.unlink()
    (output_dir / 'submitted_info.txt').write_text('')
    output = tmt.get_provider_output(
        source,
        method='fpocket',
        backend='files',
        pdb_file=submitted,
        output_dir=output_dir,
        selection=[0, 2, 3, 4],
        structure_indices=1,
        submitted_atom_indices=[0, 2, 3, 4],
        chemical_state='reference',
    )
    assert output.records == ()
    bundle = tmp_path / 'empty.zip'
    output.run.save(bundle)
    recovered = _recover(source, bundle)
    assert recovered.records == ()
    assert recovered.pockets == ()
    assert recovered.run == output.run
    assert recovered.run.get_artifact('output/submitted_info.txt') == b''


def test_rehashed_bundle_cannot_omit_original_info(captured, tmp_path):
    source, output, _, _, _, _ = captured
    root = tmp_path / 'without-info'
    for name, data in output.run.artifacts:
        if name == 'output/submitted_info.txt':
            continue
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    run = ProviderRun.capture(
        'fpocket',
        output.run.backend,
        root / 'input/submitted.pdb',
        root / 'output',
        metadata=output.run.metadata,
    )
    bundle = tmp_path / 'without-info.zip'
    run.save(bundle)
    assert ProviderRun.load(bundle) == run
    with pytest.raises(ValueError, match='artifact.*absent'):
        _recover(source, bundle)


def test_fresh_process_recovers_without_original_engine_or_network(captured, tmp_path):
    source, output, bundle, _, _, _ = captured
    source_file = tmp_path / 'source.h5msm'
    msm.convert(source, to_form='file:h5msm', output_filename=source_file)
    script = """
import builtins, json, socket, subprocess, sys, urllib.request
import topomt as tmt
original_import = builtins.__import__
attempts = []
def guarded_import(name, *args, **kwargs):
    if name.split('.')[0] in {'fpocket', 'pocketeer', 'alphaspace2', 'pycasta', 'castpfoldpy'}:
        attempts.append(name)
        raise AssertionError('Original engine import attempted: ' + name)
    return original_import(name, *args, **kwargs)
def forbidden(*args, **kwargs):
    attempts.append('execution/network')
    raise AssertionError('Execution or network attempted')
builtins.__import__ = guarded_import
subprocess.run = forbidden
subprocess.Popen = forbidden
socket.create_connection = forbidden
urllib.request.urlopen = forbidden
result = tmt.get_provider_output(sys.argv[1], method='fpocket', backend='files', bundle_file=sys.argv[2])
assert result.run.run_id == sys.argv[3]
assert not attempts
print(json.dumps({'run_id': result.run.run_id, 'pockets': len(result.pockets), 'attempts': attempts}))
"""
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    completed = subprocess.run(
        [
            sys.executable,
            '-B',
            '-c',
            script,
            str(source_file),
            str(bundle),
            output.run.run_id,
        ],
        env=environment,
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(completed.stdout)['attempts'] == []
