"""Execute the frozen tetrahedron study through public original-provider APIs.

This is case-specific experiment orchestration, not a new engine or benchmark
framework. Run only after reviewing resources and the committed protocol.
Outputs must use a new directory; reviewed evidence is never overwritten.
"""

import argparse
import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import molsysmt as msm
import numpy as np
from pyunitwizard import QuantityRecord

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun
from topomt.third_party._execution import ProviderUnavailableError

CASE = (
    Path(__file__).resolve().parents[2]
    / 'docs/content/benchlab/synthetic/regular_tetrahedron'
)
LOCATION_KEYS = {
    'pykvfinder': {'upstream_root', 'python_cmd'},
    'ghecom': {'ghecom_cmd'},
    'caver': {'caver_home', 'java_cmd'},
    'mole': {'mole_cmd'},
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record(value: Any, unit: str, field: str) -> dict:
    return QuantityRecord.from_quantity(
        puw.quantity(value, unit), field=field
    ).to_dict()


def _options(row: dict, locations: dict, protocol: dict) -> dict[str, Any]:
    method = row['method']
    paths = locations.get(method, {})
    if not isinstance(paths, dict) or set(paths) - LOCATION_KEYS[method]:
        raise ValueError(
            'Tool configuration admits location options only; scientific settings belong in the frozen protocol'
        )
    options = dict(paths)
    for name, value in row['options'].items():
        if isinstance(value, dict):
            unit = 'angstroms**3' if name == 'volume_cutoff' else 'angstroms'
            value = QuantityRecord.from_dict(value).to_quantity(field=name, unit=unit)
        options[name] = value
    options.update(workers=protocol['workers'], timeout=protocol['timeout_seconds'])
    if method in {'caver', 'mole'}:
        options['memory_mb'] = protocol['managed_heap_mib']
    if method in {'pykvfinder', 'ghecom'}:
        options['max_grid_points'] = protocol['max_grid_points']
    return options


def _submitted(run: ProviderRun, directory: Path) -> dict:
    path = directory / 'submitted.pdb'
    path.write_bytes(run.get_artifact('input/input.pdb'))
    xyz = np.asarray(
        puw.get_value(msm.get(str(path), coordinates=True), to_unit='angstroms')
    ).reshape(-1, 3)
    lines = [
        line
        for line in path.read_text().splitlines()
        if line.startswith(('ATOM  ', 'HETATM'))
    ]
    return {
        'file': str(path.name),
        'sha256': _sha(path),
        'atom_count': len(lines),
        'coordinates': _record(xyz, 'angstroms', 'coordinates'),
        'record_types': sorted({line[:6].strip() for line in lines}),
        'atom_name_columns': [line[12:16] for line in lines],
        'residue_name_columns': [line[17:20] for line in lines],
    }


def _execute(row: dict, locations: dict, protocol: dict, output: Path) -> dict:
    directory = output / row['id']
    directory.mkdir()
    entry = {
        key: row[key]
        for key in (
            'id',
            'method',
            'scenario',
            'options',
            'probe_label',
            'interpretation',
        )
    }
    entry.update(
        evidence_mode='current_original_execution',
        record_counts=None,
        original_bundle=None,
    )
    run = None
    started = time.monotonic()
    try:
        result = tmt.get_provider_output(
            str(CASE / protocol['source_file']),
            method=row['method'],
            **_options(row, locations, protocol),
        )
        run = result.run
        counts: dict[str, int] = {}
        for record in result.records:
            counts[record.record_kind] = counts.get(record.record_kind, 0) + 1
        entry.update(
            status='completed',
            record_counts=counts,
            record_count=len(result.records),
            record_ids=[record.source_id for record in result.records],
            completed_empty=not result.records,
        )
    except ImportError as error:
        entry.update(
            status='unavailable'
            if isinstance(error, ProviderUnavailableError)
            else 'dependency_failure',
            error_type=type(error).__name__,
            reason=str(error),
        )
    except Exception as error:
        run = getattr(error, 'run', None)
        entry.update(
            status='execution_failed',
            error_type=type(error).__name__,
            reason=str(error),
        )
    entry['elapsed_time'] = _record(
        time.monotonic() - started, 'seconds', 'elapsed_time'
    )
    if isinstance(run, ProviderRun):
        bundle = directory / (
            'original.zip' if entry['status'] == 'completed' else 'failed.zip'
        )
        run.save(bundle)
        entry['original_bundle'] = {
            'file': str(bundle.relative_to(output)),
            'sha256': _sha(bundle),
            'run_id': run.run_id,
        }
        entry['original_backend'] = run.backend
        entry['original_version'] = run.metadata.get('version')
        entry['actual_input'] = _submitted(run, directory)
    (directory / 'observation.json').write_text(
        json.dumps(entry, indent=2, allow_nan=False) + '\n'
    )
    return entry


def main() -> int:
    """Run this one reviewed protocol into a new observation directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--tools',
        type=Path,
        required=True,
        help='JSON containing only local engine location options',
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='New output directory; existing directories are refused',
    )
    parser.add_argument(
        '--positive-cutoff-diagnostic',
        action='store_true',
        help='Use the separately declared post-observation one-voxel cutoff protocol',
    )
    args = parser.parse_args()
    filename = (
        'positive_cutoff_protocol.json'
        if args.positive_cutoff_diagnostic
        else 'protocol.json'
    )
    protocol_file = CASE / 'artifacts/comparisons_v1' / filename
    protocol = json.loads(protocol_file.read_text())
    for relative, expected in protocol['preserved_files'].items():
        if _sha(CASE / relative) != expected:
            raise ValueError(f'Frozen input or previous evidence changed: {relative}')
    if protocol['execute_services'] or protocol['workers'] != 1:
        raise ValueError('This protocol admits serial local execution only')
    locations = json.loads(args.tools.read_text())
    if set(locations) - LOCATION_KEYS.keys():
        raise ValueError('Only the four selected local methods are admitted')
    args.output.mkdir(parents=True, exist_ok=False)
    report = {
        'schema': 'topomt.benchlab.original-observations/1',
        'case_id': protocol['case_id'],
        'study_version': protocol['study_version'],
        'protocol_sha256': _sha(protocol_file),
        'model_audit_sha256': protocol['model_audit_sha256'],
        'created_utc': datetime.now(UTC).isoformat(),
        'topomt_version': str(tmt.__version__),
        'source_file': protocol['source_file'],
        'source_sha256': protocol['source_sha256'],
        'entries': [],
        'performance_interpretation': 'Client wall times are receipts, not a cross-method performance benchmark',
    }
    failures: dict[str, str] = {}
    for row in protocol['runs']:
        if Path(row['id']).name != row['id'] or row['id'].startswith('.'):
            raise ValueError('Invalid observation identifier')
        if row['method'] in failures:
            entry = {
                key: row[key]
                for key in (
                    'id',
                    'method',
                    'scenario',
                    'options',
                    'probe_label',
                    'interpretation',
                )
            }
            entry.update(
                status='not_executed_after_failure',
                cause_id=failures[row['method']],
                evidence_mode='not_executed',
                record_counts=None,
                original_bundle=None,
            )
        else:
            entry = _execute(row, locations, protocol, args.output)
            if row['scenario'] == 'standard' and entry['status'] != 'completed':
                failures[row['method']] = row['id']
        report['entries'].append(entry)
        (args.output / 'observations.json').write_text(
            json.dumps(report, indent=2, allow_nan=False) + '\n'
        )
        print(
            json.dumps(
                {
                    key: entry.get(key)
                    for key in ('id', 'status', 'record_counts', 'reason', 'cause_id')
                }
            ),
            flush=True,
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
