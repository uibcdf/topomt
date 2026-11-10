"""Render the independently localized two-region face; never overwrite evidence."""

import argparse
import json
from pathlib import Path

import matplotlib
import numpy as np
import pyunitwizard as puw
from pyunitwizard import QuantityRecord

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon


def render(output: Path) -> None:
    """Draw the declared probe-center section and verified points in angstroms."""
    if output.exists():
        raise ValueError('Choose a new output; retained figures are immutable')
    folder = Path(__file__).resolve().parent
    case = folder.parents[1]
    fixture = json.loads((case / f'artifacts/{case.name}_v1/input.json').read_text())
    protocol = json.loads((folder / 'protocol.json').read_text())
    certificate = json.loads((folder / 'certificate.json').read_text())
    quantity = QuantityRecord.from_dict(fixture['coordinates']).to_quantity(
        field='coordinates', unit='angstroms'
    )
    centers = np.asarray(puw.get_value(quantity, to_unit='angstroms'))
    radii = QuantityRecord.from_dict(fixture['atom_radii']).to_quantity(
        field='atom_radii', unit='angstroms'
    )
    expanded = (
        np.asarray(puw.get_value(radii, to_unit='angstroms'))
        + protocol['probe_angstroms']
    )
    face = next(
        row for row in certificate['faces'] if len(row['localization']['regions']) > 1
    )
    triangle = centers[face['atom_indices']]
    origin = triangle[0]
    axis = triangle[1] - origin
    axis /= np.linalg.norm(axis)
    normal = np.cross(axis, triangle[2] - origin)
    normal /= np.linalg.norm(normal)
    basis = np.array([axis, np.cross(normal, axis)])
    planar = (triangle - origin) @ basis.T
    projected = (centers - origin) @ basis.T
    heights = (centers - origin) @ normal
    valid = expanded**2 - heights**2 > 0
    circle_radii = np.sqrt(np.maximum(0.0, expanded**2 - heights**2))
    witnesses = np.array(
        [
            np.asarray(row['barycentric_weights']) @ planar
            for row in face['localization']['regions']
        ]
    )
    figure, axes = plt.subplots(1, 3, figsize=(13.5, 4.5), layout='constrained')
    for index, ax in enumerate(axes):
        carrier = Polygon(
            planar, closed=True, facecolor='#b8e3f5', edgecolor='#dd8200', linewidth=1.8
        )
        ax.add_patch(carrier)
        for center, radius in zip(projected[valid], circle_radii[valid], strict=True):
            disk = Circle(
                center, radius, facecolor='#d6d6d6', edgecolor='#888888', linewidth=0.7
            )
            ax.add_patch(disk)
            disk.set_clip_path(carrier)
            disk.set_clip_box(ax.bbox)
            disk.set_in_layout(False)
        ax.scatter(
            witnesses[:, 0],
            witnesses[:, 1],
            c=['#c44e52', '#166b3a'],
            marker='*',
            s=90,
            zorder=5,
        )
        ax.set_aspect('equal')
        ax.set_xlabel('Face coordinate u (Å)')
        ax.set_ylabel('Face coordinate v (Å)')
        if index == 0:
            ax.set_xlim(planar[:, 0].min() - 0.12, planar[:, 0].max() + 0.12)
            ax.set_ylim(planar[:, 1].min() - 0.12, planar[:, 1].max() + 0.12)
            ax.set_title('All-atom section on carrier face [18, 31, 39]')
        else:
            point = witnesses[index - 1]
            ax.set_xlim(point[0] - 0.08, point[0] + 0.08)
            ax.set_ylim(point[1] - 0.08, point[1] + 0.08)
            ax.set_title(f'Free region {index}: local detail')
    figure.suptitle(
        'Closed shell, 0.05 Å probe: two independently separated openings on one face'
    )
    figure.text(
        0.5,
        -0.035,
        'Gray: expanded-ball exclusion; blue: allowed probe centers; stars: verified witnesses. Count comes from the certificate.',
        ha='center',
        fontsize=10,
    )
    figure.savefig(output, dpi=160, bbox_inches='tight')
    plt.close(figure)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    render(parser.parse_args().output)
