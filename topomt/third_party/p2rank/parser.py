"""Decode P2Rank 2.5.1 original predictions without closed-volume claims."""

import csv
import io
from typing import Any

from topomt.provider_output import ProviderRun
from topomt.third_party._protocol import artifact, finite, measurement, points_geometry
from topomt.third_party.output import ProviderRecord

from .output import P2RankOutput


def parse_output(run: ProviderRun) -> P2RankOutput:
    """Keep original site names, ranks, scores and declared point centers."""
    names = [
        name[7:]
        for name, _ in run.artifacts
        if name.startswith('output/') and name.endswith('_predictions.csv')
    ]
    if len(names) != 1:
        raise ValueError('P2Rank requires exactly one original predictions CSV')
    filename = names[0]
    reader = csv.DictReader(
        io.StringIO(artifact(run, filename).decode('utf-8')), skipinitialspace=True
    )
    if reader.fieldnames is not None:
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
    expected = {
        'name',
        'rank',
        'score',
        'probability',
        'sas_points',
        'surf_atoms',
        'center_x',
        'center_y',
        'center_z',
        'residue_ids',
        'surf_atom_ids',
    }
    if (
        reader.fieldnames is None
        or set(reader.fieldnames) != expected
        or len(reader.fieldnames) != len(expected)
    ):
        raise ValueError('Unsupported P2Rank 2.5.1 predictions header')
    records = []
    ranks = set()
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError('Malformed P2Rank predictions row')
        fields: dict[str, Any] = {key: value.strip() for key, value in row.items()}
        for key in ('rank', 'sas_points', 'surf_atoms'):
            fields[key] = int(fields[key])
            if fields[key] < (1 if key == 'rank' else 0):
                raise ValueError('Invalid P2Rank rank/count')
        if fields['rank'] in ranks or not fields['name']:
            raise ValueError('Duplicate rank or absent P2Rank name')
        ranks.add(fields['rank'])
        probability = finite(fields['probability'], nonnegative=True)
        if probability > 1:
            raise ValueError('P2Rank probability is outside [0,1]')
        fields['external_measurements'] = {
            key: measurement(
                run,
                fields[key],
                'dimensionless',
                key,
                filename,
                f'Original P2Rank {key}; not affinity or independent binding evidence',
            )
            for key in ('score', 'probability')
        }
        geometry = points_geometry(
            'predicted_center',
            [[fields['center_x'], fields['center_y'], fields['center_z']]],
            'P2Rank reported predicted-site center; not a closed pocket or ligand pose',
        )
        records.append(
            ProviderRecord(
                fields['name'],
                'site',
                run,
                atom_labels=tuple(fields['surf_atom_ids'].split()),
                atom_role='unmapped_original_surface_atom_ids',
                _fields=fields,
                _geometries=(geometry,),
            )
        )
    return P2RankOutput(run, tuple(records))
