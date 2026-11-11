"""Original specialist-provider contracts; no detector execution is mocked as science."""

import importlib

import pytest

import topomt as tmt
from tests.methods.pycasta.test_input_context import source
from tests.test_new_provider_parsers import captured
from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError
from topomt.third_party.output import ProviderOutput, ProviderRecord

__all__ = ['source']


@pytest.mark.parametrize(
    'kind,collection', [('region', 'regions'), ('interface', 'interfaces')]
)
def test_specialist_records_keep_distinct_scientific_collections(
    tmp_path, kind, collection
):
    run = captured(tmp_path, 'contract_fixture', {'original.txt': 'protocol fixture'})
    record = ProviderRecord('reported-1', kind, run)
    output_type = type(
        'SpecialistOutput', (ProviderOutput,), {'provider': run.provider}
    )
    result = output_type(run, (record,))
    assert getattr(result, collection) == (record,)
    assert result.pockets == result.cavities == result.channels == result.sites == ()


@pytest.mark.parametrize(
    'provider,backend', [('hole', 'cli'), ('povme', 'library'), ('pisa', 'cli')]
)
def test_specialist_methods_are_selected_without_importing_scientific_engines(
    provider, backend
):
    from topomt._private.arg_digestion.provider_dispatch import DEFAULT_BACKENDS

    assert DEFAULT_BACKENDS[provider] == backend
    api = importlib.import_module(f'topomt.third_party.{provider}.api')
    assert callable(api.get_output)


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_hole_fixed_units_and_steering_are_owned_by_argdigest(
    source, monkeypatch, policy
):
    execution = importlib.import_module('topomt.third_party._execution')
    seen = []
    monkeypatch.setattr(execution, 'get_output', lambda *args: seen.append(args))
    with puw.context(standard_units=policy):
        tmt.get_provider_output(
            source,
            method='hole',
            origin=puw.quantity([0.1, 0.2, 0.3], 'nm'),
            direction=[0, 0, 2],
            sample_step=puw.quantity(50, 'pm'),
            end_radius=puw.quantity(0.7, 'nm'),
            random_seed=12345,
        )
    options = seen[0][3]
    assert options['origin'] == pytest.approx([1, 2, 3])
    assert options['direction'] == pytest.approx([0, 0, 1])
    assert options['sample_step'] == pytest.approx(0.5)
    assert options['end_radius'] == pytest.approx(7.0)


@pytest.mark.parametrize(
    'provider,options',
    [
        ('hole', {'direction': [0, 0, 0]}),
        ('hole', {'sample_step': puw.quantity(1, 'ps')}),
        ('hole', {'random_seed': -1}),
        ('hole', {'workers': 2}),
        ('povme', {'workers': 2}),
        ('povme', {'inclusion_regions': []}),
        (
            'povme',
            {
                'inclusion_regions': [
                    {'shape': 'sphere', 'center': [0, 0, 0], 'radius': -1}
                ]
            },
        ),
        ('pisa', {'workers': 2}),
    ],
)
def test_specialist_invalid_options_fail_before_execution(
    source, monkeypatch, provider, options
):
    execution = importlib.import_module('topomt.third_party._execution')
    monkeypatch.setattr(
        execution,
        'get_output',
        lambda *args, **kwargs: pytest.fail('Invalid arguments reached execution'),
    )
    with pytest.raises(ArgumentError) as caught:
        tmt.get_provider_output(source, method=provider, **options)
    assert next(iter(options)) in str(caught.value)
