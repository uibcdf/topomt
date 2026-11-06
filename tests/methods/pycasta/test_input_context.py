"""Synthetic controls for original pyCASTA source admission and capture."""

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import molsysmt as msm
import numpy as np
import pytest
from scipy.spatial import Delaunay

from tests.methods.fpocket4.test_chemical_context import _with_states
from tests.methods.fpocket4.test_input_preparation import _pdb_frame
from topomt import pyunitwizard as puw
from topomt.third_party.pycasta import library


@pytest.fixture
def source(tmp_path):
    path = tmp_path / 'seed.pdb'
    extra = (
        'HETATM    5  C1  LIG B   2      20.000  20.000  20.000  1.00  0.00           C\n'
        'HETATM    6  C2  LIG B   2      30.000  20.000  20.000  1.00  0.00           C\n'
    )
    path.write_text(_pdb_frame() + extra + 'END\n')
    result = _with_states(msm.convert(path, to_form='molsysmt.MolSys'), reference=1)
    second = msm.copy(result)
    msm.set(
        second,
        coordinates=msm.get(second, coordinates=True)
        + puw.quantity([0.2, -0.1, 0.3], 'nm'),
    )
    msm.append_structures(result, msm.convert(second, to_form='molsysmt.Structures'))
    return result


def forbidden(*args, **kwargs):
    pytest.fail('Original discovery/execution preceded source admission.')


@pytest.fixture
def fake_original(monkeypatch, tmp_path):
    root = tmp_path / 'original'
    root.mkdir()
    (root / 'run_analysis.py').write_text('# Synthetic worker; never executed.\n')
    calls = []

    def run(command, **options):
        calls.append(command)
        pdb, result_path, configuration_path = map(Path, command[-3:])
        coordinates = np.asarray(
            [
                [float(line[start : start + 8]) for start in (30, 38, 46)]
                for line in pdb.read_text().splitlines()
                if line.startswith('ATOM  ')
            ]
        )
        simplices = Delaunay(coordinates).simplices
        result = {
            'protein_coords': coordinates.tolist(),
            'ranked_pockets': [list(range(len(simplices)))],
            'pocket_volumes': [125.0],
            'ranking_scores': [8.5],
            'pocket_depths': [2.0],
            'mouth_area': [3.0],
            'mouth_perimeter': [4.0],
            'representative_points': [
                coordinates[simplices].mean(axis=(0, 1)).tolist()
            ],
            'validation_methods': [None],
            'ligand_coords': [],
        }
        result_path.write_text(json.dumps(result))
        configuration_path.write_text(
            json.dumps(
                {
                    'use_cgal': False,
                    'filter_alpha_by_sasa': False,
                    'save_alpha': True,
                    'validation_method': 'SASA',
                    'use_existing_results': False,
                    'manual_alpha': None,
                    'version_tag': 'bov1',
                    'distribution_version': 'synthetic-1',
                }
            )
        )
        output = result_path.parent / 'bov1'
        output.mkdir()
        np.savez(
            output / f'{pdb.stem}.alpha.npz',
            protein_coords=coordinates,
            tetrahedra=coordinates[simplices],
        )
        return SimpleNamespace(stdout='synthetic original output\n', stderr='')

    monkeypatch.setattr(library, 'subprocess', SimpleNamespace(run=run))
    return root, calls


@pytest.mark.parametrize(
    'inventory,reference,selector,message',
    [
        ('two', 0, 1, 'nonreference'),
        ('two', None, 'reference', 'ambiguous'),
        ('absent', 0, 'reference', 'absent'),
        ('empty', None, 'reference', 'zero chemical states'),
    ],
)
def test_reference_admission_precedes_export_and_discovery(
    source, monkeypatch, inventory, reference, selector, message
):
    if inventory == 'absent':
        # Current MolSysMT refuses constructing this invalid inventory. Exercise
        # the admission boundary with a converted source reporting its absence.
        invalid = object()
        convert = msm.convert

        def converted(value, **kwargs):
            if value is invalid:
                return SimpleNamespace(chemical_states=None)
            return convert(value, **kwargs)

        monkeypatch.setattr(msm, 'convert', converted)
    else:
        invalid = _with_states(source, inventory=inventory, reference=reference)
    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', forbidden)
    monkeypatch.setattr(library, '_get_source_root', forbidden)
    with pytest.raises(ValueError, match=message):
        library.get_topography(
            invalid, chemical_state=selector, upstream_root='/unused'
        )


@pytest.mark.parametrize('damage', ['coordinates', 'row_map', 'serials', 'models'])
def test_submitted_context_precedes_original_execution(source, monkeypatch, damage):
    prepare = library.prepare_wrapper_input_pdb

    def corrupt(*args, **kwargs):
        path, indices = prepare(*args, **kwargs)
        lines = path.read_text().splitlines()
        rows = [
            i for i, line in enumerate(lines) if line.startswith(('ATOM  ', 'HETATM'))
        ]
        if damage == 'coordinates':
            i = rows[0]
            lines[i] = lines[i][:30] + f'{9.0:8.3f}' + lines[i][38:]
        elif damage == 'row_map':
            indices = indices[::-1]
        elif damage == 'serials':
            i, j = rows[:2]
            lines[j] = lines[j][:6] + lines[i][6:11] + lines[j][11:]
        else:
            lines = [
                'MODEL        1',
                *lines,
                'ENDMDL',
                'MODEL        2',
                *lines,
                'ENDMDL',
            ]
        path.write_text('\n'.join(lines) + '\n')
        return path, indices

    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', corrupt)
    monkeypatch.setattr(library, '_get_source_root', forbidden)
    with pytest.raises(ValueError):
        library.get_topography(source, upstream_root='/unused', structure_indices=1)


def test_live_capture_binds_full_source_reference_frame_and_verified_simplices(
    source, fake_original
):
    root, calls = fake_original
    before = copy.deepcopy(
        msm.convert(
            source.chemical_states, to_form='molsysmt.ChemicalStatesDict'
        ).to_dict()
    )
    result = library.get_topography(
        source,
        selection=[5, 3, 2, 1, 0],
        structure_indices=1,
        chemical_state=np.int64(1),
        upstream_root=root,
    )
    run = next(iter(result.provider_runs.values()))
    metadata = run.metadata
    assert len(calls) == 1
    assert calls[0][1:4] == ['-I', '-B', '-c']
    assert metadata['selected_atom_indices'] == [0, 1, 2, 3, 5]
    submitted = next(data for name, data in run.artifacts if name.startswith('input/'))
    rows = [
        line
        for line in submitted.decode().splitlines()
        if line.startswith(('ATOM  ', 'HETATM'))
    ]
    expected = [
        i
        for i, line in zip(metadata['selected_atom_indices'], rows, strict=True)
        if line.startswith('ATOM  ')
    ]
    assert metadata['protein_atom_indices'] == expected
    assert metadata['structure_indices'] == 1
    assert metadata['chemical_state_context']['reference_index'] == 1
    assert metadata['distribution_version'] == 'synthetic-1'
    assert metadata['output_protocol']['schema_version'] == 1
    context = json.loads(run.get_artifact('output/topomt_source_context.json'))
    assert context['n_atoms'] == 6 and context['coordinates']['unit'] == 'nm'
    assert run.get_artifact('output/topomt_tetrahedron_indices.json')
    np.testing.assert_equal(
        msm.convert(
            source.chemical_states, to_form='molsysmt.ChemicalStatesDict'
        ).to_dict(),
        before,
    )


def test_worker_retains_observed_origins_and_exact_original_source_bytes(tmp_path):
    root, output = tmp_path / 'original', tmp_path / 'output'
    root.mkdir()
    output.mkdir()
    config = (
        'USE_CGAL=False\nFILTER_ALPHA_BY_SASA=False\nSAVE_ALPHA=True\n'
        'VALIDATION_METHOD="Mesh"\nUSE_EXISTING_RESULTS=False\nMANUAL_ALPHA=None\n'
    )
    analysis = 'VERSION_TAG="synthetic"\ndef process_pdb(path):\n    return {"ranked_pockets": []}\n'
    (root / 'config.py').write_text(config)
    (root / 'run_analysis.py').write_text(analysis)
    result = subprocess.run(
        [
            sys.executable,
            '-I',
            '-B',
            '-c',
            library._PYCASTA_WORKER,
            str(root),
            str(tmp_path / 'unused.pdb'),
            str(output / 'result.json'),
            str(output / 'configuration.json'),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    receipt = json.loads((output / 'topomt_worker_origins.json').read_text())
    assert receipt['source_root'] == str(root)
    assert 'environment' not in receipt
    for name, original in [('config.py', config), ('run_analysis.py', analysis)]:
        data = (output / 'topomt_worker_sources' / name).read_bytes()
        assert data == original.encode()
        identity = receipt['source_files']['output/topomt_worker_sources/' + name]
        assert identity['sha256'] == hashlib.sha256(data).hexdigest()
        assert identity['path'] == str(root / name)
        assert receipt['modules'][name[:-3]]['file'] == str(root / name)
