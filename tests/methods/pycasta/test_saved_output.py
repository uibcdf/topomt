"""Recover captured pyCASTA arrays without executing the original engine."""

import copy
import io
import json
import subprocess
import sys
from dataclasses import fields, is_dataclass

import molsysmt as msm
import numpy as np
import pytest

from tests.methods.pycasta.test_input_context import fake_original as fake_original
from tests.methods.pycasta.test_input_context import source as source
from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun
from topomt.third_party.output import _from_topography
from topomt.third_party.pycasta import library
from topomt.third_party.pycasta.output import PyCASTAOutput


@pytest.fixture
def captured(source, fake_original, tmp_path):
    root, _ = fake_original
    topography = library.get_topography(
        source,
        selection=[5, 3, 2, 1, 0],
        structure_indices=1,
        chemical_state=1,
        upstream_root=root,
    )
    output = _from_topography(topography, PyCASTAOutput)
    path = tmp_path / 'original.zip'
    output.run.save(path)
    return output, path


def recover(source, path):
    from topomt.third_party.pycasta.files import load_output

    return load_output(source, bundle_file=path)


def equal(actual, expected):
    if not isinstance(expected, (str, bytes, dict)) and puw.is_quantity(expected):
        np.testing.assert_allclose(
            puw.get_value(actual, to_unit=puw.get_unit(expected)),
            puw.get_value(expected),
            rtol=0,
            atol=1e-12,
        )
    elif is_dataclass(expected):
        for item in fields(expected):
            equal(getattr(actual, item.name), getattr(expected, item.name))
    elif isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key in expected:
            equal(actual[key], expected[key])
    elif isinstance(expected, (list, tuple)):
        assert len(actual) == len(expected)
        for left, right in zip(actual, expected, strict=True):
            equal(left, right)
    elif isinstance(expected, (float, np.floating)):
        np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)
    else:
        assert actual == expected


def rewrite(run, folder, mutate):
    metadata, artifacts = run.metadata, dict(run.artifacts)
    mutate(metadata, artifacts)
    for name, data in artifacts.items():
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    input_name = next(name for name in artifacts if name.startswith('input/'))
    run = ProviderRun.capture(
        run.provider, run.backend, folder / input_name, folder / 'output', metadata
    )
    path = folder / 'rewritten.zip'
    run.save(path)
    return path


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_saved_result_preserves_every_field_geometry_and_original_identity(
    source, captured, policy, monkeypatch
):
    original, path = captured

    def forbidden(*args, **kwargs):
        pytest.fail(
            'Recovery attempted discovery, triangulation or subprocess execution.'
        )

    monkeypatch.setattr(library, 'Delaunay', forbidden)
    monkeypatch.setattr(library, '_get_source_root', forbidden)
    monkeypatch.setattr(library.subprocess, 'run', forbidden)
    with puw.context(standard_units=[*policy, 'radians']):
        active = copy.deepcopy(puw.configure.report()['standard_units'])
        result = recover(source, path)
        assert result.run == original.run
        assert len(result.pockets) == len(original.pockets) == 1
        actual, expected = result.pockets[0], original.pockets[0]
        assert actual.source_id == expected.source_id == 'pycasta:0'
        assert actual.atom_indices == expected.atom_indices
        assert actual.atom_role == 'region_tetrahedron_vertices'
        assert actual.fields.keys() == expected.fields.keys()
        equal(actual.fields, expected.fields)
        np.testing.assert_allclose(
            result.input_points_nm, original.input_points_nm, rtol=0, atol=1e-12
        )
        equal(actual.geometries, expected.geometries)
        assert puw.configure.report()['standard_units'] == active


@pytest.mark.parametrize(
    'mutation', ['selected', 'unselected', 'charges', 'label', 'reference']
)
def test_changed_full_source_is_rejected(source, captured, mutation):
    source = msm.copy(source)
    if mutation in ('selected', 'unselected'):
        index = 0 if mutation == 'selected' else 4
        xyz = msm.get(source, selection=[index], structure_indices=1, coordinates=True)
        msm.set(
            source,
            selection=[index],
            structure_indices=1,
            coordinates=xyz + puw.quantity([[[0.01, 0, 0]]], 'nm'),
        )
    elif mutation == 'charges':
        msm.set(source, element='atom', formal_charge=1, chemical_state=1)
    elif mutation == 'label':
        msm.set(source, element='atom', selection=[4], atom_name='CHANGED')
    else:
        payload = msm.convert(
            source.chemical_states, to_form='molsysmt.ChemicalStatesDict'
        ).to_dict()
        payload['reference_chemical_state_index'] = 0
        source.chemical_states = msm.convert(
            msm.ChemicalStatesDict(payload), to_form='molsysmt.ChemicalStates'
        )
    with pytest.raises(ValueError):
        recover(source, captured[1])


@pytest.mark.parametrize(
    'mutation',
    [
        'legacy',
        'context',
        'protocol',
        'unit',
        'map_range',
        'map_bool',
        'map_duplicate',
        'protein_map',
        'tetra_range',
        'tetra_bool',
        'tetra_empty',
        'position',
        'npz_object',
        'npz_shape',
        'npz_nonfinite',
        'volume_count',
        'score_nan',
        'json_duplicate',
    ],
)
def test_malformed_saved_evidence_is_rejected(source, captured, tmp_path, mutation):
    def mutate(metadata, artifacts):
        if mutation == 'legacy':
            metadata.pop('chemical_state_context')
        elif mutation == 'context':
            artifacts.pop('output/topomt_source_context.json')
        elif mutation in ('protocol', 'unit'):
            if mutation == 'protocol':
                metadata.pop('output_protocol')
            else:
                metadata['output_protocol']['units']['protein_coords'] = 'pm'
        elif mutation.startswith('map_'):
            name = 'output/topomt_tetrahedron_indices.json'
            data = json.loads(artifacts[name])
            data['simplices'][0][0] = {
                'map_range': 999,
                'map_bool': True,
                'map_duplicate': data['simplices'][0][1],
            }[mutation]
            artifacts[name] = json.dumps(data).encode()
        elif mutation == 'protein_map':
            metadata['protein_atom_indices'][0] = metadata['selected_atom_indices'][-1]
        elif mutation in {'position', 'npz_object', 'npz_shape', 'npz_nonfinite'}:
            name = metadata['alpha_artifact']
            with np.load(io.BytesIO(artifacts[name]), allow_pickle=False) as arrays:
                values = {k: arrays[k] for k in arrays.files}
            if mutation == 'npz_object':
                values['protein_coords'] = values['protein_coords'].astype(object)
            elif mutation == 'npz_shape':
                values['tetrahedra'] = values['tetrahedra'][:, :, :2]
            else:
                values['tetrahedra'] = values['tetrahedra'].copy()
                values['tetrahedra'][0, 0, 0] = (
                    float('nan')
                    if mutation == 'npz_nonfinite'
                    else values['tetrahedra'][0, 0, 0] + 1
                )
            buffer = io.BytesIO()
            np.savez(buffer, **values)
            artifacts[name] = buffer.getvalue()
        else:
            name = 'output/topomt_returned_result.json'
            data = json.loads(artifacts[name])
            if mutation == 'json_duplicate':
                artifacts[name] = b'{"ranked_pockets":[],"ranked_pockets":[]}'
                return
            if mutation == 'volume_count':
                data['pocket_volumes'] = []
            elif mutation == 'score_nan':
                data['ranking_scores'] = [float('nan')]
            else:
                data['ranked_pockets'] = {
                    'tetra_range': [[999]],
                    'tetra_bool': [[True]],
                    'tetra_empty': [[]],
                }[mutation]
            artifacts[name] = json.dumps(data).encode()

    path = rewrite(captured[0].run, tmp_path / 'rewritten', mutate)
    with pytest.raises(ValueError):
        recover(source, path)


def test_recovered_result_survives_bundle_removal_and_source_mutation(source, captured):
    output = recover(source, captured[1])
    points = copy.deepcopy(output.input_points_nm)
    captured[1].unlink()
    msm.set(
        source,
        structure_indices=1,
        coordinates=msm.get(source, structure_indices=1, coordinates=True)
        + puw.quantity([10, 0, 0], 'nm'),
    )
    assert output.input_points_nm == points
    assert output.run == captured[0].run


def test_available_empty_original_pocket_list_remains_empty(source, captured, tmp_path):
    def mutate(metadata, artifacts):
        name = 'output/topomt_returned_result.json'
        result = json.loads(artifacts[name])
        for key in (
            'ranked_pockets',
            'pocket_volumes',
            'ranking_scores',
            'pocket_depths',
            'mouth_area',
            'mouth_perimeter',
            'representative_points',
            'validation_methods',
        ):
            result[key] = []
        artifacts[name] = json.dumps(result).encode()

    path = rewrite(captured[0].run, tmp_path / 'empty', mutate)
    output = recover(source, path)
    assert output.pockets == ()
    assert output.input_coordinates is not None


def test_fresh_reader_does_not_import_original_or_library(source, captured, tmp_path):
    path = tmp_path / 'source.h5msm'
    msm.convert(source, to_form='file:h5msm', output_filename=path)
    script = """
import importlib.abc
import sys
attempts=[]
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pycasta','config','run_analysis'} or fullname == 'topomt.third_party.pycasta.library':
            attempts.append(fullname)
            raise AssertionError('Reader attempted original/library import: '+fullname)
sys.meta_path.insert(0, Block())
import topomt as tmt
from topomt import pyunitwizard as puw
with puw.context(standard_units=['pm','fs','radians']):
    output=tmt.get_provider_output(sys.argv[1], method='pycasta', backend='files', bundle_file=sys.argv[2])
assert len(output.pockets)==1 and output.run.run_id==sys.argv[3]
assert not attempts
assert not {'pycasta','run_analysis','config'}.intersection(sys.modules)
"""
    result = subprocess.run(
        [
            sys.executable,
            '-c',
            script,
            str(path),
            str(captured[1]),
            captured[0].run.run_id,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
