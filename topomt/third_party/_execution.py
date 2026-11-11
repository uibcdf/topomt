"""Private orchestration for source-bound original local providers."""

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import replace
from importlib import import_module
from pathlib import Path
from typing import Any

import numpy as np
from depdigest import check_dependency

from topomt._ackredit import original_provider
from topomt._depdigest import DOC_URL, LIBRARIES
from topomt._private.arg_digestion.external_arguments import _error
from topomt._private.smonitor import TopoMTException, signal
from topomt.provider_output import ProviderRun
from topomt.third_party._common import (
    prepare_wrapper_input_pdb,
    validate_single_frame_pdb,
)
from topomt.third_party._saved_json import read_json
from topomt.third_party.output import ProviderOutput
from topomt.third_party.pdb_context import (
    reference_chemical_context,
    source_input_context,
    validate_reference_chemical_context,
    validate_source_input_context,
    validate_submitted_pdb,
)

PROTOCOL = 'topomt.original-local@1'


class ProviderExecutionError(TopoMTException, RuntimeError):
    """Original execution failed; this is distinct from absent dependencies."""

    catalog_key = 'ProviderExecutionError'
    run: ProviderRun | None = None

    def __init__(
        self,
        message: str | None = None,
        *,
        provider: str | None = None,
        reason: str | None = None,
    ) -> None:
        fields = {
            key: value
            for key, value in {'provider': provider, 'reason': reason}.items()
            if value is not None
        }
        TopoMTException.__init__(self, message, **fields)


class ProviderUnavailableError(TopoMTException, ImportError):
    """A selected original route lacks its declared local prerequisite."""

    catalog_key = 'ProviderUnavailableError'

    def __init__(
        self,
        message: str | None = None,
        *,
        provider: str | None = None,
        requirement: str | None = None,
    ) -> None:
        fields = {
            key: value
            for key, value in {'provider': provider, 'requirement': requirement}.items()
            if value is not None
        }
        TopoMTException.__init__(self, message, **fields)


def executable_command(key: str, command: str) -> str:
    """Check the selected executable, then execute that same resolved path."""
    selected = (
        str(Path(command).expanduser().resolve())
        if os.path.dirname(command)
        else command
    )
    declaration = LIBRARIES[key]
    try:
        check_dependency(
            key,
            kind='executable',
            executable=selected,
            pypi_name=declaration.get('pypi'),
            conda_name=declaration.get('conda'),
            conda_channel=declaration.get('channel'),
            doc_url=DOC_URL,
            caller='original_provider',
            exception_class=ImportError,
        )
    except ImportError as error:
        raise ProviderUnavailableError(provider=key, requirement=selected) from error
    resolved = shutil.which(selected)
    if resolved is None:
        raise ProviderUnavailableError(provider=key, requirement=selected)
    return str(Path(resolved).resolve())


def file_identity(path: Path) -> dict[str, Any]:
    """Fingerprint the exact original executable, module or data file."""
    with path.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    return {'path': str(path.resolve()), 'sha256': digest, 'size': path.stat().st_size}


def java_setup(
    provider: str, options: dict, jar_relative: str
) -> tuple[Path, str, list[str]]:
    """Locate one distribution and the same Java command used for execution."""
    home = options.get(provider + '_home')
    if home is None or not (Path(home) / jar_relative).is_file():
        raise ProviderUnavailableError(
            provider=provider, requirement=f'{provider}_home containing {jar_relative}'
        )
    home = Path(home).resolve()
    java = executable_command('java', options.get('java_cmd', 'java'))
    command = [
        java,
        f'-Xmx{options.get("memory_mb", 1024)}m',
        f'-XX:ActiveProcessorCount={options.get("workers", 1)}',
        '-Djava.awt.headless=true',
    ]
    return home, java, command


@signal(tags=['provider', 'original', 'execution'])
def run_command(
    command: list[str],
    directory: Path,
    *,
    timeout: float,
    workers: int,
    extra_env: dict[str, str] | None = None,
    allowed_returncodes: tuple[int, ...] = (0,),
) -> int:
    """Run without a shell; cap worker defaults and retain bounded log files."""
    environment = dict(os.environ)
    environment.update(
        {
            key: str(workers)
            for key in (
                'OMP_NUM_THREADS',
                'OPENBLAS_NUM_THREADS',
                'MKL_NUM_THREADS',
                'NUMBA_NUM_THREADS',
                'OMP_THREAD_LIMIT',
            )
        }
    )
    environment.update(extra_env or {})
    with (
        (directory / 'stdout.txt').open('wb') as stdout,
        (directory / 'stderr.txt').open('wb') as stderr,
    ):
        try:
            result = subprocess.run(
                command,
                cwd=directory,
                env=environment,
                stdout=stdout,
                stderr=stderr,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise ProviderExecutionError(
                provider=Path(command[0]).name,
                reason=f'timeout after {timeout} seconds',
            ) from error
    if result.returncode not in allowed_returncodes:
        tail = b'\n'.join(
            (directory / name).read_bytes()[-4096:]
            for name in ('stdout.txt', 'stderr.txt')
        ).decode('utf-8', errors='replace')
        raise ProviderExecutionError(
            provider=Path(command[0]).name, reason=f'exit {result.returncode}: {tail}'
        )
    return result.returncode


def check_grid_budget(
    pdb: Path,
    *,
    step: float,
    padding: float,
    limit: int,
    octree_depth: int | None = None,
) -> int:
    """Reject a conservative bounding-grid estimate before a grid engine runs."""
    rows = [
        line
        for line in pdb.read_text().splitlines()
        if line.startswith(('ATOM  ', 'HETATM'))
    ]
    points = np.array([[float(line[i : i + 8]) for i in (30, 38, 46)] for line in rows])
    dimensions = np.ceil((np.ptp(points, axis=0) + 2 * padding) / step) + 3
    if not np.isfinite(dimensions).all():
        _error(
            'max_grid_points', limit, None, 'Grid dimensions exceed finite arithmetic.'
        )
    sizes = [int(dimension) for dimension in dimensions]
    if octree_depth is not None:
        quantum = 2**octree_depth
        sizes = [((size + quantum - 1) // quantum) * quantum for size in sizes]
        estimate = sum(
            int(np.prod([size // 2**level for size in sizes], dtype=object))
            for level in range(octree_depth + 1)
        )
    else:
        estimate = int(np.prod(sizes, dtype=object))
    if estimate > limit:
        _error(
            'max_grid_points',
            limit,
            None,
            f'Conservative grid estimate {estimate} exceeds this explicit limit; use a smaller input/region or coarser step.',
        )
    return estimate


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, np.ndarray)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def _source_options(options: dict) -> dict:
    return {
        key: options.get(key, default)
        for key, default in [
            ('selection', 'all'),
            ('structure_indices', 0),
            ('chemical_state', 'reference'),
            ('syntax', 'MolSysMT'),
        ]
    }


def _bind_output(run: ProviderRun, context: dict) -> ProviderOutput:
    parsed = import_module(f'topomt.third_party.{run.provider}.parser').parse_output(
        run
    )
    return replace(
        parsed, input_points_nm=tuple(map(tuple, context['coordinates']['value']))
    )


def recover(provider: str, molecular_system: Any, bundle_file: Path) -> ProviderOutput:
    """Verify source context and input row mapping before engine-free parsing."""
    run = ProviderRun.load(bundle_file)
    if run.provider != provider or run.backend != (
        'library' if provider == 'pykvfinder' else 'cli'
    ):
        raise ValueError(
            'Saved provider/backend identity disagrees with the selected reader'
        )
    metadata = run.metadata
    if (
        metadata.get('adapter_protocol') != PROTOCOL
        or metadata.get('execution_status') != 'completed'
    ):
        raise ValueError('Unsupported original-local source-context protocol')
    from topomt._private.arg_digestion.external_arguments import (
        digest_selection,
        digest_structure_indices,
        digest_syntax,
    )

    try:
        selection = digest_selection(metadata['selection'])
        frame = digest_structure_indices(metadata['structure_indices'])
        syntax = digest_syntax(metadata['syntax'])
        context = read_json(
            run.get_artifact('output/topomt_source_context.json'), provider=provider
        )
        indices = metadata['selected_atom_indices']
        if (
            not isinstance(indices, list)
            or not indices
            or any(type(index) is not int for index in indices)
        ):
            raise ValueError('Invalid submitted atom indices')
        validate_reference_chemical_context(
            molecular_system, metadata['chemical_state_context'], provider=provider
        )
        validate_source_input_context(molecular_system, context, frame)
        with tempfile.TemporaryDirectory(
            prefix=f'topomt_{provider}_recovery_'
        ) as temporary:
            path = Path(temporary) / 'input.pdb'
            path.write_bytes(run.get_artifact('input/input.pdb'))
            validate_single_frame_pdb(path, provider=provider)
            validate_submitted_pdb(
                molecular_system,
                path,
                indices,
                selection=selection,
                structure_indices=frame,
                syntax=syntax,
            )
    except (KeyError, TypeError) as error:
        raise ValueError('Missing or invalid saved original source context') from error
    return _bind_output(run, context)


@signal(tags=['provider', 'original', 'source'])
@original_provider
def get_output(
    provider: str, molecular_system: Any, backend: str, options: dict[str, Any]
) -> ProviderOutput:
    """Coordinate one selected original engine or its engine-free saved reader."""
    if backend == 'files':
        if set(options) != {'bundle_file'}:
            _error(
                'bundle_file',
                options,
                None,
                'Saved recovery requires only bundle_file; execution/source-context overrides are forbidden.',
            )
        return recover(provider, molecular_system, options['bundle_file'])
    if 'bundle_file' in options:
        _error(
            'bundle_file',
            options['bundle_file'],
            None,
            'bundle_file requires backend=files.',
        )
    if provider == 'pykvfinder' and options.get('probe_in', 1.4) >= options.get(
        'probe_out', 4.0
    ):
        _error(
            'probe_out',
            options.get('probe_out'),
            None,
            'probe_out must exceed probe_in.',
        )
    if provider == 'ghecom' and options.get('probe_small', 1.87) >= options.get(
        'probe_large', 6.0
    ):
        _error(
            'probe_large',
            options.get('probe_large'),
            None,
            'probe_large must exceed probe_small.',
        )
    if provider == 'caver' and 'origin' not in options:
        _error(
            'origin',
            None,
            None,
            'CAVER requires an explicit starting-point length quantity.',
        )
    if provider == 'ghecom' and options.get('workers', 1) != 1:
        _error(
            'workers',
            options['workers'],
            None,
            'The admitted GHECOM route is serial; use workers=1.',
        )
    engine = import_module(f'topomt.third_party.{provider}.runner')
    engine.ensure_available(options)
    source = _source_options(options)
    chemical = reference_chemical_context(
        molecular_system, source['chemical_state'], provider=provider
    )
    with tempfile.TemporaryDirectory(prefix=f'topomt_{provider}_') as temporary:
        root = Path(temporary)
        output = root / 'results'
        output.mkdir()
        original, indices = prepare_wrapper_input_pdb(
            molecular_system,
            tmpdir=root,
            selection=source['selection'],
            structure_indices=source['structure_indices'],
            syntax=source['syntax'],
        )
        submitted = root / 'input.pdb'
        if original != submitted:
            original.rename(submitted)
        validate_single_frame_pdb(submitted, provider=provider)
        validate_submitted_pdb(
            molecular_system,
            submitted,
            indices,
            selection=source['selection'],
            structure_indices=source['structure_indices'],
            syntax=source['syntax'],
        )
        context = source_input_context(molecular_system, source['structure_indices'])
        (output / 'topomt_source_context.json').write_text(
            json.dumps(context, allow_nan=False)
        )
        base_metadata = {
            'adapter_protocol': PROTOCOL,
            **_jsonable(source),
            'selected_atom_indices': indices.tolist(),
            'chemical_state_context': chemical,
        }
        try:
            metadata, additional = engine.run(submitted, output, options)
        except ProviderExecutionError as error:
            size = sum(
                path.stat().st_size for path in output.rglob('*') if path.is_file()
            )
            if size <= 128 * 1024 * 1024:
                error.run = ProviderRun.capture(
                    provider,
                    backend,
                    submitted,
                    output,
                    metadata={**base_metadata, 'execution_status': 'failed'},
                )
            raise
        total = sum(path.stat().st_size for path in output.rglob('*') if path.is_file())
        if total > 128 * 1024 * 1024:
            raise ProviderExecutionError(
                provider=provider,
                reason='original output exceeds the 128 MiB capture budget',
            )
        metadata.update(base_metadata)
        metadata['execution_status'] = 'completed'
        run = ProviderRun.capture(
            provider,
            backend,
            submitted,
            output,
            metadata=_jsonable(metadata),
            additional_inputs=additional,
        )
        try:
            return _bind_output(run, context)
        except ValueError as cause:
            failed_run = ProviderRun.capture(
                provider,
                backend,
                submitted,
                output,
                metadata={
                    **run.metadata,
                    'execution_status': 'failed',
                    'failure_stage': 'result_validation',
                },
                additional_inputs=additional,
            )
            result_error = ProviderExecutionError(
                provider=provider, reason=f'original result is invalid: {cause}'
            )
            result_error.run = failed_run
            raise result_error from cause
