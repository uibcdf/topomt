"""Recover genuine archived original outputs without AlphaSpace2 or MDTraj."""

import copy
import hashlib
import json
import subprocess
import sys
import zipfile
from dataclasses import fields, is_dataclass
from pathlib import Path

import molsysmt as msm
import numpy as np
import pytest
from argdigest import UnknownArgumentError

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError
from topomt.provider_output import ProviderRun


def _compare(actual, expected):
    if isinstance(expected, dict) and '_quantity' in expected:
        _compare(puw.get_value(actual, to_unit=expected['unit']), expected['_quantity'])
    elif isinstance(expected, dict) and '_nonfinite' in expected:
        np.testing.assert_equal(actual, float(expected['_nonfinite']))
    elif isinstance(expected, dict) and '_set' in expected:
        assert sorted(actual, key=repr) == expected['_set']
    elif is_dataclass(actual):
        _compare({f.name: getattr(actual, f.name) for f in fields(actual)}, expected)
    elif isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key in expected:
            _compare(actual[key], expected[key])
    elif isinstance(expected, list):
        assert len(actual) == len(expected)
        for left, right in zip(actual, expected):
            _compare(left, right)
    elif isinstance(expected, float):
        np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)
    else:
        assert actual == expected


@pytest.fixture(scope='module')
def captured(tmp_path_factory):
    folder = tmp_path_factory.mktemp('original_alphaspace2_saved')
    archive = Path(__file__).parent / 'data/saved_outputs.zip'
    with zipfile.ZipFile(archive) as z:
        manifest = json.loads(z.read('manifest.json'))
        assert manifest['producer'] == '4bb881d1d6f0f4e542dd28e0e5947f9bf066127c'
        for name, row in manifest['members'].items():
            data = z.read(name)
            assert len(data) == row['bytes']
            assert hashlib.sha256(data).hexdigest() == row['sha256']
            path = folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    result = {}
    for tag in ('bound', 'unbound'):
        root = folder / tag
        result[tag] = {
            'root': root,
            'bundle': root / 'original.zip',
            'source': msm.convert(root / 'receptor.h5msm', to_form='molsysmt.MolSys'),
            'binder': msm.convert(root / 'binder.h5msm', to_form='molsysmt.MolSys')
            if tag == 'bound'
            else None,
            'witness': json.loads((root / 'legacy_fields.json').read_text()),
        }
    return result


def recover(case, **options):
    return tmt.get_provider_output(
        case['source'],
        method='alphaspace2',
        backend='files',
        bundle_file=case['bundle'],
        binder=case['binder'],
        **options,
    )


def rewrite(case, folder, mutate):
    run = ProviderRun.load(case['bundle'])
    metadata, artifacts = copy.deepcopy(run.metadata), dict(run.artifacts)
    mutate(metadata, artifacts)
    original_input = run.metadata['receptor_input_artifact']
    for name, data in artifacts.items():
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    output = folder / 'output'
    output.mkdir(exist_ok=True)
    additional = {
        n.removeprefix('input/'): folder / n
        for n in artifacts
        if n.startswith('input/') and n != original_input
    }
    captured_run = ProviderRun.capture(
        run.provider,
        run.backend,
        folder / original_input,
        output,
        metadata,
        additional_inputs=additional,
    )
    path = folder / 'rewritten.zip'
    captured_run.save(path)
    return {**case, 'bundle': path}


@pytest.mark.parametrize('tag', ['bound', 'unbound'])
@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_saved_records_preserve_legacy_fields_and_original_run(captured, tag, policy):
    case = captured[tag]
    with puw.context(standard_units=[*policy, 'radians']):
        output = recover(case)
        assert output.run == ProviderRun.load(case['bundle'])
        witness = case['witness']
        _compare(output.input_points_nm, witness['input_points_nm'])
        assert len(output.records) == len(witness['records']) == 61
        for actual, expected in zip(output.records, witness['records']):
            assert actual.record_kind == 'pocket' and actual.run == output.run
            assert actual.run_id == output.run.run_id
            _compare(
                {
                    name: getattr(actual, name)
                    for name in (
                        'source_id',
                        'atom_indices',
                        'atom_labels',
                        'atom_role',
                        'parent_source_ids',
                        'fields',
                        'geometries',
                    )
                },
                expected,
            )


@pytest.mark.parametrize('role', ['source', 'binder'])
@pytest.mark.parametrize(
    'mutation', ['coordinates', 'unselected', 'charges', 'label', 'reference']
)
def test_changed_either_source_is_rejected(captured, role, mutation):
    case = {**captured['bound'], role: msm.copy(captured['bound'][role])}
    value = case[role]
    frame = 1 if role == 'source' else 0
    state = 1 if role == 'source' else 0
    if mutation in {'coordinates', 'unselected'}:
        metadata = ProviderRun.load(case['bundle']).metadata
        selected = (
            metadata['selected_atom_indices']
            if role == 'source'
            else metadata['binder']['selected_atom_indices']
        )
        index = (
            selected[0]
            if mutation == 'coordinates'
            else next(
                i for i in range(msm.get(value, n_atoms=True)) if i not in selected
            )
        )
        xyz = msm.get(
            value, selection=[index], structure_indices=frame, coordinates=True
        )
        msm.set(
            value,
            selection=[index],
            structure_indices=frame,
            coordinates=xyz + puw.quantity([[[0.01, 0, 0]]], 'nm'),
        )
    elif mutation == 'charges':
        msm.set(value, element='atom', formal_charge=1, chemical_state=state)
    elif mutation == 'label':
        msm.set(value, element='atom', selection=[0], atom_name='CHANGED')
    else:
        payload = msm.convert(
            value.chemical_states, to_form='molsysmt.ChemicalStatesDict'
        ).to_dict()
        payload['reference_chemical_state_index'] = 1 - state
        value.chemical_states = msm.convert(
            msm.ChemicalStatesDict(payload), to_form='molsysmt.ChemicalStates'
        )
    with pytest.raises(ValueError):
        recover(case)


@pytest.mark.parametrize(
    'key',
    [
        'selection',
        'structure_indices',
        'chemical_state',
        'min_vertices',
        'upstream_root',
        'binder_selection',
        'binder_structure_indices',
        'binder_chemical_state',
    ],
)
def test_saved_execution_context_cannot_be_overridden(captured, key):
    with pytest.raises(UnknownArgumentError, match=key):
        recover(captured['bound'], **{key: 0})


@pytest.mark.parametrize('value', [None, '', True, 1, 'bad\0path'])
def test_bundle_path_is_digested_before_file_work(captured, value):
    case = {**captured['bound'], 'bundle': value}
    with pytest.raises(ArgumentError, match='bundle_file'):
        recover(case)


def test_bound_source_presence_is_explicit(captured):
    with pytest.raises(ValueError, match='binder'):
        recover({**captured['bound'], 'binder': None})
    with pytest.raises(ValueError, match='binder'):
        recover({**captured['unbound'], 'binder': captured['bound']['binder']})


@pytest.mark.parametrize(
    'mutation',
    [
        'missing_context',
        'missing_chemical',
        'chemical_bool',
        'chemical_float',
        'frame',
        'map',
        'serial_map',
        'filter',
        'protocol',
        'protocol_schema',
    ],
)
def test_invalid_saved_metadata_is_rejected(captured, tmp_path, mutation):
    def corrupt(metadata, artifacts):
        if mutation == 'missing_context':
            artifacts.pop(metadata['source_context_artifact'])
        elif mutation == 'missing_chemical':
            metadata.pop('chemical_state_context')
        elif mutation == 'chemical_bool':
            metadata['chemical_state_context']['reference_index'] = True
        elif mutation == 'chemical_float':
            metadata['chemical_state_context']['state_count'] = 2.0
        elif mutation == 'frame':
            metadata['binder']['structure_indices'] = True
        elif mutation == 'map':
            metadata['selected_atom_indices'].reverse()
        elif mutation == 'serial_map':
            metadata['atom_serial_to_index'] = {'1': False}
        elif mutation == 'filter':
            metadata['min_vertices'] = True
        elif mutation == 'protocol':
            metadata['output_protocol']['units']['_alpha_xyz'] = 'nm'
        else:
            metadata['output_protocol']['schema_version'] = True

    with pytest.raises(ValueError):
        recover(rewrite(captured['bound'], tmp_path, corrupt))


@pytest.mark.parametrize('role', ['source', 'binder'])
@pytest.mark.parametrize('mutation', ['missing', 'unit', 'schema', 'coordinate_type'])
def test_saved_source_supplement_schema_is_strict(captured, tmp_path, role, mutation):
    def corrupt(metadata, artifacts):
        context = metadata if role == 'source' else metadata['binder']
        name = context['source_context_artifact']
        if mutation == 'missing':
            artifacts.pop(name)
            return
        record = json.loads(artifacts[name])
        if mutation == 'unit':
            record['coordinates']['unit'] = 'pm'
        elif mutation == 'schema':
            record['schema_version'] = True
        else:
            record['coordinates']['value'][0][0] = str(
                record['coordinates']['value'][0][0]
            )
        artifacts[name] = json.dumps(record).encode()

    with pytest.raises(ValueError):
        recover(rewrite(captured['bound'], tmp_path, corrupt))


@pytest.mark.parametrize(
    'mutation',
    [
        'missing',
        'schema',
        'unknown',
        'duplicate_key',
        'nan_constant',
        'alpha_shape',
        'negative_radius',
        'lining_bool',
        'lining_bounds',
        'duplicate_lining',
        'alpha_contact',
        'beta_group',
        'pocket_beta',
        'property_index',
        'property_space',
        'invalid_nonfinite',
        'nonfinite_volume',
        'score_shape',
        'labels',
        'radius_protocol',
    ],
)
def test_invalid_original_snapshot_is_rejected(captured, tmp_path, mutation):
    def corrupt(metadata, artifacts):
        name = 'output/topomt_snapshot.json'
        if mutation == 'missing':
            artifacts.pop(name)
            return
        data = json.loads(artifacts[name])
        if mutation == 'duplicate_key':
            artifacts[name] = b'{"schema_version":1,' + artifacts[name][1:]
            return
        if mutation == 'schema':
            data['schema_version'] = 2
        elif mutation == 'unknown':
            data['future_field'] = 0
        elif mutation == 'nan_constant':
            data['_alpha_radii'][0] = float('nan')
        elif mutation == 'alpha_shape':
            data['_alpha_xyz'][0] = [1, 2]
        elif mutation == 'negative_radius':
            data['_alpha_radii'][0] = -1
        elif mutation == 'lining_bool':
            data['_alpha_lining'][0][0] = True
        elif mutation == 'lining_bounds':
            data['_alpha_lining'][0][0] = 10**9
        elif mutation == 'duplicate_lining':
            data['_alpha_lining'][0] = [0, 0, 1, 2]
        elif mutation == 'alpha_contact':
            data['_alpha_contact'][0] = 1
        elif mutation == 'beta_group':
            data['_beta_alpha_index_list'][0] = [10**9]
        elif mutation == 'pocket_beta':
            data['_pocket_beta_index_list'][0] = []
        elif mutation == 'property_index':
            data['pocket_properties'][0]['index'] = True
        elif mutation == 'property_space':
            data['pocket_properties'][0]['space'] += 100
        elif mutation == 'invalid_nonfinite':
            data['beta_properties'][0]['occupancy_nonpolar'] = {'nonfinite': 'wrong'}
        elif mutation == 'nonfinite_volume':
            data['pocket_properties'][0]['occupied_space'] = {'nonfinite': 'nan'}
        elif mutation == 'score_shape':
            data['_beta_scores'][0] = [0, 1]
        elif mutation == 'labels':
            data['atom_names'].pop()
        elif mutation == 'radius_protocol':
            data['_alpha_radii'][0] *= 0.1
        artifacts[name] = json.dumps(data).encode()

    with pytest.raises(ValueError):
        recover(rewrite(captured['bound'], tmp_path, corrupt))


def test_saved_filter_can_preserve_available_empty_output(captured, tmp_path):
    def high_filter(metadata, artifacts):
        metadata['min_vertices'] = 10**6

    result = recover(rewrite(captured['bound'], tmp_path, high_filter))
    assert result.pockets == () and result.input_points_nm


def test_recovery_never_imports_original_engines(captured):
    case = captured['bound']
    script = """
import importlib.abc,sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split('.')[0] in {'alphaspace2','mdtraj'}:
            raise AssertionError('Optional engine imported by saved reader: '+fullname)
sys.meta_path.insert(0,Block())
import topomt as tmt
result=tmt.get_provider_output(sys.argv[1],method='alphaspace2',backend='files',bundle_file=sys.argv[3],binder=sys.argv[2])
assert len(result.pockets)==61
assert not {'alphaspace2','mdtraj'}.intersection(sys.modules)
"""
    result = subprocess.run(
        [
            sys.executable,
            '-c',
            script,
            str(case['root'] / 'receptor.h5msm'),
            str(case['root'] / 'binder.h5msm'),
            str(case['bundle']),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize('tag', ['bound', 'unbound'])
@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_current_original_converter_preserves_captured_legacy_fields(
    captured, tag, policy
):
    pytest.importorskip('alphaspace2')
    pytest.importorskip('mdtraj')
    case = captured[tag]
    old_run = ProviderRun.load(case['bundle'])
    metadata = old_run.metadata
    options = {
        key: metadata[key] for key in ('selection', 'structure_indices', 'min_vertices')
    }
    options['chemical_state'] = metadata['chemical_state_context']['index']
    if case['binder'] is not None:
        context = metadata['binder']
        options.update(
            binder=case['binder'],
            binder_selection=context['selection'],
            binder_structure_indices=context['structure_indices'],
            binder_chemical_state=context['chemical_state_context']['index'],
        )
    with puw.context(standard_units=[*policy, 'radians']):
        current = tmt.get_provider_output(
            case['source'], method='alphaspace2', **options
        )

    def compare_identity(value):
        # Compare attributed run identity by role without rewriting either real
        # run, original artifact or retained witness bytes.
        if isinstance(value, str) and value == old_run.run_id:
            return current.run.run_id
        if isinstance(value, dict):
            return {k: compare_identity(v) for k, v in value.items()}
        if isinstance(value, list):
            return [compare_identity(v) for v in value]
        return value

    expected = compare_identity(case['witness']['records'])
    assert len(current.records) == len(expected)
    for actual, record in zip(current.records, expected):
        _compare(
            {
                name: getattr(actual, name)
                for name in (
                    'source_id',
                    'atom_indices',
                    'atom_labels',
                    'atom_role',
                    'parent_source_ids',
                    'fields',
                    'geometries',
                )
            },
            record,
        )


def test_recovered_result_survives_bundle_deletion_and_real_source_changes(
    captured, tmp_path
):
    case = captured['bound']
    bundle = tmp_path / 'copied.zip'
    bundle.write_bytes(case['bundle'].read_bytes())
    case = {
        **case,
        'source': msm.copy(case['source']),
        'binder': msm.copy(case['binder']),
        'bundle': bundle,
    }
    result = recover(case)
    bundle.unlink()
    for role, frame, state in [('source', 1, 1), ('binder', 0, 0)]:
        value = case[role]
        msm.set(
            value,
            structure_indices=frame,
            coordinates=msm.get(value, structure_indices=frame, coordinates=True)
            + puw.quantity([[[1.0, 0.0, 0.0]]], 'nm'),
        )
        msm.set(value, element='atom', formal_charge=1, chemical_state=state)
    _compare(result.input_points_nm, case['witness']['input_points_nm'])
    for actual, expected in zip(result.records, case['witness']['records']):
        _compare(
            {
                name: getattr(actual, name)
                for name in (
                    'source_id',
                    'atom_indices',
                    'atom_labels',
                    'atom_role',
                    'parent_source_ids',
                    'fields',
                    'geometries',
                )
            },
            expected,
        )
