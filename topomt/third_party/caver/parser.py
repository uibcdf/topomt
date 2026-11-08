"""Parse the variable-width original CAVER 3.02 tunnel-profile CSV."""

import csv
import io
from typing import Any

from topomt.provider_output import ProviderRun
from topomt.third_party._protocol import artifact, finite, measurement, points_geometry
from topomt.third_party.output import ProviderRecord

from .output import CaverOutput


def parse_output(run: ProviderRun) -> CaverOutput:
    """Keep snapshot/cluster/tunnel identity and ordered original axes."""
    filename = 'analysis/tunnel_profiles.csv'
    rows = csv.reader(
        io.StringIO(artifact(run, filename).decode('utf-8')), skipinitialspace=True
    )
    header = next(rows, None)
    if (
        header is None
        or len(header) < 14
        or header[:3] != ['Snapshot', 'Tunnel cluster', 'Tunnel']
        or header[12] != 'Axis'
    ):
        raise ValueError('Unsupported CAVER tunnel profile header')
    grouped: dict[tuple[str, ...], tuple[list[str], dict[str, list[float | None]]]] = {}
    for row in rows:
        if not row:
            continue
        row = [x.strip() for x in row]
        if len(row) < 14 or not all(row[:3]):
            raise ValueError('Malformed CAVER tunnel profile')
        key = tuple(row[:3])
        entry = grouped.setdefault(key, (row[:12], {}))
        if entry[0] != row[:12] or row[12] in entry[1]:
            raise ValueError('Inconsistent or duplicate CAVER profile axes')
        values = [None if x == '-' else finite(x) for x in row[13:]]
        entry[1][row[12]] = values
    records = []
    for identity, (prefix, axes) in grouped.items():
        if (
            not {'X', 'Y', 'Z', 'R'} <= axes.keys()
            or len({len(v) for v in axes.values()}) != 1
            or not axes['X']
        ):
            raise ValueError('CAVER profile axes are incomplete or unequal')
        if any(x is None for k in ('X', 'Y', 'Z', 'R') for x in axes[k]):
            raise ValueError('CAVER geometry axes contain unavailable values')
        points = list(zip(axes['X'], axes['Y'], axes['Z'], strict=True))
        geometry = points_geometry(
            'centerline',
            points,
            'Ordered CAVER tunnel samples with original local free radii; no tunnel volume is inferred',
            axes['R'],
        )
        fields: dict[str, Any] = dict(zip(header[:11], prefix[:11], strict=True))
        fields['profiles'] = {
            axis: {'value': values, 'unit': 'angstroms'}
            for axis, values in axes.items()
        }
        fields['external_measurements'] = {
            key: measurement(
                run,
                finite(prefix[index], nonnegative=True),
                unit,
                header[index],
                filename,
                definition,
            )
            for key, index, unit, definition in [
                ('throughput', 3, 'dimensionless', 'CAVER original throughput'),
                (
                    'bottleneck_radius',
                    5,
                    'angstroms',
                    'CAVER original bottleneck radius',
                ),
                (
                    'curvature',
                    9,
                    'dimensionless',
                    'CAVER path length to endpoint-distance ratio',
                ),
                (
                    'length',
                    10,
                    'angstroms',
                    'CAVER original tunnel length; not inferred from resampling',
                ),
            ]
        }
        records.append(
            ProviderRecord(
                ':'.join(identity),
                'channel',
                run,
                atom_role='unavailable_tunnel_lining_atoms',
                _fields=fields,
                _geometries=(geometry,),
            )
        )
    return CaverOutput(run, tuple(records))
