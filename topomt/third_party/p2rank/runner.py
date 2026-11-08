"""Run original P2Rank directly with explicit JVM limits and one worker."""

import os
from pathlib import Path

from topomt.third_party._execution import (
    ProviderExecutionError,
    file_identity,
    java_setup,
    run_command,
)


def ensure_available(options: dict) -> None:
    java_setup('p2rank', options, 'bin/p2rank.jar')


def run(pdb: Path, output: Path, options: dict) -> tuple[dict, dict]:
    home, java, command = java_setup('p2rank', options, 'bin/p2rank.jar')
    # Invoke the same original Java main class as prank. The distributed launcher
    # appends -Xmx2048m, which would override a caller's smaller heap request.
    command += [
        '-cp',
        os.pathsep.join([str(home / 'bin/p2rank.jar'), str(home / 'bin/lib/*')]),
        'cz.siret.prank.program.Main',
        'predict',
        '-f',
        str(pdb),
        '-o',
        str(output),
        '-threads',
        str(options.get('workers', 1)),
        '-visualizations',
        '0',
        '-c',
        options.get('model', 'default'),
    ]
    run_command(
        command,
        output,
        timeout=options.get('timeout', 300),
        workers=options.get('workers', 1),
        extra_env={'INSTALL_DIR': str(home)},
    )
    if (output / 'stdout.txt').read_text().splitlines()[0].strip() != 'P2Rank 2.5.1':
        raise ProviderExecutionError(
            provider='p2rank',
            reason='unsupported original version; expected P2Rank 2.5.1',
        )
    identities = {
        str(path.relative_to(home)): file_identity(path)
        for folder in ('bin', 'config', 'models')
        for path in sorted((home / folder).rglob('*'))
        if path.is_file()
    }
    return {
        'version': '2.5.1',
        'java': file_identity(Path(java)),
        'distribution_files': identities,
        'command': command,
        'model': options.get('model', 'default'),
        'resources': {
            'workers': options.get('workers', 1),
            'java_heap_mib': options.get('memory_mb', 1024),
        },
    }, {}
