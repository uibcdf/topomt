"""Capture the selected six-case review without changing frozen case evidence.

Run with one allowed CPU and bounded memory, for example using the command in
the review receipt. Original providers, reference discovery and volume sampling
are outside this capture. Reference bytes are verified and reused explicitly.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _write(path: Path, value: dict) -> None:
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def _capture(protocol_path: Path, output: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    protocol = json.loads(protocol_path.read_text())
    for relative, digest in protocol['frozen_files'].items():
        if _sha256(root / relative) != digest:
            raise ValueError(f'Frozen evidence differs: {relative}')
    if len(os.sched_getaffinity(0)) != 1:
        raise ValueError('This small receiving selection requires one CPU affinity')
    start = time.monotonic()
    output.mkdir(parents=True, exist_ok=False)
    import topomt
    from devtools.benchlab.ball_study import receive as receive_balls
    from devtools.benchlab.capture_volume import encode_quantities, study_module
    from devtools.benchlab.public_contract import describe_public_contract
    from devtools.benchlab.residence_witnesses import inspect_residence_witnesses

    receipt: dict[str, Any] = {
        'schema': 'topomt.benchlab.six-case-source-receiving/1',
        'issue': 'uibcdf/topomt#187',
        'captured_at': datetime.now(timezone.utc).isoformat(),
        'protocol_sha256': _sha256(protocol_path),
        'source_revision': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=root, text=True
        ).strip(),
        'worktree_status_before': subprocess.check_output(
            ['git', 'status', '--short'], cwd=root, text=True
        ).splitlines(),
        'interpreter': sys.executable,
        'python_version': sys.version,
        'origins': {'topomt': topomt.__file__},
        'versions': {
            name: version(name)
            for name in (
                'numpy',
                'scipy',
                'numba',
                'molsysmt',
                'pyunitwizard',
                'ackredit',
            )
        },
        'affinity': sorted(os.sched_getaffinity(0)),
        'thread_environment': {
            name: os.environ.get(name)
            for name in (
                'OMP_NUM_THREADS',
                'OPENBLAS_NUM_THREADS',
                'MKL_NUM_THREADS',
                'NUMBA_NUM_THREADS',
            )
        },
        'address_space_limit_bytes': resource.getrlimit(resource.RLIMIT_AS)[0],
        'runtime_files_sha256': {
            str(path.relative_to(root)): _sha256(path)
            for path in [
                root / 'topomt/_version.py',
                *sorted((root / 'topomt/dfnd').rglob('*.py')),
                *sorted((root / 'devtools/benchlab').glob('*.py')),
            ]
        },
        'references': 'Retained independent certificates reused by verified hash; no fresh reference discovery or checker execution in this capture',
        'cases': [],
        'scope': 'Fresh public receiving and bounded residence-point diagnosis on the frozen 19 profiles; no whole-region/path certification, provider comparison, installed-package or protein claim',
    }
    receipt['dependency_sources'] = {}
    for name in ('molsysmt', 'pyunitwizard', 'ackredit'):
        spec = importlib.util.find_spec(name)
        if spec is None or spec.origin is None:
            raise ValueError(f'This receiving environment lacks {name}')
        source_root = Path(spec.origin).resolve().parents[1]
        receipt['origins'][name] = spec.origin
        receipt['dependency_sources'][name] = {
            'revision': subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], cwd=source_root, text=True
            ).strip(),
            'status': subprocess.check_output(
                ['git', 'status', '--short'], cwd=source_root, text=True
            ).splitlines(),
        }
    for case in protocol['cases']:
        directory = root / case['directory']
        receive = (
            study_module(directory).receive
            if case['reader'] == 'public_study'
            else receive_balls
        )
        case_start = time.monotonic()
        observations = []
        for probe in case['probes_angstroms']:
            topo = receive(directory, probe)
            observations.append(
                {
                    'probe_angstroms': probe,
                    'public_observation': describe_public_contract(topo),
                    'residence_witnesses': inspect_residence_witnesses(topo),
                    'topography_attribution': topomt.get_attribution(topo),
                }
            )
        record = {
            'schema': 'topomt.benchlab.six-case-observations/1',
            'case': case['name'],
            'input_sha256': case['input_sha256'],
            'protocol_sha256': receipt['protocol_sha256'],
            'source_revision': receipt['source_revision'],
            'observations': encode_quantities(observations),
        }
        target = output / f'{case["name"]}.json'
        _write(target, record)
        receipt['cases'].append(
            {
                'case': case['name'],
                'observations_sha256': _sha256(target),
                'profiles': len(observations),
                'wall_seconds': time.monotonic() - case_start,
            }
        )
        print(case['name'], len(observations), 'profiles captured', flush=True)
    for relative, digest in protocol['frozen_files'].items():
        if _sha256(root / relative) != digest:
            raise ValueError(f'Original evidence changed during capture: {relative}')
    receipt['frozen_files_unchanged'] = len(protocol['frozen_files'])
    receipt['loaded_molsysmt_native_modules'] = {}
    for name, module in tuple(sys.modules.items()):
        location = getattr(module, '__file__', None)
        if (
            name.startswith('molsysmt.')
            and isinstance(location, str)
            and location.endswith('.so')
        ):
            receipt['loaded_molsysmt_native_modules'][name] = {
                'path': location,
                'sha256': _sha256(Path(location)),
            }
    receipt['wall_seconds'] = time.monotonic() - start
    receipt['peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    _write(output / 'receipt.json', receipt)
    print('Completed', receipt['wall_seconds'], 's;', receipt['peak_rss_kib'], 'KiB')


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    _capture(args.protocol, args.output)


if __name__ == '__main__':
    _main()
