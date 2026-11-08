"""Decode reviewed original MOLE JSON without inferring solvent geometry."""

from typing import Any

from topomt.provider_output import ProviderRun
from topomt.third_party._protocol import artifact, finite, measurement, points_geometry
from topomt.third_party._saved_json import read_json
from topomt.third_party.output import ProviderGeometry, ProviderRecord

from .output import MoleOutput

VERSION = '2.5.26.10.26'
FILENAME = 'json/data.json'
CHANNEL_TYPES = {
    'Tunnels': 'Tunnel',
    'Pores': 'Pore',
    'MergedPores': 'Pore',
    'Paths': 'Path',
}


def _mapping(value: Any) -> dict:
    if not isinstance(value, dict):
        raise ValueError('MOLE requires an original object')
    return value


def _list(value: Any) -> list:
    if not isinstance(value, list):
        raise ValueError('MOLE requires an original array')
    return value


def _identifier(value: Any) -> str:
    if (type(value) is int and value >= 0) or (
        isinstance(value, str) and value.isdecimal()
    ):
        return str(value)
    raise ValueError('MOLE requires a nonnegative original identifier')


def _mesh(original: dict) -> tuple[tuple[ProviderGeometry, ...], dict]:
    geometries = []
    meshes = {}
    for part in ('Inner', 'Boundary'):
        mesh = _mapping(_mapping(original['Mesh'])[part])
        vertices = _list(mesh['Vertices'])
        triangles = _list(mesh['Triangles'])
        if len(vertices) % 3 or len(triangles) % 3:
            raise ValueError('MOLE mesh triples are incomplete')
        points = [vertices[i : i + 3] for i in range(0, len(vertices), 3)]
        if any(
            type(index) is not int or not 0 <= index < len(points)
            for index in triangles
        ):
            raise ValueError('MOLE mesh has invalid triangle indices')
        geometries.append(
            points_geometry(
                part.lower() + '_mesh_vertices',
                points,
                'Original MOLE cavity facet vertices; triangle topology is retained in fields.mesh, without an independent closed-region claim',
            )
        )
        meshes[part] = {
            'vertices': {'value': points, 'unit': 'angstroms'},
            'triangles': triangles,
        }
    return tuple(geometries), meshes


def _cavity(run: ProviderRun, group: str, item: dict) -> ProviderRecord:
    expected = 'Void' if group == 'Voids' else 'Cavity'
    if item['Type'] != expected:
        raise ValueError('MOLE cavity type disagrees with its collection')
    identity = f'{group}:{_identifier(item["Id"])}'
    depth = item['Depth']
    if type(depth) is not int or depth < 0:
        raise ValueError('MOLE tetrahedron depth is invalid')
    geometries, meshes = _mesh(item)
    fields = {'source_group': group, 'original': item, 'mesh': meshes}
    fields['external_measurements'] = {
        name: measurement(
            run,
            finite(item[field], nonnegative=True),
            unit,
            field,
            FILENAME,
            definition,
        )
        for name, field, unit, definition in [
            (
                'tetrahedral_volume',
                'Volume',
                'angstroms**3',
                'Original MOLE sum of retained Delaunay tetrahedron volumes; not solvent-excluded free volume',
            ),
            (
                'depth_length',
                'DepthLength',
                'angstroms',
                'Original MOLE cavity graph depth length',
            ),
        ]
    }
    return ProviderRecord(
        identity,
        'cavity',
        run,
        atom_role='unavailable_cavity_atom_map',
        _fields=fields,
        _geometries=geometries,
    )


def _channel(
    run: ProviderRun, group: str, item: dict, parents: set[str]
) -> ProviderRecord:
    if item['Type'] != CHANNEL_TYPES[group]:
        raise ValueError('MOLE channel type disagrees with its collection')
    cavity_id = None if item['Cavity'] is None else _identifier(item['Cavity'])
    identity = f'{group}:{cavity_id if cavity_id is not None else "none"}:{_identifier(item["Id"])}'
    profile = _list(item['Profile'])
    if not profile:
        raise ValueError('MOLE channel has an empty profile')
    points = [[row[axis] for axis in 'XYZ'] for row in profile]
    geometries = []
    for field, name in [
        ('Radius', 'centerline'),
        ('FreeRadius', 'free_radius_centerline'),
        ('BRadius', 'b_radius_centerline'),
    ]:
        geometries.append(
            points_geometry(
                name,
                points,
                f'Original ordered MOLE channel samples with original {field}; no swept volume is inferred',
                [row[field] for row in profile],
            )
        )
    distances = [finite(row['Distance'], nonnegative=True) for row in profile]
    parameters = [finite(row['T'], nonnegative=True) for row in profile]
    if (
        any(a > b for a, b in zip(distances, distances[1:]))
        or any(a > b for a, b in zip(parameters, parameters[1:]))
        or parameters[-1] > 1
    ):
        raise ValueError('MOLE profile is not ordered in distance/spline parameter')
    parent = 'Cavities:' + cavity_id if cavity_id is not None else ''
    return ProviderRecord(
        identity,
        'channel',
        run,
        atom_role='unavailable_channel_lining_atom_map',
        parent_source_ids=(parent,) if parent in parents else (),
        _geometries=tuple(geometries),
        _fields={
            'source_group': group,
            'original': item,
            'profile_distance': {'value': distances, 'unit': 'angstroms'},
            'external_measurements': {
                'profile_length': measurement(
                    run,
                    distances[-1],
                    'angstroms',
                    'Profile[-1].Distance',
                    FILENAME,
                    'Original MOLE final approximate profile distance, rounded to 0.001 angstrom; not recomputed from rounded points',
                )
            },
        },
    )


def parse_output(run: ProviderRun) -> MoleOutput:
    """Validate the reviewed complete JSON and retain its original feature kinds."""
    data = _mapping(read_json(artifact(run, FILENAME), provider='mole'))
    if data.get('Version') != VERSION:
        raise ValueError(f'Unsupported MOLE original version; expected {VERSION}')
    records: list[ProviderRecord] = []
    try:
        _mapping(data['Config'])
        _mapping(data['Origins'])
        finite(data['Timing'], nonnegative=True)
        if type(data['FoundOrigin']) is not bool:
            raise ValueError('MOLE origin status must be boolean')
        cavities = _mapping(data['Cavities'])
        _mesh(_mapping(cavities['Surface']))
        for group in ('Cavities', 'Voids'):
            records.extend(
                _cavity(run, group, _mapping(item)) for item in _list(cavities[group])
            )
        parents = {record.source_id for record in records}
        channels = _mapping(data['Channels'])
        for group in CHANNEL_TYPES:
            records.extend(
                _channel(run, group, _mapping(item), parents)
                for item in _list(channels[group])
            )
    except (KeyError, TypeError, IndexError) as error:
        raise ValueError('Missing or malformed MOLE original JSON fields') from error
    if len({record.source_id for record in records}) != len(records):
        raise ValueError('Duplicate MOLE original feature identity')
    return MoleOutput(run, tuple(records))
