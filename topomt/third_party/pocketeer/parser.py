"""Read Pocketeer's original JSON and TopoMT's explicit mask supplement."""

import json
from types import SimpleNamespace
from typing import Any, NoReturn

import numpy as np


def _invalid(field: str) -> NoReturn:
    raise ValueError(f'Invalid Pocketeer saved output: {field}.')


def _read_json(data: bytes) -> Any:
    """Read JSON while rejecting ambiguous duplicate keys and nonfinite constants."""

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                _invalid(f'duplicate JSON key {key}')
            result[key] = value
        return result

    def constant(value):
        _invalid(f'nonfinite JSON constant {value}')

    try:
        return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError('Invalid Pocketeer saved JSON.') from error


def _integer(value: Any, field: str, *, nonnegative: bool = True) -> int:
    if type(value) is not int or nonnegative and value < 0:
        _invalid(field)
    return value


def _number(value: Any, field: str, *, minimum: float | None = None) -> float:
    if type(value) not in (int, float):
        _invalid(field)
    try:
        number = float(value)
    except (OverflowError, ValueError):
        _invalid(field)
    if not np.isfinite(number) or minimum is not None and number < minimum:
        _invalid(field)
    return number


def _point(value: Any, field: str) -> np.ndarray:
    if not isinstance(value, list) or len(value) != 3:
        _invalid(field)
    return np.array([_number(item, field) for item in value], dtype=float)


def _keys(value: Any, keys: set[str], field: str) -> None:
    if not isinstance(value, dict) or set(value) != keys:
        _invalid(field + ' schema')


def _output_protocol() -> dict[str, Any]:
    return {
        'schema_version': 1,
        'artifact': 'output/pocketeer_pockets.json',
        'units': {
            'centroid': 'angstroms',
            'spheres[*].center': 'angstroms',
            'spheres[*].radius': 'angstroms',
            'spheres[*].mean_sasa': 'angstroms**2',
            'volume': 'angstroms**3',
            'score': '1',
        },
    }


def parse_pockets(
    data: bytes,
    masks_data: bytes,
    n_submitted: int,
    n_filtered: int,
    protocol: dict[str, Any],
) -> list[Any]:
    """Decode original pocket fields without importing Pocketeer or Biotite.

    Parameters
    ----------
    data : bytes
        Original pocketeer_pockets.json, in its angstrom-based protocol.
    masks_data : bytes
        Schema 1 TopoMT mask supplement; one literal boolean per submitted atom.
    n_submitted : int
        Submitted PDB atom-row count.
    n_filtered : int
        Atom count after the original detector's filtering.
    protocol : dict
        Recorded artifact/field unit protocol; must match the supported explicit
        angstrom/area/volume/dimensionless contract.

    Returns
    -------
    list
        Decoded data records with original IDs, order, masks and measurements.
        An available empty original result remains an empty list.

    Raises
    ------
    ValueError
        If schema, finite values, counts, IDs or index bounds are inconsistent.
        No mask, residue, measurement or geometric value is inferred.
    """
    _keys(protocol, {'schema_version', 'artifact', 'units'}, 'output unit protocol')
    if type(protocol['schema_version']) is not int or protocol != _output_protocol():
        _invalid('output unit protocol')
    pockets, masks = _read_json(data), _read_json(masks_data)
    _keys(masks, {'schema_version', 'pockets'}, 'mask supplement')
    if type(masks['schema_version']) is not int or masks['schema_version'] != 1:
        _invalid('mask schema version')
    if (
        not isinstance(pockets, list)
        or not isinstance(masks['pockets'], list)
        or len(pockets) != len(masks['pockets'])
    ):
        _invalid('pocket/mask count')
    seen = set()
    result = []
    for pocket, mask in zip(pockets, masks['pockets']):
        _keys(
            pocket,
            {
                'pocket_id',
                'spheres',
                'centroid',
                'volume',
                'score',
                'residues',
                'n_spheres',
                'n_residues',
            },
            'pocket',
        )
        _keys(mask, {'pocket_id', 'mask'}, 'mask')
        identity = _integer(pocket['pocket_id'], 'pocket ID')
        if identity in seen or _integer(mask['pocket_id'], 'mask ID') != identity:
            _invalid('duplicate or conflicting pocket/mask ID')
        seen.add(identity)
        membership = mask['mask']
        if (
            not isinstance(membership, list)
            or len(membership) != n_submitted
            or any(type(value) is not bool for value in membership)
        ):
            _invalid('mask length or boolean type')
        spheres, residues = pocket['spheres'], pocket['residues']
        if (
            not isinstance(spheres, list)
            or not isinstance(residues, list)
            or _integer(pocket['n_spheres'], 'sphere count') != len(spheres)
            or _integer(pocket['n_residues'], 'residue count') != len(residues)
        ):
            _invalid('sphere/residue counts')
        sphere_ids = set()
        decoded = []
        for sphere in spheres:
            _keys(
                sphere,
                {'sphere_id', 'center', 'radius', 'mean_sasa', 'atom_indices'},
                'sphere',
            )
            sphere_id = _integer(sphere['sphere_id'], 'sphere ID')
            if sphere_id in sphere_ids:
                _invalid('duplicate sphere ID')
            sphere_ids.add(sphere_id)
            vertices = sphere['atom_indices']
            if not isinstance(vertices, list) or len(vertices) != 4:
                _invalid('four sphere-defining atom indices')
            vertices = [_integer(index, 'sphere atom index') for index in vertices]
            if len(set(vertices)) != 4 or any(
                index >= n_filtered for index in vertices
            ):
                _invalid('sphere-defining atom indices outside filtered map')
            radius = _number(sphere['radius'], 'sphere radius', minimum=0)
            if radius == 0:
                _invalid('zero sphere radius')
            decoded.append(
                SimpleNamespace(
                    sphere_id=sphere_id,
                    center=_point(sphere['center'], 'sphere center'),
                    radius=radius,
                    mean_sasa=_number(sphere['mean_sasa'], 'sphere SASA', minimum=0),
                    atom_indices=vertices,
                )
            )
        decoded_residues = []
        for residue in residues:
            _keys(residue, {'chain_id', 'res_id', 'res_name'}, 'residue')
            if not isinstance(residue['chain_id'], str) or not isinstance(
                residue['res_name'], str
            ):
                _invalid('residue labels')
            decoded_residues.append(
                (
                    residue['chain_id'],
                    _integer(residue['res_id'], 'residue ID', nonnegative=False),
                    residue['res_name'],
                )
            )
        if len(set(decoded_residues)) != len(decoded_residues):
            _invalid('duplicate residues')
        result.append(
            SimpleNamespace(
                pocket_id=identity,
                spheres=decoded,
                centroid=_point(pocket['centroid'], 'pocket centroid'),
                volume=_number(pocket['volume'], 'pocket volume', minimum=0),
                score=_number(pocket['score'], 'pocket score'),
                residues=decoded_residues,
                mask=np.array(membership, dtype=bool),
            )
        )
    return result
