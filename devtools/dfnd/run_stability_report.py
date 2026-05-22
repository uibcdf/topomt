"""Run DFND stability checks on local PDB or CASTpFold zip files.

This harness is intentionally not a scientific validation tool. It checks that
DFND runs on real molecular inputs and that the raw records are internally
coherent enough for implementation hardening.
"""

import argparse
import tempfile
import time
from pathlib import Path
from zipfile import ZipFile

from topomt import get_topography


DEFAULT_SYSTEMS = ('1crn', '1rop', '2pk4', '3phv', '8rat', '1stp')
PUBLIC_DOMAIN_FAMILIES = {
    'void_domain',
    'pocket_domain',
    'multi_external_link_domain',
}


def _extract_first_pdb_from_zip(zip_path: Path, output_dir: Path) -> Path:
    with ZipFile(zip_path) as zip_file:
        pdb_names = sorted(
            name for name in zip_file.namelist() if name.lower().endswith('.pdb')
        )
        if not pdb_names:
            raise ValueError(f'No PDB file found in {zip_path}')
        pdb_name = pdb_names[0]
        output_path = output_dir / Path(pdb_name).name
        output_path.write_bytes(zip_file.read(pdb_name))
        return output_path


def _resolve_input(system_id: str, data_dir: Path, output_dir: Path) -> Path:
    direct = Path(system_id)
    if direct.exists():
        return direct
    pdb_path = data_dir / f'{system_id}.pdb'
    if pdb_path.exists():
        return pdb_path
    zip_path = data_dir / f'{system_id}.zip'
    if zip_path.exists():
        return _extract_first_pdb_from_zip(zip_path, output_dir)
    raise FileNotFoundError(f'Could not resolve {system_id!r} under {data_dir}')


def _summarize_topography(
    system_id: str,
    pdb_path: Path,
    elapsed: float,
    topography,
) -> dict:
    records = topography.dfnd_records
    family_counts = {}
    for domain in records['concavity_domains']:
        family = domain['domain_family']
        family_counts[family] = family_counts.get(family, 0) + 1

    public_features = topography.get_features(by='shape', value='concavity')
    public_count = len(public_features)
    expected_public_count = sum(
        count
        for family, count in family_counts.items()
        if family in PUBLIC_DOMAIN_FAMILIES
    )
    volume_topological = sum(
        domain['volume_topological_resident'] for domain in records['concavity_domains']
    )
    volume_solvent = sum(
        domain['volume_solvent_estimate']
        for domain in records['concavity_domains']
    )
    return {
        'system_id': system_id,
        'pdb_path': str(pdb_path),
        'elapsed_s': elapsed,
        'n_tetrahedra': len(records['tetrahedra']),
        'n_faces': len(records['faces']),
        'n_domains': len(records['concavity_domains']),
        'n_public_features': public_count,
        'expected_public_features': expected_public_count,
        'family_counts': family_counts,
        'volume_topological_resident': volume_topological,
        'volume_solvent_estimate': volume_solvent,
        'status': (
            'ok'
            if public_count == expected_public_count
            else 'inconsistent_public_count'
        ),
    }


def run_system(system_id: str, data_dir: Path, selection: str, tmp_dir: Path) -> dict:
    pdb_path = _resolve_input(system_id, data_dir, tmp_dir)
    start = time.perf_counter()
    topography = get_topography(
        str(pdb_path),
        method='dfnd',
        selection=selection,
        probe_radius=1.4,
        min_size=0,
        hydrogen_policy='exclude',
        transit_policy='with_connectors',
    )
    elapsed = time.perf_counter() - start
    return _summarize_topography(system_id, pdb_path, elapsed, topography)


def _format_family_counts(family_counts: dict) -> str:
    if not family_counts:
        return '-'
    return ', '.join(f'{key}:{value}' for key, value in sorted(family_counts.items()))


def write_markdown_report(records: list[dict], output_path: Path) -> None:
    lines = [
        '# DFND Real-System Stability Report',
        '',
        'This is an engineering stability report, not a cavity-detection validation report.',
        '',
        '| system | status | time_s | tetrahedra | domains | public_features | '
        'families | volume_topological_resident | volume_solvent_estimate |',
        '| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |',
    ]
    for record in records:
        lines.append(
            '| {system_id} | {status} | {elapsed_s:.2f} | {n_tetrahedra} | {n_domains} | '
            '{n_public_features} | {families} | {volume_topological_resident:.3f} | '
            '{volume_solvent_estimate:.3f} |'.format(
                families=_format_family_counts(record['family_counts']),
                **record,
            )
        )
    output_path.write_text('\n'.join(lines) + '\n')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('systems', nargs='*', default=list(DEFAULT_SYSTEMS))
    parser.add_argument(
        '--data-dir',
        default='topomt/data/CASTpFold_server',
        type=Path,
        help='Directory containing local PDB or zip files.',
    )
    parser.add_argument(
        '--selection',
        default="molecule_type in ['protein', 'peptide']",
        help='MolSysMT selection used before DFND.',
    )
    parser.add_argument('--output', type=Path, default=None)
    args = parser.parse_args()

    records = []
    with tempfile.TemporaryDirectory(prefix='dfnd-stability-') as tmp_name:
        tmp_dir = Path(tmp_name)
        for system_id in args.systems:
            records.append(run_system(system_id, args.data_dir, args.selection, tmp_dir))

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        write_markdown_report(records, args.output)
    else:
        for record in records:
            print(record)


if __name__ == '__main__':
    main()
