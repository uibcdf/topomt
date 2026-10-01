"""Compare all closed voids and four analytical measures in pinned archives."""

import argparse
import hashlib
import json
import math
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

import numpy as np

from devtools.castp.compare_castp3_oracles import (
    DEFAULT_SELECTION,
    _atom_id_lookup,
    atom_ids_from_castp_labels,
    compare_atom_id_sets,
)
from topomt import pyunitwizard as puw
from topomt.io.load_CASTp import _parse_poc_file, _parse_poc_info_file
from topomt.third_party.castp3.core.castp_core import build_castp_geometry
from topomt.third_party.castp3.core.castp_core.volbl import voids_measurements

MEASURES = (
    ('area_sa', 'solvent_accessible_area', 'angstrom**2'),
    ('area_ms', 'molecular_surface_area', 'angstrom**2'),
    ('volume_sa', 'solvent_accessible_volume', 'angstrom**3'),
    ('volume_ms', 'molecular_surface_volume', 'angstrom**3'),
)
ROUNDING_ALLOWANCE = 0.00050001


def compare_void_measurements(oracle: list[dict], native: list[dict]) -> dict:
    """Compare memberships and measurements without collapsing duplicates.

    Parameters
    ----------
    oracle, native
        Records containing atom_serials, area_sa/area_ms in square angstroms
        and volume_sa/volume_ms in cubic angstroms. Duplicate memberships
        retain counts but their measure association is marked ambiguous.

    Returns
    -------
    dict
        Separate membership and measure outcomes. Every measure includes its
        expected/native value, absolute error, allowance and explicit unit.

    Raises
    ------
    KeyError
        If a record lacks membership or a required quantity.

    Examples
    --------
    Use ``audit_archive_voids`` for the unit-aware archive/engine conversion.
    """
    groups = []
    for records in (oracle, native):
        grouped = defaultdict(list)
        for record in records:
            grouped[frozenset(record['atom_serials'])].append(record)
        groups.append(grouped)
    expected, observed = groups
    counts = compare_atom_id_sets(
        [frozenset(record['atom_serials']) for record in native],
        [frozenset(record['atom_serials']) for record in oracle],
    )
    measures: list[dict] = []
    ambiguous = []
    for atoms in sorted(expected.keys() & observed.keys(), key=lambda ids: sorted(ids)):
        if len(expected[atoms]) != 1 or len(observed[atoms]) != 1:
            ambiguous.append(sorted(atoms))
            continue
        for field, _attribute, unit in MEASURES:
            reference = float(expected[atoms][0][field])
            actual = float(observed[atoms][0][field])
            finite = math.isfinite(reference) and math.isfinite(actual)
            difference = abs(reference - actual) if finite else None
            measures.append(
                {
                    'server_id': expected[atoms][0].get('server_id'),
                    'quantity': field,
                    'unit': unit,
                    'expected': reference if math.isfinite(reference) else None,
                    'native': actual if math.isfinite(actual) else None,
                    'absolute_error': difference,
                    'allowance': ROUNDING_ALLOWANCE,
                    'finite': finite,
                    'passed': difference is not None
                    and difference <= ROUNDING_ALLOWANCE,
                }
            )
    passed_measures = sum(row['passed'] for row in measures)
    return {
        'oracle_voids': counts[0],
        'native_voids': counts[1],
        'exact_memberships': counts[2],
        'missing_memberships': [
            sorted(atoms) for atoms in expected.keys() - observed.keys()
        ],
        'extra_memberships': [
            sorted(atoms) for atoms in observed.keys() - expected.keys()
        ],
        'ambiguous_memberships': ambiguous,
        'passed_measures': passed_measures,
        'failed_measures': len(measures) - passed_measures,
        'measures': measures,
        'passed': counts[0] == counts[1] == counts[2]
        and not ambiguous
        and passed_measures == 4 * counts[0],
    }


def audit_archive_voids(archive_path: Path, radii_model: str = 'castp3_protor') -> dict:
    """Measure archived closed voids with a fixed 1.4 angstrom probe.

    Parameters
    ----------
    archive_path
        ZIP containing the exact server PDB, poc and pocInfo records.
    radii_model
        Explicit local radius profile to evaluate.

    Returns
    -------
    dict
        Input identity and complete membership/SA/MS comparison. Open pockets
        and unmatched voids are not silently admitted as passing metrics.

    Raises
    ------
    ValueError
        If archive member identity is ambiguous.
    KeyError
        If archive feature records are incomplete.

    Examples
    --------
    ``audit_archive_voids(Path('topomt/data/CASTpFold_server/1crn.zip'))``
    """
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix='topomt_castp_void_audit_') as temporary:
        folder = Path(temporary)
        with ZipFile(archive_path) as archive:
            pdb_members = [name for name in archive.namelist() if name.endswith('.pdb')]
            if len(pdb_members) != 1:
                raise ValueError('Expected exactly one archived PDB.')
            stem = pdb_members[0][:-4]
            pdb_contents = archive.read(pdb_members[0])
            for suffix in ('pdb', 'poc', 'pocInfo'):
                (folder / f'input.{suffix}').write_bytes(
                    archive.read(f'{stem}.{suffix}')
                )
        info = _parse_poc_info_file(folder / 'input.pocInfo')
        atoms = _parse_poc_file(folder / 'input.poc')
        oracle = []
        for feature_id, feature in info.items():
            if feature['n_mouths'] != 0:
                continue
            labels = atoms[feature_id]
            oracle.append(
                {
                    'atom_serials': sorted(atom_ids_from_castp_labels(labels)),
                    'server_id': feature_id,
                    **{
                        field: float(
                            puw.get_value(info[feature_id][attribute], to_unit=unit)
                        )
                        for field, attribute, unit in MEASURES
                    },
                }
            )
        geometry = build_castp_geometry(
            folder / 'input.pdb',
            selection=DEFAULT_SELECTION,
            radii_model=radii_model,
            solvent_radius=1.4,
        )
        serials = _atom_id_lookup(folder / 'input.pdb')
        measured = voids_measurements(geometry, geometry.base_rank)
        native = []
        for void in measured.voids:
            vertices = np.unique(
                np.asarray(geometry.mesh.simplex_atom_indices)[
                    list(void.simplex_indices)
                ]
            )
            native.append(
                {
                    'atom_serials': sorted(
                        serials[int(geometry.atom_indices_map[index])]
                        for index in vertices
                    ),
                    **{
                        field: float(getattr(void, field))
                        for field, _attribute, _unit in MEASURES
                    },
                }
            )
    return {
        'case': archive_path.stem,
        'archive_sha256': hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        'pdb_sha256': hashlib.sha256(pdb_contents).hexdigest(),
        'radii_model': radii_model,
        'selection': DEFAULT_SELECTION,
        'probe_radius': {'value': 1.4, 'unit': 'angstrom'},
        'duration_seconds': time.perf_counter() - started,
        **compare_void_measurements(oracle, native),
    }


def main() -> None:
    """Run an explicit batch and return failure for any parity discrepancy."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids', nargs='+', required=True)
    parser.add_argument(
        '--zip-dir', type=Path, default=Path('topomt/data/CASTpFold_server')
    )
    parser.add_argument('--radii-model', default='castp3_protor')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cases = []
    for case in args.ids:
        report = audit_archive_voids(args.zip_dir / f'{case}.zip', args.radii_model)
        cases.append(report)
        args.output.write_text(
            json.dumps(
                {'schema': 'topomt.castp_void_audit@1', 'cases': cases},
                indent=2,
                allow_nan=False,
            )
            + '\n'
        )
        print(
            case,
            {
                key: report[key]
                for key in (
                    'oracle_voids',
                    'native_voids',
                    'exact_memberships',
                    'passed_measures',
                    'failed_measures',
                    'passed',
                )
            },
            flush=True,
        )
    raise SystemExit(0 if all(report['passed'] for report in cases) else 1)


if __name__ == '__main__':
    main()
