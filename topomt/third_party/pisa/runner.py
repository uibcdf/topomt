"""Run an externally acquired, unchanged PISA on one supplied assembly."""

import hashlib
import re
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

from .parser import VERSION, decode_reports, monomer_atom_count

RESOURCES = {
    'srs': ('index.srs', 'struct.srs', 'graph.srs'),
    'molref': ('molref.idx', 'molref.rdt'),
    'pisastore': (
        'agents.dat',
        'asm_params.dat',
        'intfstats.dat',
        'syminfo_pisa.lib',
        'rcsb_symops.dat',
    ),
}


def _configuration(options: dict) -> tuple[str, Path]:
    executable = executable_command('pisa', options.get('pisa_cmd', 'pisa'))
    home = options.get('pisa_home')
    if home is None:
        raise ProviderUnavailableError(
            provider='pisa', requirement='pisa_home containing original setup resources'
        )
    home = Path(home).resolve()
    setup = home / 'setup' if (home / 'setup').is_dir() else home
    for group, names in RESOURCES.items():
        for name in names:
            if not (setup / group / name).is_file():
                raise ProviderUnavailableError(
                    provider='pisa',
                    requirement=f'Original PISA runtime resource: {setup / group / name}',
                )
    return executable, setup


def ensure_available(options: dict) -> None:
    _configuration(options)


def run(pdb: Path, output: Path, options: dict) -> tuple[dict, dict]:
    executable, setup = _configuration(options)
    count = sum(
        line.startswith(('ATOM  ', 'HETATM')) for line in pdb.read_text().splitlines()
    )
    if count > options.get('max_atoms', 25000):
        _error(
            'max_atoms',
            options.get('max_atoms', 25000),
            None,
            'PISA input exceeds the explicit atom budget.',
        )
    sessions = output.parent / 'pisa_sessions'
    sessions.mkdir()
    config = output / 'pisa.cfg'
    config.write_text(
        f'DATA_ROOT\n{sessions}\nSRS_DIR\n{setup}/srs\nMOLREF_DIR\n{setup}/molref\nPISTORE_DIR\n{setup}/pisastore\nRASMOL_COM\nJMOL_COM\nCCP4MG_COM\nSESSION_PREFIX\ntopomt_\n'
    )
    commands: dict[str, list[str]] = {}
    invocations = [
        ('version', [executable, '-version'], (2,)),
        (
            'analysis',
            [executable, 'supplied', '-analyse', str(pdb), '--as-is', str(config)],
            (0,),
        ),
        (
            'interfaces',
            [executable, 'supplied', '-xml', 'interfaces', '--as-is', str(config)],
            (0,),
        ),
        (
            'assemblies',
            [executable, 'supplied', '-xml', 'assemblies', '--as-is', str(config)],
            (0,),
        ),
        ('monomers', [executable, 'supplied', '-list', 'monomers', str(config)], (0,)),
    ]
    additional = {'pisa.cfg': config}
    context: dict = {
        'requested_protocol_version': VERSION,
        'assembly_policy': 'supplied_as_is',
        'workers': 1,
        'max_atoms': options.get('max_atoms', 25000),
        'executable': file_identity(Path(executable)),
        'timeout': {'value': options.get('timeout', 120), 'unit': 'seconds'},
        'timeout_policy': 'per_command',
        'commands': commands,
        'resource_files': {
            f'{group}/{name}': file_identity(setup / group / name)
            for group, names in RESOURCES.items()
            for name in names
        },
        'input_fingerprints': {
            'pisa.cfg': hashlib.sha256(config.read_bytes()).hexdigest()
        },
    }
    # The version command has its own nonzero success code. Analysis/extraction
    # still require zero plus independent original-output postconditions.
    with failure_evidence(context, additional):
        for label, command, codes in invocations:
            stage = output / label
            stage.mkdir()
            commands[label] = command
            context['failure_stage'] = label
            run_command(
                command,
                stage,
                timeout=options.get('timeout', 120),
                workers=1,
                allowed_returncodes=codes,
                provider='pisa',
            )
            (output / (label + '.txt')).write_bytes((stage / 'stdout.txt').read_bytes())
            if label == 'version':
                if (
                    re.search(
                        r'\bv' + re.escape(VERSION) + r' from\b',
                        (output / 'version.txt').read_text(),
                    )
                    is None
                ):
                    raise ProviderExecutionError(
                        provider='pisa',
                        reason='Unsupported original PISA version; qualified protocol is 2.1.2',
                    )
                context['version'] = VERSION
        context['failure_stage'] = 'result_validation'
        try:
            decode_reports(
                (output / 'interfaces.txt').read_bytes(),
                (output / 'assemblies.txt').read_bytes(),
            )
            if (
                '... results written' not in (output / 'analysis.txt').read_text()
                or monomer_atom_count((output / 'monomers.txt').read_text()) != count
            ):
                raise ValueError(
                    'PISA did not complete analysis of every submitted atom'
                )
        except ValueError as cause:
            raise ProviderExecutionError(
                provider='pisa',
                reason=f'Original PISA result validation failed: {cause}',
            ) from cause
    context.pop('failure_stage')
    return context, additional
