"""Recover source-bound original pyCASTA results without the original engine."""

import json
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
from topomt._private.arg_digestion.pycasta_arguments import FILES_CALLER, OPTIONS
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

from .output import PyCASTAOutput
from .parser import parse_result, protein_atom_indices_from_pdb
from .records import result_to_topography


def _artifact(run: ProviderRun, name: Any, prefix: str = 'output') -> bytes:
    if not isinstance(name, str) or not name.startswith(prefix + '/'):
        raise ValueError('Invalid pyCASTA saved artifact path.')
    try:
        return run.get_artifact(name)
    except KeyError as error:
        raise ValueError(f'pyCASTA saved artifact is absent: {name}.') from error


def _indices(value: Any, limit: int) -> np.ndarray:
    if (
        not isinstance(value, list)
        or not value
        or any(type(i) is not int or not 0 <= i < limit for i in value)
        or len(set(value)) != len(value)
        or value != sorted(value)
    ):
        raise ValueError('Invalid pyCASTA saved source atom indices.')
    return np.asarray(value, dtype=int)


@signal(tags=['provider', 'pycasta', 'files'])
@arg_digest(**OPTIONS)
def load_output(
    molecular_system: Any = None,
    *,
    bundle_file: str | Path,
    skip_digestion: bool = False,
) -> PyCASTAOutput:
    """Recover exact original records bound to their full source context.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Full source with the saved identities, coordinates and reference state.
    bundle_file : str or pathlib.Path
        Original ProviderRun ZIP with verified artifacts and content-derived ID.
    skip_digestion : bool, default=False
        Internal bypass for already admitted arguments.

    Returns
    -------
    PyCASTAOutput
        Detached original fields and geometry. Saved empty output stays empty.

    Raises
    ------
    ArgumentError
        If source/path arguments are invalid or saved execution is overridden.
    ValueError
        If context, units, schemas, positions or index maps disagree. Historical
        runs lacking the required source/context supplements are not inferred.
    OSError
        If the bundle cannot be read.

    Examples
    --------
    >>> result = load_output('source.h5msm', bundle_file='original.zip')  # doctest: +SKIP
    """
    run = ProviderRun.load(bundle_file)
    if run.provider != 'pycasta' or run.backend != 'library':
        raise ValueError('pyCASTA recovery requires an original library run.')
    metadata = run.metadata
    required = {
        'selection',
        'structure_indices',
        'syntax',
        'chemical_state_context',
        'source_context_artifact',
        'selected_atom_indices',
        'protein_atom_indices',
        'source_sha256',
        'version_tag',
        'configuration',
        'distribution_version',
        'output_protocol',
        'alpha_artifact',
    }
    if not required.issubset(metadata):
        raise ValueError('pyCASTA saved execution/source/chemical context is absent.')
    selection = digest_selection(metadata['selection'], caller=FILES_CALLER)
    frame = digest_structure_indices(metadata['structure_indices'], caller=FILES_CALLER)
    syntax = digest_syntax(metadata['syntax'], caller=FILES_CALLER)
    validate_reference_chemical_context(
        molecular_system, metadata['chemical_state_context'], provider='pyCASTA'
    )
    context = read_json(
        _artifact(run, metadata['source_context_artifact']), provider='pyCASTA'
    )
    if not isinstance(context, dict):
        raise ValueError('Invalid pyCASTA saved full-source context.')
    validate_source_input_context(molecular_system, context, frame)
    selected = _indices(metadata['selected_atom_indices'], context['n_atoms'])
    protein = _indices(metadata['protein_atom_indices'], context['n_atoms'])
    configuration = read_json(
        _artifact(run, 'output/topomt_execution_configuration.json'), provider='pyCASTA'
    )
    if (
        not isinstance(configuration, dict)
        or json.dumps(configuration, sort_keys=True)
        != json.dumps(metadata['configuration'], sort_keys=True)
        or configuration.get('version_tag') != metadata['version_tag']
        or configuration.get('distribution_version') != metadata['distribution_version']
    ):
        raise ValueError('pyCASTA saved execution configuration disagrees.')
    inputs = [name for name, _ in run.artifacts if name.startswith('input/')]
    if len(inputs) != 1:
        raise ValueError('pyCASTA saved run requires exactly one submitted PDB.')
    expected_alpha = (
        f'output/{metadata["version_tag"]}/{Path(inputs[0]).stem}.alpha.npz'
    )
    if metadata['alpha_artifact'] != expected_alpha:
        raise ValueError(
            'pyCASTA original alpha artifact disagrees with execution context.'
        )
    state = parse_result(
        _artifact(run, 'output/topomt_returned_result.json'),
        _artifact(run, metadata['alpha_artifact']),
        _artifact(run, 'output/topomt_tetrahedron_indices.json'),
        metadata['output_protocol'],
    )
    with tempfile.TemporaryDirectory(prefix='topomt_pycasta_recovery_') as folder:
        submitted = Path(folder) / 'submitted.pdb'
        submitted.write_bytes(_artifact(run, inputs[0], 'input'))
        validate_single_frame_pdb(submitted, provider='pyCASTA')
        validate_submitted_pdb(
            molecular_system,
            submitted,
            selected,
            selection=selection,
            structure_indices=frame,
            syntax=syntax,
        )
        actual = protein_atom_indices_from_pdb(
            submitted, selected, state['protein_coords']
        )
    if not np.array_equal(actual, protein):
        raise ValueError('pyCASTA saved ATOM-to-source index map disagrees.')
    return _from_topography(
        result_to_topography(
            molecular_system,
            state,
            protein,
            run,
            selection=selection,
            structure_indices=frame,
        ),
        PyCASTAOutput,
    )
