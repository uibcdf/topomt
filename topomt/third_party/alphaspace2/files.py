"""Recover source-bound original AlphaSpace2 snapshots without optional engines."""

import json
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.alphaspace2_arguments import (
    FILES_CALLER,
    OPTIONS,
    digest_min_vertices,
)
from topomt._private.arg_digestion.external_arguments import (
    digest_selection,
    digest_structure_indices,
    digest_syntax,
)
from topomt._private.smonitor import signal
from topomt.provider_output import ProviderRun
from topomt.third_party._common import validate_single_frame_pdb
from topomt.third_party._saved_json import read_json
from topomt.third_party.output import _from_topography
from topomt.third_party.pdb_context import (
    validate_reference_chemical_context,
    validate_source_input_context,
    validate_submitted_pdb,
)

from .output import AlphaSpace2Output
from .parser import _number, parse_snapshot
from .records import snapshot_to_topography


def _artifact(run: ProviderRun, name: Any, prefix: str) -> bytes:
    if not isinstance(name, str) or not name.startswith(prefix + '/'):
        raise ValueError('Invalid AlphaSpace2 saved artifact path.')
    try:
        return run.get_artifact(name)
    except KeyError as error:
        raise ValueError(f'AlphaSpace2 saved artifact is absent: {name}') from error


def _context(
    source: Any, metadata: dict[str, Any], run: ProviderRun, input_name: Any
) -> tuple[Any, Any, np.ndarray]:
    required = {
        'selection',
        'structure_indices',
        'syntax',
        'chemical_state_context',
        'source_context_artifact',
        'selected_atom_indices',
        'atom_serial_to_index',
    }
    if not required.issubset(metadata):
        raise ValueError('AlphaSpace2 saved source/chemical context is absent.')
    selection = digest_selection(metadata['selection'], caller=FILES_CALLER)
    frame = digest_structure_indices(metadata['structure_indices'], caller=FILES_CALLER)
    syntax = digest_syntax(metadata['syntax'], caller=FILES_CALLER)
    validate_reference_chemical_context(
        source, metadata['chemical_state_context'], provider='AlphaSpace2'
    )
    context = read_json(
        _artifact(run, metadata['source_context_artifact'], 'output'),
        provider='AlphaSpace2',
    )
    if not isinstance(context, dict):
        raise ValueError('Invalid AlphaSpace2 saved source context.')
    validate_source_input_context(source, context, frame)
    indices = metadata['selected_atom_indices']
    if (
        not isinstance(indices, list)
        or not indices
        or any(type(i) is not int or not 0 <= i < context['n_atoms'] for i in indices)
        or len(set(indices)) != len(indices)
        or sorted(indices) != indices
    ):
        raise ValueError('Invalid AlphaSpace2 saved source index map.')
    selected: np.ndarray = np.asarray(indices, dtype=int)
    data = _artifact(run, input_name, 'input')
    with tempfile.TemporaryDirectory(prefix='topomt_alphaspace2_recovery_') as folder:
        path = Path(folder) / 'submitted.pdb'
        path.write_bytes(data)
        validate_single_frame_pdb(path, provider='AlphaSpace2')
        actual = validate_submitted_pdb(
            source,
            path,
            selected,
            selection=selection,
            structure_indices=frame,
            syntax=syntax,
        )
    expected = {str(k): v for k, v in actual.items()}
    if json.dumps(metadata['atom_serial_to_index'], sort_keys=True) != json.dumps(
        expected, sort_keys=True
    ):
        raise ValueError('AlphaSpace2 saved serial map disagrees with submitted rows.')
    return selection, frame, selected


@signal(tags=['provider', 'alphaspace2', 'files'])
@arg_digest(**OPTIONS)
def load_output(
    molecular_system: Any,
    *,
    bundle_file: str | Path,
    binder: Any = None,
    skip_digestion: bool = False,
) -> AlphaSpace2Output:
    """Recover original results with the exact run and both source contexts.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Full receptor source with the saved identities, frame and reference.
    bundle_file : str or pathlib.Path
        ZIP from ProviderRun.save. Its bytes, manifest and run ID are verified.
    binder : MolSysMT-compatible input, optional
        Full saved binder source. Required for a bound run and omitted for an
        unbound run; selections and frames always come from recorded metadata.
    skip_digestion : bool, default=False
        Internal bypass for already admitted argument values.

    Returns
    -------
    AlphaSpace2Output
        Detached original records and run; empty filter results remain empty.
        Captured undefined occupancy markers remain undefined values.

    Raises
    ------
    ArgumentError
        If source/path arguments or execution-context overrides are invalid.
    ValueError
        If source chemistry, coordinate context, unit protocol, schema or maps
        disagree. Historical runs lacking these contexts are not reconstructed.
    OSError
        If the requested bundle cannot be read.

    Examples
    --------
    >>> result = load_output('source.h5msm', bundle_file='original.zip')  # doctest: +SKIP
    """
    run = ProviderRun.load(bundle_file)
    if run.provider != 'alphaspace2' or run.backend != 'library':
        raise ValueError('AlphaSpace2 recovery requires an original library run.')
    metadata = run.metadata
    if not {
        'receptor_input_artifact',
        'binder',
        'min_vertices',
        'snapshot_settings',
        'output_protocol',
    }.issubset(metadata):
        raise ValueError('AlphaSpace2 saved execution/source context is absent.')
    saved_binder = metadata['binder']
    if (saved_binder is None) != (binder is None):
        raise ValueError('AlphaSpace2 binder presence must agree with the saved run.')
    if saved_binder is not None and not isinstance(saved_binder, dict):
        raise ValueError('Invalid AlphaSpace2 saved binder context.')
    selection, frame, selected = _context(
        molecular_system, metadata, run, metadata['receptor_input_artifact']
    )
    inputs = {metadata['receptor_input_artifact']}
    if saved_binder is not None:
        if 'input_artifact' not in saved_binder:
            raise ValueError('AlphaSpace2 saved binder input is absent.')
        _context(binder, saved_binder, run, saved_binder['input_artifact'])
        inputs.add(saved_binder['input_artifact'])
    actual_inputs = {name for name, _ in run.artifacts if name.startswith('input/')}
    if inputs != actual_inputs or len(inputs) != (1 if saved_binder is None else 2):
        raise ValueError(
            'AlphaSpace2 submitted input set disagrees with saved context.'
        )
    minimum = digest_min_vertices(metadata['min_vertices'], caller=FILES_CALLER)
    settings = metadata['snapshot_settings']
    names = {
        'min_r',
        'max_r',
        'beta_cluster_dist',
        'pocket_cluster_dist',
        'contact_cutoff',
    }
    if not isinstance(settings, dict) or set(settings) != names:
        raise ValueError('Invalid AlphaSpace2 original snapshot settings.')
    for name, value in settings.items():
        if _number(value, 'snapshot settings.' + name) <= 0:
            raise ValueError('AlphaSpace2 snapshot settings must be positive.')
    if settings['min_r'] >= settings['max_r']:
        raise ValueError('Invalid AlphaSpace2 original radius range.')
    state = parse_snapshot(
        _artifact(run, 'output/topomt_snapshot.json', 'output'),
        len(selected),
        metadata['output_protocol'],
    )
    radii = np.asarray(state['_alpha_radii'], dtype=float)
    if np.any(radii < settings['min_r']) or np.any(radii > settings['max_r']):
        raise ValueError(
            'AlphaSpace2 saved radii conflict with recorded physical bounds.'
        )
    return _from_topography(
        snapshot_to_topography(
            molecular_system,
            state,
            selected,
            run,
            selection=selection,
            structure_indices=frame,
            min_vertices=minimum,
        ),
        AlphaSpace2Output,
    )
