"""Execute the original isolated MoloVol CLI without changing its algorithm."""

import math
import os
import re
import select
import subprocess
import sys
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

from topomt._private.arg_digestion.external_arguments import _error
from topomt.third_party._execution import (
    ProviderExecutionError,
    ProviderUnavailableError,
    check_grid_budget,
    executable_command,
    file_identity,
    run_command,
)

from .parser import decode_report, validate_query

ELEMENTS_SHA256 = '92a7e3b352cdece923c054fc07026c5ec74135b8bd8ce071af62741529f0fa8f'


def _configuration(options: dict) -> tuple[str, Path, str | None]:
    executable = executable_command('molovol', options.get('molovol_cmd', 'molovol'))
    resource = Path(
        options.get('elements_file', Path(executable).parent / 'inputfile/elements.txt')
    )
    if not resource.is_file():
        raise ProviderUnavailableError(
            provider='molovol', requirement=f'elements_file: {resource}'
        )
    virtual = options.get('virtual_display')
    if virtual is None:
        virtual = sys.platform.startswith('linux') and not os.environ.get('DISPLAY')
    display = (
        executable_command('xvfb', options.get('xvfb_cmd', 'Xvfb')) if virtual else None
    )
    if display is not None and os.name != 'posix':
        raise ProviderUnavailableError(
            provider='molovol', requirement='POSIX virtual-display support'
        )
    return executable, resource.resolve(), display


def ensure_available(options: dict) -> None:
    _configuration(options)


def prepare_elements(
    pdb: Path, output: Path, resource: Path, overrides: dict
) -> tuple[dict, dict]:
    """Capture original and effective resources; admit every submitted element."""
    counts: Counter[str] = Counter()
    for line in pdb.read_text().splitlines():
        if not line.startswith(('ATOM  ', 'HETATM')):
            continue
        symbol = line[76:78].strip()
        if not re.fullmatch(r'[A-Z][a-z]?', symbol) or line[78:80].strip():
            _error(
                'molecular_system',
                symbol,
                None,
                'MoloVol currently requires explicit neutral PDB element fields; charged records are not admitted.',
            )
        counts[symbol] += 1
    if not counts:
        _error('molecular_system', str(pdb), None, 'MoloVol requires submitted atoms.')
    original = resource.read_bytes()
    table = {}
    lines = original.decode('utf-8').splitlines()
    for index, line in enumerate(lines):
        cells = line.split()
        if not cells or not cells[0].isdecimal():
            continue
        if len(cells) != 4 or cells[1] in table:
            _error(
                'elements_file',
                str(resource),
                None,
                'Malformed or duplicate original element entry.',
            )
        try:
            radius, weight = map(float, cells[2:])
        except ValueError:
            _error(
                'elements_file',
                str(resource),
                None,
                'Non-numeric radius or atomic weight.',
            )
        if not all(math.isfinite(item) and item >= 0 for item in (radius, weight)):
            _error(
                'elements_file',
                str(resource),
                None,
                'Non-finite or negative element property.',
            )
        table[cells[1]] = (index, cells, radius)
    if not set(overrides) <= counts.keys():
        _error(
            'element_radii',
            overrides,
            None,
            'Override only elements present in the selected input.',
        )
    effective = {}
    for symbol in counts:
        if symbol not in table:
            _error(
                'elements_file',
                symbol,
                None,
                'A submitted element is absent from the resource.',
            )
        index, cells, radius = table[symbol]
        radius = overrides.get(symbol, radius)
        if not math.isfinite(radius) or radius <= 0:
            _error(
                'element_radii',
                symbol,
                None,
                'Every submitted element needs a positive radius.',
            )
        effective[symbol] = radius
        if symbol in overrides:
            cells[2] = format(radius, '.17g')
            lines[index] = '\t'.join(cells)
    # Keep both byte-exact resource input and explicit override input. Never edit
    # the user's original table or silently replace its scientific data.
    source_copy, effective_copy = (
        output / 'elements_source.txt',
        output / 'elements.txt',
    )
    source_copy.write_bytes(original)
    effective_copy.write_bytes(
        ('\n'.join(lines) + '\n').encode() if overrides else original
    )
    identity = file_identity(resource)
    references = []
    if identity['sha256'] == ELEMENTS_SHA256:
        if counts.keys() - overrides.keys():
            references.append('alvarez_radii')
        # The upstream table explicitly marks artificial-element weights as
        # unreferenced; do not attribute those values to the IUPAC paper.
        if any(
            int(table[symbol][1][0]) <= 83 and int(table[symbol][1][0]) not in {43, 61}
            for symbol in counts
        ):
            references.append('atomic_weights_2013')
    return {
        'element_counts': dict(sorted(counts.items())),
        'effective_radii': effective,
        'radius_overrides': overrides,
        'elements_source': identity,
        'elements_effective': file_identity(effective_copy),
        'input_data_references': references,
        'radii_unit': 'angstroms',
    }, {'elements_source.txt': source_copy, 'elements.txt': effective_copy}


def _log_tail(path: Path) -> str:
    with path.open('rb') as stream:
        stream.seek(max(0, path.stat().st_size - 2048))
        return stream.read(2048).decode('utf-8', errors='replace')


@contextmanager
def private_display(executable: str | None, output: Path):
    """Own one allocated display and terminate only that child, even on failure."""
    if executable is None:
        yield {}
        return
    write_fd: int | None
    read_fd, write_fd = os.pipe()
    server = None
    log_path = output / 'xvfb.log'
    try:
        with log_path.open('wb') as log:
            server = subprocess.Popen(
                [
                    executable,
                    '-displayfd',
                    str(write_fd),
                    '-screen',
                    '0',
                    '640x480x24',
                    '-nolisten',
                    'tcp',
                ],
                pass_fds=(write_fd,),
                stdout=log,
                stderr=log,
            )
        os.close(write_fd)
        write_fd = None
        ready = select.select([read_fd], [], [], 10)[0]
        display = os.read(read_fd, 32).strip() if ready else b''
        if not display.isdigit():
            raise ProviderExecutionError(
                provider='molovol',
                reason='Own virtual display failed or timed out: '
                + _log_tail(log_path),
            )
        yield {'DISPLAY': ':' + display.decode('ascii')}
    except OSError as cause:
        raise ProviderExecutionError(
            provider='molovol', reason=f'Own virtual-display process failed: {cause}'
        ) from cause
    finally:
        os.close(read_fd)
        if write_fd is not None:
            os.close(write_fd)
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()


def run(pdb: Path, output: Path, options: dict) -> tuple[dict, dict]:
    executable, resource, display = _configuration(options)
    metadata, additional = prepare_elements(
        pdb, output, resource, options.get('element_radii', {})
    )
    probe, step, depth = (
        options.get('probe_radius', 1.4),
        options.get('grid_step', 0.2),
        options.get('octree_depth', 4),
    )
    large = options.get('large_probe_radius')
    estimate = check_grid_budget(
        pdb,
        step=step,
        padding=max(metadata['effective_radii'].values()) + (large or probe) + 2 * step,
        limit=options.get('max_grid_points', 20_000_000),
        octree_depth=depth,
    )
    surfaces = options.get('calculate_surfaces', False)
    command = [
        executable,
        '-r',
        str(probe),
        '-g',
        str(step),
        '-fs',
        str(pdb),
        '-fe',
        str(additional['elements.txt']),
        '-do',
        str(output),
        '-d',
        str(depth),
        '-ht',
        '-xr',
        '-q',
    ]
    if large is not None:
        command.extend(['-r2', str(large)])
    if surfaces:
        command.append('-sf')
    with private_display(display, output) as environment:
        returncode = run_command(
            command,
            output,
            timeout=options.get('timeout', 120),
            workers=1,
            extra_env=environment,
        )
    reports = list(output.glob('*_MoloVol-report_grid-*.txt'))
    if len(reports) != 1:
        raise ProviderExecutionError(
            provider='molovol',
            reason='A unique completed original report is absent, even if the program exited zero.',
        )
    try:
        text = reports[0].read_text()
        decoded = decode_report(text)
        validate_query(
            decoded,
            {
                'probe_radius': probe,
                'large_probe_radius': large,
                'grid_step': step,
                'octree_depth': depth,
                'calculate_surfaces': surfaces,
            },
            metadata['effective_radii'],
            metadata['element_counts'],
        )
    except ValueError as cause:
        raise ProviderExecutionError(
            provider='molovol', reason=f'Invalid original report: {cause}'
        ) from cause
    return {
        **metadata,
        'version': decoded['version'],
        'executable': file_identity(Path(executable)),
        'command': command,
        'returncode': returncode,
        'report_file': reports[0].name,
        'parameters': {
            'probe_radius': probe,
            'large_probe_radius': large,
            'grid_step': step,
            'length_unit': 'angstroms',
            'octree_depth': depth,
            'calculate_surfaces': surfaces,
        },
        'estimated_grid_points': estimate,
        'max_grid_points': options.get('max_grid_points', 20_000_000),
        'workers': 1,
        'virtual_display': display is not None,
        'geometry_policy': 'Original isolated neutral-element PDB model; original center is a bounds midpoint, not complete support',
    }, additional
