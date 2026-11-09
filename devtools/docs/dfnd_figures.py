"""Generate conceptual DFND documentation diagrams without scientific runs."""

import argparse
from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch


def _box(ax, x, y, width, height, label, color='#e0f2fe'):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle='round,pad=0.008',
            facecolor=color,
            edgecolor='#475569',
            linewidth=1.0,
        )
    )
    ax.text(
        x + width / 2,
        y + height / 2,
        label,
        ha='center',
        va='center',
        fontsize=10,
        color='#0f172a',
        linespacing=1.5,
    )


def _arrow(ax, start, end):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle='-|>',
            mutation_scale=13,
            color='#475569',
            linewidth=1.2,
        )
    )


def generate_figures(
    output_directory: Path, preview_directory: Optional[Path] = None
) -> list[Path]:
    """Write reproducible explanatory SVGs and optional PNG previews.

    Parameters
    ----------
    output_directory
        Destination for the four canonical SVG diagrams.
    preview_directory
        Optional destination for raster inspection copies.

    Returns
    -------
    list of Path
        Generated SVG paths.

    Raises
    ------
    OSError
        If a destination cannot be created or written.

    Examples
    --------
    ``generate_figures(Path('docs/content/dfnd/figures'))``
    """
    output_directory.mkdir(parents=True, exist_ok=True)
    if preview_directory is not None:
        preview_directory.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            'font.family': 'DejaVu Sans',
            'svg.fonttype': 'none',
            'svg.hashsalt': 'topomt-dfnd-method-v1',
        }
    )
    paths = []

    def save(fig, name):
        path = output_directory / f'{name}.svg'
        fig.savefig(
            path, metadata={'Date': None}, facecolor='white', bbox_inches='tight'
        )
        # Matplotlib wraps SVG path data with trailing spaces. Normalize only
        # line endings; newlines still separate the same SVG path tokens.
        path.write_text(
            '\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n'
        )
        if preview_directory is not None:
            fig.savefig(
                preview_directory / f'{name}.png',
                dpi=135,
                facecolor='white',
                bbox_inches='tight',
            )
        plt.close(fig)
        paths.append(path)

    fig, ax = plt.subplots(figsize=(12.8, 4.2))
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis('off')
    labels = [
        'Selected atoms\ncoordinates, radii,\nsource mapping',
        'Ordinary Delaunay\nfinite cells and faces',
        'Local capacities\nresidence and gates',
        'Probe query\nstates and policy',
    ]
    for x, label in zip([0.015, 0.27, 0.525, 0.78], labels, strict=True):
        _box(ax, x, 0.66, 0.205, 0.23, label)
    for x in [0.22, 0.475, 0.73]:
        _arrow(ax, (x, 0.775), (x + 0.045, 0.775))
    _arrow(ax, (0.882, 0.65), (0.882, 0.51))
    for x, label in [
        (0.72, 'Finite decomposition\ncomponents and banks'),
        (0.37, 'Characterization\nboundaries, metrics, catalog'),
        (0.02, 'Topography\nfeatures and native support'),
    ]:
        _box(ax, x, 0.25, 0.265, 0.25, label, '#dcfce7')
    _arrow(ax, (0.71, 0.375), (0.645, 0.375))
    _arrow(ax, (0.36, 0.375), (0.295, 0.375))
    ax.text(
        0.5,
        0.07,
        'Continuous all-atom free space is the reference model; '
        'this pipeline does not construct it exactly.',
        ha='center',
        fontsize=10,
        color='#475569',
    )
    save(fig, 'method_pipeline')

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8))
    centers = [(-1.2, -0.6), (1.2, -0.6), (0, 1.48)]
    for index, ax in enumerate(axes):
        ax.set(xlim=(-2.35, 2.35), ylim=(-2.2, 2.6), aspect='equal')
        ax.axis('off')
        for center in centers:
            if index:
                ax.add_patch(
                    Circle(
                        center,
                        0.96,
                        facecolor='#f1d8cf',
                        edgecolor='#9a3412',
                        linestyle='--',
                        linewidth=1.2,
                    )
                )
            ax.add_patch(
                Circle(
                    center, 0.6, facecolor='#94a3b8', edgecolor='#334155', linewidth=1.0
                )
            )
        if not index:
            ax.add_patch(
                Circle(
                    (0, -0.1),
                    0.36,
                    facecolor='#bbf7d0',
                    edgecolor='#15803d',
                    linewidth=1.3,
                )
            )
        ax.plot(0, -0.1, 'o', color='#15803d', markersize=4)
        ax.annotate(
            'Admissible probe center',
            xy=(0, -0.1),
            xytext=(0, -1.92),
            ha='center',
            fontsize=10,
            arrowprops={'arrowstyle': '->', 'color': '#15803d'},
        )
        ax.set_title(
            'Atom balls and an occupied probe'
            if not index
            else 'Expanded obstacles for probe centers',
            fontsize=11,
        )
    fig.text(
        0.5,
        0.01,
        'Two-dimensional teaching schematic; '
        'expanded radius = atom radius + probe radius.',
        ha='center',
        fontsize=10,
        color='#475569',
    )
    save(fig, 'probe_geometry')

    fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.2))
    panels = [
        (
            'Capacity axis',
            'One mesh and one query',
            'Internal gate capacities\norganize joining basins',
            'Chambers / throats',
        ),
        (
            'Probe axis',
            'One mesh; probe changes',
            'States and components\nare recomputed',
            'Probe correspondences',
        ),
        (
            'Time axis',
            'Coordinates change',
            'Mesh support may change;\nmatch contextual occurrences',
            'Tracks / events',
        ),
    ]
    for ax, (title, fixed, operation, result) in zip(axes, panels, strict=True):
        ax.set(xlim=(0, 1), ylim=(0, 1))
        ax.axis('off')
        ax.set_title(title, fontsize=12, fontweight='bold')
        _box(ax, 0.04, 0.72, 0.92, 0.15, fixed)
        _box(ax, 0.04, 0.35, 0.92, 0.22, operation, '#f1f5f9')
        _box(ax, 0.04, 0.03, 0.92, 0.16, result, '#dcfce7')
        _arrow(ax, (0.5, 0.70), (0.5, 0.59))
        _arrow(ax, (0.5, 0.33), (0.5, 0.21))
    save(fig, 'persistence_axes')

    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.8))
    positions = {
        'A': (0.10, 0.48),
        'C': (0.26, 0.48),
        'B': (0.42, 0.48),
        'D': (0.67, 0.48),
        'E': (0.84, 0.48),
        'S': (0.84, 0.19),
    }
    ocean = (0.45, 0.86)
    for index, ax in enumerate(axes):
        ax.set(xlim=(-0.02, 1.02), ylim=(0.02, 1.02))
        ax.axis('off')
        ax.set_title(
            'Include the common exterior root' if index == 0 else 'Remove OCEAN',
            fontsize=12,
            fontweight='bold',
        )
        if index == 0:
            for name in ('A', 'D'):
                point = positions[name]
                ax.plot(
                    [ocean[0], point[0]],
                    [ocean[1], point[1]],
                    '--',
                    color='#64748b',
                    linewidth=1.5,
                )
            ax.text(
                *ocean,
                'OCEAN',
                ha='center',
                va='center',
                fontsize=10,
                bbox={'boxstyle': 'round,pad=0.5', 'fc': '#f1f5f9', 'ec': '#64748b'},
            )
        else:
            for x, y, width in [
                (0.025, 0.37, 0.47),
                (0.59, 0.37, 0.33),
                (0.765, 0.08, 0.15),
            ]:
                ax.add_patch(
                    FancyBboxPatch(
                        (x, y),
                        width,
                        0.22,
                        boxstyle='round,pad=0.01',
                        facecolor='#f0fdf4',
                        edgecolor='#16a34a',
                        linewidth=1,
                    )
                )
            ax.text(
                0.5,
                0.84,
                'Three finite components',
                ha='center',
                fontsize=11,
                color='#166534',
            )
        for left, right in [('A', 'C'), ('C', 'B'), ('D', 'E')]:
            start, end = positions[left], positions[right]
            ax.plot(
                [start[0], end[0]], [start[1], end[1]], color='#334155', linewidth=2
            )
        for name, (x, y) in positions.items():
            connector = name == 'C'
            ax.scatter(
                x,
                y,
                s=950,
                marker='D' if connector else 'o',
                facecolor='#ffedd5' if connector else '#dbeafe',
                edgecolor='#9a3412' if connector else '#1e40af',
                zorder=3,
            )
            ax.text(x, y, name, ha='center', va='center', fontsize=11, zorder=4)
        ax.text(0.1, 0.28, 'Resident', ha='center', fontsize=10, color='#1e40af')
        ax.text(0.32, 0.28, 'Connector', ha='center', fontsize=10, color='#9a3412')
        ax.text(0.67, 0.16, 'Sealed', ha='right', fontsize=10, color='#475569')
    fig.text(
        0.5,
        0.01,
        'Abstract graph-policy illustration; edges are admitted contacts, '
        'not certified physical paths.',
        ha='center',
        fontsize=10,
        color='#475569',
    )
    save(fig, 'finite_decomposition')
    return paths


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--output-dir', type=Path, default=Path('docs/content/dfnd/figures')
    )
    parser.add_argument('--preview-dir', type=Path)
    arguments = parser.parse_args()
    for output in generate_figures(arguments.output_dir, arguments.preview_dir):
        print(output)
