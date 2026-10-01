"""Verify that public comparisons retain original evidence and honest failures."""

import hashlib
import json
from pathlib import Path

import pytest
from pyunitwizard import QuantityRecord

from topomt.provider_output import ProviderRun

ARTIFACT_ROOT = (
    Path(__file__).resolve().parents[1] / 'docs/content/showcase/dfnd/artifacts'
)


@pytest.mark.parametrize('case', ['regular_tetrahedron_v1', 'closed_shell_v1'])
def test_provider_panel_preserves_same_input_original_runs_and_failure_meaning(case):
    directory = ARTIFACT_ROOT / case
    report = json.loads((directory / 'report.json').read_text())
    entries = report['provider_comparisons']
    assert [entry['method'] for entry in entries] == [
        'fpocket',
        'pocketeer',
        'alphaspace2',
        'pycasta',
        'castp3',
        'castpfold',
    ]
    original_lines = (directory / 'input.pdb').read_bytes().splitlines()
    atom_lines = (directory / 'input_atom.pdb').read_bytes().splitlines()
    assert [line[6:] for line in atom_lines] == [line[6:] for line in original_lines]
    assert all(line.startswith(b'ATOM  ') for line in atom_lines[:-1])
    submitted_checksum = hashlib.sha256(
        (directory / 'input_atom.pdb').read_bytes()
    ).hexdigest()
    for entry in entries:
        submitted_file = directory / entry.get('input_file', 'input_atom.pdb')
        entry_checksum = hashlib.sha256(submitted_file.read_bytes()).hexdigest()
        assert entry['input_sha256'] == entry_checksum
        assert entry['backend'] in {'cli', 'library', 'server'}
        if entry['backend'] == 'server':
            assert entry['evidence_mode'] == 'recorded_original_server_attempt'
            assert entry['requested_probe_angstroms'] == 1.4
            assert entry['server'] == entry['method']
            if entry['status'] == 'submitted_pending':
                assert entry['submission_accepted']
                assert entry['jobid'].startswith('j_')
                assert not entry['calculation_completion_observed']
                assert entry['client_outcome'] == 'execution_failed'
        else:
            assert entry_checksum == submitted_checksum
        if entry['status'] != 'completed':
            assert entry['pocket_count'] is None
            assert entry['status'] in {
                'unavailable',
                'not_requested',
                'execution_failed',
                'submitted_pending',
            }
            continue
        assert entry['pocket_count'] == len(entry['pockets'])
        bundle = directory / entry['original_bundle']['file']
        assert (
            hashlib.sha256(bundle.read_bytes()).hexdigest()
            == entry['original_bundle']['sha256']
        )
        run = ProviderRun.load(bundle)
        assert run.run_id == entry['run_id']
        assert run.provider == (
            'castp' if entry['backend'] == 'server' else entry['method']
        )
        assert (
            hashlib.sha256(run.get_artifact(f'input/{submitted_file.name}')).hexdigest()
            == entry_checksum
        )
        for pocket in entry['pockets']:
            for geometry in pocket['geometries'].values():
                coordinates = QuantityRecord.from_dict(
                    geometry['coordinates']
                ).to_quantity(field='coordinates', unit='nm')
                assert coordinates.shape[1] == 3


@pytest.mark.parametrize('case', ['regular_tetrahedron_v1', 'closed_shell_v1'])
def test_castp_export_preserves_geometry_and_aligns_one_letter_atom_names(case):
    directory = ARTIFACT_ROOT / case
    canonical = (directory / 'input.pdb').read_bytes().splitlines()
    submitted = (directory / 'input_castp.pdb').read_bytes().splitlines()
    assert len(canonical) == len(submitted)
    for original, adjusted in zip(canonical, submitted):
        if original.startswith(b'HETATM'):
            assert adjusted.startswith(b'HETATM')
            assert adjusted[12:16] == b' C  '
            assert adjusted[:12] == original[:12]
            assert adjusted[16:] == original[16:]
        else:
            assert adjusted == original
