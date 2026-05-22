"""Run DFND probe-radius sweeps on local small molecular systems.

This script is an engineering-coherence harness. It does not validate cavity
quality. It checks whether the DFND substrate responds consistently when the
probe radius changes.
"""

import argparse
import tempfile
import time
from pathlib import Path
from zipfile import ZipFile

from topomt.dfnd.graph import DelaunayFlowNetwork


DEFAULT_SYSTEMS = ('1crn', '1rop', '2pk4', '2lyz', '3ptb')
DEFAULT_RADII = (0.8, 1.0, 1.2, 1.4, 1.8, 2.2)
DEFAULT_DATA_DIRS = (
    Path('topomt/data/CASTpFold_server'),
    Path('topomt/data/CASTp_3.0_server'),
)


def _extract_first_pdb_from_zip(zip_path: Path, output_dir: Path) -> Path:
    with ZipFile(zip_path) as zip_file:
        pdb_names = sorted(
            name for name in zip_file.namelist() if name.lower().endswith('.pdb')
        )
        if not pdb_names:
            raise ValueError(f'No PDB file found in {zip_path}')
        pdb_name = pdb_names[0]
        output_path = output_dir / f'{zip_path.stem}_{Path(pdb_name).name}'
        output_path.write_bytes(zip_file.read(pdb_name))
        return output_path


def _resolve_input(system_id: str, data_dirs: list[Path], output_dir: Path) -> Path:
    direct = Path(system_id)
    if direct.exists():
        return direct
    for data_dir in data_dirs:
        pdb_path = data_dir / f'{system_id}.pdb'
        if pdb_path.exists():
            return pdb_path
        zip_path = data_dir / f'{system_id}.zip'
        if zip_path.exists():
            return _extract_first_pdb_from_zip(zip_path, output_dir)
    searched = ', '.join(str(data_dir) for data_dir in data_dirs)
    raise FileNotFoundError(f'Could not resolve {system_id!r} under {searched}')


def _family_counts(domains: list[dict]) -> dict[str, int]:
    counts = {}
    for domain in domains:
        family = domain['domain_family']
        counts[family] = counts.get(family, 0) + 1
    return counts


def _format_family_counts(family_counts: dict[str, int]) -> str:
    if not family_counts:
        return '-'
    return ', '.join(f'{key}:{value}' for key, value in sorted(family_counts.items()))


def _summarize(
    system_id: str,
    pdb_path: Path,
    probe_radius: float,
    build_elapsed: float,
    query_elapsed: float,
    result: dict,
) -> dict:
    records = result['raw']
    tetrahedra = records['tetrahedra']
    faces = records['faces']
    domains = records['concavity_domains']
    resident_count = sum(
        1 for record in tetrahedra if record['residence_state'] == 'resident'
    )
    connector_count = sum(
        1 for record in tetrahedra if record['transit_role'] == 'transit_connector'
    )
    terminal_count = sum(
        1 for record in tetrahedra if record['transit_role'] == 'terminal_contact'
    )
    permeable_face_slots = sum(
        1 for record in faces if record['permeability_state'] == 'permeable'
    )
    marginal_tetrahedra = sum(
        1 for record in tetrahedra if 'marginal' in record['flags']
    )
    marginal_faces = sum(1 for record in faces if 'marginal' in record['flags'])
    volume_topological = sum(
        domain['volume_topological_resident'] for domain in domains
    )
    volume_solvent = sum(domain['volume_solvent_estimate'] for domain in domains)
    return {
        'system_id': system_id,
        'pdb_path': str(pdb_path),
        'probe_radius': float(probe_radius),
        'build_elapsed_s': float(build_elapsed),
        'query_elapsed_s': float(query_elapsed),
        'n_tetrahedra': len(tetrahedra),
        'n_faces': len(faces),
        'n_resident_tetrahedra': resident_count,
        'n_transit_connectors': connector_count,
        'n_terminal_contacts': terminal_count,
        'n_permeable_face_slots': permeable_face_slots,
        'n_domains': len(domains),
        'n_external_links': len(records['external_links']),
        'n_dry_components': len(result['dry']['components']),
        'n_dry_interfaces': len(records['dry_interfaces']),
        'n_marginal_tetrahedra': marginal_tetrahedra,
        'n_marginal_faces': marginal_faces,
        'volume_topological_resident': float(volume_topological),
        'volume_solvent_estimate': float(volume_solvent),
        'family_counts': _family_counts(domains),
    }


def _nonincreasing(values: list[int | float]) -> bool:
    return all(left >= right for left, right in zip(values, values[1:]))


def _invariant_records(records: list[dict]) -> list[dict]:
    by_system = {}
    for record in records:
        by_system.setdefault(record['system_id'], []).append(record)

    invariants = []
    for system_id, system_records in sorted(by_system.items()):
        ordered = sorted(system_records, key=lambda item: item['probe_radius'])
        invariants.append(
            {
                'system_id': system_id,
                'resident_nonincreasing': _nonincreasing(
                    [record['n_resident_tetrahedra'] for record in ordered]
                ),
                'permeable_faces_nonincreasing': _nonincreasing(
                    [record['n_permeable_face_slots'] for record in ordered]
                ),
                'resident_volume_nonincreasing': _nonincreasing(
                    [record['volume_solvent_estimate'] for record in ordered]
                ),
            }
        )
    return invariants


def run_sweep(
    systems: list[str],
    probe_radii: list[float],
    data_dirs: list[Path],
    selection: str,
) -> list[dict]:
    records = []
    with tempfile.TemporaryDirectory(prefix='dfnd-probe-sweep-') as tmp_name:
        tmp_dir = Path(tmp_name)
        input_paths = {
            system_id: _resolve_input(system_id, data_dirs, tmp_dir)
            for system_id in systems
        }
        for system_id in systems:
            pdb_path = input_paths[system_id]
            build_start = time.perf_counter()
            network = DelaunayFlowNetwork(
                str(pdb_path),
                selection=selection,
                hydrogen_policy='exclude',
            )
            build_elapsed = time.perf_counter() - build_start
            for probe_radius in probe_radii:
                query_start = time.perf_counter()
                result = network.get_topography(
                    probe_radius=probe_radius,
                    min_size=0,
                    transit_policy='with_connectors',
                )
                query_elapsed = time.perf_counter() - query_start
                records.append(
                    _summarize(
                        system_id,
                        pdb_path,
                        probe_radius,
                        build_elapsed,
                        query_elapsed,
                        result,
                    )
                )
    return records


def write_markdown_report(records: list[dict], output_path: Path, selection: str) -> None:
    invariants = _invariant_records(records)
    lines = [
        '# DFND Probe-Radius Sweep',
        '',
        'This is an engineering-coherence report, not a cavity-detection quality validation.',
        '',
        f'Selection: `{selection}`',
        '',
        '## Monotonicity Checks',
        '',
        '| system | resident non-increasing | permeable faces non-increasing | resident solvent volume non-increasing |',
        '| --- | --- | --- | --- |',
    ]
    for invariant in invariants:
        lines.append(
            '| {system_id} | {resident_nonincreasing} | {permeable_faces_nonincreasing} | {resident_volume_nonincreasing} |'.format(
                **invariant
            )
        )

    lines.extend(
        [
            '',
            '## Sweep Table',
            '',
            '| system | probe | build_s | query_s | tetra | resident | connectors | terminal | permeable_faces | domains | external_links | dry_components | dry_interfaces | families | volume_solvent_estimate |',
            '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |',
        ]
    )
    for record in records:
        lines.append(
            '| {system_id} | {probe_radius:.2f} | {build_elapsed_s:.2f} | {query_elapsed_s:.2f} | {n_tetrahedra} | {n_resident_tetrahedra} | {n_transit_connectors} | {n_terminal_contacts} | {n_permeable_face_slots} | {n_domains} | {n_external_links} | {n_dry_components} | {n_dry_interfaces} | {families} | {volume_solvent_estimate:.3f} |'.format(
                families=_format_family_counts(record['family_counts']),
                **record,
            )
        )
    output_path.write_text('\n'.join(lines) + '\n')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('systems', nargs='*', default=list(DEFAULT_SYSTEMS))
    parser.add_argument(
        '--probe-radius',
        dest='probe_radii',
        action='append',
        type=float,
        default=None,
        help='Probe radius to include. May be used multiple times.',
    )
    parser.add_argument(
        '--data-dir',
        dest='data_dirs',
        action='append',
        type=Path,
        default=None,
        help='Directory containing PDB or zip files. May be used multiple times.',
    )
    parser.add_argument(
        '--selection',
        default="molecule_type in ['protein', 'peptide']",
        help='MolSysMT selection used before DFND.',
    )
    parser.add_argument('--output', type=Path, default=None)
    args = parser.parse_args()

    probe_radii = args.probe_radii if args.probe_radii is not None else list(DEFAULT_RADII)
    data_dirs = args.data_dirs if args.data_dirs is not None else list(DEFAULT_DATA_DIRS)
    records = run_sweep(args.systems, probe_radii, data_dirs, args.selection)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        write_markdown_report(records, args.output, args.selection)
    else:
        for record in records:
            print(record)


if __name__ == '__main__':
    main()
