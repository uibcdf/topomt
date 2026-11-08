"""MOLE protocol/contract controls; analytical fixtures are not detector evidence."""

import copy
import importlib
import json
import subprocess
import xml.etree.ElementTree as ET

import molsysmt as msm
import numpy as np
import pytest
from argdigest import UnknownArgumentError

import topomt as tmt
from tests.methods.pycasta.test_input_context import source
from tests.test_new_provider_parsers import captured
from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError

__all__ = ['source']


def mole_json():
    """Minimal analytical data using the inspected original JSON field layout."""
    mesh = {'Vertices': [0, 0, 0, 1, 0, 0, 0, 1, 0], 'Triangles': [0, 1, 2]}
    cavity = {
        'Type': 'Cavity',
        'Id': 1,
        'Volume': 12.0,
        'Depth': 2,
        'DepthLength': 3.0,
        'Boundary': {'Residues': ['ALA 10 A'], 'Properties': {}},
        'Inner': {'Residues': ['GLY 11 A'], 'Properties': {}},
        'Properties': {},
        'Mesh': {'Inner': mesh, 'Boundary': copy.deepcopy(mesh)},
    }
    void = copy.deepcopy(cavity)
    void['Type'] = 'Void'
    surface = copy.deepcopy(cavity)
    surface.update(Type='Surface', Id=0)
    channel = {
        'Type': 'Tunnel',
        'Id': '1',
        'Cavity': '1',
        'Auto': False,
        'Fingerprint': 'L1.00',
        'Properties': {'Hydropathy': -0.2},
        'Layers': {'ResidueFlow': ['ALA 10 A'], 'LayersInfo': []},
        'Profile': [
            dict(
                X=1,
                Y=2,
                Z=3,
                Radius=0.5,
                FreeRadius=0.6,
                BRadius=0.7,
                T=0,
                Distance=0,
                Charge=0,
            ),
            dict(
                X=2,
                Y=3,
                Z=4,
                Radius=0.8,
                FreeRadius=0.9,
                BRadius=1.0,
                T=1,
                Distance=1,
                Charge=0,
            ),
        ],
    }
    return {
        'Version': '2.5.26.10.26',
        'Config': {},
        'Timing': 1,
        'FoundOrigin': False,
        'Origins': {},
        'Channels': {'Tunnels': [channel], 'Pores': [], 'MergedPores': [], 'Paths': []},
        'Cavities': {'Cavities': [cavity], 'Voids': [void], 'Surface': surface},
    }


def parsed(tmp_path, data):
    run = captured(tmp_path, 'mole', {'json/data.json': json.dumps(data)})
    return importlib.import_module('topomt.third_party.mole.parser').parse_output(run)


def test_mole_keeps_original_feature_kinds_profiles_and_tetrahedral_volume(tmp_path):
    data = mole_json()
    output = parsed(tmp_path, data)
    assert output.pockets == ()
    assert len(output.channels) == 1 and len(output.cavities) == 2
    channel = output.channels[0]
    assert channel.source_id == 'Tunnels:1:1'
    assert channel.parent_source_ids == ('Cavities:1',)
    assert channel.atom_indices is None
    np.testing.assert_allclose(
        channel.geometries['centerline'].points_nm, [[0.1, 0.2, 0.3], [0.2, 0.3, 0.4]]
    )
    np.testing.assert_allclose(channel.geometries['centerline'].radii_nm, [0.05, 0.08])
    np.testing.assert_allclose(
        channel.geometries['free_radius_centerline'].radii_nm, [0.06, 0.09]
    )
    np.testing.assert_allclose(
        channel.geometries['b_radius_centerline'].radii_nm, [0.07, 0.1]
    )
    assert channel.measurements['profile_length'].original_value == 1
    cavity = output.cavities[0]
    assert cavity.source_id == 'Cavities:1'
    assert output.cavities[1].source_id == 'Voids:1'
    volume = cavity.measurements['tetrahedral_volume']
    assert volume.original_value == 12 and volume.original_unit == 'angstroms**3'
    assert 'tetrahedr' in volume.definition and 'solvent' in volume.definition
    assert cavity.fields['original']['Mesh'] == data['Cavities']['Cavities'][0]['Mesh']
    assert cavity.fields['mesh']['Inner']['vertices']['unit'] == 'angstroms'
    assert output.original_data == data
    detached = output.original_data
    detached['Channels'].clear()
    assert output.original_data == data


def test_mole_explicit_empty_is_not_missing_output(tmp_path):
    data = mole_json()
    data['Channels']['Tunnels'] = []
    data['Cavities']['Cavities'] = []
    data['Cavities']['Voids'] = []
    assert parsed(tmp_path, data).records == ()


def test_mole_preserves_channel_collections_with_distinct_original_ids(tmp_path):
    data = mole_json()
    for group, kind in [('Pores', 'Pore'), ('MergedPores', 'Pore'), ('Paths', 'Path')]:
        item = copy.deepcopy(data['Channels']['Tunnels'][0])
        item['Type'] = kind
        data['Channels'][group].append(item)
    output = parsed(tmp_path, data)
    assert {record.source_id for record in output.channels} == {
        'Tunnels:1:1',
        'Pores:1:1',
        'MergedPores:1:1',
        'Paths:1:1',
    }


@pytest.mark.parametrize(
    'damage',
    [
        'version',
        'group',
        'profile',
        'radius',
        'distance',
        'mesh',
        'duplicate',
        'volume',
    ],
)
def test_mole_rejects_incomplete_or_invalid_original_json(tmp_path, damage):
    data = mole_json()
    channel = data['Channels']['Tunnels'][0]
    if damage == 'version':
        data['Version'] = 'unknown'
    elif damage == 'group':
        del data['Channels']['Pores']
    elif damage == 'profile':
        channel['Profile'] = []
    elif damage == 'radius':
        channel['Profile'][0]['Radius'] = -1
    elif damage == 'distance':
        channel['Profile'][1]['Distance'] = -1
    elif damage == 'mesh':
        data['Cavities']['Cavities'][0]['Mesh']['Inner']['Triangles'] = [0, 1, 999]
    elif damage == 'duplicate':
        data['Channels']['Tunnels'].append(copy.deepcopy(channel))
    else:
        data['Cavities']['Cavities'][0]['Volume'] = float('nan')
    with pytest.raises(ValueError):
        parsed(tmp_path, data)


@pytest.mark.parametrize(
    'options',
    [
        {'unknown_option': 1},
        {'workers': True},
        {'workers': 0},
        {'memory_mb': 0},
        {'timeout': -1},
        {'backend': 'native'},
        {'origin': [0, 0, 0]},
        {'interior_threshold': -1},
        {'weight_function': 'arbitrary'},
        {'compute_pores': 'yes'},
        {'min_tunnel_length': -1},
        {'backend': 'files', 'bundle_file': 'absent.zip', 'probe_radius': 3},
    ],
)
def test_mole_invalid_options_precede_dependencies_and_source(options):
    with pytest.raises((ArgumentError, UnknownArgumentError)):
        tmt.get_provider_output(object(), method='mole', **options)


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_mole_recovery_checks_source_and_never_runs_engine(
    source, tmp_path, monkeypatch, policy
):
    runner = importlib.import_module('topomt.third_party.mole.runner')
    monkeypatch.setattr(runner, 'ensure_available', lambda options: None)

    def analytical_run(pdb, output, options):
        (output / 'json').mkdir()
        (output / 'json/data.json').write_text(json.dumps(mole_json()))
        return {'evidence_kind': 'analytical_protocol_fixture'}, {}

    monkeypatch.setattr(runner, 'run', analytical_run)
    original = tmt.get_provider_output(
        source,
        method='mole',
        selection=[0, 2, 4],
        structure_indices=1,
        chemical_state=1,
    )
    bundle = tmp_path / 'original.zip'
    original.save(bundle)
    assert original.run.metadata['selected_atom_indices'] == [0, 2, 4]

    def forbidden(*args, **kwargs):
        pytest.fail('Saved MOLE reconstruction invoked an engine')

    monkeypatch.setattr(subprocess, 'run', forbidden)
    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    with puw.context(standard_units=[*policy, 'radians']):
        recovered = tmt.load_provider_output(bundle, molecular_system=source)
        assert recovered.run == original.run
        for before, after in zip(original.records, recovered.records, strict=True):
            assert before.source_id == after.source_id
            assert before.geometries == after.geometries
            for name, measurement in before.measurements.items():
                np.testing.assert_allclose(
                    puw.get_value(measurement.value, to_unit=measurement.original_unit),
                    puw.get_value(
                        after.measurements[name].value,
                        to_unit=measurement.original_unit,
                    ),
                )
    changed = msm.copy(source)
    msm.set(
        changed,
        coordinates=msm.get(changed, coordinates=True) + puw.quantity([1, 0, 0], 'nm'),
    )
    with pytest.raises(ValueError, match='coordinates'):
        tmt.load_provider_output(bundle, molecular_system=changed)


def test_mole_absence_precedes_source_conversion(monkeypatch):
    runner = importlib.import_module('topomt.third_party.mole.runner')
    execution = importlib.import_module('topomt.third_party._execution')

    def missing(options):
        raise execution.ProviderUnavailableError(provider='mole', requirement='mole2')

    def forbidden(*args, **kwargs):
        pytest.fail('An absent MOLE reached molecular conversion')

    monkeypatch.setattr(runner, 'ensure_available', missing)
    monkeypatch.setattr(execution, 'reference_chemical_context', forbidden)
    with pytest.raises(execution.ProviderUnavailableError):
        tmt.get_provider_output(object(), method='mole')


def test_mole_failure_keeps_original_bytes_without_completed_recovery(
    source, tmp_path, monkeypatch
):
    runner = importlib.import_module('topomt.third_party.mole.runner')
    execution = importlib.import_module('topomt.third_party._execution')
    monkeypatch.setattr(runner, 'ensure_available', lambda options: None)

    def fail(pdb, output, options):
        (output / 'stderr.txt').write_text('Controlled MOLE execution failure\n')
        raise execution.ProviderExecutionError(
            provider='mole', reason='controlled failure'
        )

    monkeypatch.setattr(runner, 'run', fail)
    with pytest.raises(execution.ProviderExecutionError) as caught:
        tmt.get_provider_output(source, method='mole')
    failed = caught.value.run
    assert failed is not None
    assert (
        failed.get_artifact('output/stderr.txt')
        == b'Controlled MOLE execution failure\n'
    )
    bundle = tmp_path / 'failed.zip'
    failed.save(bundle)
    with pytest.raises(ValueError, match='protocol'):
        tmt.load_provider_output(bundle, molecular_system=source)


@pytest.mark.parametrize(
    'damage', [None, 'json', 'xml', 'exception', 'completion', 'version']
)
def test_mole_runner_requires_complete_original_success(tmp_path, monkeypatch, damage):
    runner = importlib.import_module('topomt.third_party.mole.runner')
    execution = importlib.import_module('topomt.third_party._execution')
    selected = tmp_path / 'selected mole'
    selected.write_text('Analytical command identity fixture')
    pdb = tmp_path / 'input.pdb'
    pdb.write_text('REMARK Analytical fixture\n')
    output = tmp_path / 'output'
    output.mkdir()
    checked = []

    def check(key, command):
        checked.append((key, command))
        return str(selected)

    def analytical_command(argv, directory, **kwargs):
        assert argv[0] == str(selected)
        assert kwargs['workers'] == 2
        assert kwargs['extra_env']['DOTNET_GCHeapHardLimit'] == '0x20000000'
        assert kwargs['extra_env']['DOTNET_PROCESSOR_COUNT'] == '2'
        config = ET.parse(argv[1])
        origins = config.find('Origins')
        point = config.find('Origins/Origin/Point')
        assert origins is not None and point is not None
        assert origins.attrib['Auto'] == '0'
        assert point.attrib == {
            'X': '1',
            'Y': '2',
            'Z': '3',
        }
        (directory / 'xml').mkdir()
        roots = {
            'tunnels': 'Tunnels',
            'pores': 'Pores',
            'pores_merged': 'MergedPores',
            'paths': 'Paths',
            'cavities': 'Cavities',
            'startpoints': 'StartPoints',
        }
        for name, tag in roots.items():
            element = ET.Element(
                tag, {} if name == 'startpoints' else {'Version': '2.5.26.10.26'}
            )
            if damage == 'exception' and name == 'tunnels':
                ET.SubElement(element, 'Exception', Text='controlled original failure')
            if damage != 'xml' or name != 'pores':
                ET.ElementTree(element).write(directory / 'xml' / (name + '.xml'))
        (directory / 'json').mkdir()
        if damage != 'json':
            (directory / 'json/data.json').write_text(json.dumps(mole_json()))
        version = 'unknown' if damage == 'version' else '2.5.26.10.26'
        text = f'WebChemistry Tunnels {version}, original\n'
        if damage != 'completion':
            text += 'Done in 00:00:01\n'
        (directory / 'stdout.txt').write_text(text)
        (directory / 'stderr.txt').write_text('')
        return 0

    monkeypatch.setattr(runner, 'executable_command', check)
    monkeypatch.setattr(runner, 'run_command', analytical_command)
    options = {
        'mole_cmd': str(selected),
        'workers': 2,
        'memory_mb': 512,
        'origin': [1, 2, 3],
    }
    if damage is not None:
        with pytest.raises(
            execution.ProviderExecutionError, match='incomplete original'
        ):
            runner.run(pdb, output, options)
    else:
        metadata, inputs = runner.run(pdb, output, options)
        assert metadata['parameters']['probe_radius'] == {
            'value': 3.0,
            'unit': 'angstroms',
        }
        assert metadata['origin'] == {'value': [1, 2, 3], 'unit': 'angstroms'}
        assert metadata['executable']['path'] == str(selected)
        assert 'config.xml' in inputs
    assert checked == [('mole', str(selected))]
