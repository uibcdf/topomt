"""Replay bounded original CLI evidence; no engine or network is required."""

import csv
import io
import json
import re
import subprocess
import tomllib
from pathlib import Path

import molsysmt as msm
import numpy as np
import pytest

import topomt as tmt
from topomt import pyunitwizard as puw

ROOT = Path(__file__).parent / 'data/original_local'


@pytest.fixture(scope='module')
def original_source():
    return msm.convert(ROOT / 'source.pdb', to_form='molsysmt.MolSys')


@pytest.mark.parametrize(
    'provider,kind,count',
    [
        ('caver', 'channel', 47),
        ('p2rank', 'site', 5),
        ('ghecom', 'pocket', 41),
        ('pykvfinder', 'cavity', 12),
    ],
)
@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_original_cli_evidence_reconstructs_without_engine(
    original_source, provider, kind, count, policy, monkeypatch
):
    def forbidden(*args, **kwargs):
        pytest.fail('Evidence reconstruction attempted engine execution')

    monkeypatch.setattr(subprocess, 'run', forbidden)
    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    with puw.context(standard_units=[*policy, 'radians']):
        output = tmt.load_provider_output(
            ROOT / f'{provider}.zip', molecular_system=original_source
        )
        assert len(output.records) == count
        assert {r.record_kind for r in output.records} == {kind}
        assert output.run.metadata['execution_status'] == 'completed'
        first = output.records[0]
        if provider == 'caver':
            raw = list(
                csv.reader(
                    io.StringIO(
                        output.run.get_artifact(
                            'output/analysis/tunnel_profiles.csv'
                        ).decode()
                    ),
                    skipinitialspace=True,
                )
            )
            axes = {row[12]: row[13:] for row in raw[1:] if row[:3] == raw[1][:3]}
            geometry = first.geometries['centerline']
            expected = (
                np.array([[float(v) for v in axes[axis]] for axis in ('X', 'Y', 'Z')]).T
                / 10
            )
            np.testing.assert_allclose(geometry.points_nm, expected)
            np.testing.assert_allclose(
                geometry.radii_nm, np.array(axes['R'], float) / 10
            )
            assert first.measurements['length'].original_value == float(raw[1][10])
        elif provider == 'p2rank':
            prediction_rows = list(
                csv.DictReader(
                    io.StringIO(
                        output.run.get_artifact(
                            'output/input.pdb_predictions.csv'
                        ).decode()
                    ),
                    skipinitialspace=True,
                )
            )
            row = {
                key.strip(): value.strip() for key, value in prediction_rows[0].items()
            }
            assert first.measurements['probability'].original_value == float(
                row['probability']
            )
            assert first.measurements['score'].original_value == float(row['score'])
            np.testing.assert_allclose(
                first.geometries['predicted_center'].points_nm,
                [[float(row[f'center_{axis}']) / 10 for axis in 'xyz']],
            )
        elif provider == 'ghecom':
            raw = output.run.get_artifact('output/pockets.pdb').decode()
            counts = re.findall(r'^#REMARK CLUSTER\[(\d+)\] NVOXEL\s+(\d+)', raw, re.M)
            assert len(counts) == count
            assert output.run.metadata['returncode'] == 1
            assert sum(int(size) for _, size in counts) == sum(
                len(r.geometries['grid_points'].points_nm) for r in output.pockets
            )
        else:
            raw_toml = tomllib.loads(
                output.run.get_artifact('output/results.toml').decode()
            )
            for cavity in output.cavities:
                label = cavity.source_id
                assert (
                    cavity.measurements['volume'].original_value
                    == raw_toml['RESULTS']['VOLUME'][label]
                )
                assert (
                    cavity.measurements['area'].original_value
                    == raw_toml['RESULTS']['AREA'][label]
                )
            assert output.run.metadata['version'] == '0.9.6+uibcdf.2'


def test_original_evidence_receipt_checksums():
    import hashlib

    receipt = json.loads((ROOT / 'receipt.json').read_text())
    for name, expected in receipt['files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
