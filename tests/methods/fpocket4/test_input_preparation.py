"""The original engine must receive exactly the requested atoms and frame."""

import numpy as np
import pytest

from topomt.third_party.fpocket.cli import (
    _prepare_fpocket_input,
    _prepare_fpocket_input_pdb,
)


def _pdb_frame(offset=0.0):
    return ''.join(
        f'ATOM  {index:5d} {name:^4s} GLY A   1    '
        f'{x + offset:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00          {element:>2s}\n'
        for index, name, element, (x, y, z) in (
            (1, 'N', 'N', (0.0, 0.0, 0.0)),
            (2, 'CA', 'C', (1.0, 0.0, 0.0)),
            (3, 'C', 'C', (0.0, 1.0, 0.0)),
            (4, 'O', 'O', (0.0, 0.0, 1.0)),
        )
    )


@pytest.fixture
def pdb_file(tmp_path):
    source = tmp_path / 'source.pdb'
    source.write_text(_pdb_frame() + 'END\n')
    return source


def test_single_frame_submission_keeps_original_bytes(pdb_file, tmp_path):
    submission = tmp_path / 'submission'
    submission.mkdir()
    output = _prepare_fpocket_input_pdb(pdb_file, submission)
    assert output.read_bytes() == pdb_file.read_bytes()


def test_numpy_selection_submits_requested_atoms(pdb_file, tmp_path):
    submission = tmp_path / 'submission'
    submission.mkdir()
    output = _prepare_fpocket_input_pdb(
        pdb_file, submission, selection=np.array([1, 3])
    )
    atoms = [
        line for line in output.read_text().splitlines() if line.startswith('ATOM')
    ]
    assert [line[12:16].strip() for line in atoms] == ['CA', 'O']


def test_submission_map_follows_exported_source_order(pdb_file, tmp_path):
    output, indices = _prepare_fpocket_input(pdb_file, tmp_path, selection=[3, 1])
    atoms = [
        line for line in output.read_text().splitlines() if line.startswith('ATOM')
    ]
    assert [line[12:16].strip() for line in atoms] == ['CA', 'O']
    assert indices.tolist() == [1, 3]


def test_empty_selection_is_rejected_before_engine_execution(pdb_file, tmp_path):
    with pytest.raises(ValueError, match='empty atom selection'):
        _prepare_fpocket_input_pdb(pdb_file, tmp_path, selection=[])


def test_multimodel_pdb_submits_only_the_requested_first_frame(tmp_path):
    source = tmp_path / 'trajectory.pdb'
    source.write_text(
        'MODEL        1\n' + _pdb_frame() + 'ENDMDL\n'
        'MODEL        2\n' + _pdb_frame(10.0) + 'ENDMDL\nEND\n'
    )
    submission = tmp_path / 'submission'
    submission.mkdir()
    output = _prepare_fpocket_input_pdb(source, submission, structure_indices=0)
    atoms = [
        line for line in output.read_text().splitlines() if line.startswith('ATOM')
    ]
    assert len(atoms) == 4
    assert float(atoms[0][30:38]) == 0.0


def test_multiple_requested_frames_are_rejected(pdb_file, tmp_path):
    with pytest.raises(ValueError, match='one.*frame|one.*structure'):
        _prepare_fpocket_input_pdb(pdb_file, tmp_path, structure_indices=[0, 0])


def test_empty_requested_frames_are_rejected(pdb_file, tmp_path):
    with pytest.raises(ValueError, match='one.*frame|one.*structure'):
        _prepare_fpocket_input_pdb(pdb_file, tmp_path, structure_indices=[])
