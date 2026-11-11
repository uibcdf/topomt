"""POVME adapter contracts, separate from original-kernel execution."""

import importlib

import pytest

import topomt as tmt
from tests.methods.pycasta.test_input_context import source
from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError

__all__ = ['source']


def test_povme_roi_units_and_shape_are_canonical_before_execution(source, monkeypatch):
    seen = []
    monkeypatch.setattr(
        importlib.import_module('topomt.third_party._execution'),
        'get_output',
        lambda *args: seen.append(args),
    )
    with puw.context(standard_units=['pm', 'fs']):
        tmt.get_provider_output(
            source,
            method='povme',
            inclusion_regions=[
                {
                    'shape': 'box',
                    'center': puw.quantity([0.1, 0.2, 0.3], 'nm'),
                    'lengths': puw.quantity([0.4, 0.5, 0.6], 'nm'),
                }
            ],
            exclusion_regions=[
                {
                    'shape': 'sphere',
                    'center': puw.quantity([0, 0, 0], 'nm'),
                    'radius': puw.quantity(20, 'pm'),
                }
            ],
            grid_step=puw.quantity(0.1, 'nm'),
            distance_cutoff=0,
        )
    options = seen[0][3]
    assert options['inclusion_regions'][0]['center'] == pytest.approx([1, 2, 3])
    assert options['inclusion_regions'][0]['lengths'] == pytest.approx([4, 5, 6])
    assert options['exclusion_regions'][0]['radius'] == pytest.approx(0.2)
    assert options['grid_step'] == 1
    assert options['distance_cutoff'] == 0


def test_povme_region_budget_rejects_before_worker(tmp_path, monkeypatch):
    runner = importlib.import_module('topomt.third_party.povme.runner')
    monkeypatch.setattr(
        runner,
        'run_command',
        lambda *args, **kwargs: pytest.fail('Over-budget worker launched'),
    )
    source = tmp_path / 'input.pdb'
    source.write_text(
        'ATOM      1  C   ALA A   1       0.000   0.000   0.000  1.00  0.00           C\nEND\n'
    )
    with pytest.raises(ArgumentError, match='max_grid_points'):
        runner.run(
            source,
            tmp_path,
            {
                'inclusion_regions': [
                    {'shape': 'sphere', 'center': [0, 0, 0], 'radius': 100}
                ],
                'max_grid_points': 10,
            },
        )


def test_povme_dense_candidate_budget_rejects_before_worker(tmp_path, monkeypatch):
    runner = importlib.import_module('topomt.third_party.povme.runner')
    monkeypatch.setattr(
        runner,
        'run_command',
        lambda *args, **kwargs: pytest.fail('Dense-candidate worker launched'),
    )
    source = tmp_path / 'input.pdb'
    source.write_text(
        'ATOM      1  C   ALA A   1       0.000   0.000   0.000  1.00  0.00           C\nEND\n'
    )
    with pytest.raises(ArgumentError, match='max_candidate_pairs'):
        runner.run(
            source,
            tmp_path,
            {
                'inclusion_regions': [
                    {'shape': 'sphere', 'center': [0, 0, 0], 'radius': 2}
                ],
                'max_candidate_pairs': 1,
            },
        )


def test_povme_npy_header_cannot_request_an_unbacked_allocation(monkeypatch):
    import io

    import numpy as np

    from topomt.third_party.povme.parser import _points_npy

    stream = io.BytesIO()
    np.lib.format.write_array_header_1_0(
        stream, {'descr': '<f8', 'fortran_order': False, 'shape': (10**12, 3)}
    )
    monkeypatch.setattr(
        np,
        'frombuffer',
        lambda *args, **kwargs: pytest.fail(
            'Unbacked array view/allocation was attempted'
        ),
    )
    with pytest.raises(ValueError, match='header/data'):
        _points_npy(stream.getvalue())


@pytest.mark.parametrize(
    'mutation', ['returned_boolean', 'fractional_count', 'reported_units']
)
def test_povme_original_numeric_types_and_point_units_are_verified(mutation):
    import json
    from dataclasses import replace
    from pathlib import Path

    from topomt.provider_output import ProviderRun
    from topomt.third_party.povme.parser import parse_output

    run = ProviderRun.load(
        Path(__file__).parent / 'data/original_local/povme/povme-empty.zip'
    )
    receipt = json.loads(run.get_artifact('output/engine_identity.json'))
    artifacts = dict(run.artifacts)
    if mutation == 'returned_boolean':
        receipt['original_result']['1'] = False
    elif mutation == 'fractional_count':
        receipt['initial_point_count'] = float(receipt['initial_point_count'])
    else:
        artifacts['output/frame_1.pdb'] = artifacts['output/frame_1.pdb'].replace(
            b'Cubic Angstroms', b'Cubic Nanometers'
        )
    artifacts['output/engine_identity.json'] = json.dumps(receipt).encode()
    with pytest.raises(ValueError):
        parse_output(replace(run, artifacts=tuple(artifacts.items())))
