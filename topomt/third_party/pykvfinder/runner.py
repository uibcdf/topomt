"""Run original pyKVFinder in an isolated, time-bounded Python worker."""

import json
import sys
from pathlib import Path

from depdigest import dep_digest

from topomt.third_party._execution import (
    ProviderUnavailableError,
    check_grid_budget,
    executable_command,
    run_command,
)


@dep_digest('pyKVFinder', when={'upstream_root': None, 'python_cmd': None})
def _require_engine(*, upstream_root=None, python_cmd=None) -> None:
    if (
        upstream_root is not None
        and not (Path(upstream_root) / 'pyKVFinder/__init__.py').is_file()
    ):
        raise ProviderUnavailableError(
            provider='pykvfinder',
            requirement='upstream_root containing the pyKVFinder package',
        )
    if python_cmd is not None:
        executable_command('pykvfinder_python', python_cmd)


def ensure_available(options: dict) -> None:
    _require_engine(
        upstream_root=options.get('upstream_root'), python_cmd=options.get('python_cmd')
    )


@dep_digest('pyKVFinder', when={'upstream_root': None, 'python_cmd': None})
def _run_worker(
    request: Path,
    output: Path,
    *,
    upstream_root: str | None,
    python_cmd: str | None,
    timeout: float,
    workers: int,
) -> None:
    interpreter = (
        sys.executable
        if python_cmd is None
        else executable_command('pykvfinder_python', python_cmd)
    )
    run_command(
        [interpreter, str(Path(__file__).with_name('worker.py')), str(request)],
        output,
        timeout=timeout,
        workers=workers,
    )


def run(pdb: Path, output: Path, options: dict) -> tuple[dict, dict]:
    """Capture the original dictionary, exported TOML/PDB and engine identity."""
    parameters = {
        key: options.get(key, default)
        for key, default in [
            ('step', 0.6),
            ('probe_in', 1.4),
            ('probe_out', 4.0),
            ('removal_distance', 2.4),
            ('volume_cutoff', 5.0),
            ('include_depth', False),
        ]
    }
    workers = options.get('workers', 1)
    budget = check_grid_budget(
        pdb,
        step=parameters['step'],
        padding=2 * parameters['probe_out'] + 5,
        limit=options.get('max_grid_points', 4_000_000),
    )
    request = output.parent / 'worker_request.json'
    request.write_text(
        json.dumps(
            {
                'input': str(pdb),
                'output': str(output),
                'parameters': parameters,
                'workers': workers,
                'upstream_root': str(options['upstream_root'])
                if 'upstream_root' in options
                else None,
            }
        )
    )
    _run_worker(
        request,
        output,
        upstream_root=options.get('upstream_root'),
        python_cmd=options.get('python_cmd'),
        timeout=options.get('timeout', 300),
        workers=workers,
    )
    receipt = json.loads((output / 'engine_identity.json').read_text())
    units = {
        'step': 'angstroms',
        'probe_in': 'angstroms',
        'probe_out': 'angstroms',
        'removal_distance': 'angstroms',
        'volume_cutoff': 'angstroms**3',
    }
    receipt.update(
        {
            'parameters': {
                key: {'value': value, 'unit': units[key]} if key in units else value
                for key, value in parameters.items()
            },
            'resources': {
                'workers': workers,
                'timeout': {'value': options.get('timeout', 300), 'unit': 'seconds'},
                'grid_points_upper_estimate': budget,
            },
        }
    )
    return receipt, {'vdw.dat': output.parent / 'vdw.dat'}
