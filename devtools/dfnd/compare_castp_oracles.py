"""Compare DFND native domains against local CASTp-family oracle files."""

import argparse
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from devtools.castp.compare_castp3_oracles import (
    _atom_id_lookup,
    atom_ids_from_castp_labels,
    compare_atom_id_sets,
    oracle_atom_id_sets,
)
from topomt.dfnd.graph import DelaunayFlowNetwork
from topomt.io.load_CASTp import (
    _feature_type_from_n_mouths,
    _parse_mouth_file,
    _parse_poc_file,
    _parse_poc_info_file,
)


DEFAULT_SYSTEMS = (
    '1crn',
    '1rop',
    '2lyz',
    '2pk4',
    '3ptb',
    '1stp',
    '1a4j',
    '1hiv',
    '1tcd',
)
DEFAULT_FEATURE_TYPES = ('pocket', 'void', 'channel', 'mouth')
DEFAULT_SELECTION = "molecule_type in ['protein', 'peptide']"
DEFAULT_CASTP3_DIRS = (
    Path('topomt/data/CASTp_3.0_server'),
    Path('topomt/data/CASTpFold_server'),
)
DEFAULT_CASTP1_DIRS = {
    '1hiv': Path('topomt/data/HIV-1-Protease/CASTp_1hiv'),
    '1tcd': Path('topomt/data/TcTIM/CASTp_1tcd'),
}

_DFND_FAMILY_TO_CASTP = {
    'pocket': 'pocket',
    'void': 'void',
    'multi_external_link': 'channel',
}


@dataclass(frozen=True)
class SourceSummary:
    source: str
    system_id: str
    pdb_file: Path
    input_label: str
    feature_sets: dict[str, list[frozenset[int]]]


@dataclass(frozen=True)
class ComparisonRow:
    system_id: str
    source: str
    feature_type: str
    oracle_count: int | None
    dfnd_count: int
    exact_count: int | None
    oracle_only: int | None
    dfnd_only: int | None


def _extract_first_pdb_from_zip(zip_path: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
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


def _extract_zip_to_dir(zip_path: Path, output_dir: Path) -> Path:
    target_dir = output_dir / zip_path.stem
    target_dir.mkdir(parents=True, exist_ok=True)
    with ZipFile(zip_path) as zip_file:
        zip_file.extractall(target_dir)
    return target_dir


def _first_pdb_in_dir(dir_path: Path) -> Path:
    return next(dir_path.glob('*.pdb'))


def _resolve_input_pdb(system_id: str, output_dir: Path) -> Path:
    castp1_dir = DEFAULT_CASTP1_DIRS.get(system_id.lower())
    if castp1_dir is not None:
        pdb_file = castp1_dir / f'{system_id.lower()}.pdb'
        if pdb_file.exists():
            return pdb_file

    for data_dir in DEFAULT_CASTP3_DIRS:
        direct_pdb = data_dir / f'{system_id.lower()}.pdb'
        if direct_pdb.exists():
            return direct_pdb
        zip_path = data_dir / f'{system_id.lower()}.zip'
        if zip_path.exists():
            return _extract_first_pdb_from_zip(zip_path, output_dir)

    raise FileNotFoundError(f'No PDB input found for {system_id}')


def _oracle_sets_from_castp_dir(dir_path: Path) -> dict[str, list[frozenset[int]]]:
    poc_file = next(dir_path.glob('*.poc'))
    poc_info_file = next(dir_path.glob('*.pocInfo'))
    mouth_file = next(dir_path.glob('*.mouth'))

    poc_atom_labels = _parse_poc_file(poc_file)
    poc_info = _parse_poc_info_file(poc_info_file)
    mouth_atom_labels = _parse_mouth_file(mouth_file)

    result = {feature_type: [] for feature_type in DEFAULT_FEATURE_TYPES}
    for poc_id, atom_labels in poc_atom_labels.items():
        feature_type = _feature_type_from_n_mouths(poc_info[poc_id]['n_mouths'])
        if feature_type == 'branched_channel':
            feature_type = 'channel'
        if feature_type in result:
            result[feature_type].append(atom_ids_from_castp_labels(atom_labels))

    result['mouth'] = [
        atom_ids_from_castp_labels(atom_labels)
        for atom_labels in mouth_atom_labels.values()
    ]
    return result


def _available_oracle_summaries(system_id: str, tmp_dir: Path) -> list[SourceSummary]:
    lower_id = system_id.lower()
    summaries = []

    castp1_dir = DEFAULT_CASTP1_DIRS.get(lower_id)
    if castp1_dir is not None and castp1_dir.exists():
        summaries.append(
            SourceSummary(
                source='CASTp1',
                system_id=lower_id,
                pdb_file=castp1_dir / f'{lower_id}.pdb',
                input_label=str(castp1_dir / f'{lower_id}.pdb'),
                feature_sets=_oracle_sets_from_castp_dir(castp1_dir),
            )
        )

    castp30_zip = Path('topomt/data/CASTp_3.0_server') / f'{lower_id}.zip'
    if castp30_zip.exists():
        extracted_dir = _extract_zip_to_dir(castp30_zip, tmp_dir / 'castp30')
        sets = oracle_atom_id_sets(extracted_dir)
        sets['channel'] = sets.get('channel', []) + sets.get('branched_channel', [])
        summaries.append(
            SourceSummary(
                source='CASTp3.0',
                system_id=lower_id,
                pdb_file=_first_pdb_in_dir(extracted_dir),
                input_label=str(castp30_zip),
                feature_sets=sets,
            )
        )

    castpfold_zip = Path('topomt/data/CASTpFold_server') / f'{lower_id}.zip'
    if castpfold_zip.exists():
        extracted_dir = _extract_zip_to_dir(castpfold_zip, tmp_dir / 'castpfold')
        sets = oracle_atom_id_sets(extracted_dir)
        sets['channel'] = sets.get('channel', []) + sets.get('branched_channel', [])
        summaries.append(
            SourceSummary(
                source='CASTpFold',
                system_id=lower_id,
                pdb_file=_first_pdb_in_dir(extracted_dir),
                input_label=str(castpfold_zip),
                feature_sets=sets,
            )
        )

    return summaries


def _map_atom_indices_to_serials(
    atom_indices: list[int], atom_id_by_index: dict[int, int]
) -> frozenset[int]:
    return frozenset(
        atom_id_by_index[int(atom_index)]
        for atom_index in atom_indices
        if int(atom_index) in atom_id_by_index
    )


def _dfnd_feature_sets(
    result: dict,
    atom_id_by_index: dict[int, int],
) -> dict[str, list[frozenset[int]]]:
    feature_sets = {feature_type: [] for feature_type in DEFAULT_FEATURE_TYPES}
    for domain in result['raw']['wet_components']:
        feature_type = _DFND_FAMILY_TO_CASTP.get(domain['family'])
        if feature_type is None:
            continue
        feature_sets[feature_type].append(
            _map_atom_indices_to_serials(domain['atom_indices'], atom_id_by_index)
        )
        if feature_type in {'pocket', 'channel'}:
            for external_link_id in domain['external_link_ids']:
                link = result['raw']['external_links'][external_link_id - 1]
                feature_sets['mouth'].append(
                    _map_atom_indices_to_serials(link['atom_indices'], atom_id_by_index)
                )
    return feature_sets


def _dfnd_summary(
    system_id: str,
    pdb_file: Path,
    probe_radius: float,
    selection: str,
) -> tuple[dict, dict[str, list[frozenset[int]]]]:
    atom_id_by_index = _atom_id_lookup(pdb_file)
    network = DelaunayFlowNetwork(
        str(pdb_file),
        selection=selection,
        hydrogen_policy='exclude',
        radii_model='vdw',
    )
    result = network.get_topography(
        probe_radius=probe_radius,
        min_size=0,
        transit_policy='with_connectors',
    )
    domains = result['raw']['wet_components']
    metadata = {
        'system_id': system_id,
        'pdb_file': str(pdb_file),
        'n_atoms': int(network.atom_coords.shape[0]),
        'n_tetrahedra': int(network.n_tetrahedra),
        'n_domains': len(domains),
        'n_external_links': len(result['raw']['external_links']),
        'families': Counter(domain['family'] for domain in domains),
        'largest_resident_volume': max(
            (domain['volume_solvent_estimate'] for domain in domains),
            default=0.0,
        ),
    }
    return metadata, _dfnd_feature_sets(result, atom_id_by_index)


def _compare_sources(
    system_id: str,
    dfnd_sets: dict[str, list[frozenset[int]]],
    oracle_summaries: list[SourceSummary],
) -> list[ComparisonRow]:
    rows = []
    for oracle in oracle_summaries:
        for feature_type in DEFAULT_FEATURE_TYPES:
            oracle_sets = oracle.feature_sets.get(feature_type, [])
            native_sets = dfnd_sets.get(feature_type, [])
            oracle_count, dfnd_count, exact_count = compare_atom_id_sets(
                native_sets, oracle_sets
            )
            rows.append(
                ComparisonRow(
                    system_id=system_id,
                    source=oracle.source,
                    feature_type=feature_type,
                    oracle_count=oracle_count,
                    dfnd_count=dfnd_count,
                    exact_count=exact_count,
                    oracle_only=oracle_count - exact_count,
                    dfnd_only=dfnd_count - exact_count,
                )
            )
    if not oracle_summaries:
        for feature_type in DEFAULT_FEATURE_TYPES:
            rows.append(
                ComparisonRow(
                    system_id=system_id,
                    source='none',
                    feature_type=feature_type,
                    oracle_count=None,
                    dfnd_count=len(dfnd_sets.get(feature_type, [])),
                    exact_count=None,
                    oracle_only=None,
                    dfnd_only=None,
                )
            )
    return rows


def _format_count(value: int | None) -> str:
    return '-' if value is None else str(value)


def _format_families(counter: Counter) -> str:
    if not counter:
        return '-'
    return ', '.join(f'{key}:{value}' for key, value in sorted(counter.items()))


def _priority_score(rows: list[ComparisonRow]) -> tuple[int, int, int]:
    comparable = [row for row in rows if row.oracle_count is not None]
    if not comparable:
        return (999, 999, 999)
    mismatches = sum(
        abs(row.oracle_count - row.dfnd_count) + (row.oracle_only or 0)
        for row in comparable
        if row.feature_type != 'mouth'
    )
    min_exact_gap = min(
        (row.oracle_only or 0)
        for row in comparable
        if row.feature_type in DEFAULT_FEATURE_TYPES
    )
    source_penalty = 0 if any(row.source == 'CASTp3.0' for row in comparable) else 1
    return (mismatches, min_exact_gap, source_penalty)


def write_markdown(
    output_path: Path,
    dfnd_records: list[dict],
    rows_by_system: dict[str, list[ComparisonRow]],
    selection: str,
    probe_radius: float,
) -> None:
    lines = [
        '# DFND vs CASTp Oracle Validation Inventory',
        '',
        'This checkpoint compares the current DFND native decomposition against local CASTp-family oracle files. It is an inventory for choosing inspection order; it is not yet a claim of parity.',
        '',
        f'Probe radius: {probe_radius:.2f} A',
        f'Selection: {selection}',
        'Hydrogen policy: exclude',
        'DFND radii model: vdw',
        '',
        '## DFND System Summary',
        '',
        '| system | source | atoms | tetra | domains | external_links | largest_resident_volume | families | pdb_input |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |',
    ]
    for record in dfnd_records:
        family_text = _format_families(record['families'])
        lines.append(
            '| {system_id} | {source} | {n_atoms} | {n_tetrahedra} | {n_domains} | {n_external_links} | {largest_resident_volume:.3f} | {family_text} | {pdb_file} |'.format(
                family_text=family_text,
                **record,
            )
        )

    lines.extend(
        [
            '',
            '## Oracle Comparison',
            '',
            '| system | oracle | feature | oracle_count | dfnd_count | exact_atom_set_matches | oracle_only | dfnd_only |',
            '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |',
        ]
    )
    for system_id in rows_by_system:
        for row in rows_by_system[system_id]:
            lines.append(
                f'| {row.system_id} | {row.source} | {row.feature_type} | '
                f'{_format_count(row.oracle_count)} | {row.dfnd_count} | '
                f'{_format_count(row.exact_count)} | {_format_count(row.oracle_only)} | '
                f'{_format_count(row.dfnd_only)} |'
            )

    ranked = sorted(
        rows_by_system,
        key=lambda system_id: _priority_score(rows_by_system[system_id]),
    )
    lines.extend(
        [
            '',
            '## Suggested Inspection Order',
            '',
            '| rank | system | rationale |',
            '| ---: | --- | --- |',
        ]
    )
    for rank, system_id in enumerate(ranked, start=1):
        rows = rows_by_system[system_id]
        comparable = [row for row in rows if row.oracle_count is not None]
        if comparable:
            nonmouth_gap = sum(
                abs(row.oracle_count - row.dfnd_count)
                for row in comparable
                if row.feature_type != 'mouth'
            )
            exact_gap = sum(
                row.oracle_only or 0
                for row in comparable
                if row.feature_type != 'mouth'
            )
            sources = ', '.join(sorted({row.source for row in comparable}))
            rationale = f'{sources}; non-mouth count gap {nonmouth_gap}; unmatched oracle atom sets {exact_gap}'
        else:
            rationale = 'No local oracle parsed; DFND-only baseline.'
        lines.append(f'| {rank} | {system_id} | {rationale} |')

    lines.extend(
        [
            '',
            '## Reading Notes',
            '',
            '- CASTp1, CASTp3.0, and CASTpFold are kept as distinct oracle sources; CASTp3.0 and CASTpFold are not collapsed even when their files agree.',
            '- channel in this report merges CASTp channel and branched_channel because DFND currently exposes multi_external_link_domain as the topological channel-compatible family.',
            '- Exact matches compare full feature atom sets using PDB serial numbers. Count agreement without exact matches means the feature inventory is numerically similar but not atom-identical.',
            '- Mouth comparison is provisional because DFND external links are graph-derived geometric apertures, not CASTp alpha-shape mouth triangles.',
            '- This report is intended to select cases for fine inspection before algorithmic changes.',
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines) + '\n')


def run_inventory(
    systems: list[str],
    output_path: Path,
    selection: str,
    probe_radius: float,
) -> None:
    dfnd_records = []
    rows_by_system = {}
    with tempfile.TemporaryDirectory(prefix='dfnd-castp-oracle-') as tmp_name:
        tmp_dir = Path(tmp_name)
        for system_id in systems:
            lower_id = system_id.lower()
            oracle_summaries = _available_oracle_summaries(
                lower_id, tmp_dir / f'oracles_{lower_id}'
            )
            if oracle_summaries:
                for oracle in oracle_summaries:
                    metadata, dfnd_sets = _dfnd_summary(
                        lower_id, oracle.pdb_file, probe_radius, selection
                    )
                    metadata['source'] = oracle.source
                    metadata['pdb_file'] = oracle.input_label
                    dfnd_records.append(metadata)
                    key = f'{lower_id}:{oracle.source}'
                    rows_by_system[key] = _compare_sources(
                        lower_id, dfnd_sets, [oracle]
                    )
            else:
                pdb_file = _resolve_input_pdb(lower_id, tmp_dir / 'pdb')
                metadata, dfnd_sets = _dfnd_summary(
                    lower_id, pdb_file, probe_radius, selection
                )
                metadata['source'] = 'none'
                metadata['pdb_file'] = str(pdb_file)
                dfnd_records.append(metadata)
                rows_by_system[f'{lower_id}:none'] = _compare_sources(
                    lower_id, dfnd_sets, []
                )
    write_markdown(output_path, dfnd_records, rows_by_system, selection, probe_radius)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('systems', nargs='*', default=list(DEFAULT_SYSTEMS))
    parser.add_argument('--selection', default=DEFAULT_SELECTION)
    parser.add_argument('--probe-radius', type=float, default=1.4)
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('devguide/DFND/checkpoint_castp_oracle_validation_inventory.md'),
    )
    args = parser.parse_args()
    run_inventory(args.systems, args.output, args.selection, args.probe_radius)


if __name__ == '__main__':
    main()
