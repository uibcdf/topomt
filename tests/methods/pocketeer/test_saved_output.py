"""Recover original results without importing or executing the optional engine."""

import copy
import json
import subprocess
import sys
import zipfile
from dataclasses import fields, is_dataclass

import molsysmt as msm
import numpy as np
import pytest
from argdigest import UnknownArgumentError

import topomt as tmt
from tests.methods.pocketeer.test_original_handoff import original as original
from tests.methods.pocketeer.test_original_handoff import (
    reference_output as reference_output,
)
from tests.methods.pocketeer.test_original_handoff import (
    source_profile as source_profile,
)
from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError
from topomt.provider_output import ProviderRun
from topomt.third_party.output import PocketGeometry


def _equal(actual, expected):
    if not isinstance(expected, (str, bytes)) and puw.is_quantity(expected):
        np.testing.assert_allclose(
            puw.get_value(actual, to_unit=puw.get_unit(expected)),
            puw.get_value(expected),
            rtol=0,
            atol=1e-12,
        )
    elif isinstance(expected, PocketGeometry):
        assert actual.kind == expected.kind and actual.definition == expected.definition
        np.testing.assert_allclose(
            actual.points_nm, expected.points_nm, rtol=0, atol=1e-12
        )
        if expected.radii_nm is None:
            assert actual.radii_nm is None
        else:
            np.testing.assert_allclose(
                actual.radii_nm, expected.radii_nm, rtol=0, atol=1e-12
            )
    elif is_dataclass(expected):
        for field in fields(expected):
            _equal(getattr(actual, field.name), getattr(expected, field.name))
    elif isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key in expected:
            _equal(actual[key], expected[key])
    elif isinstance(expected, (list, tuple)):
        assert len(actual) == len(expected)
        for left, right in zip(actual, expected):
            _equal(left, right)
    else:
        np.testing.assert_equal(actual, expected)


@pytest.fixture
def bundle(reference_output, tmp_path):
    path = tmp_path / 'original.zip'
    reference_output.run.save(path)
    return path


def _rewrite(run, folder, mutate):
    metadata = copy.deepcopy(run.metadata)
    artifacts = dict(run.artifacts)
    mutate(metadata, artifacts)
    inputs = [name for name in artifacts if name.startswith('input/')]
    assert len(inputs) == 1
    input_file = folder / 'submitted.pdb'
    input_file.write_bytes(artifacts[inputs[0]])
    output_dir = folder / 'results'
    output_dir.mkdir()
    for name, data in artifacts.items():
        if name.startswith('output/'):
            path = output_dir / name.removeprefix('output/')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    restored = ProviderRun.capture(
        run.provider, run.backend, input_file, output_dir, metadata=metadata
    )
    path = folder / 'rewritten.zip'
    restored.save(path)
    return path


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_saved_result_preserves_all_records_and_source_context(
    bundle, reference_output, source_profile, policy
):
    source, _, _ = source_profile
    with puw.context(standard_units=[*policy, 'radians']):
        result = tmt.get_provider_output(
            source, method='pocketeer', backend='FILES', bundle_file=bundle
        )
        assert result.run == reference_output.run
        _equal(result.records, reference_output.records)
        np.testing.assert_allclose(
            puw.get_value(result.input_coordinates, to_unit='nm'),
            puw.get_value(reference_output.input_coordinates, to_unit='nm'),
            rtol=0,
            atol=1e-12,
        )


@pytest.mark.parametrize('mutation', ['coordinates', 'unselected', 'charges', 'label'])
def test_changed_source_is_rejected(bundle, source_profile, mutation):
    source, selected, _ = source_profile
    source = msm.copy(source)
    if mutation in {'coordinates', 'unselected'}:
        index = (
            selected[0]
            if mutation == 'coordinates'
            else int(
                next(
                    i for i in range(msm.get(source, n_atoms=True)) if i not in selected
                )
            )
        )
        coordinates = msm.get(
            source, selection=[index], structure_indices=1, coordinates=True
        )
        msm.set(
            source,
            selection=[index],
            structure_indices=1,
            coordinates=coordinates + puw.quantity([0.01, 0, 0], 'nm'),
        )
    elif mutation == 'charges':
        msm.set(source, element='atom', formal_charge=1, chemical_state=0)
    else:
        msm.set(source, element='atom', selection=[0], atom_name='CHANGED')
    with pytest.raises(ValueError, match='context|coordinates'):
        tmt.get_provider_output(
            source, method='pocketeer', backend='files', bundle_file=bundle
        )


@pytest.mark.parametrize(
    'key', ['selection', 'structure_indices', 'chemical_state', 'r_min']
)
def test_saved_context_cannot_be_overridden(bundle, source_profile, key):
    with pytest.raises(UnknownArgumentError, match=key):
        tmt.get_provider_output(
            source_profile[0],
            method='pocketeer',
            backend='files',
            bundle_file=bundle,
            **{key: 0},
        )


@pytest.mark.parametrize('value', [None, '', True, 1, 'bad\0path'])
def test_bundle_path_is_digested_before_file_work(source_profile, value):
    with pytest.raises(ArgumentError, match='bundle_file'):
        tmt.get_provider_output(
            source_profile[0], method='pocketeer', backend='files', bundle_file=value
        )


def test_missing_source_is_rejected_before_opening_bundle():
    with pytest.raises(ArgumentError, match='molecular_system'):
        tmt.get_provider_output(
            method='pocketeer', backend='files', bundle_file='absent.zip'
        )


def test_library_rejects_saved_file_options():
    with pytest.raises(UnknownArgumentError, match='bundle_file'):
        tmt.get_provider_output(
            object(), method='pocketeer', backend='library', bundle_file='absent.zip'
        )


@pytest.mark.parametrize(
    'field',
    ['chemical_state_context', 'selected_atom_indices', 'filtered_input_atom_indices'],
)
def test_missing_saved_context_is_rejected(
    reference_output, source_profile, tmp_path, field
):
    path = _rewrite(
        reference_output.run, tmp_path, lambda metadata, _: metadata.pop(field)
    )
    with pytest.raises(ValueError, match='context|indices'):
        tmt.get_provider_output(
            source_profile[0], method='pocketeer', backend='files', bundle_file=path
        )


@pytest.mark.parametrize(
    'field', ['selected_atom_indices', 'filtered_input_atom_indices']
)
def test_duplicate_saved_atom_maps_are_rejected(
    reference_output, source_profile, tmp_path, field
):
    def mutate(metadata, _):
        metadata[field][1] = metadata[field][0]

    path = _rewrite(reference_output.run, tmp_path, mutate)
    with pytest.raises(ValueError, match='indices|map'):
        tmt.get_provider_output(
            source_profile[0], method='pocketeer', backend='files', bundle_file=path
        )


@pytest.mark.parametrize(
    'mutation',
    [
        'mask_length',
        'mask_type',
        'mask_id',
        'sphere_count',
        'sphere_index',
        'nan',
        'negative_radius',
        'duplicate_id',
    ],
)
def test_invalid_original_records_are_rejected(
    reference_output, source_profile, tmp_path, mutation
):
    def mutate(_, artifacts):
        pockets = json.loads(artifacts['output/pocketeer_pockets.json'])
        masks = json.loads(artifacts['output/topomt_masks.json'])
        if mutation == 'mask_length':
            masks['pockets'][0]['mask'].pop()
        elif mutation == 'mask_type':
            masks['pockets'][0]['mask'][0] = 1
        elif mutation == 'mask_id':
            masks['pockets'][0]['pocket_id'] = 9999
        elif mutation == 'sphere_count':
            pockets[0]['n_spheres'] += 1
        elif mutation == 'sphere_index':
            pockets[0]['spheres'][0]['atom_indices'][0] = 10**9
        elif mutation == 'nan':
            pockets[0]['centroid'][0] = float('nan')
        elif mutation == 'negative_radius':
            pockets[0]['spheres'][0]['radius'] = -1
        else:
            pockets[1]['pocket_id'] = pockets[0]['pocket_id']
        artifacts['output/pocketeer_pockets.json'] = json.dumps(pockets).encode()
        artifacts['output/topomt_masks.json'] = json.dumps(masks).encode()

    path = _rewrite(reference_output.run, tmp_path, mutate)
    with pytest.raises(ValueError, match='Pocketeer'):
        tmt.get_provider_output(
            source_profile[0], method='pocketeer', backend='files', bundle_file=path
        )


def test_engine_free_recovery(bundle, source_profile, reference_output, tmp_path):
    source_path = tmp_path / 'source.h5msm'
    msm.convert(source_profile[0], to_form='file:h5msm', output_filename=source_path)
    script = """
import importlib.abc
import sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pocketeer', 'biotite'}:
            raise AssertionError('Saved-result route attempted optional-engine import: '+fullname)
sys.meta_path.insert(0, Block())
import topomt as tmt
result=tmt.get_provider_output(sys.argv[1],method='pocketeer',backend='files',bundle_file=sys.argv[2])
assert [r.source_id for r in result.pockets] == __import__('json').loads(sys.argv[3])
assert not {'pocketeer','biotite'}.intersection(sys.modules)
"""
    result = subprocess.run(
        [
            sys.executable,
            '-c',
            script,
            str(source_path),
            str(bundle),
            json.dumps([r.source_id for r in reference_output.pockets]),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize('empty_membership', [False, True])
def test_available_empty_results_are_preserved(
    reference_output, source_profile, tmp_path, empty_membership
):
    def mutate(_, artifacts):
        if empty_membership:
            masks = json.loads(artifacts['output/topomt_masks.json'])
            for record in masks['pockets']:
                record['mask'] = [False] * len(record['mask'])
        else:
            artifacts['output/pocketeer_pockets.json'] = b'[]'
            masks = {'schema_version': 1, 'pockets': []}
        artifacts['output/topomt_masks.json'] = json.dumps(masks).encode()

    path = _rewrite(reference_output.run, tmp_path, mutate)
    result = tmt.get_provider_output(
        source_profile[0], method='pocketeer', backend='files', bundle_file=path
    )
    if empty_membership:
        assert result.pockets
        assert all(pocket.atom_indices == () for pocket in result.pockets)
        assert all(
            pocket.atom_role == 'pocket_residue_atoms' for pocket in result.pockets
        )
    else:
        assert result.pockets == ()


@pytest.mark.parametrize(
    'mutation', ['missing', 'unit', 'schema', 'atom_label', 'coordinates']
)
def test_invalid_source_supplement_is_rejected(
    reference_output, source_profile, tmp_path, mutation
):
    def mutate(_, artifacts):
        name = 'output/topomt_source_context.json'
        if mutation == 'missing':
            artifacts.pop(name)
            return
        context = json.loads(artifacts[name])
        if mutation == 'unit':
            context['coordinates']['unit'] = 'pm'
        elif mutation == 'schema':
            context['schema_version'] = 2
        elif mutation == 'atom_label':
            context['atom_attributes']['atom_name'][0] = 'CHANGED'
        else:
            context['coordinates']['value'][0][0] += 1
        artifacts[name] = json.dumps(context).encode()

    path = _rewrite(reference_output.run, tmp_path, mutate)
    with pytest.raises(ValueError, match='context|coordinates'):
        tmt.get_provider_output(
            source_profile[0], method='pocketeer', backend='files', bundle_file=path
        )


def test_recovered_results_survive_input_removal_and_source_mutation(
    bundle, source_profile
):
    source = msm.copy(source_profile[0])
    result = tmt.get_provider_output(
        source, method='pocketeer', backend='files', bundle_file=bundle
    )
    coordinates = puw.get_value(result.input_coordinates, to_unit='nm')
    frozen = result.records
    bundle.unlink()
    msm.set(
        source,
        structure_indices=1,
        coordinates=msm.get(source, structure_indices=1, coordinates=True)
        + puw.quantity([10, 0, 0], 'nm'),
    )
    np.testing.assert_array_equal(
        puw.get_value(result.input_coordinates, to_unit='nm'), coordinates
    )
    _equal(result.records, frozen)


@pytest.mark.parametrize('missing', [True, False])
def test_saved_output_units_require_an_explicit_matching_protocol(
    reference_output, source_profile, tmp_path, missing
):
    def mutate(metadata, _):
        if missing:
            metadata.pop('output_protocol', None)
        else:
            metadata['output_protocol'] = {
                'schema_version': 1,
                'artifact': 'output/pocketeer_pockets.json',
                'units': {'volume': 'nm**3'},
            }

    path = _rewrite(reference_output.run, tmp_path, mutate)
    with pytest.raises(ValueError, match='protocol|units'):
        tmt.get_provider_output(
            source_profile[0], method='pocketeer', backend='files', bundle_file=path
        )


@pytest.mark.parametrize(
    'mutation',
    [
        'duplicate_keys',
        'unknown_field',
        'boolean_id',
        'boolean_center',
        'overflow',
        'residue_count',
    ],
)
def test_ambiguous_or_unsupported_original_json_is_rejected(
    reference_output, source_profile, tmp_path, mutation
):
    def mutate(_, artifacts):
        name = 'output/pocketeer_pockets.json'
        if mutation == 'duplicate_keys':
            artifacts[name] = artifacts[name].replace(
                b'"pocket_id":', b'"pocket_id": 0, "pocket_id":', 1
            )
            return
        pockets = json.loads(artifacts[name])
        if mutation == 'unknown_field':
            pockets[0]['uninterpreted_new_field'] = 1
        elif mutation == 'boolean_id':
            pockets[0]['pocket_id'] = True
        elif mutation == 'boolean_center':
            pockets[0]['centroid'][0] = True
        elif mutation == 'overflow':
            pockets[0]['volume'] = 10**400
        else:
            pockets[0]['n_residues'] += 1
        artifacts[name] = json.dumps(pockets).encode()

    path = _rewrite(reference_output.run, tmp_path, mutate)
    with pytest.raises(ValueError, match='Pocketeer'):
        tmt.get_provider_output(
            source_profile[0], method='pocketeer', backend='files', bundle_file=path
        )


def test_bundle_checksum_is_verified(bundle, source_profile, tmp_path):
    tampered = tmp_path / 'tampered.zip'
    with zipfile.ZipFile(bundle) as original, zipfile.ZipFile(tampered, 'w') as target:
        for name in original.namelist():
            data = original.read(name)
            if name == 'output/pocketeer_pockets.json':
                data += b' '
            target.writestr(name, data)
    with pytest.raises(ValueError, match='checksum'):
        tmt.get_provider_output(
            source_profile[0], method='pocketeer', backend='files', bundle_file=tampered
        )


@pytest.mark.parametrize('field', ['reference_index', 'state_count'])
def test_saved_chemical_context_rejects_numerically_equal_wrong_types(
    reference_output, source_profile, tmp_path, field
):
    def mutate(metadata, artifacts):
        metadata['chemical_state_context'][field] = float(
            metadata['chemical_state_context'][field]
        )

    path = _rewrite(reference_output.run, tmp_path, mutate)
    with pytest.raises(ValueError, match='chemical'):
        tmt.get_provider_output(
            source_profile[0], method='pocketeer', backend='files', bundle_file=path
        )


def test_saved_coordinate_payload_rejects_numeric_strings(
    reference_output, source_profile, tmp_path
):
    def mutate(metadata, artifacts):
        name = 'output/topomt_source_context.json'
        context = json.loads(artifacts[name])
        context['coordinates']['value'][0][0] = str(
            context['coordinates']['value'][0][0]
        )
        artifacts[name] = json.dumps(context).encode()

    path = _rewrite(reference_output.run, tmp_path, mutate)
    with pytest.raises(ValueError, match='context'):
        tmt.get_provider_output(
            source_profile[0], method='pocketeer', backend='files', bundle_file=path
        )
