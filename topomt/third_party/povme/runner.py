"""Bound a selected external POVME Python worker and capture its original files."""

import hashlib
import json
import math
import sys
from pathlib import Path

from depdigest import dep_digest

from topomt._private.arg_digestion.external_arguments import _error
from topomt.third_party._execution import (
    ProviderExecutionError,
    ProviderUnavailableError,
    executable_command,
    file_identity,
    run_command,
)
from topomt.third_party._specialist import failure_evidence


@dep_digest('povme', when={'upstream_root': None, 'python_cmd': None})
def _require_engine(
    *, upstream_root=None, python_cmd=None, pymolecule_root=None
) -> None:
    for name, root, module in [
        ('upstream_root', upstream_root, 'povme'),
        ('pymolecule_root', pymolecule_root, 'pymolecule'),
    ]:
        if root is not None and not (Path(root) / module / '__init__.py').is_file():
            raise ProviderUnavailableError(
                provider='povme', requirement=f'{name} containing {module}'
            )
    executable_command('povme_python', python_cmd or sys.executable)


def ensure_available(options: dict) -> None:
    _require_engine(
        **{
            name: options.get(name)
            for name in ['upstream_root', 'python_cmd', 'pymolecule_root']
        }
    )


def configuration(options: dict) -> dict:
    """Translate ROI controls into original Pydantic fields in fixed angstroms."""
    config = {
        'grid_spacing': options.get('grid_step', 1.0),
        'distance_cutoff': options.get('distance_cutoff', 1.09),
        'convex_hull_exclusion': options.get('convex_hull_exclusion', True),
        'contiguous_points_criteria': options.get('contiguous_points_criteria', 4),
        'use_ray': False,
        'n_cores': 1,
        'save_points': True,
        'save_individual_pocket_volumes': True,
    }
    for option, prefix in [
        ('inclusion_regions', 'points_inclusion'),
        ('exclusion_regions', 'points_exclusion'),
        ('seed_regions', 'contiguous_pocket_seed'),
    ]:
        for shape in ['sphere', 'box']:
            config[prefix + '_' + shape] = [
                {key: value for key, value in region.items() if key != 'shape'}
                for region in options.get(option, [])
                if region['shape'] == shape
            ]
    return config


def region_budget(config: dict, options: dict, n_atoms: int) -> dict:
    """Bound original mesh generation and worst-case KD-tree neighbor storage."""
    total = 0
    included = 0
    step = config['grid_spacing']
    for key, regions in config.items():
        if not isinstance(regions, list):
            continue
        for region in regions:
            lengths = (
                [2 * region['radius']] * 3 if 'radius' in region else region['lengths']
            )
            ratios = [length / step for length in lengths]
            if not all(math.isfinite(ratio) for ratio in ratios):
                _error(
                    'max_grid_points',
                    options.get('max_grid_points'),
                    None,
                    'Region grid dimensions exceed finite arithmetic.',
                )
            estimate = math.prod(math.ceil(ratio) + 3 for ratio in ratios)
            total += estimate
            if key.startswith('points_inclusion'):
                included += estimate
    if total > options.get('max_grid_points', 250000):
        _error(
            'max_grid_points',
            options.get('max_grid_points', 250000),
            None,
            f'Conservative original region grid estimate {total} exceeds the explicit budget.',
        )
    pairs = included * n_atoms
    if pairs > options.get('max_candidate_pairs', 10000000):
        _error(
            'max_candidate_pairs',
            options.get('max_candidate_pairs', 10000000),
            None,
            f'Worst-case original atom/grid neighbor count {pairs} exceeds the explicit budget.',
        )
    return {
        'grid_points_upper_estimate': total,
        'candidate_pairs_upper_estimate': pairs,
    }


def run(pdb: Path, output: Path, options: dict) -> tuple[dict, dict]:
    config = configuration(options)
    n_atoms = sum(
        line.startswith(('ATOM  ', 'HETATM')) for line in pdb.read_text().splitlines()
    )
    budget = region_budget(config, options, n_atoms)
    config_file = output / 'configuration.json'
    config_file.write_text(json.dumps(config, allow_nan=False))
    request = output.parent / 'povme_request.json'
    request.write_text(
        json.dumps(
            {
                'input': str(pdb),
                'output': str(output),
                'configuration': str(config_file),
                'upstream_root': str(options['upstream_root'])
                if options.get('upstream_root') is not None
                else None,
                'pymolecule_root': str(options['pymolecule_root'])
                if options.get('pymolecule_root') is not None
                else None,
            }
        )
    )
    interpreter = executable_command(
        'povme_python', options.get('python_cmd', sys.executable)
    )
    command = [interpreter, str(Path(__file__).with_name('worker.py')), str(request)]
    context = {
        'interpreter': file_identity(Path(interpreter)),
        'command': command,
        'workers': 1,
        'timeout': {'value': options.get('timeout', 120), 'unit': 'seconds'},
        'resources': {
            **budget,
            'max_grid_points': options.get('max_grid_points', 250000),
            'max_candidate_pairs': options.get('max_candidate_pairs', 10000000),
        },
        'input_fingerprints': {
            'configuration.json': hashlib.sha256(config_file.read_bytes()).hexdigest()
        },
    }
    additional = {'configuration.json': config_file}
    with failure_evidence(context, additional):
        code = run_command(
            command,
            output,
            timeout=options.get('timeout', 120),
            workers=1,
            allowed_returncodes=(0, 66),
            provider='povme',
        )
        if code == 66:
            missing = json.loads((output / 'missing_dependency.json').read_text())
            raise ProviderUnavailableError(
                provider='povme',
                requirement=f'Selected interpreter dependency: {missing["module"]}',
            )
        try:
            identity = json.loads((output / 'engine_identity.json').read_text())
            if identity['status'] != 'completed':
                raise ValueError('No successful original completion receipt')
        except (ValueError, OSError, KeyError) as cause:
            raise ProviderExecutionError(
                provider='povme',
                reason=f'Original worker completion was not established: {cause}',
            ) from cause
    return {**identity, **context}, additional
