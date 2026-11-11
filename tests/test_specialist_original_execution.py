"""Explicit original HOLE/PISA gates; absent requested engines must fail."""

import importlib
import os
import shutil
import subprocess
from pathlib import Path

import pytest

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt.third_party._execution import run_command

DATA = Path(__file__).parent / 'data/original_local'


@pytest.mark.parametrize(
    'provider,empty', [('hole', False), ('pisa', False), ('pisa', True)]
)
def test_specialist_original_execution_matches_direct_and_recovers(
    tmp_path, monkeypatch, provider, empty
):
    command = os.environ.get('TOPOMT_' + provider.upper() + '_CMD')
    if command is None:
        pytest.skip(
            'Set the selected TOPOMT provider command for original qualification'
        )
    assert shutil.which(command) is not None
    import ackredit

    source = DATA / provider / ('empty_input.pdb' if empty else 'input.pdb')
    if provider == 'hole':
        options = {
            'hole_cmd': command,
            'radii_file': DATA / 'hole/radii.rad',
            'origin': puw.quantity([0, 0, 0], 'angstroms'),
            'direction': [0, 0, 1],
            'sample_step': 0.5,
            'end_radius': 7.0,
            'random_seed': 12345,
        }
        doi = 'doi:10.1016/S0006-3495(93)81293-1'
    else:
        options = {'pisa_cmd': command, 'pisa_home': os.environ['TOPOMT_PISA_HOME']}
        doi = 'doi:10.1016/j.jmb.2007.05.022'
    with (
        ackredit.session('external original'),
        ackredit.capture('workflow') as workflow,
    ):
        result = tmt.get_provider_output(
            str(source), method=provider, workers=1, timeout=30, **options
        )
        reused = tmt.get_provider_output(
            str(source), method=provider, workers=1, timeout=30, **options
        )
        for output in [result, reused]:
            ids = {entry['item']['id'] for entry in output.attribution['references']}
            assert doi in ids
            assert not any('fpocket' in key or 'molovol' in key for key in ids)
        assert result.attribution['status'] == 'recorded'
    assert workflow.attribution.to_dict()['items']
    assert result.run.metadata['execution_status'] == 'completed'
    assert result.run.metadata['executable']['path'] == str(Path(command).resolve())
    direct = tmp_path / 'direct'
    direct.mkdir()
    if provider == 'hole':
        for name in ['input.pdb', 'radii.rad', 'control.in']:
            (direct / name).write_bytes(result.run.get_artifact('input/' + name))
        run_command(
            [command], direct, workers=1, timeout=30, stdin_file=direct / 'control.in'
        )
        parser = importlib.import_module('topomt.third_party.hole.parser')
        expected = parser.decode_report(
            (direct / 'stdout.txt').read_text(), (direct / 'profile.sph').read_text()
        )
        assert result.channels[0].fields['profile'] == expected['profile']
        assert len(result.channels) == 1
    else:
        expected = (
            DATA / 'pisa' / ('empty_interfaces.txt' if empty else 'interfaces.txt')
        )
        parser = importlib.import_module('topomt.third_party.pisa.parser')
        actual = parser.decode_reports(
            result.run.get_artifact('output/interfaces.txt'),
            result.run.get_artifact('output/assemblies.txt'),
        )
        prior = parser.decode_reports(
            expected.read_bytes(),
            (
                DATA / 'pisa' / ('empty_assemblies.txt' if empty else 'assemblies.txt')
            ).read_bytes(),
        )
        assert actual == prior
        assert len(result.interfaces) == (0 if empty else 1)
        if not empty:
            assert result.interfaces[0].atom_indices
            assert result.interfaces[0].atom_role == 'reported_contact_atoms'
            # Distance-cutoff contacts include atoms beyond the buried-area
            # atom inventory (12 + 8 here). Keep those original sets distinct.
            assert len(result.interfaces[0].atom_indices) == 28
    bundle = tmp_path / 'original.zip'
    result.save(bundle)
    evidence = os.environ.get('TOPOMT_SPECIALIST_EVIDENCE_DIR')
    if evidence:
        destination = Path(evidence)
        destination.mkdir(exist_ok=True, parents=True)
        result.save(destination / f'{provider}{"-empty" if empty else ""}.zip')

    def forbidden(*args, **kwargs):
        pytest.fail(
            'Saved specialist reader attempted execution or dependency discovery'
        )

    monkeypatch.setattr(subprocess, 'run', forbidden)
    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    monkeypatch.setattr(
        importlib.import_module(f'topomt.third_party.{provider}.runner'),
        'ensure_available',
        forbidden,
    )
    with ackredit.session('saved only'):
        recovered = tmt.load_provider_output(bundle, molecular_system=str(source))
        assert recovered.run == result.run
        assert recovered.attribution == result.attribution
        assert recovered.records == result.records
        assert tmt.cite(recovered)
        assert ackredit.get_attribution().to_dict()['items'] == []


@pytest.mark.parametrize('name', ['positive', 'empty', 'outside'])
def test_original_povme_fork_runs_serial_matches_direct_and_recovers(
    tmp_path, monkeypatch, name
):
    root = os.environ.get('TOPOMT_POVME_ROOT')
    if root is None:
        pytest.skip('Set TOPOMT_POVME_ROOT for the explicit serial source gate')
    assert (Path(root) / 'povme/__init__.py').is_file()
    import csv
    import io
    import sys

    import ackredit

    source = DATA / 'pisa/input.pdb'
    regions = [
        {
            'shape': 'box',
            'center': puw.quantity([0, 2.5, 5.5], 'angstroms'),
            'lengths': puw.quantity([6, 7, 9], 'angstroms'),
        }
    ]
    if name != 'positive':
        regions = [
            {
                'shape': 'sphere',
                'center': puw.quantity(
                    [0, 0, 0] if name == 'empty' else [100, 100, 100], 'angstroms'
                ),
                'radius': 0.5 if name == 'empty' else 2.0,
            }
        ]
    molecule_root = os.environ['TOPOMT_PYMOLECULE_ROOT']
    with ackredit.session('original external POVME'):
        result = tmt.get_provider_output(
            str(source),
            method='povme',
            upstream_root=root,
            pymolecule_root=molecule_root,
            python_cmd=sys.executable,
            inclusion_regions=regions,
            grid_step=1.0,
            distance_cutoff=0,
            convex_hull_exclusion=False,
            contiguous_points_criteria=0,
            workers=1,
            timeout=30,
        )
        ids = {entry['item']['id'] for entry in result.attribution['references']}
        assert {'doi:10.1016/j.jmgm.2010.10.007', 'doi:10.1021/ct500381c'} <= ids
        software = next(
            entry['item']
            for entry in result.attribution['references']
            if entry['item'].get('id') == 'topomt:reference:povme:2.2.2+uibcdf.1'
        )
        assert 'uibcdf/POVME' in software['url']
    assert len(result.regions) == 1
    assert result.pockets == result.cavities == result.channels == ()
    region = result.regions[0]
    volume = region.measurements['volume'].original_value
    assert region.measurements['volume'].original_unit == 'angstroms**3'
    if name == 'positive':
        assert volume == 330.0
    if name == 'empty':
        assert volume == 0 and region.geometries['retained_grid_points'].points_nm == ()
    if name == 'outside':
        assert volume > 0 and region.geometries == {}
        assert region.fields['point_support_status'] == 'not_written_by_original'
    direct = tmp_path / 'direct'
    direct.mkdir()
    pdb = direct / 'input.pdb'
    pdb.write_bytes(result.run.get_artifact('input/input.pdb'))
    config = direct / 'config.json'
    config.write_bytes(result.run.get_artifact('input/configuration.json'))
    code = "import json,sys; from povme.config import PocketVolumeConfig; from povme.pocket.volume import PocketVolume; config=PocketVolumeConfig(**json.load(open(sys.argv[2]))); result=PocketVolume(config).run(sys.argv[1],sys.argv[3]+'/',chunk_size=1); assert set(result)=={1}"
    run_command(
        [sys.executable, '-c', code, str(pdb), str(config), str(direct)],
        direct,
        timeout=30,
        workers=1,
        extra_env={'PYTHONPATH': os.pathsep.join([root, molecule_root])},
    )
    expected = list(csv.reader(io.StringIO((direct / 'volumes.csv').read_text())))
    assert float(expected[1][1]) == volume
    if name != 'outside':
        assert (direct / 'frame_1.pdb').read_bytes() == result.run.get_artifact(
            'output/frame_1.pdb'
        )
    bundle = tmp_path / 'povme.zip'
    result.save(bundle)
    evidence = os.environ.get('TOPOMT_SPECIALIST_EVIDENCE_DIR')
    if evidence:
        result.save(Path(evidence) / f'povme-{name}.zip')

    def forbidden(*args, **kwargs):
        pytest.fail('POVME saved reader attempted a scientific execution')

    monkeypatch.setattr(subprocess, 'run', forbidden)
    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    with ackredit.session('read only'):
        recovered = tmt.load_provider_output(bundle, molecular_system=str(source))
        assert recovered.run == result.run
        assert recovered.records == result.records
        assert recovered.attribution == result.attribution
        assert ackredit.get_attribution().to_dict()['items'] == []


def test_original_hole_recognized_amber_resource_credits_its_data(tmp_path):
    command = os.environ.get('TOPOMT_HOLE_CMD')
    if command is None:
        pytest.skip('Set TOPOMT_HOLE_CMD for the original AMBER-resource gate')
    assert shutil.which(command)
    import ackredit

    source = DATA / 'hole/carbon_input.pdb'
    with ackredit.session('original HOLE AMBER'):
        result = tmt.get_provider_output(
            str(source),
            method='hole',
            hole_cmd=command,
            origin=puw.quantity([0, 0, 0], 'angstroms'),
            direction=[0, 0, 1],
            sample_step=0.5,
            end_radius=7.0,
            timeout=30,
        )
        refs = result.attribution['references']
        paper = next(
            entry for entry in refs if entry['item']['id'] == 'doi:10.1021/ja00315a051'
        )
        assert paper['roles'] == ['input_data_reference']
        assert result.run.metadata['input_data_references'] == ['amber_1984']
        assert len(result.channels) == 1
    destination = os.environ.get('TOPOMT_SPECIALIST_EVIDENCE_DIR')
    if destination:
        result.save(Path(destination) / 'hole-amber.zip')


@pytest.mark.parametrize('provider', ['hole', 'pisa', 'povme'])
def test_original_specialist_failures_never_become_empty_success(tmp_path, provider):
    command = (
        os.environ.get('TOPOMT_' + provider.upper() + '_CMD')
        if provider != 'povme'
        else os.environ.get('TOPOMT_POVME_ROOT')
    )
    if command is None:
        pytest.skip('Set the selected original engine for failure qualification')
    import sys

    import ackredit

    from topomt.third_party._execution import ProviderExecutionError

    source = DATA / ('hole/input.pdb' if provider == 'hole' else 'pisa/input.pdb')
    if provider == 'hole':
        radii = tmp_path / 'bad.rad'
        radii.write_text('remark No van der Waals records\nBOND ???? 0.85\n')
        options = {
            'hole_cmd': command,
            'radii_file': radii,
            'origin': puw.quantity([0, 0, 0], 'angstroms'),
            'direction': [0, 0, 1],
        }
        doi = 'doi:10.1016/S0006-3495(93)81293-1'
    elif provider == 'pisa':
        invalid = tmp_path / 'unknown.pdb'
        invalid.write_text(source.read_text().replace('ALA', 'ZZZ'))
        source = invalid
        options = {'pisa_cmd': command, 'pisa_home': os.environ['TOPOMT_PISA_HOME']}
        doi = 'doi:10.1016/j.jmb.2007.05.022'
    else:
        options = {
            'upstream_root': command,
            'pymolecule_root': os.environ['TOPOMT_PYMOLECULE_ROOT'],
            'python_cmd': sys.executable,
            'inclusion_regions': [
                {
                    'shape': 'sphere',
                    'center': puw.quantity([0, 0, 0], 'angstroms'),
                    'radius': 1.0,
                }
            ],
            'exclusion_regions': [
                {
                    'shape': 'sphere',
                    'center': puw.quantity([0, 0, 0], 'angstroms'),
                    'radius': 4.0,
                }
            ],
            'convex_hull_exclusion': False,
        }
        doi = 'doi:10.1021/ct500381c'
    with ackredit.session('genuine original failure'):
        with pytest.raises(ProviderExecutionError) as caught:
            tmt.get_provider_output(
                str(source), method=provider, timeout=10, workers=1, **options
            )
        assert doi not in {
            entry['id'] for entry in ackredit.get_attribution().to_dict()['items']
        }
    assert caught.value.run.metadata['execution_status'] == 'failed'
    identity = caught.value.run.metadata[
        'interpreter' if provider == 'povme' else 'executable'
    ]
    assert len(identity['sha256']) == 64 and identity['size'] > 0
    evidence = os.environ.get('TOPOMT_SPECIALIST_EVIDENCE_DIR')
    if evidence:
        caught.value.run.save(Path(evidence) / f'{provider}-failed.zip')


@pytest.mark.parametrize('provider', ['hole', 'pisa', 'povme'])
def test_original_specialist_execution_with_genuinely_unavailable_ackredit(provider):
    command = (
        os.environ.get('TOPOMT_' + provider.upper() + '_CMD')
        if provider != 'povme'
        else os.environ.get('TOPOMT_POVME_ROOT')
    )
    if command is None:
        pytest.skip(
            'Set the selected original provider for recorder-absence qualification'
        )
    import sys

    code = """
import importlib.abc,os,sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname=='ackredit' or fullname.startswith('ackredit.'):
            raise ModuleNotFoundError('Blocked unavailable recorder',name='ackredit')
sys.meta_path.insert(0,Block())
import topomt as tmt
from topomt import pyunitwizard as puw
provider,source=sys.argv[1:]
if provider=='hole':
    options={'hole_cmd':os.environ['TOPOMT_HOLE_CMD'],'radii_file':str(__import__('pathlib').Path(source).parent/'radii.rad'),'origin':puw.quantity([0,0,0],'angstroms'),'direction':[0,0,1],'end_radius':7.0}
elif provider=='pisa':
    options={'pisa_cmd':os.environ['TOPOMT_PISA_CMD'],'pisa_home':os.environ['TOPOMT_PISA_HOME']}
else:
    options={'upstream_root':os.environ['TOPOMT_POVME_ROOT'],'pymolecule_root':os.environ['TOPOMT_PYMOLECULE_ROOT'],'inclusion_regions':[{'shape':'sphere','center':puw.quantity([0,2.5,5.5],'angstroms'),'radius':3}],'convex_hull_exclusion':False,'contiguous_points_criteria':0}
result=tmt.get_provider_output(source,method=provider,timeout=20,workers=1,**options)
assert result.attribution['status']=='unavailable'
assert result.attribution['references']
assert 'ackredit' not in sys.modules
assert result.run.metadata['execution_status']=='completed'
"""
    source = DATA / ('hole/input.pdb' if provider == 'hole' else 'pisa/input.pdb')
    subprocess.run(
        [sys.executable, '-c', code, provider, str(source)], check=True, timeout=30
    )
