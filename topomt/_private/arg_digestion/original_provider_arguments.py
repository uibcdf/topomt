"""Closed, provider-owned options for the new original-engine routes."""

from numbers import Integral
from typing import Any

import numpy as np
from argdigest import register_pipeline
from argdigest.core.context import Context

from topomt._pyunitwizard import pyunitwizard as puw

from .external_arguments import (
    _error,
    digest_chemical_state,
    digest_molecular_system,
    digest_path,
    digest_selection,
    digest_structure_indices,
    digest_syntax,
)

COMMON = {
    'selection',
    'structure_indices',
    'chemical_state',
    'syntax',
    'workers',
    'timeout',
}
PARAMETERS = {
    'pykvfinder': COMMON
    | {
        'step',
        'probe_in',
        'probe_out',
        'removal_distance',
        'volume_cutoff',
        'include_depth',
        'max_grid_points',
        'upstream_root',
        'python_cmd',
    },
    'ghecom': COMMON
    | {'grid_width', 'probe_small', 'probe_large', 'ghecom_cmd', 'max_grid_points'},
    'caver': COMMON
    | {
        'origin',
        'probe_radius',
        'shell_radius',
        'shell_depth',
        'caver_home',
        'java_cmd',
        'memory_mb',
    },
    'p2rank': COMMON | {'p2rank_home', 'java_cmd', 'memory_mb', 'model'},
    'mole': COMMON
    | {
        'mole_cmd',
        'memory_mb',
        'origin',
        'probe_radius',
        'interior_threshold',
        'min_depth',
        'min_depth_length',
        'min_tunnel_length',
        'min_pore_length',
        'surface_cover_radius',
        'origin_radius',
        'bottleneck_radius',
        'bottleneck_tolerance',
        'auto_origin_cover_radius',
        'max_auto_origins_per_cavity',
        'weight_function',
        'ignore_hetatoms',
        'ignore_hydrogens',
        'compute_pores',
        'compute_merged_pores',
    },
}


def scalar(value: Any, name: str, unit: str, *, zero: bool = False) -> float:
    """Admit one finite physical protocol scalar in its declared unit."""
    try:
        raw = puw.get_value(value, to_unit=unit) if puw.is_quantity(value) else value
        array = np.asarray(raw)
        if array.ndim == 0 and array.dtype.kind in 'iuf':
            number = float(array)
            if np.isfinite(number) and (number >= 0 if zero else number > 0):
                return number
    except (ValueError, TypeError):
        pass
    _error(
        name,
        value,
        None,
        f'Expected a finite {"nonnegative" if zero else "positive"} scalar in {unit}, or a compatible quantity.',
    )


def positive_integer(value: Any, name: str) -> int:
    if isinstance(value, Integral) and not isinstance(value, bool) and int(value) > 0:
        return int(value)
    _error(name, value, None, 'Expected a positive integer.')


def digest_origin(origin: Any, caller: str | None = None) -> list[float]:
    try:
        if puw.is_quantity(origin):
            values = np.asarray(puw.get_value(origin, to_unit='angstroms'))
            if (
                values.shape == (3,)
                and values.dtype.kind in 'iuf'
                and np.isfinite(values).all()
            ):
                return values.astype(float).tolist()
    except (ValueError, TypeError):
        pass
    _error(
        'origin', origin, caller, 'Expected a finite three-coordinate length quantity.'
    )


def digest_include_depth(include_depth: Any, caller: str | None = None) -> bool:
    if type(include_depth) is bool:
        return include_depth
    _error('include_depth', include_depth, caller, 'Expected a literal boolean.')


def command(value: Any, name: str) -> str:
    if isinstance(value, str) and value.strip() and '\0' not in value:
        return value
    _error(
        name,
        value,
        None,
        'Expected one executable command/path, not a shell expression.',
    )


def digest_model(model: Any, caller: str | None = None) -> str:
    if model in ('default', 'alphafold'):
        return model
    _error(
        'model',
        model,
        caller,
        'Expected default or alphafold; arbitrary executable Groovy configurations are not admitted.',
    )


def digest_backend(backend: Any, caller: str | None = None) -> str:
    if isinstance(backend, str):
        return backend.lower()
    _error('backend', backend, caller, 'Expected an original backend string.')


def digest_weight_function(weight_function: Any, caller: str | None = None) -> str:
    allowed = ('VoronoiScale', 'LengthAndRadius', 'Length', 'Constant')
    if isinstance(weight_function, str):
        for name in allowed:
            if name.lower() == weight_function.lower():
                return name
    _error(
        'weight_function',
        weight_function,
        caller,
        f'Expected a MOLE weight function in {allowed}.',
    )


def _boolean(name: str):
    def admit(value: Any, caller: str | None = None) -> bool:
        if type(value) is bool:
            return value
        _error(name, value, caller, 'Expected a literal boolean.')

    return admit


def digest_min_depth(min_depth: Any, caller: str | None = None) -> int:
    if (
        isinstance(min_depth, Integral)
        and not isinstance(min_depth, bool)
        and int(min_depth) >= 0
    ):
        return int(min_depth)
    _error(
        'min_depth',
        min_depth,
        caller,
        'Expected a nonnegative tetrahedron depth integer.',
    )


def _backend_rule(provider: str):
    def admit(value: Any, context: Context) -> str:
        allowed = {'files', 'library' if provider == 'pykvfinder' else 'cli'}
        if value in allowed:
            return value
        _error(
            'backend',
            value,
            context.function_name,
            f'Expected an original route in {sorted(allowed)}.',
        )

    return admit


for _provider in PARAMETERS:
    register_pipeline(kind='original_provider', name=_provider)(
        _backend_rule(_provider)
    )


def _length(name: str):
    return lambda value, caller=None: scalar(
        value,
        name,
        'angstroms',
        zero=name
        in {
            'removal_distance',
            'min_depth_length',
            'min_tunnel_length',
            'min_pore_length',
            'origin_radius',
            'bottleneck_radius',
            'bottleneck_tolerance',
        },
    )


def _integer(name: str):
    return lambda value, caller=None: positive_integer(value, name)


def _path(name: str):
    return lambda value, caller=None: (
        digest_path(value, name, caller).expanduser().resolve()
    )


def _command(name: str):
    return lambda value, caller=None: command(value, name)


ARGUMENT_DIGESTERS = {
    'backend': digest_backend,
    'molecular_system': digest_molecular_system,
    'selection': digest_selection,
    'structure_indices': digest_structure_indices,
    'chemical_state': digest_chemical_state,
    'syntax': digest_syntax,
    'origin': digest_origin,
    'include_depth': digest_include_depth,
    'model': digest_model,
    'weight_function': digest_weight_function,
    'min_depth': digest_min_depth,
    **{
        name: _boolean(name)
        for name in (
            'ignore_hetatoms',
            'ignore_hydrogens',
            'compute_pores',
            'compute_merged_pores',
        )
    },
    'timeout': lambda value, caller=None: scalar(value, 'timeout', 'seconds'),
    'volume_cutoff': lambda value, caller=None: scalar(
        value, 'volume_cutoff', 'angstroms**3', zero=True
    ),
    **{
        name: _length(name)
        for name in (
            'step',
            'probe_in',
            'probe_out',
            'removal_distance',
            'grid_width',
            'probe_small',
            'probe_large',
            'probe_radius',
            'shell_radius',
            'shell_depth',
            'interior_threshold',
            'min_depth_length',
            'min_tunnel_length',
            'min_pore_length',
            'surface_cover_radius',
            'origin_radius',
            'bottleneck_radius',
            'bottleneck_tolerance',
            'auto_origin_cover_radius',
        )
    },
    **{
        name: _integer(name)
        for name in (
            'workers',
            'memory_mb',
            'max_grid_points',
            'max_auto_origins_per_cavity',
        )
    },
    **{
        name: _path(name)
        for name in ('bundle_file', 'caver_home', 'p2rank_home', 'upstream_root')
    },
    **{
        name: _command(name)
        for name in ('java_cmd', 'ghecom_cmd', 'python_cmd', 'mole_cmd')
    },
}
OPTIONS = {
    'digestion_source': 'topomt._private.arg_digestion.original_provider_arguments',
    'digestion_style': 'registry',
    'standardizer': None,
    'function_source': 'topomt._private.arg_digestion.function.original_provider',
    'domain_source': 'topomt._private.arg_digestion.domain.original_provider',
}
PIPELINES = {
    provider: {'backend': {'kind': 'original_provider', 'rules': [provider]}}
    for provider in PARAMETERS
}
