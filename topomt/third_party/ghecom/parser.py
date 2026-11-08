"""Read original GHECOM P-mode grid clusters without manufacturing a volume."""

import re
from collections import defaultdict

from topomt.provider_output import ProviderRun
from topomt.third_party._protocol import artifact, finite, pdb_points, points_geometry
from topomt.third_party.output import ProviderRecord

from .output import GhecomOutput


def parse_output(run: ProviderRun) -> GhecomOutput:
    text = artifact(run, 'pockets.pdb').decode('utf-8')
    count = re.search(r'^REMARK\s+Ncluster\s+(\d+)\s*$', text, re.M)
    width = re.search(r'^REMARK\s+grid_width\s+(\S+)\s*$', text, re.M)
    if count is None or width is None:
        raise ValueError('GHECOM cluster/grid header is absent')
    step = finite(width[1], nonnegative=True)
    if step == 0:
        raise ValueError('GHECOM grid width must be positive')
    counts = re.findall(r'^#REMARK CLUSTER\[(\d+)\] NVOXEL\s+(\d+)\s*$', text, re.M)
    expected = {str(int(label)): int(size) for label, size in counts}
    points = defaultdict(list)
    model = None
    seen = set()
    for line in text.splitlines():
        if line.startswith('MODEL'):
            if model is not None:
                raise ValueError('Nested GHECOM cluster models')
            model = str(int(line[5:].strip()))
            if model in seen:
                raise ValueError('Duplicate GHECOM cluster model')
            seen.add(model)
        elif line.startswith('ENDMDL'):
            if model is None:
                raise ValueError('Unmatched GHECOM cluster end')
            model = None
        elif line.startswith(('ATOM  ', 'HETATM')):
            if model is None:
                raise ValueError('GHECOM grid point outside a cluster model')
            points[model].append(pdb_points((line + '\n').encode())[0][2])
    if model is not None:
        raise ValueError('Incomplete GHECOM cluster model')
    if (
        len(expected) != int(count[1])
        or len(expected) != len(counts)
        or seen != set(expected)
        or set(expected) != set(points)
        or any(len(points[label]) != size for label, size in expected.items())
    ):
        raise ValueError('GHECOM grid points and cluster counts disagree')
    records = tuple(
        ProviderRecord(
            label,
            'pocket',
            run,
            atom_role='unavailable_original_lining_atoms',
            _fields={
                'grid_point_count': expected[label],
                'grid_width': {'value': step, 'unit': 'angstroms'},
                'mode': 'P',
            },
            _geometries=(
                points_geometry(
                    'grid_points',
                    points[label],
                    'GHECOM P-mode morphological grid cluster; no exact continuous surface inferred',
                ),
            ),
        )
        for label in expected
    )
    return GhecomOutput(run, records)
