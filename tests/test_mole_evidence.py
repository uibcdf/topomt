"""Replay original MOLE bytes without an engine under two quantity policies."""

import json
import subprocess
from pathlib import Path

import numpy as np
import pytest

import topomt as tmt
from topomt import pyunitwizard as puw

ROOT = Path(__file__).parent / 'data/original_local'


@pytest.mark.parametrize(
    'bundle,source,channels,cavities',
    [
        ('mole.zip', 'source.pdb', 2, 13),
        ('mole-1tqn.zip', 'mole_1tqn.cif', 21, 15),
        ('mole-empty.zip', 'source.pdb', 0, 0),
    ],
)
@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_original_mole_evidence_reconstructs_without_engine(
    bundle, source, channels, cavities, policy, monkeypatch
):
    def forbidden(*args, **kwargs):
        pytest.fail('Saved MOLE reconstruction attempted original execution')

    monkeypatch.setattr(subprocess, 'run', forbidden)
    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    with puw.context(standard_units=[*policy, 'radians']):
        output = tmt.load_provider_output(
            ROOT / bundle, molecular_system=str(ROOT / source)
        )
        assert len(output.channels) == channels
        assert len(output.cavities) == cavities
        assert output.pockets == ()
        assert output.run.metadata['execution_status'] == 'completed'
        assert output.run.metadata['version'] == '2.5.26.10.26'
        original = json.loads(output.run.get_artifact('output/json/data.json'))
        assert output.original_data == original
        for record in output.channels:
            raw = record.fields['original']
            assert raw in original['Channels'][record.fields['source_group']]
            expected = [[point[axis] for axis in 'XYZ'] for point in raw['Profile']]
            for field, kind in [
                ('Radius', 'centerline'),
                ('FreeRadius', 'free_radius_centerline'),
                ('BRadius', 'b_radius_centerline'),
            ]:
                geometry = record.geometries[kind]
                np.testing.assert_allclose(
                    puw.get_value(geometry.coordinates, to_unit='angstroms'), expected
                )
                np.testing.assert_allclose(
                    puw.get_value(geometry.radii, to_unit='angstroms'),
                    [point[field] for point in raw['Profile']],
                )
            assert (
                record.measurements['profile_length'].original_value
                == raw['Profile'][-1]['Distance']
            )
        for record in output.cavities:
            raw = record.fields['original']
            assert raw in original['Cavities'][record.fields['source_group']]
            measurement = record.measurements['tetrahedral_volume']
            assert measurement.original_value == raw['Volume']
            np.testing.assert_allclose(
                puw.get_value(measurement.value, to_unit='angstroms**3'), raw['Volume']
            )
            for part in ('Inner', 'Boundary'):
                geometry = record.geometries[part.lower() + '_mesh_vertices']
                np.testing.assert_allclose(
                    puw.get_value(geometry.coordinates, to_unit='angstroms'),
                    np.asarray(raw['Mesh'][part]['Vertices']).reshape(-1, 3),
                )
        if bundle == 'mole-1tqn.zip':
            assert {key: len(value) for key, value in original['Channels'].items()} == {
                'Tunnels': 14,
                'Pores': 3,
                'MergedPores': 4,
                'Paths': 0,
            }
