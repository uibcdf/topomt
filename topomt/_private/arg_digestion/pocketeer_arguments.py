"""Original Pocketeer 0.4 argument contracts and physical protocol units."""

from numbers import Integral
from pathlib import Path
from typing import Any

import numpy as np
from argdigest import register_pipeline
from argdigest.core.context import Context

from topomt import pyunitwizard as puw

from .external_arguments import (
    _error,
    digest_chemical_state,
    digest_molecular_system,
    digest_selection,
    digest_skip_digestion,
    digest_structure_indices,
    digest_syntax,
)

API_CALLER = 'topomt.third_party.pocketeer.api.get_output'
LIBRARY_CALLER = 'topomt.third_party.pocketeer.library.get_topography'
PROVIDER_PARAMETERS = (
    'r_min',
    'r_max',
    'polar_probe_radius',
    'sasa_threshold',
    'merge_distance',
    'min_spheres',
    'ignore_hydrogens',
    'ignore_water',
    'ignore_hetero',
)


def _scalar(
    value: Any,
    argument: str,
    unit: str,
    caller: str | None,
    *,
    allow_zero: bool = False,
) -> float:
    try:
        raw = puw.get_value(value, to_unit=unit) if puw.is_quantity(value) else value
        array = np.asarray(raw)
        if array.ndim == 0 and array.dtype.kind in 'iuf':
            number = float(array)
            if np.isfinite(number) and (number >= 0 if allow_zero else number > 0):
                return number
    except (TypeError, ValueError):
        pass
    _error(
        argument,
        value,
        caller,
        f'Expected a finite {"nonnegative" if allow_zero else "positive"} scalar in {unit} or a compatible quantity.',
    )


def digest_r_min(r_min: Any, caller: str | None = None) -> float:
    return _scalar(r_min, 'r_min', 'angstroms', caller)


def digest_r_max(r_max: Any, caller: str | None = None) -> float:
    return _scalar(r_max, 'r_max', 'angstroms', caller)


def digest_polar_probe_radius(
    polar_probe_radius: Any, caller: str | None = None
) -> float:
    return _scalar(polar_probe_radius, 'polar_probe_radius', 'angstroms', caller)


def digest_sasa_threshold(sasa_threshold: Any, caller: str | None = None) -> float:
    return _scalar(sasa_threshold, 'sasa_threshold', 'angstroms**2', caller)


def digest_merge_distance(merge_distance: Any, caller: str | None = None) -> float:
    # Zero is an explicit no-distance-merge setting accepted by the original API.
    return _scalar(
        merge_distance, 'merge_distance', 'angstroms', caller, allow_zero=True
    )


def digest_min_spheres(min_spheres: Any, caller: str | None = None) -> int:
    if (
        isinstance(min_spheres, Integral)
        and not isinstance(min_spheres, bool)
        and int(min_spheres) > 0
    ):
        return int(min_spheres)
    _error('min_spheres', min_spheres, caller, 'Expected a positive integer.')


def _boolean(value: Any, argument: str, caller: str | None) -> bool:
    if type(value) is bool:
        return value
    _error(argument, value, caller, 'Expected a literal boolean.')


def digest_ignore_hydrogens(ignore_hydrogens: Any, caller: str | None = None) -> bool:
    return _boolean(ignore_hydrogens, 'ignore_hydrogens', caller)


def digest_ignore_water(ignore_water: Any, caller: str | None = None) -> bool:
    return _boolean(ignore_water, 'ignore_water', caller)


def digest_ignore_hetero(ignore_hetero: Any, caller: str | None = None) -> bool:
    return _boolean(ignore_hetero, 'ignore_hetero', caller)


def digest_upstream_root(upstream_root: Any, caller: str | None = None) -> str | None:
    if upstream_root is None:
        return None
    if (
        isinstance(upstream_root, (str, Path))
        and str(upstream_root).strip()
        and '\0' not in str(upstream_root)
    ):
        return str(Path(upstream_root).expanduser().resolve())
    _error(
        'upstream_root',
        upstream_root,
        caller,
        'Expected None or a nonempty source path.',
    )


@register_pipeline(kind='pocketeer', name='radius_range')
def check_radius_range(value: Any, context: Context) -> Any:
    # Both supplied values have been digested before pipelines run. Omitted
    # options retain the original API's defaults without entering run.parameters.
    minimum = context.all_args.get('r_min', 3.0)
    maximum = context.all_args.get('r_max', 6.0)
    if maximum <= minimum:
        _error('r_max', maximum, LIBRARY_CALLER, 'r_max must be greater than r_min.')
    return value


@register_pipeline(kind='pocketeer', name='original_backend')
def digest_original_backend(value: Any, context: Context) -> str:
    if isinstance(value, str) and value.lower() in {'library', 'wrapper'}:
        return value.lower()
    _error(
        'backend', value, API_CALLER, 'Expected library or wrapper for original output.'
    )


@register_pipeline(kind='pocketeer', name='gateway_backend')
def digest_gateway_backend(value: Any, context: Context) -> str:
    if isinstance(value, str) and value.lower() in {'native', 'library', 'wrapper'}:
        return value.lower()
    _error(
        'backend', value, context.function_name, 'Expected native, library or wrapper.'
    )


@register_pipeline(kind='pocketeer', name='skip')
def digest_skip(value: Any, context: Context) -> bool:
    return digest_skip_digestion(value, caller=context.function_name)


ARGUMENT_DIGESTERS = {
    'molecular_system': digest_molecular_system,
    'chemical_state': digest_chemical_state,
    'selection': digest_selection,
    'structure_indices': digest_structure_indices,
    'syntax': digest_syntax,
    'upstream_root': digest_upstream_root,
    'r_min': digest_r_min,
    'r_max': digest_r_max,
    'polar_probe_radius': digest_polar_probe_radius,
    'sasa_threshold': digest_sasa_threshold,
    'merge_distance': digest_merge_distance,
    'min_spheres': digest_min_spheres,
    'ignore_hydrogens': digest_ignore_hydrogens,
    'ignore_water': digest_ignore_water,
    'ignore_hetero': digest_ignore_hetero,
    'skip_digestion': digest_skip_digestion,
}
OPTIONS = {
    'digestion_source': 'topomt._private.arg_digestion.pocketeer_arguments',
    'digestion_style': 'registry',
    'standardizer': None,
    'function_source': 'topomt._private.arg_digestion.function.pocketeer',
    'domain_source': 'topomt._private.arg_digestion.domain.pocketeer',
}
GATEWAY_PIPELINES = {
    'backend': {'kind': 'pocketeer', 'rules': ['gateway_backend']},
    'skip_digestion': {'kind': 'pocketeer', 'rules': ['skip']},
}
ORIGINAL_PIPELINES = {
    **GATEWAY_PIPELINES,
    'backend': {'kind': 'pocketeer', 'rules': ['original_backend']},
}
RADIUS_PIPELINES = {
    name: {'kind': 'pocketeer', 'rules': ['radius_range']}
    for name in ('r_min', 'r_max')
}
