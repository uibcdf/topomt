"""Compare native CASTp3 records against persisted CASTpFold oracle ZIPs."""

from __future__ import annotations

import argparse
import tempfile
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from topomt.io.load_CASTp import (
    _feature_type_from_n_mouths,
    _parse_mouth_file,
    _parse_poc_file,
    _parse_poc_info_file,
)
from topomt.third_party.castp3._native_impl import castp as native_castp3


DEFAULT_ZIP_DIR = Path('topomt/data/CASTpFold_server')
DEFAULT_FEATURE_TYPES = ('pocket', 'void', 'channel', 'branched_channel', 'mouth')
DEFAULT_SELECTION = 'molecule_type in ["protein", "peptide"]'


@dataclass(frozen=True)
class ParityRow:
    """One feature-type parity summary."""

    pdb_id: str
    feature_type: str
    oracle_count: int
    native_count: int
    exact_count: int


def atom_ids_from_castp_labels(atom_labels: set[str]) -> frozenset[int]:
    """Return stable PDB atom IDs from CASTp atom labels."""

    return frozenset(int(label.split('-', 1)[0]) for label in atom_labels)


def compare_atom_id_sets(
    native_sets: list[frozenset[int]],
    oracle_sets: list[frozenset[int]],
) -> tuple[int, int, int]:
    """Return oracle count, native count, and exact multiset matches."""

    native_counter = Counter(native_sets)
    oracle_counter = Counter(oracle_sets)
    exact_count = sum((native_counter & oracle_counter).values())
    return len(oracle_sets), len(native_sets), exact_count


def oracle_atom_id_sets(extracted_dir: str | Path) -> dict[str, list[frozenset[int]]]:
    """Return CASTpFold oracle feature atom sets keyed by feature type."""

    extracted_dir = Path(extracted_dir)
    poc_file = next(extracted_dir.glob('*.poc'))
    poc_info_file = next(extracted_dir.glob('*.pocInfo'))
    mouth_file = next(extracted_dir.glob('*.mouth'))

    poc_atom_labels = _parse_poc_file(poc_file)
    poc_info = _parse_poc_info_file(poc_info_file)

    result: dict[str, list[frozenset[int]]] = {
        feature_type: [] for feature_type in DEFAULT_FEATURE_TYPES
    }

    for poc_id, atom_labels in poc_atom_labels.items():
        feature_type = _feature_type_from_n_mouths(poc_info[poc_id]['n_mouths'])
        result.setdefault(feature_type, []).append(atom_ids_from_castp_labels(atom_labels))

    mouth_atom_labels = _parse_mouth_file(mouth_file)
    result['mouth'] = [
        atom_ids_from_castp_labels(atom_labels)
        for atom_labels in mouth_atom_labels.values()
    ]

    return result


def _atom_id_lookup(molecular_system) -> dict[int, int]:
    """Return native atom-index to PDB-serial mapping from an input PDB file.

    CASTp `.poc` and `.mouth` files use the PDB atom serial field, not
    necessarily MolSysMT's normalized `atom_id`. For oracle parity, the stable
    comparison frame is therefore the fixed-width serial in columns 7-11 of the
    exact PDB bundled in the oracle ZIP.
    """

    pdb_file = Path(molecular_system)
    atom_serials = []
    with pdb_file.open('r', encoding='utf-8') as handle:
        for line in handle:
            if not line.startswith(('ATOM', 'HETATM')):
                continue
            atom_serials.append(int(line[6:11]))

    return {
        atom_index: atom_serial
        for atom_index, atom_serial in enumerate(atom_serials)
    }


def _record_atom_ids(
    atom_indices: list[int],
    atom_id_by_index: dict[int, int],
) -> frozenset[int]:
    return frozenset(atom_id_by_index[int(atom_index)] for atom_index in atom_indices)


def native_atom_id_sets(
    records: list[dict],
    atom_id_by_index: dict[int, int],
) -> dict[str, list[frozenset[int]]]:
    """Return native feature atom sets keyed by server-comparable feature type."""

    result: dict[str, list[frozenset[int]]] = {
        feature_type: [] for feature_type in DEFAULT_FEATURE_TYPES
    }

    for record in records:
        feature_type = record.get('feature_type')
        if feature_type in result:
            result[feature_type].append(
                _record_atom_ids(record.get('atom_indices', []), atom_id_by_index)
            )
        for mouth in record.get('mouths', []):
            result['mouth'].append(
                _record_atom_ids(mouth.get('atom_indices', []), atom_id_by_index)
            )

    return result


def compare_castp3_oracle_zip(
    zip_file: str | Path,
    *,
    radii_model: str = 'protor',
    probe_limited_depth: bool = False,
    peripheral_atom_expansion_steps: int = 0,
    alpha_boundary_epsilon_length: float = 0.0,
    alpha_boundary_face_epsilon_rank: int = 0,
    probe_radius: float = 1.4,
    selection: str = DEFAULT_SELECTION,
    feature_types: tuple[str, ...] = DEFAULT_FEATURE_TYPES,
) -> list[ParityRow]:
    """Compare one CASTpFold oracle ZIP against the native CASTp3 path."""

    zip_file = Path(zip_file)
    pdb_id = zip_file.stem.lower()

    with tempfile.TemporaryDirectory(prefix='topomt_castp3_oracle_') as tmpdir:
        tmpdir_path = Path(tmpdir)
        with zipfile.ZipFile(zip_file) as handle:
            handle.extractall(tmpdir_path)

        pdb_file = next(tmpdir_path.glob('*.pdb'))
        atom_id_by_index = _atom_id_lookup(pdb_file)

        records, mesh = native_castp3(
            pdb_file,
            selection=selection,
            probe_radius=probe_radius,
            radii_model=radii_model,
            probe_limited_depth=probe_limited_depth,
            peripheral_atom_expansion_steps=int(peripheral_atom_expansion_steps),
            alpha_boundary_epsilon_length=float(alpha_boundary_epsilon_length),
            alpha_boundary_face_epsilon_rank=int(alpha_boundary_face_epsilon_rank),
        )
        del mesh

        oracle_sets = oracle_atom_id_sets(tmpdir_path)
        native_sets = native_atom_id_sets(records, atom_id_by_index)

    rows = []
    for feature_type in feature_types:
        oracle_count, native_count, exact_count = compare_atom_id_sets(
            native_sets.get(feature_type, []),
            oracle_sets.get(feature_type, []),
        )
        rows.append(
            ParityRow(
                pdb_id=pdb_id,
                feature_type=feature_type,
                oracle_count=oracle_count,
                native_count=native_count,
                exact_count=exact_count,
            )
        )

    return rows


def render_markdown_table(rows: list[ParityRow]) -> str:
    """Render parity rows as a markdown table."""

    lines = [
        '| pdb | type | oracle | native | exact |',
        '|---|---:|---:|---:|---:|',
    ]
    for row in rows:
        lines.append(
            f'| {row.pdb_id} | {row.feature_type} | {row.oracle_count} | '
            f'{row.native_count} | {row.exact_count} |'
        )
    return '\n'.join(lines) + '\n'


def _selected_zip_files(args: argparse.Namespace) -> list[Path]:
    zip_dir = Path(args.zip_dir)
    if args.ids:
        zip_files = [zip_dir / f'{pdb_id.lower()}.zip' for pdb_id in args.ids]
    else:
        zip_files = sorted(zip_dir.glob('*.zip'))

    if args.limit is not None:
        zip_files = zip_files[: int(args.limit)]

    missing = [path for path in zip_files if not path.exists()]
    if missing:
        missing_text = ', '.join(str(path) for path in missing)
        raise FileNotFoundError(f'Missing oracle ZIP file(s): {missing_text}')

    return zip_files


def main() -> None:
    """Run native-vs-oracle CASTp3 parity comparisons."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip-dir', type=Path, default=DEFAULT_ZIP_DIR)
    parser.add_argument('--ids', nargs='*', help='Explicit PDB IDs to compare.')
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--radii-model', default='protor')
    parser.add_argument('--selection', default=DEFAULT_SELECTION)
    parser.add_argument('--probe-radius', type=float, default=1.4)
    parser.add_argument('--probe-limited-depth', action='store_true', default=False)
    parser.add_argument('--full-depth', action='store_false', dest='probe_limited_depth')
    parser.add_argument(
        '--peripheral-atom-expansion-steps',
        type=int,
        default=0,
        help=(
            'Experimental reporting-only atom expansion from neighboring '
            'tetrahedra. Default 0 keeps canonical native atom sets.'
        ),
    )
    parser.add_argument(
        '--alpha-boundary-epsilon-length',
        type=float,
        default=0.0,
        help=(
            'Experimental global alpha-boundary tolerance in angstroms. '
            'A positive value subtracts this amount from effective inflated '
            'radii before building the weighted triangulation. Default 0.0 '
            'keeps canonical native geometry.'
        ),
    )
    parser.add_argument(
        '--alpha-boundary-face-epsilon-rank',
        type=int,
        default=0,
        help=(
            'Experimental face-only alpha boundary tolerance in rank units. '
            'Closed faces within this many ranks below alpha are treated as '
            'open for boundary/mouth reporting. Default 0 keeps canonical '
            'face membership.'
        ),
    )
    parser.add_argument('--output-md', type=Path, default=None)
    args = parser.parse_args()

    rows = []
    for zip_file in _selected_zip_files(args):
        rows.extend(
            compare_castp3_oracle_zip(
                zip_file,
                radii_model=args.radii_model,
                probe_limited_depth=args.probe_limited_depth,
                peripheral_atom_expansion_steps=args.peripheral_atom_expansion_steps,
                alpha_boundary_epsilon_length=args.alpha_boundary_epsilon_length,
                alpha_boundary_face_epsilon_rank=args.alpha_boundary_face_epsilon_rank,
                probe_radius=args.probe_radius,
                selection=args.selection,
            )
        )

    markdown = render_markdown_table(rows)
    if args.output_md is None:
        print(markdown, end='')
    else:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(markdown)


if __name__ == '__main__':
    main()
