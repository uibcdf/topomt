"""Bound fpocket capture and recovery using shared source-context validators."""

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from topomt._private.arg_digestion.external_arguments import (
    digest_selection,
    digest_syntax,
)
from topomt._private.arg_digestion.fpocket_arguments import SAVED_CALLER
from topomt.provider_output import ProviderRun
from topomt.third_party._common import validate_single_frame_pdb
from topomt.third_party._saved_json import read_json
from topomt.third_party.pdb_context import (
    source_input_context,
    validate_reference_chemical_context,
    validate_source_input_context,
    validate_submitted_pdb,
)
from topomt.topography.Topography import Topography

from .model import FpocketResult
from .parser import parse_fpocket_output

_CONTEXT = 'output/topomt_source_context.json'


def capture_bound_run(
    molecular_system: Any,
    result: FpocketResult,
    backend: str,
    metadata: dict[str, Any],
    *,
    structure_indices: Any,
) -> ProviderRun:
    """Add adapter provenance in owned staging, preserving original file bytes."""
    supplemental = result.output_dir / 'topomt_source_context.json'
    if supplemental.exists() or supplemental.is_symlink():
        raise ValueError('Original fpocket output collides with its source supplement.')
    context = source_input_context(molecular_system, structure_indices)
    frame = metadata['structure_indices']
    if isinstance(frame, str) and frame.lower() == 'all':
        # The full context above already requires exactly one source frame.
        frame = 0
    metadata = {
        **metadata,
        'structure_indices': _frame(frame),
        'source_binding_protocol': 1,
        'source_context_artifact': _CONTEXT,
    }
    with tempfile.TemporaryDirectory(prefix='topomt_fpocket_capture_') as folder:
        staging = Path(folder) / 'output'
        shutil.copytree(result.output_dir, staging, symlinks=True)
        (staging / 'topomt_source_context.json').write_text(
            json.dumps(context, sort_keys=True, allow_nan=False), encoding='utf-8'
        )
        return ProviderRun.capture(
            'fpocket', backend, result.source_pdb, staging, metadata=metadata
        )


def _frame(value: Any) -> int | list[int]:
    if type(value) is int and value >= 0:
        return value
    if (
        isinstance(value, list)
        and len(value) == 1
        and type(value[0]) is int
        and value[0] >= 0
    ):
        return value
    raise ValueError(
        'Invalid fpocket saved source frame; exactly one index is required.'
    )


def _map(value: Any, n_atoms: int) -> list[int]:
    if (
        not isinstance(value, list)
        or not value
        or any(type(index) is not int or not 0 <= index < n_atoms for index in value)
        or len(set(value)) != len(value)
    ):
        raise ValueError('Invalid fpocket saved submitted atom map.')
    return value


def _artifact(run: ProviderRun, name: str) -> bytes:
    try:
        return run.get_artifact(name)
    except KeyError as error:
        raise ValueError(
            f'Fpocket saved source/result artifact is absent: {name}'
        ) from error


def recover_topography(molecular_system: Any, run: ProviderRun) -> Topography:
    """Recover only the recorded source-bound original acquisition routes."""
    from .files import fpocket_result_to_topography

    if run.provider != 'fpocket' or run.backend not in {'cli', 'wrapper', 'files'}:
        raise ValueError('Fpocket recovery requires an original cli/wrapper/files run.')
    metadata = run.metadata
    required = {
        'source_binding_protocol',
        'source_context_artifact',
        'selection',
        'structure_indices',
        'syntax',
        'chemical_state_context',
        'submitted_atom_indices',
        'atom_serial_to_index',
    }
    if (
        not required.issubset(metadata)
        or type(metadata.get('source_binding_protocol')) is not int
        or metadata['source_binding_protocol'] != 1
        or metadata.get('source_context_artifact') != _CONTEXT
    ):
        raise ValueError(
            'Fpocket bundle lacks the supported full-source binding protocol/context.'
        )
    selection = digest_selection(metadata['selection'], caller=SAVED_CALLER)
    frame = _frame(metadata['structure_indices'])
    syntax = digest_syntax(metadata['syntax'], caller=SAVED_CALLER)
    validate_reference_chemical_context(
        molecular_system, metadata['chemical_state_context'], provider='fpocket'
    )
    context = read_json(_artifact(run, _CONTEXT), provider='fpocket')
    if not isinstance(context, dict):
        raise ValueError('Invalid fpocket saved full-source context.')
    validate_source_input_context(molecular_system, context, frame)
    submitted_indices = _map(metadata['submitted_atom_indices'], context['n_atoms'])
    inputs = [name for name, _ in run.artifacts if name.startswith('input/')]
    if (
        len(inputs) != 1
        or len(Path(inputs[0]).parts) != 2
        or not inputs[0].endswith('.pdb')
    ):
        raise ValueError('Fpocket saved run requires exactly one submitted PDB.')
    with tempfile.TemporaryDirectory(prefix='topomt_fpocket_recovery_') as folder:
        root = Path(folder)
        for name, data in run.artifacts:
            target = root / name  # ProviderRun.load admitted canonical relative names.
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        submitted = root / inputs[0]
        validate_single_frame_pdb(submitted, provider='fpocket')
        serial_map = validate_submitted_pdb(
            molecular_system,
            submitted,
            submitted_indices,
            selection=selection,
            structure_indices=frame,
            syntax=syntax,
        )
        expected = {str(serial): index for serial, index in serial_map.items()}
        if json.dumps(metadata['atom_serial_to_index'], sort_keys=True) != json.dumps(
            expected, sort_keys=True
        ):
            raise ValueError('Fpocket saved serial/source atom map disagrees.')
        _artifact(run, f'output/{submitted.stem}_info.txt')
        result = parse_fpocket_output(submitted, root / 'output')
        if any(
            serial not in serial_map
            for pocket in result.pockets
            for serial in pocket.atom_serials
        ):
            raise ValueError(
                'Fpocket pocket atom serial is outside the submitted source map.'
            )
        return fpocket_result_to_topography(
            molecular_system,
            result,
            selection=selection,
            structure_indices=frame,
            syntax=syntax,
            backend=run.backend,
            submitted_atom_indices=submitted_indices,
            chemical_state_context=metadata['chemical_state_context'],
            _provider_run=run,
        )
