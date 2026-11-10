import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pyunitwizard as puw
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pyunitwizard import QuantityRecord
from scipy.spatial import ConvexHull

root = Path(__file__).resolve().parents[3]

parser = argparse.ArgumentParser(
    description='Render the fixed-input contact illustration to a new file'
)
parser.add_argument('--output', type=Path, required=True)
output = parser.parse_args().output
if output.exists():
    raise FileExistsError('Choose a new presentation figure path')


def coords(case):
    record = json.loads((root / case / f'artifacts/{case}_v1/input.json').read_text())[
        'coordinates'
    ]
    return np.asarray(
        puw.get_value(
            QuantityRecord.from_dict(record).to_quantity(
                field='coordinates', unit='angstroms'
            ),
            to_unit='angstroms',
        )
    )


parent = coords('closed_shell')
child = coords('shell_with_opening')
fig = plt.figure(figsize=(12, 6.2), layout='constrained')
for i, (xyz, title) in enumerate(
    [
        (parent, 'Closed parent: enclosed origin'),
        (child, 'Opened subset: certified escape'),
    ],
    1,
):
    ax = fig.add_subplot(1, 2, i, projection='3d')
    ax.add_collection3d(
        Poly3DCollection(
            xyz[ConvexHull(xyz).simplices],
            facecolors='tan',
            edgecolors='grey',
            alpha=0.06,
            linewidths=0.35,
        )
    )
    ax.scatter(*xyz.T, s=10, color='dimgray')
    ax.scatter(0, 0, 0, s=35, color='tab:blue')
    if i == 2:
        ax.add_collection3d(
            Poly3DCollection(
                [child[[0, 1, 2]]],
                facecolors='tab:orange',
                edgecolors='tab:orange',
                alpha=0.4,
            )
        )
        ax.plot([0, 0], [0, 11], [0, 0], color='tab:green', lw=2)
    ax.set(
        xlim=(-8, 8),
        ylim=(-8, 12),
        zlim=(-8, 8),
        xlabel='x (Å)',
        ylabel='y (Å)',
        zlabel='z (Å)',
        title=title,
    )
    ax.set_box_aspect((16, 20, 16))
    ax.view_init(elev=20, azim=-40)
fig.suptitle('Same atomic radii and 1.4 Å probe; six atoms deleted', fontsize=14)
handles = [
    Line2D([], [], marker='o', linestyle='', color='dimgray', label='Atomic centers'),
    Line2D([], [], marker='o', linestyle='', color='tab:blue', label='Declared origin'),
    Line2D([], [], color='tab:orange', lw=5, label='Native contact carrier triangle'),
    Line2D([], [], color='tab:green', lw=2, label='Independent all-atom escape ray'),
]
fig.legend(handles=handles, loc='outside lower center', ncols=2, frameon=False)
fig.savefig(output, dpi=150, bbox_inches='tight')
