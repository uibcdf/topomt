"""Invoke an unchanged external HOLE executable with explicit input cards."""

import hashlib
from pathlib import Path

from topomt._private.arg_digestion.external_arguments import _error
from topomt.third_party._execution import (
    ProviderExecutionError,
    ProviderUnavailableError,
    executable_command,
    file_identity,
    run_command,
)
from topomt.third_party._specialist import failure_evidence

from .parser import decode_report

AMBER_SOURCE_SHA256 = 'd09b6e01434d7f76bed6dfe61e51a936c6820030bcaf52a86fd13a39d5207a73'


def _configuration(options: dict) -> tuple[str, Path]:
    executable = executable_command('hole', options.get('hole_cmd', 'hole'))
    resource = Path(
        options.get('radii_file', Path(executable).parent.parent / 'rad/simple.rad')
    )
    if not resource.is_file():
        raise ProviderUnavailableError(
            provider='hole',
            requirement=f'Explicit radii_file or original rad/simple.rad: {resource}',
        )
    return executable, resource.resolve()


def ensure_available(options: dict) -> None:
    _configuration(options)


def run(pdb: Path, output: Path, options: dict) -> tuple[dict, dict]:
    executable, resource = _configuration(options)
    count = sum(
        line.startswith(('ATOM  ', 'HETATM')) for line in pdb.read_text().splitlines()
    )
    if count > options.get('max_atoms', 25000):
        _error(
            'max_atoms',
            options.get('max_atoms', 25000),
            None,
            'HOLE input exceeds the explicit atom budget.',
        )
    query: dict = {
        name: options.get(name, default)
        for name, default in [
            ('origin', None),
            ('direction', None),
            ('sample_step', 0.5),
            ('end_radius', 10.0),
            ('random_seed', 12345),
        ]
    }
    query['length_unit'] = 'angstroms'
    controls = 'COORD input.pdb\nRADIUS radii.rad\nSPHPDB profile.sph\n'
    controls += (
        '\n'.join(
            f'{card} '
            + (
                ' '.join(format(x, '.17g') for x in query[key])
                if key in {'origin', 'direction'}
                else str(query[key])
            )
            for card, key in [
                ('CPOINT', 'origin'),
                ('CVECT', 'direction'),
                ('SAMPLE', 'sample_step'),
                ('ENDRAD', 'end_radius'),
                ('RASEED', 'random_seed'),
            ]
        )
        + '\nSHORTO 0\n'
    )
    (output / 'input.pdb').write_bytes(pdb.read_bytes())
    (output / 'radii.rad').write_bytes(resource.read_bytes())
    (output / 'control.in').write_text(controls)
    additional = {name: output / name for name in ['control.in', 'radii.rad']}
    radii_identity = {**file_identity(output / 'radii.rad'), 'path': str(resource)}
    context: dict = {
        'parameters': query,
        'workers': 1,
        'max_atoms': options.get('max_atoms', 25000),
        'timeout': {'value': options.get('timeout', 120), 'unit': 'seconds'},
        'executable': file_identity(Path(executable)),
        'radii_source': radii_identity,
        'input_data_references': ['amber_1984']
        if radii_identity['sha256'] == AMBER_SOURCE_SHA256
        else [],
        'input_fingerprints': {
            name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name, path in additional.items()
        },
        'command': [executable],
    }
    with failure_evidence(context, additional):
        code = run_command(
            [executable],
            output,
            timeout=options.get('timeout', 120),
            workers=1,
            stdin_file=output / 'control.in',
            provider='hole',
        )
        try:
            data = decode_report(
                (output / 'stdout.txt').read_text(),
                (output / 'profile.sph').read_text(),
            )
            if data['atom_count'] != count or data['parameters'] != query:
                raise ValueError('HOLE submitted input and reported query disagree')
        except (ValueError, OSError) as cause:
            raise ProviderExecutionError(
                provider='hole',
                reason=f'Original HOLE result validation failed: {cause}',
            ) from cause
    return {**context, 'version': data['version'], 'returncode': code}, additional
