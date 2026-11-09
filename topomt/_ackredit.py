"""Deferred optional attribution at successful scientific boundaries.

Applications own Ackredit sessions. The small host ledger retains our explicit
declarations when the optional recorder is absent or fails; it does not inspect
the provider registry, infer execution from imports, or implement a renderer.
"""

import json
import logging
import sys
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache, wraps
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Optional

from depdigest import dep_digest, is_installed

_active: ContextVar[tuple] = ContextVar('topomt_attribution', default=())
SCHEMA = 'topomt.scientific_attribution@1'

_METHODS = {
    'fpocket': ('fpocket',),
    'fpocket_druggability': ('fpocket_druggability',),
    'pocketeer': ('fpocket',),  # Upstream explicitly requests this article.
    'alphaspace2': ('alphaspace2',),
    'pycasta': ('pycasta', 'cast'),
    'castp': ('cast',),
    'castp3': ('castp3', 'cast'),
    'castpfold': ('castpfold', 'cast'),
    'pykvfinder': ('pykvfinder',),
    'ghecom': ('ghecom',),
    'caver': ('caver',),
    'p2rank': ('p2rank',),
    'mole': ('mole',),
    'dfnd': (),  # No published DFND paper exists; cite the executed software.
    'geometry': (),
    'qhull': ('qhull',),
    'numpy': ('numpy',),
    'scipy': ('scipy',),
    'numba': ('numba',),
    'vina': ('vina',),
    'sasa': ('shrake_rupley',),
    'biotite': ('biotite',),
    'biotite_sasa': ('biotite', 'shrake_rupley'),
    'mdtraj': ('mdtraj',),
    'mdtraj_sasa': ('mdtraj', 'shrake_rupley'),
    'marching_cubes': ('marching_cubes', 'skimage'),
    'sklearn': ('sklearn',),
    'networkx': ('networkx',),
    'dijkstra': ('dijkstra',),
    'brandes': ('brandes',),
}
_URLS = {
    'fpocket': 'https://github.com/Discngine/fpocket',
    'pocketeer': 'https://github.com/cch1999/pocketeer',
    'alphaspace2': 'https://github.com/RedesignScience/AlphaSpace2',
    'pycasta': 'https://github.com/giorgioluciano/pycasta',
    'castp': 'https://sts.bioe.uic.edu/castp/',
    'castp3': 'https://sts.bioe.uic.edu/castp/',
    'castpfold': 'https://cfold.bme.uic.edu/castpfold/',
    'pykvfinder': 'https://github.com/LBC-LNBio/pyKVFinder',
    'ghecom': 'https://pdbj.org/ghecom/',
    'caver': 'https://www.caver.cz/',
    'p2rank': 'https://github.com/rdk/p2rank',
    'mole': 'https://github.com/sb-ncbr/webchemistry',
    'numpy': 'https://numpy.org/',
    'scipy': 'https://scipy.org/',
    'numba': 'https://numba.pydata.org/',
    'biotite': 'https://www.biotite-python.org/',
    'mdtraj': 'https://mdtraj.org/',
    'sklearn': 'https://scikit-learn.org/',
    'networkx': 'https://networkx.org/',
    'skimage': 'https://scikit-image.org/',
    'qhull': 'https://www.qhull.org/',
}


@dep_digest('ackredit')
def _load_backend():
    import ackredit

    return ackredit


def backend():
    """Load the optional recorder only at an explicit attribution boundary."""
    try:
        return _load_backend() if is_installed('ackredit') else None
    except ModuleNotFoundError as error:
        if error.name == 'ackredit':
            return None
        raise


def _failed(operation: str, error: Exception) -> None:
    from ._private.smonitor.emitter import warn
    from ._private.smonitor.warnings import AttributionTrackingWarning

    try:
        reason = f'{type(error).__name__}: {error}'
    except Exception:
        reason = type(error).__name__
    diagnostic = AttributionTrackingWarning(
        extra={'operation': operation, 'reason': reason}
    )
    try:
        warn(diagnostic)
    except Exception as failure:
        # A promoted instance has already emitted its catalog event. Attribution
        # is optional even when the application promotes that warning to an error.
        if failure is not diagnostic:
            logging.getLogger('topomt.attribution').warning(
                'AttributionTrackingWarning during %s: %s',
                operation,
                reason,
                extra={'code': 'AttributionTrackingWarning', 'operation': operation},
            )


def _producer() -> dict:
    from ._version import __version__

    return {'name': 'TopoMT', 'version': __version__}


@lru_cache(maxsize=None)
def _installed_version(distribution: str) -> Optional[str]:
    try:
        return version(distribution)
    except PackageNotFoundError:
        return None


def _references(method: str, route: str, target: str, metadata: dict) -> list[dict]:
    from ._bibliography import ARTICLES

    producer = _producer()
    software = {
        'biotite_sasa': 'biotite',
        'mdtraj_sasa': 'mdtraj',
        'marching_cubes': 'skimage',
    }.get(method, method)
    native = route in ('native', 'topomt', 'criterion')
    if not native:
        software = {
            'dijkstra': 'networkx',
            'brandes': 'networkx',
            'fpocket_druggability': 'fpocket',
        }.get(method, software)
    observed_version = metadata.get('version') or metadata.get('distribution_version')
    if (
        not native
        and observed_version is None
        and software
        in (
            'numpy',
            'scipy',
            'numba',
            'biotite',
            'mdtraj',
            'sklearn',
            'networkx',
            'skimage',
        )
    ):
        observed_version = _installed_version(
            'scikit-learn' if software == 'sklearn' else software
        )
    context = {
        'method': method,
        'route': route,
        'software': 'TopoMT' if native else software,
        'version': producer['version'] if native else observed_version,
        'producer': producer,
        'identity': deepcopy(metadata),
    }
    host = {
        'id': f'topomt:software:{producer["version"]}',
        'type': 'software',
        'title': 'TopoMT',
        'version': producer['version'],
        'url': 'https://github.com/uibcdf/topomt',
        'authors': ['Diego Prada-Gracia', 'Liliana M. Moreno-Vargas'],
    }
    entries = [
        {
            'item': host,
            'target': target,
            'roles': ['executed_software'],
            'context': {
                **context,
                'software': 'TopoMT',
                'version': producer['version'],
            },
        }
    ]
    for key in _METHODS[method]:
        entries.append(
            {
                'item': deepcopy(ARTICLES[key]),
                'target': target,
                'roles': [
                    'scientific_criterion'
                    if native
                    or key
                    in (
                        'cast',
                        'shrake_rupley',
                        'dijkstra',
                        'brandes',
                        'marching_cubes',
                        'fpocket_druggability',
                    )
                    else 'software_description'
                ],
                'context': deepcopy(context),
            }
        )
    if native and method != 'sasa':
        entries.extend(_references('numpy', 'original', target, {}))
    if method == 'qhull':
        entries.extend(_references('scipy', 'original', target, {}))
    if method in ('dijkstra', 'brandes') and route == 'original':
        entries.extend(_references('networkx', 'original', target, {}))
    if software in _URLS:
        # An unknown version remains unknown. Content fingerprints, if supplied
        # by the engine adapter, distinguish it from another unidentified build.
        identity = json.dumps(metadata, sort_keys=True, allow_nan=False)
        import hashlib

        suffix = (
            str(observed_version)
            if observed_version
            else 'unreported-' + hashlib.sha256(identity.encode()).hexdigest()[:16]
        )
        item = {
            'id': f'topomt:reference:{software}:{suffix}',
            'type': 'software',
            'title': software,
            'url': _URLS[software],
        }
        if observed_version:
            item['version'] = str(observed_version)
        entries.append(
            {
                'item': item,
                'target': target,
                'roles': [
                    'reference_implementation' if native else 'executed_software'
                ],
                'context': {
                    **context,
                    'software': software,
                    'version': observed_version,
                },
            }
        )
    return entries


def _metadata(result: Any) -> dict:
    run = getattr(result, 'run', None)
    if run is None:
        runs = getattr(result, 'provider_runs', {})
        if len(runs) == 1:
            run = next(iter(runs.values()))
    if run is None:
        return {}
    # Preserve the adapter's original execution identity, never the reader's
    # currently installed upstream version. Inputs/coordinates are not copied.
    return {
        key: value
        for key, value in run.metadata.items()
        if key
        in (
            'version',
            'distribution_version',
            'version_tag',
            'executable_sha256',
            'source_sha256',
            'api_sha256',
            'snapshot_source_sha256',
            'executable',
            'engine_jar',
            'distribution_files',
            'source_revision',
            'package_source',
        )
    }


def _fpocket_druggability_reported(result: Any) -> bool:
    """Detect accepted original score evidence; do not infer it from imports."""
    run = getattr(result, 'run', None)
    runs = (run,) if run is not None else getattr(result, 'provider_runs', {}).values()
    return any(
        name.endswith('_info.txt')
        and (b'Druggability Score' in data or b'Drug Score' in data)
        for run in runs
        for name, data in run.artifacts
    )


@contextmanager
def operation(method: str, *, route: str = 'native', target: Optional[str] = None):
    """Record successful work without taking ownership of scientific exceptions."""
    if method not in _METHODS:
        raise ValueError(f'Undeclared scientific attribution method: {method}')
    target = target or f'topomt.{method}'
    state: dict[str, Any] = {
        'references': {},
        'status': 'unavailable',
        'result': None,
        'ackredit': None,
    }
    parents = _active.get()
    token = _active.set((*parents, state))
    provider = capture = scope = None
    try:
        try:
            provider = backend()
            if provider is not None:
                pending = provider.capture(target, context={'producer': _producer()})
                pending.__enter__()
                capture = pending
                pending = provider.scope(target)
                pending.__enter__()
                scope = pending
                state['status'] = 'recorded'
        except Exception as error:
            state['status'] = 'failed'
            _failed('start attribution', error)
            provider = None
        try:
            yield state
        except BaseException:
            # Clean up only provider contexts; never swallow/replace science.
            raise
        else:
            refs = _references(method, route, target, _metadata(state['result']))
            if (
                method == 'fpocket'
                and route == 'original'
                and _fpocket_druggability_reported(state['result'])
            ):
                refs.extend(
                    _references(
                        'fpocket_druggability',
                        route,
                        target,
                        _metadata(state['result']),
                    )
                )
            refs.extend(state.get('reused', []))
            state['references'].update(
                {json.dumps(entry, sort_keys=True): entry for entry in refs}
            )
            if provider is not None:
                try:
                    for entry in refs:
                        provider.register_item(**deepcopy(entry['item']))
                        provider.track_item(
                            entry['item']['id'],
                            used_by=entry['target'],
                            roles=entry['roles'],
                            context=deepcopy(entry['context']),
                        )
                except Exception as error:
                    state['status'] = 'failed'
                    _failed('record scientific references', error)
    finally:
        for context in (scope, capture):
            if context is not None:
                try:
                    context.__exit__(*sys.exc_info())
                except Exception as error:
                    state['status'] = 'failed'
                    _failed('finish attribution', error)
        if capture is not None:
            try:
                state['ackredit'] = capture.attribution.to_dict()
            except Exception as error:
                state['status'] = 'failed'
                _failed('snapshot attribution', error)
        _active.reset(token)
        if parents:
            parent = parents[-1]
            parent['references'].update(deepcopy(state['references']))
            if state['status'] == 'failed':
                parent['status'] = 'failed'


def _payload(state: dict) -> dict:
    return {
        'schema': SCHEMA,
        'producer': _producer(),
        'status': state['status'],
        'references': deepcopy(list(state['references'].values())),
        'ackredit': deepcopy(state['ackredit']),
    }


def _attach(result: Any, payload: dict) -> Any:
    from .provider_output import ProviderRun
    from .third_party.output import ProviderOutput

    content = json.dumps(
        payload, sort_keys=True, separators=(',', ':'), allow_nan=False
    )
    if isinstance(result, ProviderOutput):
        run = replace(result.run, attribution_json=content)
        return replace(
            result,
            run=run,
            records=tuple(replace(record, run=run) for record in result.records),
        )
    if isinstance(result, ProviderRun):
        return replace(result, attribution_json=content)
    if isinstance(result, dict):
        result['scientific_attribution'] = deepcopy(payload)
    elif hasattr(result, '__dict__'):
        result._attribution_json = content
        if hasattr(result, 'provider_runs'):
            result.provider_runs = {
                key: replace(run, attribution_json=content)
                for key, run in result.provider_runs.items()
            }
    return result


def attributed(method: str, *, route: str = 'native', retain: bool = True):
    """Decorate a meaningful completed operation, retaining its return contract."""

    def decorate(function):
        target = f'{function.__module__}.{function.__qualname__}'

        @wraps(function)
        def wrapped(*args, **kwargs):
            # Small geometry helpers called inside an already attributed
            # calculation are covered there; do not instrument scalar loops.
            if (
                method == 'geometry'
                and function.__name__ not in ('__init__', '_initialize_geometry')
                and _active.get()
            ):
                return function(*args, **kwargs)
            if (
                function.__name__ == '__init__'
                and (args[1] if len(args) > 1 else kwargs.get('points')) is None
            ):
                return function(*args, **kwargs)
            with operation(method, route=route, target=target) as state:
                result = function(*args, **kwargs)
                state['result'] = result
                if method == 'dfnd' and args:
                    mesh = getattr(args[0], 'mesh', None)
                    saved = attribution_of(args[0]) if mesh is not None else None
                    saved = saved or attribution_of(mesh)
                    if saved:
                        state['reused'] = [
                            {
                                **deepcopy(entry),
                                'target': target,
                                'roles': ['reused_result'],
                                'context': {
                                    **deepcopy(entry['context']),
                                    'relationship': 'reused_geometry',
                                },
                            }
                            for entry in saved['references']
                        ]
            if function.__name__ in ('__init__', '_initialize_geometry'):
                _attach(args[0], _payload(state))
                return result
            if not retain or (method == 'geometry' and isinstance(result, dict)):
                return result
            return _attach(result, _payload(state))

        return wrapped

    return decorate


def original_provider(function):
    """Credit the common original-engine executor while skipping saved readers."""
    from inspect import signature

    parameters = signature(function)

    @wraps(function)
    def wrapped(*args, **kwargs):
        bound = parameters.bind(*args, **kwargs).arguments
        if bound['backend'] == 'files':
            return function(*args, **kwargs)
        with operation(
            bound['provider'], route='original', target='topomt.get_provider_output'
        ) as state:
            result = function(*args, **kwargs)
            state['result'] = result
        return _attach(result, _payload(state))

    return wrapped


def scientific_call(method: str, function, /, *args, **kwargs):
    """Credit a reached backend once within the current meaningful operation.

    Keep external classes/functions themselves intact. Suppression is local to
    this operation, so a new result/capture still observes reused references.
    Failed scientific calls earn no successful backend credit.
    """
    states = _active.get()
    parent = states[-1] if states else None
    if parent is not None and method in parent.get('calls', ()):
        return function(*args, **kwargs)
    route = 'criterion' if method == 'fpocket_druggability' else 'original'
    with operation(method, route=route):
        result = function(*args, **kwargs)
    if parent is not None:
        parent.setdefault('calls', set()).add(method)
    return result


def attribution_of(result: Any) -> Optional[dict[str, Any]]:
    """Read a detached host declaration without loading the optional recorder."""
    if isinstance(result, dict):
        return deepcopy(result.get('scientific_attribution'))
    content = getattr(result, '_attribution_json', None) or getattr(
        result, 'attribution_json', None
    )
    if content is not None:
        return json.loads(content)
    run = getattr(result, 'run', None)
    if run is None:
        runs = getattr(result, 'provider_runs', {})
        if len(runs) == 1:
            run = next(iter(runs.values()))
    return None if run is None else run.attribution
