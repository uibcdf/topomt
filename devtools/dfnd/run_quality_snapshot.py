"""Generate a qualitative DFND domain snapshot for small real systems."""

import argparse
import tempfile
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from topomt.dfnd.graph import DelaunayFlowNetwork
from devtools.dfnd.run_probe_sweep import DEFAULT_DATA_DIRS, DEFAULT_SYSTEMS, _resolve_input


def _family_counts(domains):
    counts = {}
    for domain in domains:
        family = domain['family']
        counts[family] = counts.get(family, 0) + 1
    return counts


def _format_counts(counts):
    if not counts:
        return '-'
    return ', '.join(f'{key}:{value}' for key, value in sorted(counts.items()))


def _top_domains(domains, limit):
    return sorted(
        domains,
        key=lambda domain: (
            domain['volume_solvent_estimate'],
            domain['n_resident_nodes'],
            domain['n_nodes'],
        ),
        reverse=True,
    )[:limit]


def run_snapshot(systems, data_dirs, selection, probe_radius, top_n):
    records = []
    with tempfile.TemporaryDirectory(prefix='dfnd-quality-snapshot-') as tmp_name:
        tmp_dir = Path(tmp_name)
        for system_id in systems:
            pdb_path = _resolve_input(system_id, data_dirs, tmp_dir)
            build_start = time.perf_counter()
            network = DelaunayFlowNetwork(
                str(pdb_path),
                selection=selection,
                hydrogen_policy='exclude',
            )
            build_elapsed = time.perf_counter() - build_start
            query_start = time.perf_counter()
            result = network.get_topography(
                probe_radius=probe_radius,
                min_size=0,
                transit_policy='with_connectors',
            )
            query_elapsed = time.perf_counter() - query_start
            domains = result['raw']['wet_components']
            records.append(
                {
                    'system_id': system_id,
                    'pdb_path': str(pdb_path),
                    'build_elapsed_s': build_elapsed,
                    'query_elapsed_s': query_elapsed,
                    'n_tetrahedra': len(result['raw']['tetrahedra']),
                    'n_domains': len(domains),
                    'n_external_links': len(result['raw']['external_links']),
                    'n_dry_components': len(result['dry']['components']),
                    'n_dry_interfaces': len(result['raw']['dry_interfaces']),
                    'family_counts': _family_counts(domains),
                    'top_domains': _top_domains(domains, top_n),
                }
            )
    return records


def write_markdown(records, output_path, selection, probe_radius):
    lines = [
        '# DFND Qualitative Domain Snapshot',
        '',
        'This report is a qualitative engineering snapshot. It is not a CASTp/fpocket parity report and it does not claim biological correctness.',
        '',
        f'Probe radius: `{probe_radius:.2f} Å`',
        f'Selection: `{selection}`',
        '',
        '## System Summary',
        '',
        '| system | build_s | query_s | tetra | domains | external_links | dry_components | dry_interfaces | families |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |',
    ]
    for record in records:
        lines.append(
            '| {system_id} | {build_elapsed_s:.2f} | {query_elapsed_s:.2f} | {n_tetrahedra} | {n_domains} | {n_external_links} | {n_dry_components} | {n_dry_interfaces} | {families} |'.format(
                families=_format_counts(record['family_counts']),
                **record,
            )
        )

    lines.extend(['', '## Largest Resident Domains', ''])
    for record in records:
        lines.extend(
            [
                f"### {record['system_id']}",
                '',
                '| rank | id | family | nodes | resident | connectors | external_links | atoms | volume_solvent_estimate | path_capacity_min | flags |',
                '| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |',
            ]
        )
        for rank, domain in enumerate(record['top_domains'], start=1):
            path_capacity = domain['path_capacity_min']
            path_capacity_text = '-' if path_capacity is None else f'{path_capacity:.3f}'
            flags = ','.join(domain['flags']) if domain['flags'] else '-'
            lines.append(
                '| {rank} | {id} | {family} | {n_nodes} | {n_resident_nodes} | {n_transit_connector_nodes} | {n_external_links} | {n_atoms} | {volume_solvent_estimate:.3f} | {path_capacity} | {flags_text} |'.format(
                    rank=rank,
                    n_atoms=len(domain['atom_indices']),
                    path_capacity=path_capacity_text,
                    flags_text=flags,
                    **domain,
                )
            )
        lines.append('')

    lines.extend(
        [
            '## Reading Notes',
            '',
            '- The table is sorted by resident solvent-volume estimate, then resident nodes, then total nodes.',
            '- Large numbers of small voids are expected at this stage and should be evaluated later with reporting filters, not by changing the core decomposition.',
            '- `channel_domain` is still a topological multi-link label; biological channel/tunnel interpretation remains a later morphology step.',
        ]
    )
    output_path.write_text('\n'.join(lines) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('systems', nargs='*', default=list(DEFAULT_SYSTEMS))
    parser.add_argument('--data-dir', dest='data_dirs', action='append', type=Path, default=None)
    parser.add_argument('--selection', default="molecule_type in ['protein', 'peptide']")
    parser.add_argument('--probe-radius', type=float, default=1.4)
    parser.add_argument('--top-n', type=int, default=5)
    parser.add_argument('--output', type=Path, default=None)
    args = parser.parse_args()

    data_dirs = args.data_dirs if args.data_dirs is not None else list(DEFAULT_DATA_DIRS)
    records = run_snapshot(
        args.systems,
        data_dirs,
        args.selection,
        args.probe_radius,
        args.top_n,
    )
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(records, args.output, args.selection, args.probe_radius)
    else:
        for record in records:
            print(record)


if __name__ == '__main__':
    main()
