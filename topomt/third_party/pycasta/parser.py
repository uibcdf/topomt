"""Validate captured pyCASTA results without executing or triangulating them."""

from io import BytesIO
from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile

import numpy as np

from topomt.third_party._saved_json import read_json


def output_protocol() -> dict[str, Any]:
    """Return the fixed numerical units and schema of this adapter's evidence."""
    return {
        'schema_version': 1,
        'units': {
            'protein_coords': 'angstroms',
            'tetrahedra': 'angstroms',
            'pocket_volumes': 'angstroms**3',
            'ranking_scores': 'unspecified',
            'pocket_depths': 'angstroms',
            'representative_points': 'angstroms',
            'mouth_area': 'angstroms**2',
            'mouth_perimeter': 'angstroms',
        },
    }


def _number(
    value: Any, field: str, *, nonnegative: bool = False, undefined: bool = False
) -> float:
    if undefined and isinstance(value, dict) and set(value) == {'nonfinite'}:
        marker = value['nonfinite']
        if isinstance(marker, str) and marker in {'nan', 'inf', '-inf'}:
            return float(marker)
    if type(value) not in (int, float):
        raise ValueError(f'Invalid pyCASTA saved numeric field: {field}.')
    try:
        number = float(value)
    except OverflowError as error:
        raise ValueError(f'Invalid pyCASTA saved numeric field: {field}.') from error
    if not np.isfinite(number) or nonnegative and number < 0:
        raise ValueError(f'Invalid pyCASTA saved numeric field: {field}.')
    return number


def _coordinates(value: Any, field: str) -> np.ndarray:
    if not isinstance(value, list) or any(
        not isinstance(row, list) or len(row) != 3 for row in value
    ):
        raise ValueError(f'Invalid pyCASTA saved coordinate shape: {field}.')
    return np.asarray(
        [[_number(v, field) for v in row] for row in value], dtype=float
    ).reshape(-1, 3)


def protein_atom_indices_from_pdb(
    input_pdb: Path, selected_atom_indices: np.ndarray, protein_coords_ang: np.ndarray
) -> np.ndarray:
    """Bind original ATOM coordinates to submitted row order, skipping HETATM."""
    rows = [
        line
        for line in input_pdb.read_text().splitlines()
        if line.startswith(('ATOM  ', 'HETATM'))
    ]
    if len(rows) != len(selected_atom_indices):
        raise ValueError('Submitted PDB atom count differs from the source selection.')
    positions = [i for i, line in enumerate(rows) if line.startswith('ATOM  ')]
    coordinates: np.ndarray = np.asarray(
        [
            [float(rows[i][start : start + 8]) for start in (30, 38, 46)]
            for i in positions
        ],
        dtype=float,
    ).reshape(-1, 3)
    if not np.array_equal(coordinates, protein_coords_ang):
        raise ValueError(
            'pyCASTA protein coordinate order differs from submitted PDB ATOM records.'
        )
    return selected_atom_indices[positions]


def parse_result(
    result_bytes: bytes, alpha_bytes: bytes, index_bytes: bytes, protocol: Any
) -> dict[str, Any]:
    """Validate original arrays and their persisted, already verified index map.

    No triangulation, ligand validation or original-provider import occurs here.
    The NPZ coordinates must agree exactly with the original returned JSON and
    the persisted map. Original numerical units are explicitly negotiated.
    """
    if (
        not isinstance(protocol, dict)
        or type(protocol.get('schema_version')) is not int
        or protocol != output_protocol()
    ):
        raise ValueError('Unsupported pyCASTA saved output protocol or units.')
    result = read_json(result_bytes, provider='pyCASTA')
    indices = read_json(index_bytes, provider='pyCASTA')
    if not isinstance(result, dict) or not isinstance(indices, dict):
        raise ValueError('Invalid pyCASTA saved result or index map.')
    required = {'protein_coords', 'ranked_pockets', 'pocket_volumes', 'ranking_scores'}
    if not required.issubset(result):
        raise ValueError('Incomplete pyCASTA original returned result.')
    coords = _coordinates(result['protein_coords'], 'protein_coords')
    if len(coords) < 4:
        raise ValueError('pyCASTA requires at least four original protein coordinates.')
    if (
        set(indices) != {'schema_version', 'simplices'}
        or type(indices['schema_version']) is not int
        or indices['schema_version'] != 1
    ):
        raise ValueError('Invalid pyCASTA saved tetrahedron-index schema.')
    rows = indices['simplices']
    if not isinstance(rows, list) or any(
        not isinstance(row, list)
        or len(row) != 4
        or any(type(i) is not int or not 0 <= i < len(coords) for i in row)
        or len(set(row)) != 4
        for row in rows
    ):
        raise ValueError('Invalid pyCASTA saved tetrahedron atom indices.')
    simplices: np.ndarray = np.asarray(rows, dtype=int).reshape(-1, 4)
    try:
        with ZipFile(BytesIO(alpha_bytes)) as archive:
            if len(archive.namelist()) != len(set(archive.namelist())):
                raise ValueError('Duplicate pyCASTA alpha-array members.')
        with np.load(BytesIO(alpha_bytes), allow_pickle=False) as alpha:
            original_coords = alpha['protein_coords']
            tetrahedra = alpha['tetrahedra']
        if (
            original_coords.dtype.kind not in 'iuf'
            or tetrahedra.dtype.kind not in 'iuf'
            or original_coords.shape != coords.shape
            or tetrahedra.shape != (len(simplices), 4, 3)
            or not np.isfinite(original_coords).all()
            or not np.isfinite(tetrahedra).all()
            or not np.array_equal(original_coords, coords)
            or not np.array_equal(tetrahedra, coords[simplices])
        ):
            raise ValueError(
                'pyCASTA original alpha positions disagree with the saved index map.'
            )
    except (KeyError, OSError, EOFError, BadZipFile) as error:
        raise ValueError(
            'Invalid or incomplete pyCASTA original alpha array.'
        ) from error
    pockets = result['ranked_pockets']
    if not isinstance(pockets, list) or any(
        not isinstance(row, list)
        or not row
        or any(type(i) is not int or not 0 <= i < len(simplices) for i in row)
        or len(set(row)) != len(row)
        for row in pockets
    ):
        raise ValueError('Invalid pyCASTA original pocket tetrahedron indices.')
    count = len(pockets)
    for key in (
        'pocket_volumes',
        'ranking_scores',
        'pocket_depths',
        'mouth_area',
        'mouth_perimeter',
    ):
        if key not in result:
            continue
        values = result[key]
        lengths = {count} if key in {'pocket_volumes', 'ranking_scores'} else {0, count}
        if not isinstance(values, list) or len(values) not in lengths:
            raise ValueError(f'Invalid pyCASTA original pocket field length: {key}.')
        result[key] = [
            _number(v, key, nonnegative=key != 'ranking_scores', undefined=True)
            for v in values
        ]
    if 'representative_points' in result:
        points = _coordinates(result['representative_points'], 'representative_points')
        if len(points) not in (0, count):
            raise ValueError('Invalid pyCASTA representative-point count.')
        result['representative_points'] = points.tolist()
    if 'validation_methods' in result:
        values = result['validation_methods']
        if (
            not isinstance(values, list)
            or len(values) not in (0, count)
            or any(v is not None and not isinstance(v, str) for v in values)
        ):
            raise ValueError('Invalid pyCASTA original validation outcomes.')
    return {'result': result, 'protein_coords': coords, 'simplices': simplices}
