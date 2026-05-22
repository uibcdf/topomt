import numpy as np
import pytest

from topomt.dfnd import dfnd
from topomt.dfnd.graph import DelaunayFlowNetwork


def _minimal_coordinates():
    return np.array(
        [
            [1.874, 1.874, 1.874],
            [1.874, -1.874, -1.874],
            [-1.874, 1.874, -1.874],
            [-1.874, -1.874, 1.874],
        ],
        dtype=float,
    )


def _write_minimal_pdb(path):
    path.write_text(
        '\n'.join(
            [
                'ATOM      1  C1  GLY A   1       1.874   1.874   1.874  1.00  0.00           C',
                'ATOM      2  C2  GLY A   1       1.874  -1.874  -1.874  1.00  0.00           C',
                'ATOM      3  C3  GLY A   1      -1.874   1.874  -1.874  1.00  0.00           C',
                'ATOM      4  C4  GLY A   1      -1.874  -1.874   1.874  1.00  0.00           C',
                'END',
                '',
            ]
        )
    )


def test_dfnd_rejects_empty_molecular_selection(tmp_path):
    pdb_path = tmp_path / 'minimal.pdb'
    _write_minimal_pdb(pdb_path)

    with pytest.raises(ValueError, match='selection produced no atoms'):
        dfnd(str(pdb_path), selection=[])


def test_dfnd_from_arrays_rejects_too_few_atoms():
    with pytest.raises(ValueError, match='Not enough atoms'):
        DelaunayFlowNetwork.from_arrays(
            _minimal_coordinates()[:3],
            np.full(3, 1.7),
        )


def test_dfnd_from_arrays_rejects_non_finite_coordinates():
    coordinates = _minimal_coordinates()
    coordinates[0, 0] = np.nan

    with pytest.raises(ValueError, match='coordinates must be finite'):
        DelaunayFlowNetwork.from_arrays(coordinates, np.full(4, 1.7))


def test_dfnd_from_arrays_rejects_invalid_radii():
    with pytest.raises(ValueError, match='radii must be positive'):
        DelaunayFlowNetwork.from_arrays(
            _minimal_coordinates(),
            np.array([1.7, 1.7, 0.0, 1.7]),
        )

    with pytest.raises(ValueError, match='radii must be finite'):
        DelaunayFlowNetwork.from_arrays(
            _minimal_coordinates(),
            np.array([1.7, 1.7, np.nan, 1.7]),
        )
