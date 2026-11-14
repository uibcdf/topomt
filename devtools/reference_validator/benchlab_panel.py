"""Measure the current exact validator on frozen BenchLab inputs, one case at a time.

This driver constructs finite candidate queries, never a general region count.
Each saved Model/proof is independently checked. Worker isolation gives useful
case resource measurements without treating a process-lifetime RSS difference
as the peak memory of a later case.
"""

import argparse
import hashlib
import os
import resource
import subprocess
import sys
import time
from dataclasses import replace
from importlib.metadata import version
from pathlib import Path
from typing import Any, Optional

from .capture_hull_sterics import _name, _write
from .model import (
    HullDomain,
    Model,
    Tetrahedron,
    decode_point,
    encode_point,
    point,
    scalar,
)
from .producer import domain_certificate, partition
from .receiving import freeze_hull_model
from .storage import read_record, read_record_with_digest
from .verify import verify
from .verify.geometry import contains, point_is_free, volume

ROOT = Path(__file__).resolve().parents[2]


def _host() -> dict[str, Any]:
    memory = {
        line.split(':')[0]: int(line.split()[1])
        for line in Path('/proc/meminfo').read_text().splitlines()
        if line.startswith(('MemTotal:', 'MemAvailable:'))
    }
    pressure = {
        line.split()[0]: float(line.split()[1].split('=')[1])
        for line in Path('/proc/pressure/memory').read_text().splitlines()
    }
    swap = {
        line.split()[0]: int(line.split()[1])
        for line in Path('/proc/vmstat').read_text().splitlines()
        if line.startswith(('pswpin ', 'pswpout '))
    }
    safe = (
        memory['MemAvailable']
        >= max(memory['MemTotal'] // 5, 4 * 1024**2) + 2 * 1024**2
        and pressure['some'] < 5
        and pressure['full'] < 1
    )
    return {
        'safe': safe,
        'memory_kib': memory,
        'memory_pressure_avg10': pressure,
        'swap_pages': swap,
        'load_average': list(os.getloadavg()),
    }


def _phase(wall: float, cpu: float) -> dict[str, float]:
    return {
        'wall_seconds': time.perf_counter() - wall,
        'cpu_seconds': time.process_time() - cpu,
    }


def _rays(model: Model) -> list[dict[str, Any]]:
    if not isinstance(model.domain, HullDomain) or not contains(
        model.domain, point((0, 0, 0))
    ):
        raise ValueError(
            'Panel boundary rays require a verified hull containing the origin'
        )
    domain = model.domain
    targets = []
    for axis, label in enumerate('xyz'):
        for sign in [-1, 1]:
            extent = min(
                scalar(plane[3]) / (plane[axis] * sign)
                for plane in domain.planes
                if plane[axis] * sign > 0
            )
            target = point([extent * sign if i == axis else 0 for i in range(3)])
            targets.append(
                (
                    f'axis_{label}_{"positive" if sign > 0 else "negative"}',
                    target,
                    'axis',
                )
            )
    if len(model.atoms) == len(domain.vertices) == 4:
        for index, plane in enumerate(domain.planes):
            face = [
                v
                for v in domain.vertices
                if sum(n * x for n, x in zip(plane[:3], v)) == plane[3]
            ]
            targets.append(
                (
                    f'tetra_face_{index}',
                    point([sum(v[i] for v in face) / len(face) for i in range(3)]),
                    'tetra_face',
                )
            )
    rays = []
    for name, target, family in targets:
        active = [
            i
            for i, plane in enumerate(domain.planes)
            if sum(n * x for n, x in zip(plane[:3], target)) == plane[3]
        ]
        if not contains(domain, target) or not active:
            raise ValueError(
                'Boundary candidate is not an exact point of the declared hull'
            )
        rays.append(
            {
                'name': name,
                'family': family,
                'target': encode_point(target),
                'active_planes': active,
            }
        )
    return rays


def _persist(
    model: Model, cert: dict[str, Any], directory: Path, name: str
) -> dict[str, Any]:
    name = _name(name)
    certificate_file = directory / f'{name}.certificate.json'
    _write(certificate_file, cert)
    saved = read_record(certificate_file)
    try:
        checked = verify(model, saved)
    except ValueError as exc:
        if cert['kind'] != 'path' or not str(exc).startswith('Path collides or leaves'):
            raise
        checked = {
            'verification_status': 'rejected_candidate',
            'model_sha256': model.digest,
            'reason': str(exc),
            'scope': 'The specified candidate is invalid; physical disconnection is not established.',
        }
    _write(directory / f'{name}.verification.json', checked)
    return checked


def _observe(
    model: Model, kind: str, data: dict[str, Any], directory: Path, name: str
) -> dict[str, Any]:
    if kind == 'convex_domain':
        cert = domain_certificate(model)
    else:
        cert = {
            'schema': 'topomt.reference-validator.certificate/1',
            'kind': kind,
            'model_sha256': model.digest,
            'arithmetic': 'rational-exact/1',
            **data,
        }
        if kind == 'point':
            x = decode_point(data['point'])
            cert['claim'] = (
                'outside_domain'
                if not contains(model.domain, x)
                else 'free'
                if point_is_free(model, x)
                else 'blocked'
            )
    return _persist(model, cert, directory, name)


def _profile(
    base: Model,
    row: dict[str, Any],
    probe: float,
    directory: Path,
    rays: list[dict[str, Any]],
) -> dict[str, Any]:
    import pyunitwizard as puw

    start_wall, start_cpu = time.perf_counter(), time.process_time()
    phases = {}
    model = replace(
        base,
        probe=scalar(
            puw.get_value(
                puw.quantity(probe, 'angstroms'), to_unit='nm', value_type=float
            )
        ),
    )
    directory.mkdir(parents=True, exist_ok=False)
    _write(directory / 'model.json', model.to_record())
    phases['probe_and_model_write'] = _phase(start_wall, start_cpu)
    wall, cpu = time.perf_counter(), time.process_time()
    saved = Model.from_record(read_record(directory / 'model.json'))
    if saved != model:
        raise ValueError('Saved panel model differs from the received spheres/hull')
    phases['saved_model_check'] = _phase(wall, cpu)
    wall, cpu = time.perf_counter(), time.process_time()
    queries = directory / 'queries'
    queries.mkdir()
    origin = encode_point(point((0, 0, 0)))
    observed_origin = _observe(saved, 'point', {'point': origin}, queries, 'origin')
    whole = _observe(saved, 'convex_domain', {}, queries, 'whole_hull')
    observed_rays = []
    for ray in rays:
        target = _observe(
            saved, 'point', {'point': ray['target']}, queries, ray['name'] + '_target'
        )
        path = _observe(
            saved,
            'path',
            {'points': [origin, ray['target']]},
            queries,
            ray['name'] + '_path',
        )
        observed_rays.append(
            {
                **ray,
                'target_state': target['point_state'],
                'path_validated': path.get('path_validated', False),
                'path_status': path['verification_status'],
            }
        )
    named = {
        _name(name): _observe(saved, 'point', {'point': x}, queries, name)[
            'point_state'
        ]
        for name, x in row['named_points'].items()
    }
    extra = {}
    for name, points in row['extra_paths'].items():
        result = _observe(saved, 'path', {'points': points}, queries, name)
        extra[name] = {
            'path_validated': result.get('path_validated', False),
            'verification_status': result['verification_status'],
        }
    phases['query_production_and_saved_proof_checks'] = _phase(wall, cpu)
    tetrahedral = None
    if row['tetrahedron_partition'] is not None:
        wall, cpu = time.perf_counter(), time.process_time()
        if len(saved.atoms) != 4:
            raise ValueError(
                'Tetrahedral panel route requires exactly four source atoms'
            )
        tetra = replace(saved, domain=Tetrahedron(tuple(a.center for a in saved.atoms)))
        if volume(tetra.domain) != volume(saved.domain):
            raise ValueError('The four-center tetrahedron and verified hull differ')
        _write(directory / 'tetrahedron_model.json', tetra.to_record())
        original = Model.from_record(read_record(directory / 'tetrahedron_model.json'))
        tetrahedral = _persist(
            original,
            partition(original, **row['tetrahedron_partition']),
            queries,
            'tetrahedron_partition',
        )
        phases['tetrahedron_partition_and_check'] = _phase(wall, cpu)
    return {
        'probe_angstroms': probe,
        'model_sha256': saved.digest,
        'origin_state': observed_origin['point_state'],
        'whole_hull': whole,
        'rays': observed_rays,
        'named_points': named,
        'extra_paths': extra,
        'tetrahedron_partition': tetrahedral,
        'tetrahedron_domain_basis': 'conv(the same four source centers), with identical atoms/radii/probe/source'
        if tetrahedral is not None
        else None,
        'phases': phases,
        'profile_wall_seconds': time.perf_counter() - start_wall,
        'profile_cpu_seconds': time.process_time() - start_cpu,
    }


def _worker(protocol: Path, name: str, output: Path) -> None:
    spec, digest = read_record_with_digest(protocol)
    policy = spec['resources']
    cpu_hard = resource.getrlimit(resource.RLIMIT_CPU)[1]
    cpu_limit = (
        min(policy['per_case_cpu_seconds'], cpu_hard)
        if cpu_hard != resource.RLIM_INFINITY
        else policy['per_case_cpu_seconds']
    )
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
    resource.setrlimit(
        resource.RLIMIT_AS,
        (policy['address_space_limit_bytes'], policy['address_space_limit_bytes']),
    )
    if len(os.sched_getaffinity(0)) != 1:
        raise ValueError('Panel worker requires one CPU affinity')
    for key in (
        'OMP_NUM_THREADS',
        'OPENBLAS_NUM_THREADS',
        'MKL_NUM_THREADS',
        'NUMEXPR_NUM_THREADS',
        'RAYON_NUM_THREADS',
    ):
        os.environ[key] = '1'
    row = next(c for c in spec['cases'] if c['name'] == name)
    wall, cpu = time.perf_counter(), time.process_time()
    certificate, hull_digest = read_record_with_digest(ROOT / row['hull'])
    if hull_digest != row['hull_sha256']:
        raise ValueError('Frozen source hull proof changed')
    base = freeze_hull_model(
        ROOT / row['input'],
        probe_angstroms=row['probes_angstroms'][0],
        certificate=certificate,
    )
    if base.source_sha256 != row['input_sha256'] or len(base.atoms) != row['n_atoms']:
        raise ValueError('Received panel input differs from the frozen source')
    rays = _rays(base)
    setup = _phase(wall, cpu)
    output.mkdir(parents=True, exist_ok=False)
    profiles = []
    for index, probe in enumerate(row['probes_angstroms']):
        profiles.append(_profile(base, row, probe, output / f'profile_{index}', rays))
        print(f'probe {probe:g} A: independently checked', flush=True)
    import pyunitwizard as puw

    usage = resource.getrusage(resource.RUSAGE_SELF)
    _write(
        output / 'result.json',
        {
            'schema': 'topomt.reference-validator.panel-case/1',
            'status': 'completed',
            'name': name,
            'protocol_sha256': digest,
            'input_sha256': base.source_sha256,
            'n_atoms': len(base.atoms),
            'geometric_volume_nm3': [
                str(volume(base.domain).numerator),
                str(volume(base.domain).denominator),
            ],
            'setup': setup,
            'profiles': profiles,
            'peak_rss_kib_linux': usage.ru_maxrss,
            'worker_reported_cpu_seconds': usage.ru_utime + usage.ru_stime,
            'cpu_limit_seconds': cpu_limit,
            'address_space_limit_bytes': resource.getrlimit(resource.RLIMIT_AS)[0],
            'cpu_affinity': sorted(os.sched_getaffinity(0)),
            'dependency_versions': {
                key: version(key) for key in ['pyunitwizard', 'numpy']
            },
            'quantity_codec_source_sha256': hashlib.sha256(
                Path(puw.__file__).read_bytes()
            ).hexdigest(),
        },
    )


def _launch(
    protocol: Path, name: str, output: Path, policy: dict[str, Any]
) -> dict[str, Any]:
    log_dir = output / 'logs'
    log_dir.mkdir(exist_ok=True)
    stdout_path, stderr_path = (
        log_dir / f'{name}.stdout.txt',
        log_dir / f'{name}.stderr.txt',
    )
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter()
    stop = None
    samples = []
    with stdout_path.open('x') as stdout, stderr_path.open('x') as stderr:
        child = subprocess.Popen(
            [
                sys.executable,
                '-m',
                'devtools.reference_validator.benchlab_panel',
                str(protocol.resolve()),
                str((output / 'cases' / name).resolve()),
                '--worker',
                name,
            ],
            cwd=ROOT,
            stdout=stdout,
            stderr=stderr,
        )
        emitted = 0
        while child.poll() is None:
            try:
                child.wait(timeout=policy['monitor_interval_seconds'])
            except subprocess.TimeoutExpired:
                sample = _host()
                samples.append(sample)
                if time.perf_counter() - start >= policy['per_case_wall_seconds']:
                    stop = 'wall_limit'
                elif not sample['safe']:
                    stop = 'host_resource_pressure'
                if stop:
                    child.terminate()
                    try:
                        child.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait(timeout=3)
            lines = stdout_path.read_text().splitlines()
            for line in lines[emitted:]:
                print(f'{name}: {line}', flush=True)
            emitted = len(lines)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    timing = {
        'worker_wall_seconds': time.perf_counter() - start,
        'worker_cpu_seconds': after.ru_utime
        + after.ru_stime
        - before.ru_utime
        - before.ru_stime,
        'host_samples': samples,
    }
    if stop or child.returncode != 0:
        return {
            'status': 'unresolved',
            'reason': stop or 'worker_failed',
            'returncode': child.returncode,
            'stderr_tail': stderr_path.read_text()[-1800:],
            'n_components': None,
            **timing,
        }
    result = read_record(output / 'cases' / name / 'result.json')
    if result['status'] != 'completed' or result['name'] != name:
        raise ValueError('Malformed panel worker result')
    return {**result, **timing}


def capture(
    protocol: Path, output: Path, *, cases: Optional[tuple[str, ...]] = None
) -> None:
    """Execute explicitly selected cases sequentially with bounded worker resources.

    Parameters
    ----------
    protocol, output : Path
        Frozen panel protocol and a new receiving directory.
    cases : tuple of str, optional
        Selected case names. Default selects only the first, cheap tetrahedron.

    Returns
    -------
    None
        Case results, proofs, timings, logs and a checksum receipt are persisted.

    Raises
    ------
    ValueError
        Protocol, case selection, source binding or resource envelope is invalid.
    FileExistsError
        Receiving already exists; earlier artifacts are preserved.
    """
    spec, digest = read_record_with_digest(protocol)
    if spec['schema'] != 'topomt.reference-validator.benchlab-panel/1':
        raise ValueError('Unsupported BenchLab panel protocol')
    policy = spec['resources']
    if (
        policy['cpus'] != 1
        or policy['concurrency'] != 1
        or policy['address_space_limit_bytes'] != 2 * 1024**3
        or not 1 <= policy['per_case_cpu_seconds'] <= 180
        or not 1 <= policy['per_case_wall_seconds'] <= 240
        or not 1 <= policy['monitor_interval_seconds'] <= 5
    ):
        raise ValueError('Panel resource policy exceeds its bounded envelope')
    if (
        len(os.sched_getaffinity(0)) != 1
        or not 0 < resource.getrlimit(resource.RLIMIT_AS)[0] <= 2 * 1024**3
    ):
        raise ValueError(
            'Panel parent requires one CPU affinity and a 2 GiB address ceiling'
        )
    available = [row['name'] for row in spec['cases']]
    chosen = cases if cases is not None else (available[0],)
    if (
        not chosen
        or len(set(chosen)) != len(chosen)
        or any(_name(name) not in available for name in chosen)
    ):
        raise ValueError('Invalid panel case selection')
    for name, expected in spec['reference_files'].items():
        if read_record_with_digest(ROOT / name)[1] != expected:
            raise ValueError('Frozen panel reference changed')
    output.mkdir(parents=True, exist_ok=False)
    results = {}
    start = time.perf_counter()
    for name in chosen:
        host = _host()
        if not host['safe']:
            results[name] = {
                'status': 'deferred_resources',
                'n_components': None,
                'host': host,
            }
            continue
        print(
            f'Starting {name}: one CPU, <=2 GiB, <={policy["per_case_wall_seconds"]} wall seconds',
            flush=True,
        )
        results[name] = _launch(protocol, name, output, policy)
        results[name]['host_before'] = host
        results[name]['host_after'] = _host()
        print(f'Finished {name}: {results[name]["status"]}', flush=True)
    files = {
        str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.rglob('*'))
        if p.is_file()
    }
    tool_root = Path(__file__).parent
    _write(
        output / 'receipt.json',
        {
            'schema': 'topomt.reference-validator.benchlab-panel-receiving/1',
            'owner': spec['owner'],
            'protocol_sha256': digest,
            'source_revision': subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True
            ).strip(),
            'producer_files_sha256': {
                str(p.relative_to(tool_root)): hashlib.sha256(
                    p.read_bytes()
                ).hexdigest()
                for p in sorted(tool_root.rglob('*.py'))
            },
            'selected_cases': list(chosen),
            'cases': results,
            'elapsed_seconds': time.perf_counter() - start,
            'resource_policy': policy,
            'parent_cpu_affinity': sorted(os.sched_getaffinity(0)),
            'parent_peak_rss_kib_linux': resource.getrusage(
                resource.RUSAGE_SELF
            ).ru_maxrss,
            'execution_mode': 'local_sequential',
            'files': files,
            'scope': spec['scope'],
        },
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path)
    parser.add_argument('output', type=Path)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--case', action='append')
    selection.add_argument('--all-cases', action='store_true')
    parser.add_argument('--worker')
    args = parser.parse_args()
    if args.worker:
        _worker(args.protocol, args.worker, args.output)
    else:
        selected = (
            tuple(row['name'] for row in read_record(args.protocol)['cases'])
            if args.all_cases
            else tuple(args.case)
            if args.case
            else None
        )
        capture(args.protocol, args.output, cases=selected)
