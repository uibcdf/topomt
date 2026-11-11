"""MoloVol argument and report controls, separate from original execution."""

import importlib
import json
from dataclasses import replace
from pathlib import Path

import pytest
from argdigest import UnknownArgumentError

import topomt as tmt
from tests.methods.pycasta.test_input_context import source
from tests.test_new_provider_parsers import captured
from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError

__all__ = ['source']


def test_molovol_resource_budget_rejects_before_engine_start(tmp_path, monkeypatch):
    from topomt.third_party.molovol import runner

    monkeypatch.setattr(
        runner,
        '_configuration',
        lambda options: ('/tools/molovol', DATA / 'elements.txt', None),
    )
    monkeypatch.setattr(
        runner,
        'run_command',
        lambda *args, **kwargs: pytest.fail('Over-budget MoloVol execution started'),
    )
    with pytest.raises(ArgumentError, match='max_grid_points'):
        runner.run(DATA / 'input.pdb', tmp_path, {'max_grid_points': 1})


def test_molovol_saved_source_change_is_rejected():
    import molsysmt as msm

    changed = msm.convert(str(DATA / 'input.pdb'), to_form='molsysmt.MolSys')
    msm.set(
        changed,
        coordinates=msm.get(changed, coordinates=True) + puw.quantity([1, 0, 0], 'nm'),
    )
    with pytest.raises(ValueError, match='coordinates'):
        tmt.load_provider_output(DATA / 'isolated.zip', molecular_system=changed)


DATA = Path(__file__).parent / 'data/original_local/molovol'
REPORT = 'input_MoloVol-report_grid-0.1_rad1-1.4.txt'


def parse(tmp_path, text=None):
    run = captured(
        tmp_path,
        'molovol',
        {REPORT: (DATA / REPORT).read_text() if text is None else text},
    )
    return importlib.import_module('topomt.third_party.molovol.parser').parse_output(
        run
    )


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_molovol_report_preserves_distinct_regions_volumes_and_units(tmp_path, policy):
    with puw.context(standard_units=policy):
        result = parse(tmp_path)
        assert len(result.cavities) == 1
        cavity = result.cavities[0]
        assert cavity.source_id == '2'
        assert cavity.fields['reported_type'] == 'Isolated'
        assert cavity.atom_indices is None
        assert cavity.measurements['occupied_volume'].original_value == 12.036
        assert cavity.measurements['accessible_volume'].original_value == 0.076
        assert puw.get_value(
            cavity.measurements['occupied_volume'].value, to_unit='angstroms**3'
        ) == pytest.approx(12.036)
        assert result.measurements['molecular_volume'].original_value == 86.84
        assert (
            result.measurements[
                'molecular_volume_with_isolated_cavities'
            ].original_value
            == 98.876
        )
        assert 'probe_core_volume' not in result.measurements
        assert result.original_data['regions'][0]['reported_type'] == 'Outside'
        assert result.original_data['regions'][0]['occupied_volume'] is None
        assert result.report_text == (DATA / REPORT).read_text()
        assert puw.get_value(
            result.element_radii['C'], to_unit='angstroms'
        ) == pytest.approx(1.7)
        assert cavity.geometries['region_center'].points_nm == ((0.0, 0.0, 0.0),)
        assert result.pockets == result.channels == ()
        copied = result.original_data
        copied['regions'].clear()
        assert len(result.original_data['regions']) == 2


def test_molovol_explicit_outside_only_report_has_no_internal_cavity(tmp_path):
    text = (DATA / REPORT).read_text()
    text = (
        '\n'.join(
            line
            for line in text.splitlines()
            if not (line.startswith('2 ') and 'Isolated' in line)
        )
        + '\n'
    )
    text = text.replace('98.876000', '86.840000')
    result = parse(tmp_path, text)
    assert result.cavities == ()
    assert result.original_data['regions'][0]['reported_type'] == 'Outside'


@pytest.mark.parametrize(
    'mutation',
    [
        'version',
        'truncated',
        'nan',
        'missing_radii',
        'periodic',
        'cavity_limit',
        'negative_region',
        'length_unit',
        'missing_length_unit',
        'volume_dimension',
        'cavity_units',
        'center_axes',
    ],
)
def test_molovol_incomplete_or_invalid_original_reports_are_rejected(
    tmp_path, mutation
):
    text = (DATA / REPORT).read_text()
    text = {
        'version': lambda s: s.replace('version: 1.2.0', 'version: 0.0.0'),
        'truncated': lambda s: s.split('// Surface map information //')[0],
        'nan': lambda s: s.replace('82.436000', 'nan'),
        'missing_radii': lambda s: s.replace('C : 1.7 A', ''),
        'periodic': lambda s: s.replace(
            'Crystal unit cell analysis: No', 'Crystal unit cell analysis: Yes'
        ),
        'cavity_limit': lambda s: s.replace(
            'Note 1:', 'Maximum number of cavities reached.\nNote 1:'
        ),
        'negative_region': lambda s: s.replace(
            '12.036        0.076', '-12.036       0.076'
        ),
        'length_unit': lambda s: s.replace(
            'Probe radius: 1.4 A', 'Probe radius: 1.4 nm'
        ),
        'missing_length_unit': lambda s: s.replace(
            'Grid resolution: 0.1 A', 'Grid resolution: 0.1'
        ),
        'volume_dimension': lambda s: s.replace('82.436000 A^3', '82.436000 A^2'),
        'cavity_units': lambda s: s.replace('Volume (A^3)', 'Volume (nm^3)'),
        'center_axes': lambda s: s.replace('x       y       z', 'z       y       x'),
    }[mutation](text)
    with pytest.raises(ValueError):
        parse(tmp_path, text)


@pytest.mark.parametrize(
    'options', [{'workers': 2}, {'probe_radius': 1.4, 'large_probe_radius': 1.2}]
)
def test_molovol_invalid_parameter_groups_fail_in_argdigest(
    monkeypatch, source, options
):
    execution = importlib.import_module('topomt.third_party._execution')

    def forbidden(*args, **kwargs):
        pytest.fail('Invalid MoloVol groups reached execution')

    monkeypatch.setattr(execution, 'get_output', forbidden)
    with pytest.raises(ArgumentError):
        tmt.get_provider_output(source, method='molovol', **options)


def test_molovol_checks_the_selected_command_without_an_installer_guess(
    source, tmp_path
):
    from topomt.third_party._execution import ProviderUnavailableError

    with pytest.raises(ProviderUnavailableError) as caught:
        tmt.get_provider_output(
            source,
            method='molovol',
            molovol_cmd=str(tmp_path / 'missing'),
            virtual_display=False,
        )
    assert str(tmp_path / 'missing') in str(caught.value)


def test_molovol_grid_budget_includes_octree_alignment_and_all_levels():
    from topomt.third_party._execution import check_grid_budget

    count = check_grid_budget(
        DATA / 'input.pdb', step=0.1, padding=3.3, limit=2_000_000, octree_depth=4
    )
    assert count == 1_605_583
    with pytest.raises(ArgumentError, match='max_grid_points'):
        check_grid_budget(
            DATA / 'input.pdb', step=0.1, padding=3.3, limit=5_000_000, octree_depth=8
        )


def test_molovol_prepares_captured_radii_without_changing_the_original_table(tmp_path):
    from topomt.third_party.molovol.runner import prepare_elements

    before = (DATA / 'elements.txt').read_bytes()
    metadata, files = prepare_elements(
        DATA / 'input.pdb', tmp_path, DATA / 'elements.txt', {'C': 1.7}
    )
    assert (DATA / 'elements.txt').read_bytes() == before
    assert metadata['effective_radii'] == {'C': 1.7}
    assert metadata['element_counts'] == {'C': 4}
    assert metadata['input_data_references'] == ['atomic_weights_2013']
    assert b'6\tC\t1.7\t' in files['elements.txt'].read_bytes()
    assert files['elements_source.txt'].read_bytes() == before
    default_dir = tmp_path / 'default'
    default_dir.mkdir()
    default, _ = prepare_elements(
        DATA / 'input.pdb', default_dir, DATA / 'elements.txt', {}
    )
    assert default['input_data_references'] == ['alvarez_radii', 'atomic_weights_2013']


@pytest.mark.parametrize('overrides', [{'Xx': 1.2}, {'C': 0}])
def test_molovol_rejects_invalid_resource_overrides(tmp_path, overrides):
    from topomt.third_party.molovol.runner import prepare_elements

    with pytest.raises(ArgumentError):
        prepare_elements(DATA / 'input.pdb', tmp_path, DATA / 'elements.txt', overrides)


@pytest.mark.parametrize('startup_failure', [False, True])
def test_molovol_owns_and_cleans_its_display_without_changing_global_environment(
    tmp_path, monkeypatch, startup_failure
):
    import os

    from topomt.third_party.molovol import runner

    events = []

    class OwnDisplay:
        def __init__(self, argv, **kwargs):
            assert '-displayfd' in argv and argv[-2:] == ['-nolisten', 'tcp']
            events.append('started')

        def terminate(self):
            events.append('terminate')

        def wait(self, timeout=None):
            events.append('wait')

    monkeypatch.setenv('DISPLAY', ':existing')
    monkeypatch.setattr(runner.subprocess, 'Popen', OwnDisplay)
    monkeypatch.setattr(runner.select, 'select', lambda *args: ([1], [], []))
    monkeypatch.setattr(
        runner.os, 'read', lambda *args: b'' if startup_failure else b'42\n'
    )
    expected = runner.ProviderExecutionError if startup_failure else RuntimeError
    with pytest.raises(expected):
        with runner.private_display('/tools/Xvfb', tmp_path) as environment:
            assert environment == {'DISPLAY': ':42'}
            assert os.environ['DISPLAY'] == ':existing'
            raise RuntimeError('Original engine failed')
    assert events == ['started', 'terminate', 'wait']
    assert os.environ['DISPLAY'] == ':existing'


def test_molovol_is_an_optional_original_provider():
    from topomt._private.arg_digestion.provider_dispatch import DEFAULT_BACKENDS

    assert DEFAULT_BACKENDS['molovol'] == 'cli'
    assert tmt.third_party.molovol.MoloVolOutput.provider == 'molovol'


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_molovol_arguments_reach_the_owner_in_fixed_units(monkeypatch, source, policy):
    calls = []
    execution = importlib.import_module('topomt.third_party._execution')

    def receive(provider, molecular_system, backend, options):
        calls.append((provider, backend, options))
        return 'accepted'

    monkeypatch.setattr(execution, 'get_output', receive)
    with puw.context(standard_units=policy):
        result = tmt.get_provider_output(
            source,
            method='MOLOVOL',
            probe_radius=puw.quantity(0.14, 'nm'),
            grid_step=puw.quantity(10, 'pm'),
            large_probe_radius=puw.quantity(0.4, 'nm'),
            element_radii={'C': puw.quantity(0.17, 'nm')},
            virtual_display=True,
            workers=1,
        )
    assert result == 'accepted'
    provider, backend, options = calls[0]
    assert (provider, backend) == ('molovol', 'cli')
    assert options['probe_radius'] == pytest.approx(1.4)
    assert options['grid_step'] == pytest.approx(0.1)
    assert options['large_probe_radius'] == pytest.approx(4.0)
    assert options['element_radii']['C'] == pytest.approx(1.7)


@pytest.mark.parametrize(
    'options',
    [
        {'grid_step': 0},
        {'grid_step': puw.quantity(1, 'ps')},
        {'probe_radius': -1},
        {'large_probe_radius': float('nan')},
        {'octree_depth': -1},
        {'virtual_display': 'yes'},
        {'element_radii': {'C': -1}},
        {'element_radii': {'C\nH': 1.7}},
        {'element_radii': {'C': puw.quantity(1, 'K')}},
    ],
)
def test_molovol_invalid_arguments_fail_before_execution(source, options):
    with pytest.raises(ArgumentError) as caught:
        tmt.get_provider_output(source, method='molovol', **options)
    assert next(iter(options)) in str(caught.value)


def test_molovol_unknown_options_are_not_ignored(source):
    with pytest.raises(UnknownArgumentError):
        tmt.get_provider_output(source, method='molovol', arbitrary_option=True)


@pytest.mark.parametrize(
    'name,expected_count',
    [('isolated', 1), ('empty', 0), ('two_probe', 5), ('table_radii', 1)],
)
@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_molovol_original_evidence_is_engine_free_and_source_bound(
    name, expected_count, policy, monkeypatch
):
    import subprocess

    ackredit = pytest.importorskip('ackredit')

    def forbidden(*args, **kwargs):
        pytest.fail('Reading original evidence executed a process')

    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    with (
        puw.context(standard_units=[*policy, 'radians']),
        ackredit.session('saved MoloVol'),
    ):
        result = tmt.load_provider_output(
            DATA / f'{name}.zip', molecular_system=str(DATA / 'input.pdb')
        )
        assert len(result.cavities) == expected_count
        assert result.attribution['status'] == 'recorded'
        assert result.run.metadata['version'] == '1.2.0'
        assert puw.get_value(
            result.element_radii['C'], to_unit='angstroms'
        ) == pytest.approx(1.77 if name == 'table_radii' else 1.7)
        assert tmt.cite(result)
        assert not ackredit.get_attribution().to_dict()['items']


@pytest.mark.parametrize(
    'mutation', ['effective_radii', 'probe', 'element_counts', 'resource', 'report']
)
def test_molovol_saved_evidence_rejects_inconsistent_query_or_resources(mutation):
    from topomt.provider_output import ProviderRun
    from topomt.third_party.molovol.parser import parse_output

    run = ProviderRun.load(DATA / 'isolated.zip')
    metadata = run.metadata
    if mutation == 'effective_radii':
        metadata['effective_radii']['C'] = 1.9
    elif mutation == 'probe':
        metadata['parameters']['probe_radius'] = 1.3
    elif mutation == 'element_counts':
        metadata['element_counts']['C'] = 5
    elif mutation == 'resource':
        metadata['elements_effective']['sha256'] = '0' * 64
    else:
        run = replace(
            run,
            artifacts=tuple(
                (name, data.replace(b'Probe radius: 1.4 A', b'Probe radius: 1.3 A'))
                for name, data in run.artifacts
            ),
        )
    run = replace(run, metadata_json=json.dumps(metadata))
    with pytest.raises(ValueError):
        parse_output(run)


@pytest.fixture
def replay_original(monkeypatch):
    """Replay captured bytes for wrapper-failure controls, never original qualification."""
    from topomt.provider_output import ProviderRun
    from topomt.third_party.molovol import runner

    original = ProviderRun.load(DATA / 'isolated.zip')

    def run(pdb, output, options):
        additional = {}
        for name, data in original.artifacts:
            if name.startswith('output/') and not name.endswith(
                'topomt_source_context.json'
            ):
                (output / name.removeprefix('output/')).write_bytes(data)
            if name in {'input/elements.txt', 'input/elements_source.txt'}:
                relative = name.removeprefix('input/')
                path = output / relative
                path.write_bytes(data)
                additional[relative] = path
        return original.metadata, additional

    monkeypatch.setattr(runner, 'ensure_available', lambda options: None)
    monkeypatch.setattr(runner, 'run', run)
    return runner


@pytest.mark.parametrize('state', ['absent', 'failed'])
def test_molovol_optional_attribution_failure_preserves_completed_science(
    replay_original, monkeypatch, state
):
    from contextlib import nullcontext

    from topomt import _ackredit

    ackredit = pytest.importorskip('ackredit')
    if state == 'absent':
        monkeypatch.setattr(_ackredit, 'backend', lambda: None)
    else:
        monkeypatch.setattr(ackredit, 'track_item', lambda *args, **kwargs: 1 / 0)
    with (
        ackredit.session('optional recording'),
        pytest.warns(Warning) if state == 'failed' else nullcontext(),
    ):
        result = tmt.get_provider_output(str(DATA / 'input.pdb'), method='molovol')
    assert len(result.cavities) == 1
    assert result.attribution['status'] == (
        'unavailable' if state == 'absent' else 'failed'
    )
    assert 'doi:10.1107/S1600576722004988' in {
        entry['item']['id'] for entry in result.attribution['references']
    }


def test_molovol_failed_original_is_retained_without_completion_credit(
    replay_original, monkeypatch, tmp_path
):
    from topomt.third_party._execution import ProviderExecutionError

    ackredit = pytest.importorskip('ackredit')

    def fail(pdb, output, options):
        (output / 'stderr.txt').write_text('Original test execution failed')
        raise ProviderExecutionError(provider='molovol', reason='test failure')

    monkeypatch.setattr(replay_original, 'run', fail)
    with ackredit.session('failed original'):
        with pytest.raises(ProviderExecutionError) as caught:
            tmt.get_provider_output(str(DATA / 'input.pdb'), method='molovol')
        assert 'doi:10.1107/S1600576722004988' not in {
            item['id'] for item in ackredit.get_attribution().to_dict()['items']
        }
    run = caught.value.run
    assert run.metadata['execution_status'] == 'failed'
    assert run.get_artifact('output/stderr.txt') == b'Original test execution failed'
    path = tmp_path / 'failed.zip'
    run.save(path)
    with pytest.raises(ValueError, match='protocol'):
        tmt.load_provider_output(path, molecular_system=str(DATA / 'input.pdb'))


def test_molovol_reading_needs_neither_engine_display_nor_recorder_in_fresh_process():
    import subprocess
    import sys

    script = """
import sys
import importlib.abc
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'ackredit' or fullname.startswith('ackredit.') or fullname == 'topomt.third_party.molovol.runner':
            raise ModuleNotFoundError('Blocked optional execution dependency', name=fullname)
sys.meta_path.insert(0, Block())
import topomt as tmt
result = tmt.load_provider_output(sys.argv[1], molecular_system=sys.argv[2])
assert len(result.cavities) == 1
assert result.attribution['status'] == 'recorded'
assert result.run.metadata['version'] == '1.2.0'
assert 'ackredit' not in sys.modules
assert 'topomt.third_party.molovol.runner' not in sys.modules
"""
    subprocess.run(
        [
            sys.executable,
            '-c',
            script,
            str(DATA / 'isolated.zip'),
            str(DATA / 'input.pdb'),
        ],
        check=True,
        timeout=30,
    )
