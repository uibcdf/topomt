"""Audit native CASTp3 voids against CASTpFold oracle ZIPs."""

import argparse
import sys
import tempfile
import zipfile
from collections import Counter, deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from devtools.castp.compare_castp3_oracles import (
    DEFAULT_SELECTION,
    DEFAULT_ZIP_DIR,
    _atom_id_lookup,
    _record_atom_ids,
    oracle_atom_id_sets,
)
from topomt.third_party.castp3.core.castp_core import (
    build_castp_feature_records,
    build_castp_geometry,
)
from topomt.third_party.castp3.core.castp_core.components import (
    _base_triangle_in_complex,
    _probe_rank,
    _triangle_in_complex_at,
)


def _atom_table(pdb_file: Path) -> dict[int, str]:
    atom_data = {}
    for line in pdb_file.read_text().splitlines():
        if not line.startswith(('ATOM', 'HETATM')):
            continue
        serial = int(line[6:11])
        atom = line[12:16].strip()
        residue = line[17:20].strip()
        chain = line[21].strip()
        residue_id = line[22:26].strip()
        element = line[76:78].strip()
        occupancy = line[54:60].strip()
        b_factor = line[60:66].strip()
        atom_data[serial] = (
            f'{serial} {atom} {residue} {chain} {residue_id} '
            f'{element} occ={occupancy} b={b_factor}'
        )
    return atom_data


def _jaccard(left: frozenset[int], right: frozenset[int]) -> float:
    if not left and not right:
        return 1.0
    return len(left & right) / len(left | right)


def _native_void_sets(records: list[dict], atom_lookup: dict[int, int]) -> list[frozenset[int]]:
    return [
        _record_atom_ids(record.get('atom_indices', []), atom_lookup)
        for record in records
        if record.get('feature_type') == 'void'
    ]


def _best_native_matches(
    oracle_sets: list[frozenset[int]],
    native_sets: list[frozenset[int]],
) -> list[tuple[int, int, float]]:
    matches = []
    for oracle_index, oracle_set in enumerate(oracle_sets):
        if not native_sets:
            matches.append((oracle_index, -1, 0.0))
            continue
        native_index = max(
            range(len(native_sets)),
            key=lambda index: (
                _jaccard(oracle_set, native_sets[index]),
                len(oracle_set & native_sets[index]),
                -abs(len(oracle_set) - len(native_sets[index])),
            ),
        )
        matches.append(
            (
                int(oracle_index),
                int(native_index),
                float(_jaccard(oracle_set, native_sets[native_index])),
            )
        )
    return matches


def _serials_for_simplex(geometry, atom_lookup: dict[int, int], simplex_index: int) -> list[int]:
    return [
        int(atom_lookup[int(atom_index)])
        for atom_index in geometry.mesh.simplices[int(simplex_index)]
    ]


def _serials_for_face(
    geometry,
    atom_lookup: dict[int, int],
    simplex_index: int,
    face_index: int,
) -> list[int]:
    return [
        int(atom_lookup[int(atom_index)])
        for atom_index in geometry.mesh.get_face_atoms(int(simplex_index), int(face_index))
    ]


def _neighbor_atom_variants(
    geometry,
    void_records: list[dict],
    atom_lookup: dict[int, int],
) -> dict[str, list[frozenset[int]]]:
    variants = {
        'base': [],
        'simplices_plus_ifiev': [],
        'wall_opposite_base_complex': [],
        'wall_opposite_attached_base_complex': [],
        'wall_full_base_complex': [],
    }

    for record in void_records:
        component = {int(index) for index in record.get('tetrahedron_indices', [])}
        base_atoms = {int(atom_index) for atom_index in record.get('atom_indices', [])}
        element_atoms = set(base_atoms)
        for face in record.get('iF', []):
            element_atoms.update(int(atom_index) for atom_index in face)
        for edge in record.get('iE', []):
            element_atoms.update(int(atom_index) for atom_index in edge)
        element_atoms.update(int(atom_index) for atom_index in record.get('iV', []))

        wall_opposite = set(base_atoms)
        wall_opposite_attached = set(base_atoms)
        wall_full = set(base_atoms)
        for simplex_index in component:
            simplex_atoms = {
                int(atom_index)
                for atom_index in geometry.mesh.simplices[int(simplex_index)]
            }
            for face_index, neighbor_index in enumerate(
                geometry.mesh.neighbors[int(simplex_index)]
            ):
                neighbor_index = int(neighbor_index)
                if neighbor_index == -1 or neighbor_index in component:
                    continue
                if not _base_triangle_in_complex(geometry, simplex_index, face_index):
                    continue

                neighbor_atoms = {
                    int(atom_index)
                    for atom_index in geometry.mesh.simplices[neighbor_index]
                }
                face_atoms = {
                    int(atom_index)
                    for atom_index in geometry.mesh.get_face_atoms(
                        int(simplex_index),
                        int(face_index),
                    )
                }
                opposite_atoms = neighbor_atoms - face_atoms
                wall_opposite.update(opposite_atoms)
                wall_full.update(neighbor_atoms)
                if int(geometry.face_rho_ranks[int(simplex_index), int(face_index)]) == 0:
                    wall_opposite_attached.update(opposite_atoms)

        variants['base'].append(
            frozenset(atom_lookup[int(atom_index)] for atom_index in base_atoms)
        )
        variants['simplices_plus_ifiev'].append(
            frozenset(atom_lookup[int(atom_index)] for atom_index in element_atoms)
        )
        variants['wall_opposite_base_complex'].append(
            frozenset(atom_lookup[int(atom_index)] for atom_index in wall_opposite)
        )
        variants['wall_opposite_attached_base_complex'].append(
            frozenset(atom_lookup[int(atom_index)] for atom_index in wall_opposite_attached)
        )
        variants['wall_full_base_complex'].append(
            frozenset(atom_lookup[int(atom_index)] for atom_index in wall_full)
        )

    return variants


def _variant_exact_count(
    native_sets: list[frozenset[int]],
    oracle_sets: list[frozenset[int]],
) -> int:
    return sum((Counter(native_sets) & Counter(oracle_sets)).values())


def _neighbor_hits_for_atom(
    geometry,
    atom_lookup: dict[int, int],
    component: set[int],
    serial: int,
    max_distance: int,
) -> list[dict]:
    local_by_serial = {serial_id: atom_index for atom_index, serial_id in atom_lookup.items()}
    atom_index = int(local_by_serial[int(serial)])
    containing = {
        simplex_index
        for simplex_index, simplex in enumerate(geometry.mesh.simplices)
        if atom_index in {int(value) for value in simplex}
    }
    queue = deque((simplex_index, 0) for simplex_index in component)
    visited = set(component)
    hits = []
    beta_rank = _probe_rank(geometry, 1.4)

    while queue:
        simplex_index, distance = queue.popleft()
        if simplex_index in containing and distance == 0:
            hits.append(
                {
                    'simplex': int(simplex_index),
                    'distance': int(distance),
                    'serials': _serials_for_simplex(geometry, atom_lookup, simplex_index),
                }
            )
        if distance >= int(max_distance):
            continue
        for face_index, neighbor_index in enumerate(geometry.mesh.neighbors[simplex_index]):
            neighbor_index = int(neighbor_index)
            if neighbor_index < 0 or neighbor_index in visited:
                continue
            visited.add(neighbor_index)
            queue.append((neighbor_index, distance + 1))

            if neighbor_index in containing:
                hits.append(
                    {
                        'simplex': int(neighbor_index),
                        'distance': int(distance + 1),
                        'serials': _serials_for_simplex(
                            geometry,
                            atom_lookup,
                            neighbor_index,
                        ),
                        'through_face': _serials_for_face(
                            geometry,
                            atom_lookup,
                            simplex_index,
                            face_index,
                        ),
                        'base_complex': bool(
                            _base_triangle_in_complex(geometry, simplex_index, face_index)
                        ),
                        'beta_complex': bool(
                            _triangle_in_complex_at(
                                geometry,
                                simplex_index,
                                face_index,
                                beta_rank,
                            )
                        ),
                        'face_rho_rank': int(
                            geometry.face_rho_ranks[int(simplex_index), int(face_index)]
                        ),
                        'from_rho_rank': int(geometry.simplex_rho_ranks[int(simplex_index)]),
                        'to_rho_rank': int(geometry.simplex_rho_ranks[int(neighbor_index)]),
                    }
                )
    return hits


def audit_zip(
    zip_file: Path,
    *,
    selection: str,
    radii_model: str,
    max_distance: int,
) -> str:
    pdb_id = zip_file.stem.lower()
    lines = [f'## {pdb_id}', '']

    with tempfile.TemporaryDirectory(prefix='topomt_castp3_void_audit_') as tmpdir:
        tmpdir_path = Path(tmpdir)
        with zipfile.ZipFile(zip_file) as handle:
            handle.extractall(tmpdir_path)

        pdb_file = next(tmpdir_path.glob('*.pdb'))
        atom_lookup = _atom_id_lookup(pdb_file)
        atom_table = _atom_table(pdb_file)
        geometry = build_castp_geometry(
            pdb_file,
            selection=selection,
            solvent_radius=1.4,
            radii_model=radii_model,
        )
        records = build_castp_feature_records(
            geometry,
            probe_radius=1.4,
            probe_limited_depth=False,
        )
        void_records = [
            record
            for record in records
            if record.get('feature_type') == 'void'
        ]
        oracle_sets = oracle_atom_id_sets(tmpdir_path)['void']
        native_sets = _native_void_sets(void_records, atom_lookup)

        exact = _variant_exact_count(native_sets, oracle_sets)
        lines.append(f'Native void parity: `{len(oracle_sets)}/{len(native_sets)}/{exact}`.')
        lines.append('')

        variants = _neighbor_atom_variants(geometry, void_records, atom_lookup)
        lines.extend(
            [
                '| variant | exact |',
                '|---|---:|',
            ]
        )
        for name, variant_sets in variants.items():
            variant_exact = _variant_exact_count(variant_sets, oracle_sets)
            lines.append(f'| {name} | {variant_exact}/{len(oracle_sets)} |')
        lines.append('')

        matches = _best_native_matches(oracle_sets, native_sets)
        lines.extend(
            [
                '| oracle | native | jaccard | oracle atoms | native atoms | missing | extra | native tetrahedra |',
                '|---:|---:|---:|---:|---:|---|---|---:|',
            ]
        )
        for oracle_index, native_index, score in matches:
            oracle_set = oracle_sets[oracle_index]
            native_set = (
                native_sets[native_index]
                if native_index >= 0
                else frozenset()
            )
            missing = sorted(oracle_set - native_set)
            extra = sorted(native_set - oracle_set)
            n_tetra = (
                len(void_records[native_index].get('tetrahedron_indices', []))
                if native_index >= 0
                else 0
            )
            if not missing and not extra:
                continue
            lines.append(
                f'| {oracle_index + 1} | {native_index + 1 if native_index >= 0 else "-"} '
                f'| {score:.4f} | {len(oracle_set)} | {len(native_set)} | '
                f'`{missing}` | `{extra}` | {n_tetra} |'
            )
        lines.append('')

        matched_native = {
            native_index
            for _oracle_index, native_index, score in matches
            if native_index >= 0 and score > 0.80
        }
        unmatched_native = [
            index
            for index in range(len(native_sets))
            if index not in matched_native
            and native_sets[index] not in oracle_sets
        ]
        if unmatched_native:
            lines.extend(
                [
                    'Unmatched native voids:',
                    '',
                    '| native | atoms | tetrahedra |',
                    '|---:|---|---:|',
                ]
            )
            for native_index in unmatched_native:
                lines.append(
                    f'| {native_index + 1} | `{sorted(native_sets[native_index])}` | '
                    f'{len(void_records[native_index].get("tetrahedron_indices", []))} |'
                )
            lines.append('')

        for oracle_index, native_index, score in matches:
            if native_index < 0 or score >= 1.0:
                continue
            oracle_set = oracle_sets[oracle_index]
            native_set = native_sets[native_index]
            missing = sorted(oracle_set - native_set)
            if not missing:
                continue
            component = {
                int(index)
                for index in void_records[native_index].get('tetrahedron_indices', [])
            }
            lines.append(
                f'Missing atom neighborhood for oracle {oracle_index + 1} '
                f'vs native {native_index + 1}:'
            )
            lines.append('')
            for serial in missing:
                lines.append(f'- `{atom_table.get(serial, str(serial))}`')
                hits = _neighbor_hits_for_atom(
                    geometry,
                    atom_lookup,
                    component,
                    serial,
                    max_distance,
                )
                for hit in hits[:8]:
                    lines.append(
                        '  - '
                        f'd={hit["distance"]} tet={hit["simplex"]} '
                        f'atoms={hit["serials"]} '
                        f'face={hit.get("through_face", [])} '
                        f'base={hit.get("base_complex", "")} '
                        f'beta={hit.get("beta_complex", "")} '
                        f'face_rho={hit.get("face_rho_rank", "")} '
                        f'rho={hit.get("from_rho_rank", "")}->{hit.get("to_rho_rank", "")}'
                    )
            lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip-dir', type=Path, default=DEFAULT_ZIP_DIR)
    parser.add_argument('--ids', nargs='+', required=True)
    parser.add_argument('--selection', default=DEFAULT_SELECTION)
    parser.add_argument('--radii-model', default='protor')
    parser.add_argument('--max-distance', type=int, default=2)
    parser.add_argument('--output-md', type=Path, default=None)
    args = parser.parse_args()

    sections = []
    for pdb_id in args.ids:
        zip_file = args.zip_dir / f'{pdb_id.lower()}.zip'
        if not zip_file.exists():
            raise FileNotFoundError(f'Missing oracle ZIP file: {zip_file}')
        sections.append(
            audit_zip(
                zip_file,
                selection=args.selection,
                radii_model=args.radii_model,
                max_distance=args.max_distance,
            )
        )

    output = '# CASTp3 Void Audit\n\n' + '\n'.join(sections)
    if args.output_md is None:
        print(output, end='')
    else:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(output)


if __name__ == '__main__':
    main()
