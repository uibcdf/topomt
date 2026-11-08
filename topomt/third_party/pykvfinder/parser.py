"""Read original pyKVFinder 0.9.6 TOML and cavity-point PDB files."""

import tomllib
from collections import defaultdict

from topomt.provider_output import ProviderRun
from topomt.third_party._protocol import (
    artifact,
    finite,
    measurement,
    pdb_points,
    points_geometry,
)
from topomt.third_party.output import ProviderRecord

from .output import PyKVFinderOutput


def parse_output(run: ProviderRun) -> PyKVFinderOutput:
    """Decode original cavity labels without inferring closed solvent volumes."""
    data = tomllib.loads(artifact(run, 'results.toml').decode('utf-8'))
    results = data.get('RESULTS', {})
    volumes, areas = results.get('VOLUME'), results.get('AREA')
    if (
        not isinstance(volumes, dict)
        or not isinstance(areas, dict)
        or set(volumes) != set(areas)
    ):
        raise ValueError('pyKVFinder requires matching VOLUME and AREA tables')
    points = defaultdict(list)
    for label, _, point in pdb_points(artifact(run, 'cavities.pdb')):
        if label not in volumes:
            raise ValueError('pyKVFinder point label has no descriptor')
        points[label].append(point)
    if set(points) != set(volumes):
        raise ValueError('pyKVFinder cavity grid and descriptor labels disagree')
    records = []
    for label in volumes:
        if len(label) != 3 or not label.startswith('K'):
            raise ValueError('Invalid original pyKVFinder cavity label')
        fields = {
            key: value[label]
            for key, value in results.items()
            if isinstance(value, dict) and label in value
        }
        measurements = {}
        for key, unit in [
            ('VOLUME', 'angstroms**3'),
            ('AREA', 'angstroms**2'),
            ('MAX_DEPTH', 'angstroms'),
            ('AVG_DEPTH', 'angstroms'),
        ]:
            if key in fields:
                value = finite(fields[key], nonnegative=True)
                measurements[key.lower()] = measurement(
                    run,
                    value,
                    unit,
                    key,
                    'results.toml',
                    f'pyKVFinder original {key}; grid/probe definition retained in run parameters',
                )
        fields['external_measurements'] = measurements
        records.append(
            ProviderRecord(
                label,
                'cavity',
                run,
                atom_role='unmapped_interface_residues',
                _fields=fields,
                _geometries=(
                    points_geometry(
                        'grid_points',
                        points[label],
                        'pyKVFinder cavity/surface grid points; not a continuous closed region',
                    ),
                ),
            )
        )
    return PyKVFinderOutput(run, tuple(records))
