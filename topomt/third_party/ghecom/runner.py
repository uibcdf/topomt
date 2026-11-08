"""Execute original GHECOM P-mode with explicit grid/probe parameters."""

from pathlib import Path

from topomt.third_party._execution import (
    check_grid_budget,
    executable_command,
    file_identity,
    run_command,
)


def ensure_available(options: dict) -> None:
    executable_command('ghecom', options.get('ghecom_cmd', 'ghecom'))


def run(pdb: Path, output: Path, options: dict) -> tuple[dict, dict]:
    executable = executable_command('ghecom', options.get('ghecom_cmd', 'ghecom'))
    identity_dir = output / 'identity'
    identity_dir.mkdir()
    run_command(
        [executable], identity_dir, timeout=5, workers=1, allowed_returncodes=(0, 1)
    )
    help_text = (identity_dir / 'stdout.txt').read_text()
    if 'LastModDate:2026/08/17' not in help_text:
        from topomt.third_party._execution import ProviderExecutionError

        raise ProviderExecutionError(
            provider='ghecom',
            reason='unsupported original CLI revision; the admitted protocol is 2026/08/17',
        )
    width, small, large = (
        options.get(key, default)
        for key, default in [
            ('grid_width', 0.8),
            ('probe_small', 1.87),
            ('probe_large', 6.0),
        ]
    )
    estimate = check_grid_budget(
        pdb,
        step=width,
        padding=2 * large + 5,
        limit=options.get('max_grid_points', 4_000_000),
    )
    command = [
        executable,
        'P',
        '-ipdb',
        str(pdb),
        '-opocpdb',
        str(output / 'pockets.pdb'),
        '-gw',
        str(width),
        '-rs',
        str(small),
        '-rl',
        str(large),
        '-cluspock',
        'T',
    ]
    workers = options.get('workers', 1)
    if workers != 1:
        from topomt._private.arg_digestion.external_arguments import _error

        _error(
            'workers',
            workers,
            None,
            'The admitted GHECOM route is serial; use workers=1.',
        )
    returncode = run_command(
        command,
        output,
        timeout=options.get('timeout', 300),
        workers=1,
        allowed_returncodes=(0, 1),
    )
    if '#ERROR' in (output / 'stdout.txt').read_text():
        from topomt.third_party._execution import ProviderExecutionError

        raise ProviderExecutionError(
            provider='ghecom',
            reason='original tool reported an error; inspect original stdout',
        )
    # This reviewed revision ends main() with return(1), even on success.
    # Require complete parsed postconditions, not merely an existing file.
    from topomt.provider_output import ProviderRun

    from .parser import parse_output

    parse_output(ProviderRun.capture('ghecom', 'cli', pdb, output))
    return {
        'version': '2026/08/17',
        'executable': file_identity(Path(executable)),
        'command': command,
        'mode': 'P',
        'returncode': returncode,
        'completion_rule': 'Reviewed 2026/08/17 main returns 1; no original error and complete cluster/model/count postconditions required',
        'parameters': {
            key: {'value': value, 'unit': 'angstroms'}
            for key, value in [
                ('grid_width', width),
                ('probe_small', small),
                ('probe_large', large),
            ]
        },
        'resources': {'workers': 1, 'grid_points_upper_estimate': estimate},
    }, {}
