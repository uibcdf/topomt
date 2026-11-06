"""Recover original Pocketeer outputs without importing the optional engine."""

import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.external_arguments import (
    digest_selection,
    digest_structure_indices,
    digest_syntax,
)
from topomt._private.arg_digestion.pocketeer_arguments import FILES_CALLER, OPTIONS
from topomt._private.smonitor import signal
from topomt.provider_output import ProviderRun
from topomt.third_party._common import validate_single_frame_pdb
from topomt.third_party.output import _from_topography
from topomt.third_party.pdb_context import (
    reference_chemical_context,
    validate_source_input_context,
    validate_submitted_pdb,
)

from .output import PocketeerOutput
from .parser import _read_json, parse_pockets
from .records import pockets_to_topography


def _indices(
    value: Any, name: str, limit: int, *, allow_empty: bool = False
) -> np.ndarray:
    if (
        not isinstance(value, list)
        or not value
        and not allow_empty
        or any(type(index) is not int or index < 0 or index >= limit for index in value)
        or len(set(value)) != len(value)
        or value != sorted(value)
    ):
        raise ValueError(f'Invalid Pocketeer saved {name} indices/map.')
    return np.asarray(value, dtype=int)


def _artifact(run: ProviderRun, name: str) -> bytes:
    try:
        return run.get_artifact(name)
    except KeyError as error:
        raise ValueError(
            f'Pocketeer saved output/context artifact is absent: {name}'
        ) from error


@signal(tags=['provider', 'pocketeer', 'files'])
@arg_digest(**OPTIONS)
def load_output(
    molecular_system: Any,
    *,
    bundle_file: str | Path,
    skip_digestion: bool = False,
) -> PocketeerOutput:
    """Recover a captured original run bound to its full source context.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Full source with the saved atom inventory, frame and reference state.
    bundle_file : str or pathlib.Path
        ZIP created by ProviderRun.save after original Pocketeer execution.
        Manifest, artifact bytes and run ID are verified by ProviderRun.load.
    skip_digestion : bool, default=False
        Internal bypass for already admitted arguments.

    Returns
    -------
    PocketeerOutput
        Detached original records with the original library run and attributed
        measurements. Available empty output stays empty. Source-coordinate
        agreement uses 1e-12 nm; PDB row agreement uses 0.00051 angstroms.

    Raises
    ------
    ArgumentError
        If source/path arguments are invalid or saved context is overridden.
    ValueError
        If integrity, context, schema, maps or finite measurements disagree.
        Historical runs lacking source/chemical context cannot be reconstructed.
    OSError
        If the requested bundle cannot be read.

    Examples
    --------
    >>> result = load_output('source.h5msm', bundle_file='original.zip')  # doctest: +SKIP
    """
    run = ProviderRun.load(bundle_file)
    if run.provider != 'pocketeer' or run.backend != 'library':
        raise ValueError('Pocketeer recovery requires an original library run.')
    metadata = run.metadata
    required = {
        'selection',
        'structure_indices',
        'syntax',
        'chemical_state_context',
        'selected_atom_indices',
        'filtered_input_atom_indices',
    }
    if not required.issubset(metadata):
        raise ValueError(
            'Pocketeer saved source/chemical context or indices are absent.'
        )
    selection = digest_selection(metadata['selection'], caller=FILES_CALLER)
    frame = digest_structure_indices(metadata['structure_indices'], caller=FILES_CALLER)
    syntax = digest_syntax(metadata['syntax'], caller=FILES_CALLER)
    chemical = metadata['chemical_state_context']
    if not isinstance(chemical, dict) or type(chemical.get('index')) is not int:
        raise ValueError('Invalid Pocketeer saved chemical-state context.')
    if chemical != reference_chemical_context(
        molecular_system, chemical['index'], provider='Pocketeer'
    ):
        raise ValueError(
            'Source chemical-state context disagrees with the saved Pocketeer run.'
        )
    source_context = _read_json(_artifact(run, 'output/topomt_source_context.json'))
    if not isinstance(source_context, dict):
        raise ValueError('Invalid Pocketeer saved source context.')
    validate_source_input_context(molecular_system, source_context, frame)
    selected = _indices(
        metadata['selected_atom_indices'], 'selected atom', source_context['n_atoms']
    )
    filtered = _indices(
        metadata['filtered_input_atom_indices'],
        'filtered atom',
        len(selected),
        allow_empty=True,
    )
    input_names = [name for name, _ in run.artifacts if name.startswith('input/')]
    if len(input_names) != 1:
        raise ValueError('Pocketeer saved run requires exactly one submitted PDB.')
    with tempfile.TemporaryDirectory(prefix='topomt_pocketeer_recovery_') as folder:
        submitted = Path(folder) / 'submitted.pdb'
        submitted.write_bytes(run.get_artifact(input_names[0]))
        validate_single_frame_pdb(submitted, provider='Pocketeer')
        validate_submitted_pdb(
            molecular_system,
            submitted,
            selected,
            selection=selection,
            structure_indices=frame,
            syntax=syntax,
        )
    pockets = parse_pockets(
        _artifact(run, 'output/pocketeer_pockets.json'),
        _artifact(run, 'output/topomt_masks.json'),
        len(selected),
        len(filtered),
        metadata.get('output_protocol'),
    )
    return _from_topography(
        pockets_to_topography(
            molecular_system,
            pockets,
            selected,
            filtered,
            run,
            selection=selection,
            structure_indices=frame,
        ),
        PocketeerOutput,
    )
