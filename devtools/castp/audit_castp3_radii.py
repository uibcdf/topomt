"""Audit radius-profile compatibility with archived CASTpFold orthospheres.

Bulbs do not identify supporting atom IDs. Compatible contacts and single-change
candidates are conditional geometric evidence, not a recovered server table.
All numerical inputs to the geometry operation below are in angstroms.
"""

import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from scipy.spatial import cKDTree

from topomt.third_party.castp3.core.castp_core.geometry import (
    _PROTOR_PROTEIN_BACKBONE_TYPES,
    _PROTOR_PROTEIN_HEAVY_ATOM_TYPES,
    _castp3_protor_radii_for_labels,
    _infer_protor_type_for_atom,
    _protor_radii_for_labels,
)


def audit_bulb_contacts(
    coordinates: np.ndarray,
    atomic_radii: np.ndarray,
    center: np.ndarray,
    bulb_radius: float,
    probe_radius: float = 1.4,
    *,
    rounding_half_width: float = 0.00005,
    candidate_window: float = 0.25,
) -> dict:
    """Check equal-power contacts and conditional one-change candidates.

    Parameters
    ----------
    coordinates, atomic_radii, center, bulb_radius, probe_radius
        Atom positions, base radii, printed bulb and probe, all in angstroms.
    rounding_half_width
        Maximum rounding error of each printed center coordinate and radius.
    candidate_window
        Search window around a base radius for unresolved candidates. This is
        not a compatibility tolerance and cannot turn a mismatch into a pass.

    Returns
    -------
    dict
        Status, contact indices and conditional candidate radius intervals
        carrying their unit. Four contacts must span three dimensions and the
        bulb must have no interior atom under the evaluated profile. A single
        candidate assumes the other radii and three anchors are correct.

    Raises
    ------
    ValueError
        For inconsistent arrays or nonfinite/invalid geometry parameters.

    Examples
    --------
    Use ``audit_archive`` to audit fixed PDB and bulb records together.
    """
    coordinates = np.asarray(coordinates, dtype=float)
    atomic_radii = np.asarray(atomic_radii, dtype=float)
    center = np.asarray(center, dtype=float)
    if coordinates.shape != (len(atomic_radii), 3) or center.shape != (3,):
        raise ValueError('Coordinate and radius shapes do not agree.')
    if (
        not np.all(np.isfinite(coordinates))
        or not np.all(np.isfinite(atomic_radii))
        or not np.all(np.isfinite(center))
        or not np.all(
            np.isfinite(
                [bulb_radius, probe_radius, rounding_half_width, candidate_window]
            )
        )
        or np.any(atomic_radii <= 0)
        or bulb_radius < 0
        or probe_radius < 0
        or rounding_half_width < 0
        or candidate_window <= 0
    ):
        raise ValueError('Finite positive radii and a nonnegative probe are required.')
    distances = np.linalg.norm(coordinates - center, axis=1)
    position_error = np.sqrt(3) * rounding_half_width
    lower_squared = (
        np.maximum(distances - position_error, 0) ** 2
        - (bulb_radius + rounding_half_width) ** 2
    )
    upper_squared = (distances + position_error) ** 2 - max(
        bulb_radius - rounding_half_width, 0
    ) ** 2
    lower = np.sqrt(np.maximum(lower_squared, 0)) - probe_radius
    upper = np.sqrt(np.maximum(upper_squared, 0)) - probe_radius
    contacts = np.flatnonzero((lower <= atomic_radii) & (atomic_radii <= upper))
    interior = np.flatnonzero(upper < atomic_radii)
    status = 'unresolved'
    candidates = []
    if len(contacts) >= 4:
        span = coordinates[contacts] - coordinates[contacts[0]]
        if np.linalg.matrix_rank(span) == 3:
            status = 'compatible' if len(interior) == 0 else 'conflict'
    elif len(contacts) == 3:
        possible = np.flatnonzero(
            (upper > 0)
            & (lower < atomic_radii + candidate_window)
            & (upper > atomic_radii - candidate_window)
        )
        for index in possible:
            if index in contacts or any(other != index for other in interior):
                continue
            vertices: np.ndarray = np.append(contacts, index)
            if (
                np.linalg.matrix_rank(coordinates[vertices] - coordinates[vertices[0]])
                != 3
            ):
                continue
            candidates.append(
                {
                    'index': int(index),
                    'radius_interval': {
                        'lower': float(max(lower[index], 0)),
                        'upper': float(upper[index]),
                        'unit': 'angstrom',
                    },
                }
            )
        if candidates:
            status = 'single_candidate' if len(candidates) == 1 else 'ambiguous'
    return {
        'status': status,
        'contacts': contacts.tolist(),
        'interior': interior.tolist(),
        'candidates': candidates,
    }


def parse_contribution_atom_serials(contents: bytes, pdb_contents: bytes) -> set[int]:
    """Read contribution membership and verify its source atom identity.

    Parameters
    ----------
    contents, pdb_contents
        Exact contribution CSV and original PDB bytes from one archived job.

    Returns
    -------
    set[int]
        Original PDB serials explicitly listed by the contribution output.
        No scalar contribution or later variable-width CSV field is parsed.

    Raises
    ------
    ValueError
        If identities are missing, duplicated or inconsistent with the PDB.

    Examples
    --------
    Use ``audit_archive(..., atom_source='contributions')`` for paired inputs.
    """
    source = {}
    for line in pdb_contents.decode().splitlines():
        if line.startswith(('ATOM', 'HETATM')):
            serial = int(line[6:11])
            if serial in source:
                raise ValueError('Duplicate source atom identity.')
            source[serial] = (
                line[:6].strip(),
                line[12:16].strip(),
                line[17:20].strip(),
            )
    serials: set[int] = set()
    for row in csv.reader(io.StringIO(contents.decode())):
        if not row or row[0] not in {'ATOM', 'HETATM'}:
            continue
        if len(row) < 4:
            raise ValueError('Incomplete contribution atom identity.')
        serial = int(row[1])
        if serial in serials or source.get(serial) != (row[0], row[2], row[3]):
            raise ValueError(
                'Contribution atom identity does not match the source PDB.'
            )
        serials.add(serial)
    if not serials:
        raise ValueError('No contribution atom identity records.')
    return serials


def audit_archive(
    archive_path: Path, probe_radius: float = 1.4, *, atom_source: str = 'pdb'
) -> dict:
    """Return profile observations from one exact archived PDB/bulb pair.

    Parameters
    ----------
    archive_path
        CASTpFold ZIP containing one PDB and one bulb JSON.
    probe_radius
        Probe used by that archived job, in angstroms; supplied explicitly.
    atom_source
        ``'pdb'`` retains raw supported atom rows; ``'contributions'`` uses
        independently verified contribution membership to study input policy.

    Returns
    -------
    dict
        Hashed input identity, omitted-atom accounting, both profile reports and
        label coverage. An unobserved label is not certified by its presence.

    Raises
    ------
    ValueError
        If archive member identity or PDB serial identity is ambiguous.
    KeyError
        For malformed bulb records.

    Examples
    --------
    ``audit_archive(Path('topomt/data/CASTpFold_server/1hew.zip'))``
    """
    if atom_source not in {'pdb', 'contributions'}:
        raise ValueError('Unknown archived atom source.')
    with ZipFile(archive_path) as archive:
        members = {}
        suffixes = ('.pdb', '.bulb.json') + (
            ('.contrib.csv',) if atom_source == 'contributions' else ()
        )
        for suffix in suffixes:
            names = [name for name in archive.namelist() if name.endswith(suffix)]
            if len(names) != 1:
                raise ValueError(f'Expected one {suffix} member, found {len(names)}.')
            members[suffix] = archive.read(names[0])
    included = (
        parse_contribution_atom_serials(members['.contrib.csv'], members['.pdb'])
        if atom_source == 'contributions'
        else None
    )
    rows = []
    skipped: Counter[str] = Counter()
    serials = set()
    for line in members['.pdb'].decode().splitlines():
        if not line.startswith(('ATOM', 'HETATM')):
            continue
        serial = int(line[6:11])
        if serial in serials:
            raise ValueError(f'Duplicate PDB atom serial {serial}.')
        serials.add(serial)
        group, name = line[17:20].strip(), line[12:16].strip()
        element = line[76:78].strip() or name[0]
        if group not in _PROTOR_PROTEIN_HEAVY_ATOM_TYPES:
            skipped['non_supported_residue'] += 1
            continue
        if (
            name not in _PROTOR_PROTEIN_HEAVY_ATOM_TYPES[group]
            and name not in _PROTOR_PROTEIN_BACKBONE_TYPES
        ):
            skipped['non_supported_atom'] += 1
            continue
        if included is not None and serial not in included:
            skipped['absent_from_contributions'] += 1
            continue
        atom_type = _infer_protor_type_for_atom(group, name, element, 0)
        rows.append(
            {
                'serial': serial,
                'label': f'{group}:{name}',
                'type': atom_type,
                'residue': f'{line[21:27].strip()}:{line[16].strip()}',
                'group': group,
                'name': name,
                'element': element,
                'coordinates': [
                    float(line[a:b]) for a, b in ((30, 38), (38, 46), (46, 54))
                ],
            }
        )
    if not rows:
        raise ValueError('No supported protein heavy atoms in the archived PDB.')
    coordinates = np.asarray([row['coordinates'] for row in rows])
    tree = cKDTree(coordinates)
    groups = np.asarray([row['group'] for row in rows])
    names = np.asarray([row['name'] for row in rows])
    elements = np.asarray([row['element'] for row in rows])
    bonds: np.ndarray = np.zeros(len(rows), dtype=int)
    bulbs = json.loads(members['.bulb.json'])
    profiles = {}
    for profile, operation in (
        ('protor', _protor_radii_for_labels),
        ('castp3_protor', _castp3_protor_radii_for_labels),
    ):
        radii = operation(groups, names, elements, bonds)
        maximum_expanded_radius = float(np.max(radii)) + probe_radius + 0.25
        statuses: Counter[str] = Counter()
        observed = defaultdict(set)
        candidates = []
        unresolved = []
        for feature_id, feature_bulbs in enumerate(bulbs, start=1):
            for bulb_id, bulb in enumerate(feature_bulbs):
                center = np.asarray([bulb['c'][axis] for axis in 'xyz'])
                radius = float(bulb['r'])
                cutoff = (
                    np.sqrt(maximum_expanded_radius**2 + (radius + 0.00005) ** 2)
                    + 0.0001
                )
                neighbors = np.asarray(tree.query_ball_point(center, cutoff), dtype=int)
                result = audit_bulb_contacts(
                    coordinates[neighbors],
                    radii[neighbors],
                    center,
                    radius,
                    probe_radius,
                )
                statuses[result['status']] += 1
                if result['status'] != 'compatible':
                    unresolved.append(
                        {
                            'feature_id': feature_id,
                            'bulb_id': bulb_id,
                            'status': result['status'],
                            'contact_serials': [
                                rows[neighbors[index]]['serial']
                                for index in result['contacts']
                            ],
                            'interior_serials': [
                                rows[neighbors[index]]['serial']
                                for index in result['interior']
                            ],
                            'candidate_serials': [
                                rows[neighbors[item['index']]]['serial']
                                for item in result['candidates']
                            ],
                        }
                    )
                if result['status'] == 'compatible':
                    for local in result['contacts']:
                        row = rows[neighbors[local]]
                        observed[row['label']].add(row['serial'])
                if result['status'] == 'single_candidate':
                    candidate = result['candidates'][0]
                    row = rows[neighbors[candidate['index']]]
                    candidates.append(
                        {
                            'feature_id': feature_id,
                            'bulb_id': bulb_id,
                            'serial': row['serial'],
                            'label': row['label'],
                            'residue': row['residue'],
                            'radius_interval': candidate['radius_interval'],
                            'baseline_radius': {
                                'value': float(radii[neighbors[candidate['index']]]),
                                'unit': 'angstrom',
                            },
                        }
                    )
        profiles[profile] = {
            'bulb_statuses': dict(statuses),
            'observed_atoms': {
                key: sorted(value) for key, value in sorted(observed.items())
            },
            'single_change_candidates': candidates,
            'unresolved_bulbs': unresolved,
        }
    return {
        'case': archive_path.stem,
        'archive_sha256': hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        'pdb_sha256': hashlib.sha256(members['.pdb']).hexdigest(),
        'bulbs_sha256': hashlib.sha256(members['.bulb.json']).hexdigest(),
        'probe_radius': {'value': probe_radius, 'unit': 'angstrom'},
        'supported_atoms': len(rows),
        'skipped_atoms': dict(skipped),
        'label_presence': dict(sorted(Counter(row['label'] for row in rows).items())),
        'profiles': profiles,
    } | (
        {
            'atom_source': atom_source,
            'contributions_sha256': hashlib.sha256(members['.contrib.csv']).hexdigest(),
        }
        if included is not None
        else {}
    )


def summarize_audits(cases: list[dict]) -> dict:
    """Summarize hashed archives without conflating presence with observation.

    Parameters
    ----------
    cases
        Reports returned by ``audit_archive`` for distinct archived inputs.

    Returns
    -------
    dict
        Per-label counts, profile status counts, conditional candidates and
        input hashes. Observations count unique atom serials per archive.

    Raises
    ------
    ValueError
        If case names are duplicated or profiles account for different bulbs.

    Examples
    --------
    ``summarize_audits([audit_archive(Path('example.zip'))])``
    """
    if len({case['case'] for case in cases}) != len(cases):
        raise ValueError('Duplicate archived case identity.')
    presence: Counter[str] = Counter()
    observed: dict[str, Counter[str]] = defaultdict(Counter)
    statuses: dict[str, Counter[str]] = defaultdict(Counter)
    candidates: list[dict] = []
    identities = []
    bulb_count = 0
    for case in cases:
        presence.update(case['label_presence'])
        totals = {
            sum(profile['bulb_statuses'].values())
            for profile in case['profiles'].values()
        }
        if len(totals) != 1:
            raise ValueError('Profiles account for different bulb counts.')
        bulb_count += totals.pop()
        for name, profile in case['profiles'].items():
            statuses[name].update(profile['bulb_statuses'])
            observed[name].update(
                {
                    label: len(serials)
                    for label, serials in profile['observed_atoms'].items()
                }
            )
            # Canonical ASP/GLU candidates remain in the full report. Preserve
            # new candidates against the existing opt-in profile here.
            if name == 'castp3_protor':
                candidates.extend(
                    {'case': case['case'], **candidate}
                    for candidate in profile['single_change_candidates']
                )
        identities.append(
            {
                key: case[key]
                for key in (
                    'case',
                    'archive_sha256',
                    'pdb_sha256',
                    'bulbs_sha256',
                    'probe_radius',
                    'supported_atoms',
                    'skipped_atoms',
                )
            }
            | {
                'profiles': {
                    name: profile['bulb_statuses']
                    for name, profile in case['profiles'].items()
                }
            }
            | {
                key: case[key]
                for key in ('atom_source', 'contributions_sha256')
                if key in case
            }
        )
    return {
        'schema': 'topomt.castp_radius_summary@1',
        'archive_count': len(cases),
        'bulb_count': bulb_count,
        'profile_statuses': {name: dict(counts) for name, counts in statuses.items()},
        'label_coverage': {
            label: {'present_atoms': count}
            | {f'observed_{name}': counts[label] for name, counts in observed.items()}
            for label, count in sorted(presence.items())
        },
        'castp3_protor_candidates': candidates,
        'cases': identities,
    }


def main() -> None:
    """Write an offline corpus report; no radius/profile changes are made."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--zip-dir', type=Path, default=Path('topomt/data/CASTpFold_server')
    )
    parser.add_argument('--ids', nargs='+')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--summary-output', type=Path)
    parser.add_argument('--probe-radius', type=float, default=1.4)
    parser.add_argument(
        '--atom-source', choices=('pdb', 'contributions'), default='pdb'
    )
    args = parser.parse_args()
    paths = (
        [args.zip_dir / f'{case}.zip' for case in args.ids]
        if args.ids
        else sorted(args.zip_dir.glob('*.zip'))
    )
    cases = []
    for path in paths:
        result = audit_archive(path, args.probe_radius, atom_source=args.atom_source)
        cases.append(result)
        print(
            path.stem,
            {key: value['bulb_statuses'] for key, value in result['profiles'].items()},
            flush=True,
        )
    args.output.write_text(
        json.dumps({'schema': 'topomt.castp_radius_audit@1', 'cases': cases}, indent=2)
        + '\n'
    )
    if args.summary_output is not None:
        args.summary_output.write_text(
            json.dumps(summarize_audits(cases), indent=2) + '\n'
        )


if __name__ == '__main__':
    main()
