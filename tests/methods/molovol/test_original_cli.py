"""Explicit original-engine gate; protocol-only tests never qualify execution."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

import topomt as tmt
from topomt.third_party._execution import run_command
from topomt.third_party.molovol.parser import decode_report
from topomt.third_party.molovol.runner import private_display

DATA = Path(__file__).resolve().parents[2] / 'data/original_local/molovol'
COMMAND = os.environ.get('TOPOMT_MOLOVOL_CMD')
pytestmark = pytest.mark.skipif(
    COMMAND is None, reason='Set TOPOMT_MOLOVOL_CMD for original MoloVol qualification'
)


@pytest.mark.parametrize(
    'name,options',
    [
        (
            'isolated',
            {'probe_radius': 1.4, 'grid_step': 0.1, 'calculate_surfaces': True},
        ),
        ('empty', {'probe_radius': 6.0, 'grid_step': 0.3}),
        (
            'two_probe',
            {'probe_radius': 1.4, 'large_probe_radius': 4.0, 'grid_step': 0.2},
        ),
        ('table_radii', {'probe_radius': 1.4, 'grid_step': 0.2}),
    ],
)
def test_original_molovol_matches_direct_report_and_recovers(
    tmp_path, monkeypatch, name, options
):
    assert COMMAND is not None
    resolved = shutil.which(COMMAND)
    assert resolved is not None, (
        'A requested original gate cannot skip a missing executable'
    )
    executable = str(Path(resolved).resolve())
    ackredit = pytest.importorskip('ackredit')
    original_display = os.environ.get('DISPLAY')
    with ackredit.session('original MoloVol'), ackredit.capture('enclosing') as capture:
        result = tmt.get_provider_output(
            str(DATA / 'input.pdb'),
            method='molovol',
            molovol_cmd=executable,
            elements_file=DATA / 'elements.txt',
            **({} if name == 'table_radii' else {'element_radii': {'C': 1.7}}),
            virtual_display=True,
            timeout=60,
            workers=1,
            **options,
        )
        ids = {entry['item']['id'] for entry in result.attribution['references']}
        assert 'doi:10.1107/S1600576722004988' in ids
        assert 'doi:10.1515/pac-2015-0305' in ids
        assert ('doi:10.1039/C3DT50599E' in ids) == (name == 'table_radii')
        assert not any(
            'fpocket' in value or 'S0567739476001551' in value for value in ids
        )
    assert capture.attribution.to_dict()['items']
    assert os.environ.get('DISPLAY') == original_display
    if name == 'empty':
        assert result.records == ()
    if name == 'isolated':
        assert len(result.cavities) == 1
        assert (
            result.cavities[0].measurements['occupied_volume'].original_value == 12.036
        )
    assert result.run.metadata['executable']['path'] == executable
    assert result.run.metadata['execution_status'] == 'completed'
    direct = tmp_path / 'direct'
    direct.mkdir()
    source, elements = tmp_path / 'input.pdb', tmp_path / 'elements.txt'
    source.write_bytes(result.run.get_artifact('input/input.pdb'))
    elements.write_bytes(result.run.get_artifact('input/elements.txt'))
    argv = list(result.run.metadata['command'])
    for flag, value in [('-fs', source), ('-fe', elements), ('-do', direct)]:
        argv[argv.index(flag) + 1] = str(value)
    xvfb = shutil.which('Xvfb')
    assert xvfb is not None
    with private_display(xvfb, direct) as environment:
        assert (
            run_command(argv, direct, timeout=60, workers=1, extra_env=environment) == 0
        )
    (report,) = direct.glob('*_MoloVol-report_grid-*.txt')
    assert decode_report(report.read_text()) == result.original_data
    bundle = tmp_path / f'{name}.zip'
    result.save(bundle)
    evidence = os.environ.get('TOPOMT_MOLOVOL_EVIDENCE_DIR')
    if evidence:
        destination = Path(evidence)
        destination.mkdir(parents=True, exist_ok=True)
        result.save(destination / f'{name}.zip')
        (destination / f'{name}_metadata.json').write_text(
            json.dumps(result.run.metadata, indent=2) + '\n'
        )

    def forbidden(*args, **kwargs):
        pytest.fail('Saved original MoloVol recovery executed a process')

    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    monkeypatch.setattr(subprocess, 'run', forbidden)
    with ackredit.session('read saved MoloVol'):
        restored = tmt.load_provider_output(
            bundle, molecular_system=str(DATA / 'input.pdb')
        )
        assert restored.run == result.run
        assert restored.original_data == result.original_data
        assert restored.attribution == result.attribution
        assert tmt.cite(restored)
        assert not ackredit.get_attribution().to_dict()['items']
