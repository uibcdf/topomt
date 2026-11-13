"""Retain hull/clip controls and sequential resource-bounded original sources."""

import argparse
import hashlib
import inspect
import json
import os
import resource
import subprocess
import sys
import time
from importlib.metadata import version
from pathlib import Path
from typing import Any

from .center_hull import clip_certificate, hull_certificate
from .hull_model import CenterSource, HullLimits
from .model import Box, decode_point, decode_scalar, record_digest
from .receiving import freeze_centers
from .storage import read_record, read_record_with_digest
from .verify.center_hull import verify_hull


def _write(path: Path, value: object) -> None:
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def _allocation() -> dict[str, str | None] | None:
    """Retain only reported scheduler resource identifiers, never the environment."""
    if 'SLURM_JOB_ID' not in os.environ:
        return None
    return {
        name: os.environ.get(key)
        for name, key in [
            ('job_id', 'SLURM_JOB_ID'),
            ('partition', 'SLURM_JOB_PARTITION'),
            ('cpus_per_task', 'SLURM_CPUS_PER_TASK'),
            ('memory_per_node_mb', 'SLURM_MEM_PER_NODE'),
        ]
    }


def _save(
    directory: Path,
    source: CenterSource,
    certificate: dict[str, Any],
    limits: HullLimits,
) -> dict[str, Any]:
    directory.mkdir(parents=True, exist_ok=False)
    _write(directory / 'source.json', source.to_record())
    _write(directory / 'certificate.json', certificate)
    saved = CenterSource.from_record(read_record(directory / 'source.json'))
    checked = verify_hull(
        saved, read_record(directory / 'certificate.json'), limits=limits
    )
    _write(directory / 'verification.json', checked)
    return checked


def _resources(value: dict[str, Any]) -> dict[str, int]:
    expected = {'cpu_seconds', 'wall_seconds', 'address_space_limit_bytes', 'cpus'}
    if set(value) != expected or any(type(v) is not int for v in value.values()):
        raise ValueError('Malformed hull pilot resource policy')
    if (
        not 1 <= value['cpu_seconds'] <= 30
        or not 1 <= value['wall_seconds'] <= 40
        or not 128 * 1024**2 <= value['address_space_limit_bytes'] <= 2 * 1024**3
        or value['cpus'] != 1
    ):
        raise ValueError('Hull pilot resource policy exceeds its conservative envelope')
    return value


def _worker(protocol: Path, name: str, output: Path) -> None:
    spec = read_record(protocol)
    policy = _resources(spec['per_case_resources'])
    if len(os.sched_getaffinity(0)) != 1:
        raise ValueError('Hull worker requires one CPU affinity')
    resource.setrlimit(
        resource.RLIMIT_AS,
        (policy['address_space_limit_bytes'], policy['address_space_limit_bytes']),
    )
    resource.setrlimit(
        resource.RLIMIT_CPU, (policy['cpu_seconds'], policy['cpu_seconds'])
    )
    root = Path(__file__).resolve().parents[2]
    row = next(c for c in spec['original_inputs'] if c['name'] == name)
    start = time.monotonic()
    source = freeze_centers(root / row['input'])
    if (
        source.source_sha256 != row['input_sha256']
        or len(source.centers) != row['n_atoms']
    ):
        raise ValueError('Original center input differs from the frozen protocol')
    limits = HullLimits(**spec['limits'])
    certificate = hull_certificate(source, limits=limits)
    checked = _save(output, source, certificate, limits)
    import pyunitwizard as puw
    from pyunitwizard import QuantityRecord

    quantity_root = Path(puw.__file__).resolve().parents[1]
    quantity_revision = None
    if (quantity_root / '.git').exists():
        revision = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=quantity_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if revision.returncode == 0:
            quantity_revision = revision.stdout.strip()
    result = {
        'schema': 'topomt.reference-validator.hull-case-receiving/1',
        'status': 'accepted',
        'source_sha256': source.digest,
        'input_sha256': source.source_sha256,
        'certificate_sha256': checked['certificate_sha256'],
        'verification_sha256': record_digest(checked),
        'n_centers': len(source.centers),
        'n_vertices': len(checked['vertices']),
        'n_facets': len(checked['facets']),
        'geometric_volume': checked['geometric_volume'],
        'volume_unit': 'nm**3',
        'elapsed_seconds': time.monotonic() - start,
        'peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'cpu_affinity': sorted(os.sched_getaffinity(0)),
        'address_space_limit_bytes': resource.getrlimit(resource.RLIMIT_AS)[0],
        'cpu_limit_seconds': resource.getrlimit(resource.RLIMIT_CPU)[0],
        'slurm_allocation': _allocation(),
        'quantity_receiving': {
            'dependency_versions': {
                name: version(name) for name in ['pyunitwizard', 'numpy']
            },
            'quantity_codec_source_revision': quantity_revision,
            'quantity_record_definition_sha256': hashlib.sha256(
                Path(inspect.getfile(QuantityRecord)).read_bytes()
            ).hexdigest(),
        },
    }
    _write(output / 'result.json', result)


def _run_worker(
    protocol: Path, name: str, output: Path, wall_seconds: int
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            '-m',
            'devtools.reference_validator.capture_hulls',
            str(protocol.resolve()),
            str(output.resolve()),
            '--worker',
            name,
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        timeout=wall_seconds,
    )


def capture(
    protocol: Path, output: Path, *, original_cases: tuple[str, ...] = ()
) -> None:
    """Save geometric controls and explicitly selected original inputs sequentially.

    Original-source workers have individual CPU/address-space/wall ceilings.
    A stopped/failed worker remains unresolved, never a geometric empty result.
    Use one CPU affinity and an external parent memory/deadline envelope.
    """
    spec, protocol_digest = read_record_with_digest(protocol)
    if spec['schema'] != 'topomt.reference-validator.center-hull-pilot/1':
        raise ValueError('Unsupported hull pilot protocol')
    if len(os.sched_getaffinity(0)) != 1:
        raise ValueError('Hull pilot requires one CPU affinity')
    policy = _resources(spec['per_case_resources'])
    limits = HullLimits(**spec['limits'])
    names = [row['name'] for row in spec['original_inputs']]
    if len(set(original_cases)) != len(original_cases) or any(
        name not in names for name in original_cases
    ):
        raise ValueError('Original source selection is invalid')
    output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    fixtures = {}
    clips = {}
    originals = {}
    sources = {}
    certificates = {}
    for row in spec['fixtures']:
        name = row['name']
        if (
            not isinstance(name, str)
            or not name.replace('_', '').isalnum()
            or name in fixtures
        ):
            raise ValueError('Invalid or duplicate hull fixture name')
        source = CenterSource.from_record(row['source'])
        certificate = hull_certificate(source, limits=limits)
        checked = _save(output / 'fixtures' / name, source, certificate, limits)
        if (
            checked['geometric_volume'] != row['expected_volume']
            or len(checked['vertices']) != row['expected_vertices']
            or len(checked['facets']) != row['expected_facets']
        ):
            raise ValueError('Hull fixture did not establish its independent control')
        fixtures[name] = {
            'source_sha256': source.digest,
            'certificate_sha256': checked['certificate_sha256'],
            'verification_sha256': record_digest(checked),
            'geometric_volume': checked['geometric_volume'],
        }
        sources[name], certificates[name] = source, certificate
    for row in spec['cube_clips']:
        name = row['name']
        if (
            not isinstance(name, str)
            or not name.replace('_', '').isalnum()
            or name in clips
        ):
            raise ValueError('Invalid or duplicate hull clip name')
        box = Box(decode_point(row['lower']), decode_point(row['upper']))
        certificate = clip_certificate(
            sources['cube'], certificates['cube'], box, limits=limits
        )
        checked = _save(output / 'clips' / name, sources['cube'], certificate, limits)
        if checked['geometric_dimension'] != row['dimension'] or decode_scalar(
            checked['geometric_volume']
        ) != decode_scalar(row['volume']):
            raise ValueError('Hull clip did not establish its independent control')
        clips[name] = {
            'source_sha256': sources['cube'].digest,
            'certificate_sha256': checked['certificate_sha256'],
            'verification_sha256': record_digest(checked),
            'geometric_volume': checked['geometric_volume'],
            'geometric_dimension': checked['geometric_dimension'],
        }
    root = Path(__file__).resolve().parents[2]
    for name in original_cases:
        row = next(c for c in spec['original_inputs'] if c['name'] == name)
        _, digest = read_record_with_digest(root / row['input'])
        if digest != row['input_sha256']:
            raise ValueError('Original input file changed after the protocol freeze')
        directory = output / 'originals' / name
        try:
            completed = _run_worker(protocol, name, directory, policy['wall_seconds'])
            if completed.returncode == 0:
                received = read_record(directory / 'result.json')
                if (
                    received['schema']
                    != 'topomt.reference-validator.hull-case-receiving/1'
                    or received['status'] != 'accepted'
                    or received['input_sha256'] != row['input_sha256']
                ):
                    raise ValueError('Malformed or unbound hull worker receipt')
                originals[name] = received
            else:
                originals[name] = {
                    'status': 'unresolved',
                    'reason': 'worker_failed',
                    'returncode': completed.returncode,
                    'stderr_tail': completed.stderr[-1500:],
                }
        except subprocess.TimeoutExpired:
            originals[name] = {'status': 'unresolved', 'reason': 'wall_limit'}
        print(f'Hull source {name}: {originals[name]["status"]}', flush=True)
    files = {
        str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.rglob('*.json'))
    }
    receipt = {
        'schema': 'topomt.reference-validator.hull-receiving/1',
        'protocol_sha256': protocol_digest,
        'source_revision': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=root, text=True
        ).strip(),
        'producer_files_sha256': {
            name: hashlib.sha256(
                (Path(__file__).parent / name).read_bytes()
            ).hexdigest()
            for name in [
                'center_hull.py',
                'hull_model.py',
                'capture_hulls.py',
                'receiving.py',
                'verify/polytope.py',
                'verify/center_hull.py',
            ]
        },
        'fixtures': fixtures,
        'clips': clips,
        'originals': originals,
        'original_selection': list(original_cases),
        'per_case_resources': policy,
        'concurrency': 1,
        'slurm_allocation': _allocation(),
        'files': files,
        'elapsed_seconds': time.monotonic() - start,
        'parent_peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'child_peak_rss_kib_linux': resource.getrusage(
            resource.RUSAGE_CHILDREN
        ).ru_maxrss,
        'cpu_affinity': sorted(os.sched_getaffinity(0)),
        'address_space_limit_bytes': resource.getrlimit(resource.RLIMIT_AS)[0],
        'free_volume_status': 'not_computed',
        'free_topology_status': 'not_computed',
    }
    _write(output / 'receipt.json', receipt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--worker')
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--original-case', action='append', default=[])
    selection.add_argument('--all-originals', action='store_true')
    args = parser.parse_args()
    if args.worker:
        _worker(args.protocol, args.worker, args.output)
    else:
        selected = (
            tuple(row['name'] for row in read_record(args.protocol)['original_inputs'])
            if args.all_originals
            else tuple(args.original_case)
        )
        capture(args.protocol, args.output, original_cases=selected)
