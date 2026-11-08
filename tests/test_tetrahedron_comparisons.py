"""Independent model and evidence guards for the tetrahedron comparison stage."""

import ast
import base64
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from pyunitwizard import QuantityRecord

from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun

CASE = (
    Path(__file__).resolve().parents[1]
    / 'docs/content/benchlab/synthetic/regular_tetrahedron'
)
DIRECTORY = CASE / 'artifacts/comparisons_v1'


def scalar(record, field, unit):
    quantity = QuantityRecord.from_dict(record).to_quantity(field=field, unit=unit)
    return float(puw.get_value(quantity, to_unit=unit))


def test_tetrahedron_comparison_protocol_preserves_inputs_and_declares_controls():
    protocol = json.loads((DIRECTORY / 'protocol.json').read_text())
    assert protocol['schema'] == 'topomt.benchlab.comparison-protocol/1'
    assert protocol['case_id'] == 'regular_tetrahedron'
    for relative, checksum in protocol['preserved_files'].items():
        assert hashlib.sha256((CASE / relative).read_bytes()).hexdigest() == checksum
    assert (
        protocol['preserved_files']['artifacts/regular_tetrahedron_v1/input.json']
        == '8634f70afdaf21cb8388887f5f80ae73dc36ef4f043198a10b525a93ebde5ce3'
    )
    canonical = (
        (CASE / 'artifacts/regular_tetrahedron_v1/input.pdb').read_bytes().splitlines()
    )
    exported = (CASE / protocol['source_file']).read_bytes().splitlines()
    assert [line[6:] for line in canonical] == [line[6:] for line in exported]
    assert protocol['execute_services'] is False
    assert protocol['workers'] == 1
    runs = protocol['runs']
    assert len(runs) == 14
    assert len({run['id'] for run in runs}) == len(runs)
    for provider in ('pykvfinder', 'ghecom', 'caver', 'mole'):
        selected = [run for run in runs if run['method'] == provider]
        assert selected[0]['scenario'] == 'standard'
        assert selected[0]['id'] == provider + '-standard'
        if provider != 'mole':
            assert [
                scalar(row['probe_label'], 'probe_label', 'angstroms')
                for row in selected[1:]
            ] == [1.2, 1.4, 1.7]
    assert all(run['probe_label'] is None for run in runs if run['method'] == 'mole')


def test_tetrahedron_radius_audit_separates_atomic_models_and_rounding_topology():
    audit = json.loads((DIRECTORY / 'model_audit.json').read_text())
    r_native = scalar(audit['radii']['native']['radius'], 'radius', 'angstroms')
    r_grid = scalar(audit['radii']['pykvfinder']['radius'], 'radius', 'angstroms')
    r_mole = scalar(audit['radii']['mole']['radius'], 'radius', 'angstroms')
    assert (r_native, r_grid, r_mole) == (1.7, 1.66, 1.61)
    assert audit['radii']['pykvfinder']['evidence_mode'] == 'original_read_pdb'
    assert (
        audit['radii']['mole']['evidence_mode'] == 'pinned_source_default_no_override'
    )
    edge = 5.3
    rounded = np.array(
        [
            [1.874, 1.874, 1.874],
            [1.874, -1.874, -1.874],
            [-1.874, 1.874, -1.874],
            [-1.874, -1.874, 1.874],
        ]
    )
    actual_edge = np.linalg.norm(rounded[0] - rounded[1])
    assert edge / np.sqrt(3) - r_grid < 1.4 < actual_edge / np.sqrt(3) - r_grid
    assert edge / np.sqrt(3) - r_native < 1.4 < edge * np.sqrt(6) / 4 - r_native
    assert actual_edge / np.sqrt(3) - r_mole > 1.4
    assert (
        audit['clearance_interpretation']
        == 'Independent ball-model implications, not detector predictions'
    )


def test_original_study_runner_decodes_units_and_forbids_unfrozen_settings():
    from devtools.benchlab.run_regular_tetrahedron_comparisons import _options

    protocol = json.loads((DIRECTORY / 'protocol.json').read_text())
    row = next(row for row in protocol['runs'] if row['id'] == 'pykvfinder-probe-1p4')
    with puw.context(standard_units=['pm', 'fs', 'radians']):
        options = _options(
            row, {'pykvfinder': {'upstream_root': '/example/source'}}, protocol
        )
        assert options['workers'] == 1 and options['timeout'] == 45
        assert puw.get_value(options['probe_in'], to_unit='angstroms') == 1.4
        assert puw.get_value(options['volume_cutoff'], to_unit='angstroms**3') == 0
    with pytest.raises(ValueError, match='location'):
        _options(row, {'pykvfinder': {'probe_in': 10}}, protocol)


def test_study_continues_controls_after_control_failure_and_stops_after_standard_failure(
    tmp_path, monkeypatch
):
    from devtools.benchlab import run_regular_tetrahedron_comparisons as runner

    executed = []

    def observe(row, locations, protocol, output):
        executed.append(row['id'])
        failed = row['id'] in {'pykvfinder-probe-1p2', 'caver-standard'}
        return {
            **row,
            'status': 'execution_failed' if failed else 'completed',
            'record_counts': None if failed else {},
            'original_bundle': None,
        }

    locations = tmp_path / 'tools.json'
    locations.write_text('{}')
    output = tmp_path / 'runs'
    monkeypatch.setattr(runner, '_execute', observe)
    monkeypatch.setattr(
        sys, 'argv', ['study', '--tools', str(locations), '--output', str(output)]
    )
    assert runner.main() == 0
    assert 'pykvfinder-probe-1p4' in executed and 'pykvfinder-probe-1p7' in executed
    assert not any(name.startswith('caver-probe') for name in executed)
    report = json.loads((output / 'observations.json').read_text())
    skipped = [
        entry
        for entry in report['entries']
        if entry['status'] == 'not_executed_after_failure'
    ]
    assert len(skipped) == 3
    assert {entry['cause_id'] for entry in skipped} == {'caver-standard'}


def test_reviewed_comparison_notebook_displays_verified_records_without_execution():
    notebook = json.loads((CASE / 'comparisons.ipynb').read_text())
    cells = [cell for cell in notebook['cells'] if cell['cell_type'] == 'code']
    assert cells and all(cell['execution_count'] is not None for cell in cells)
    outputs = [output for cell in cells for output in cell['outputs']]
    assert not any(output['output_type'] == 'error' for output in outputs)
    pngs = [
        output['data']['image/png']
        for output in outputs
        if 'image/png' in output.get('data', {})
    ]
    assert len(pngs) == 2
    for png, name in zip(
        pngs, ['atomic_models.png', 'original_grid_regions.png'], strict=True
    ):
        assert base64.b64decode(''.join(png)) == (DIRECTORY / name).read_bytes()
    displayed = [
        json.loads(''.join(output['data']['text/plain']))
        for cell in cells
        if 'topomt-comparison-study' in cell.get('metadata', {}).get('tags', [])
        for output in cell['outputs']
        if 'text/plain' in output.get('data', {})
    ]
    assert displayed == [json.loads((DIRECTORY / 'comparison_report.json').read_text())]
    for cell in cells:
        tree = ast.parse(''.join(cell['source']))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not any(
                    alias.name.startswith(('subprocess', 'requests', 'urllib'))
                    for alias in node.names
                )
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {
                    'get_provider_output',
                    'run',
                    'Popen',
                    'save',
                    'write_text',
                    'write_bytes',
                }


def test_original_comparison_receipts_preserve_failures_and_declared_diagnostics():
    receipt = json.loads((DIRECTORY / 'evidence_receipt.json').read_text())
    for relative, expected in receipt['files'].items():
        assert (
            hashlib.sha256((DIRECTORY / relative).read_bytes()).hexdigest() == expected
        )
    main = json.loads(
        (DIRECTORY / 'original_observations/observations.json').read_text()
    )
    assert len(main['entries']) == 14
    for entry in main['entries']:
        if entry['original_bundle']:
            run = ProviderRun.load(
                DIRECTORY / 'original_observations' / entry['original_bundle']['file']
            )
            assert run.run_id == entry['original_bundle']['run_id']
            assert run.metadata['execution_status'] == (
                'completed' if entry['status'] == 'completed' else 'failed'
            )
            source = run.get_artifact('input/input.pdb')
            assert hashlib.sha256(source).hexdigest() == main['source_sha256']
        if entry['status'] != 'completed':
            assert entry['record_counts'] is None
            assert 'record_count' not in entry
        if entry['status'] == 'not_executed_after_failure':
            assert entry['cause_id'] == entry['method'] + '-standard'
    diagnostic = json.loads((DIRECTORY / 'positive_cutoff_protocol.json').read_text())
    assert diagnostic['frozen_before_original_topography'] is False
    for row in diagnostic['runs']:
        assert scalar(
            row['options']['volume_cutoff'], 'volume_cutoff', 'angstroms**3'
        ) == pytest.approx(0.2**3)


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_original_comparison_recovery_is_engine_free_and_retains_spatial_meaning(
    policy, monkeypatch
):
    import subprocess

    import topomt as tmt

    def forbidden(*args, **kwargs):
        pytest.fail('Comparison replay attempted original execution')

    monkeypatch.setattr(subprocess, 'run', forbidden)
    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    source = CASE / 'artifacts/regular_tetrahedron_v1/input_atom.pdb'
    with puw.context(standard_units=[*policy, 'radians']):
        for folder in ('original_observations', 'positive_cutoff_observations'):
            report = json.loads((DIRECTORY / folder / 'observations.json').read_text())
            for entry in report['entries']:
                if not entry['original_bundle']:
                    continue
                bundle = DIRECTORY / folder / entry['original_bundle']['file']
                if entry['status'] != 'completed':
                    with pytest.raises(ValueError, match='protocol'):
                        tmt.load_provider_output(bundle, molecular_system=source)
                    continue
                output = tmt.load_provider_output(bundle, molecular_system=source)
                assert len(output.records) == entry['record_count']
                if entry['id'] == 'ghecom-probe-1p2':
                    xyz = puw.get_value(
                        output.records[0].geometries['grid_points'].coordinates,
                        to_unit='angstroms',
                    )
                    assert xyz.shape == (263, 3)
                if entry['id'] == 'pykvfinder-one-voxel-1p4':
                    xyz = puw.get_value(
                        output.records[0].geometries['grid_points'].coordinates,
                        to_unit='angstroms',
                    )
                    assert np.min(xyz) < -4 and np.max(xyz) > 5
                    assert (
                        output.records[0].measurements['volume'].original_value == 73.09
                    )
