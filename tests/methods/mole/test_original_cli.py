"""Designated original MOLE gate: a requested missing engine must fail."""

import hashlib
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

import topomt as tmt

SOURCE = Path(__file__).resolve().parents[2] / 'data/original_local/source.pdb'
COMMAND = os.environ.get('TOPOMT_MOLE_CMD')
pytestmark = pytest.mark.skipif(
    COMMAND is None, reason='Set TOPOMT_MOLE_CMD for the designated original CLI gate'
)


@pytest.fixture
def selected_command():
    assert COMMAND is not None
    resolved = shutil.which(COMMAND)
    assert resolved is not None, 'Requested MOLE gate cannot skip an absent engine'
    return str(Path(resolved).resolve())


@pytest.mark.parametrize(
    'source_file,options',
    [
        (SOURCE, {}),
        (
            SOURCE.with_name('mole_1tqn.cif'),
            {'compute_pores': True, 'compute_merged_pores': True},
        ),
    ],
)
def test_original_mole_agrees_with_public_output(
    selected_command, tmp_path, monkeypatch, source_file, options
):
    result = tmt.get_provider_output(
        str(source_file),
        method='mole',
        mole_cmd=selected_command,
        workers=1,
        timeout=90,
        **options,
    )
    assert result.channels and result.cavities
    if options:
        assert result.original_data['Channels']['Pores']
        assert result.original_data['Channels']['MergedPores']
    assert result.run.metadata['executable']['path'] == selected_command
    assert (
        result.run.metadata['executable']['sha256']
        == hashlib.sha256(Path(selected_command).read_bytes()).hexdigest()
    )
    source = tmp_path / 'input.pdb'
    source.write_bytes(result.run.get_artifact('input/input.pdb'))
    config = ET.fromstring(result.run.get_artifact('input/config.xml'))
    input_element = config.find('Input')
    assert input_element is not None
    input_element.text = str(source)
    direct_output = tmp_path / 'direct'
    directory_element = config.find('WorkingDirectory')
    assert directory_element is not None
    directory_element.text = str(direct_output)
    filename = tmp_path / 'config.xml'
    ET.ElementTree(config).write(filename, encoding='utf-8', xml_declaration=True)
    environment = dict(os.environ)
    environment.update(
        DOTNET_PROCESSOR_COUNT='1',
        DOTNET_GCHeapHardLimit='0x40000000',
        DOTNET_CLI_TELEMETRY_OPTOUT='1',
    )
    completed = subprocess.run(
        [selected_command, str(filename)],
        env=environment,
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    direct = json.loads((direct_output / 'json/data.json').read_text())
    assert result.original_data['Channels'] == direct['Channels']
    assert result.original_data['Cavities'] == direct['Cavities']
    for record in result.channels:
        assert (
            record.fields['original']
            in direct['Channels'][record.fields['source_group']]
        )
    for record in result.cavities:
        original = record.fields['original']
        assert original in direct['Cavities'][record.fields['source_group']]
        assert (
            record.measurements['tetrahedral_volume'].original_value
            == original['Volume']
        )
    bundle = tmp_path / 'original.zip'
    result.save(bundle)

    def forbidden(*args, **kwargs):
        pytest.fail('Saved original MOLE output reran the engine')

    monkeypatch.setattr(subprocess, 'run', forbidden)
    restored = tmt.load_provider_output(bundle, molecular_system=str(source_file))
    assert restored.run == result.run
    assert restored.original_data == result.original_data


def test_original_mole_valid_empty_is_recoverable(selected_command, tmp_path):
    result = tmt.get_provider_output(
        str(SOURCE),
        method='mole',
        mole_cmd=selected_command,
        interior_threshold=1e6,
        workers=1,
        timeout=90,
    )
    assert result.records == ()
    assert result.run.metadata['execution_status'] == 'completed'
    bundle = tmp_path / 'empty.zip'
    result.save(bundle)
    restored = tmt.load_provider_output(bundle, molecular_system=str(SOURCE))
    assert restored.records == () and restored.run == result.run


def test_original_mole_failure_has_nonzero_status(selected_command, tmp_path):
    environment = dict(os.environ)
    environment.update(DOTNET_PROCESSOR_COUNT='1', DOTNET_GCHeapHardLimit='0x40000000')
    failed = subprocess.run(
        [selected_command, str(tmp_path / 'absent.xml')],
        env=environment,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert failed.returncode != 0
    assert 'Error:' in failed.stdout and failed.stderr
