"""Original CASTp option admission without provider or filesystem work."""

from numbers import Integral
from pathlib import Path
from typing import Any

import numpy as np
from argdigest import register_pipeline
from argdigest.core.context import Context

from .external_arguments import (
    _error,
    digest_chemical_state,
    digest_path,
    digest_selection,
    digest_skip_digestion,
    digest_structure_indices,
    digest_syntax,
)

API_CALLER = 'topomt.third_party.castp.api.get_output'
FILES_CALLER = 'topomt.third_party.castp.files.load_output'
RECOVERY_CALLER = 'topomt.third_party.castp.files.recover_output'
SOURCE_PARAMETERS = (
    'source_atom_indices',
    'selection',
    'structure_indices',
    'syntax',
    'chemical_state',
)
RAW_PARAMETERS = (
    'poc_file',
    'pocInfo_file',
    'mouth_file',
    'mouthInfo_file',
    'pdb_file',
    'zip_file',
    'dir_path',
    'submitted_input_pdb',
    'provider_backend',
    'provider_server',
    'provider_jobid',
    'probe_radius',
    'provider_metadata',
    *SOURCE_PARAMETERS,
)
SAVED_PARAMETERS = ('bundle_file', 'provider_server')
SERVER_PARAMETERS = (
    'server',
    'selection',
    'structure_indices',
    'syntax',
    'probe_radius',
    'email',
    'wait',
    'extra_wait',
    'retries',
    'timeout',
    'output_zip_file',
)


def normalize_backend(caller: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(kwargs)
    if isinstance(normalized.get('backend'), str):
        normalized['backend'] = normalized['backend'].lower()
    return normalized


def digest_molecular_system(molecular_system: Any, caller: str | None = None) -> Any:
    if molecular_system is None and caller == RECOVERY_CALLER:
        _error(
            'molecular_system',
            molecular_system,
            caller,
            'Saved recovery requires its full molecular source.',
        )
    return molecular_system


def digest_source_atom_indices(
    source_atom_indices: Any, caller: str | None = None
) -> Any:
    if source_atom_indices is None:
        return None
    if isinstance(source_atom_indices, (list, tuple, range, np.ndarray)):
        try:
            array = np.asarray(source_atom_indices)
        except (TypeError, ValueError):
            array = np.asarray(0)
        if (
            array.ndim == 1
            and all(
                isinstance(i, Integral)
                and not isinstance(i, (bool, np.bool_))
                and int(i) >= 0
                for i in source_atom_indices
            )
            and len(set(map(int, source_atom_indices))) == len(source_atom_indices)
        ):
            return source_atom_indices
    _error(
        'source_atom_indices',
        source_atom_indices,
        caller,
        'Expected a unique one-dimensional sequence of nonnegative integer source indices, in archive PDB row order.',
    )


def _optional_path(value: Any, argument: str, caller: str | None) -> Path | None:
    return None if value is None else digest_path(value, argument, caller)


def digest_zip_file(zip_file: Any, caller: str | None = None) -> Path | None:
    return _optional_path(zip_file, 'zip_file', caller)


def digest_dir_path(dir_path: Any, caller: str | None = None) -> Path | None:
    return _optional_path(dir_path, 'dir_path', caller)


def digest_poc_file(poc_file: Any, caller: str | None = None) -> Path | None:
    return _optional_path(poc_file, 'poc_file', caller)


def digest_poc_info_file(pocInfo_file: Any, caller: str | None = None) -> Path | None:
    return _optional_path(pocInfo_file, 'pocInfo_file', caller)


def digest_mouth_file(mouth_file: Any, caller: str | None = None) -> Path | None:
    return _optional_path(mouth_file, 'mouth_file', caller)


def digest_mouth_info_file(
    mouthInfo_file: Any, caller: str | None = None
) -> Path | None:
    return _optional_path(mouthInfo_file, 'mouthInfo_file', caller)


def digest_pdb_file(pdb_file: Any, caller: str | None = None) -> Path | None:
    return _optional_path(pdb_file, 'pdb_file', caller)


def digest_submitted_input_pdb(
    submitted_input_pdb: Any, caller: str | None = None
) -> Path | None:
    return _optional_path(submitted_input_pdb, 'submitted_input_pdb', caller)


def digest_bundle_file(bundle_file: Any, caller: str | None = None) -> Path:
    return digest_path(bundle_file, 'bundle_file', caller)


# Legacy provenance fields retain their established IO-owned validation. These
# explicit registrations prevent an admitted value from becoming an undigested warning.
def digest_provider_backend(provider_backend: Any, caller: str | None = None) -> Any:
    return provider_backend


def digest_provider_server(provider_server: Any, caller: str | None = None) -> Any:
    return provider_server


def digest_provider_jobid(provider_jobid: Any, caller: str | None = None) -> Any:
    return provider_jobid


def digest_probe_radius(probe_radius: Any, caller: str | None = None) -> Any:
    return probe_radius


def digest_provider_metadata(provider_metadata: Any, caller: str | None = None) -> Any:
    return provider_metadata


@register_pipeline(kind='castp', name='original_backend')
def digest_original_backend(value: Any, context: Context) -> str:
    if not isinstance(value, str) or value.lower() not in {
        'server',
        'castpfold',
        'files',
    }:
        _error(
            'backend',
            value,
            context.function_name,
            'Expected server, castpfold or files for original output.',
        )
    backend = value.lower()
    if backend == 'files' and context.all_args.get('bundle_file') is not None:
        allowed = {'molecular_system', 'backend', 'skip_digestion', *SAVED_PARAMETERS}
        for name in sorted(set(context.all_args) - allowed):
            _error(
                name,
                context.all_args[name],
                context.function_name,
                'Saved CASTp bundles supply their recorded source and archive context; overrides are not admitted.',
            )
        if context.all_args.get('molecular_system') is None:
            _error(
                'molecular_system',
                None,
                context.function_name,
                'Saved recovery requires its full molecular source.',
            )
        digest_bundle_file(
            context.all_args['bundle_file'], caller=context.function_name
        )
    return backend


@register_pipeline(kind='castp', name='skip')
def digest_skip(value: Any, context: Context) -> bool:
    return digest_skip_digestion(value, caller=context.function_name)


ARGUMENT_DIGESTERS = {
    'molecular_system': digest_molecular_system,
    'source_atom_indices': digest_source_atom_indices,
    'selection': digest_selection,
    'structure_indices': digest_structure_indices,
    'syntax': digest_syntax,
    'chemical_state': digest_chemical_state,
    'zip_file': digest_zip_file,
    'dir_path': digest_dir_path,
    'poc_file': digest_poc_file,
    'pocInfo_file': digest_poc_info_file,
    'mouth_file': digest_mouth_file,
    'mouthInfo_file': digest_mouth_info_file,
    'pdb_file': digest_pdb_file,
    'submitted_input_pdb': digest_submitted_input_pdb,
    'bundle_file': digest_bundle_file,
    'provider_backend': digest_provider_backend,
    'provider_server': digest_provider_server,
    'provider_jobid': digest_provider_jobid,
    'probe_radius': digest_probe_radius,
    'provider_metadata': digest_provider_metadata,
    'skip_digestion': digest_skip_digestion,
}
OPTIONS = {
    'digestion_source': 'topomt._private.arg_digestion.castp_arguments',
    'digestion_style': 'registry',
    'standardizer': normalize_backend,
    'function_source': 'topomt._private.arg_digestion.function.castp',
    'domain_source': 'topomt._private.arg_digestion.domain.castp',
}
ORIGINAL_PIPELINES = {
    'backend': {'kind': 'castp', 'rules': ['original_backend']},
    'skip_digestion': {'kind': 'castp', 'rules': ['skip']},
}
