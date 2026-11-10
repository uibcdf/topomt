"""Plot retained volume definitions; native95% and reference99.9% are distinct."""

import argparse
import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def render(output: Path) -> None:
    """Render the frozen resident examples without overwriting a retained plot."""
    if output.exists():
        raise ValueError('Choose a new versioned figure path')
    collection = Path(__file__).resolve().parent.parent
    figure, axes = plt.subplots(1, 3, figsize=(12, 4.8), layout='constrained')
    examples = [
        ('regular_tetrahedron', 'Tetrahedron · 1.2 Å'),
        ('closed_shell', 'Closed shell · 0.2 Å'),
        ('shell_with_opening', 'Opening · 1.4 Å'),
    ]
    keys = ['carrier', 'bare_empty', 'probe_center']
    colors = ['#bababa', '#4477aa', '#cc8844']
    for ax, (case, title) in zip(axes, examples, strict=True):
        folder = collection / case / 'artifacts/volume_study_v1'
        native = json.loads((folder / 'native_receiving.json').read_text())['domains'][
            0
        ]
        reference = json.loads((folder / 'independent_reference.json').read_text())[
            'domains'
        ][0]['reference']
        values = np.array(
            [native['comparisons'][key]['actual_volume_nm3'] * 1000 for key in keys]
        )
        ax.bar(range(3), values, color=colors, width=0.65, alpha=0.8)
        for index, key in enumerate(keys):
            value = values[index]
            if key == 'carrier':
                ax.plot(
                    index,
                    reference['carrier_volume'] * 1000,
                    'D',
                    color='black',
                    markersize=4,
                )
            else:
                low, high = (
                    np.array(native['comparisons'][key]['native_interval_nm3']) * 1000
                )
                ax.errorbar(
                    index - 0.06,
                    value,
                    yerr=np.array([[value - low], [high - value]]),
                    fmt='o',
                    color='#17496c',
                    capsize=3,
                    markersize=4,
                )
                row = reference[key]
                point = row['estimate'] * 1000
                low, high = np.array(row['interval']) * 1000
                ax.errorbar(
                    index + 0.06,
                    point,
                    yerr=np.array([[point - low], [high - point]]),
                    fmt='D',
                    color='black',
                    capsize=3,
                    markersize=4,
                )
            ax.annotate(
                f'{value:.2f}',
                (index, value),
                xytext=(0, 10),
                textcoords='offset points',
                ha='center',
                fontsize=10,
            )
        ax.set_xticks(range(3), ['Carrier', 'Bare empty', 'Probe centers'])
        ax.tick_params(axis='x', labelrotation=12)
        ax.set_ylabel('Volume (Å³)')
        ax.set_title(title)
        ax.set_ylim(0, values.max() * 1.18)
        ax.grid(axis='y', alpha=0.15)
    figure.suptitle('The same finite support, three different measured sets')
    figure.legend(
        handles=[
            Line2D(
                [],
                [],
                marker='o',
                color='#17496c',
                linestyle='none',
                label='Native MC · 95% interval',
            ),
            Line2D(
                [],
                [],
                marker='D',
                color='black',
                linestyle='none',
                label='Independent Cartesian reference · 99.9% bound',
            ),
        ],
        loc='outside lower center',
        ncols=2,
        frameon=False,
    )
    figure.savefig(output, dpi=160)
    plt.close(figure)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    render(parser.parse_args().output)
