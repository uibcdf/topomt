"""Native length options have real value contracts at the public dispatcher."""

import warnings

import pytest

from tests.test_benchlab_public_topography import molecular_input
from topomt import get_topography
from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError
from topomt.dfnd import DFNDMeshConfig


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_explicit_dfnd_radii_model_has_a_digester_and_preserves_geometry(policy):
    system, selection, fixture, _, query = molecular_input('regular_tetrahedron')
    with puw.context(standard_units=[*policy, 'radians']):
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter('always')
            topo = get_topography(
                system,
                method='dfnd',
                selection=selection,
                radii_model='vdw',
                probe_radius=puw.quantity(1.4, 'angstroms'),
                **query,
            )
        assert not any('No digester is registered' in str(w.message) for w in captured)
        assert topo.dfnd.network.mesh_config.radii_model == 'vdw'
        assert topo.dfnd.network.atom_radii * 10 == pytest.approx(
            fixture['atom_radii']['values']
        )
        assert len(topo.get_features(by='type', value='void')) == 1


@pytest.mark.parametrize('model', ['vdw', 'protor', 'provided'])
def test_radii_model_digester_preserves_the_inner_config_contract(model):
    from topomt._private.arg_digestion.argument.radii_model import digest_radii_model

    assert (
        digest_radii_model(model, method='dfnd')
        == DFNDMeshConfig(radii_model=model).radii_model
    )


@pytest.mark.parametrize('model', ['VDW', 'unknown', None, 1, ['vdw'], {'vdw': True}])
def test_invalid_dfnd_radii_model_reports_the_public_argument(model):
    system, selection, _, _, _ = molecular_input('regular_tetrahedron')
    with pytest.raises(ArgumentError, match='radii_model'):
        get_topography(system, selection=selection, method='dfnd', radii_model=model)


@pytest.mark.parametrize('model', ['castp_param', 'castp1_pdb2alf', 'protor'])
@pytest.mark.parametrize(
    'selector',
    [{'method': 'castp'}, {'engine': 'castp'}, {'method': 'dfnd', 'engine': 'castp'}],
)
def test_other_radius_models_keep_their_own_dispatch_contract(
    monkeypatch, model, selector
):
    import importlib

    dispatcher = importlib.import_module('topomt.get_topography')
    received = []

    def receive(topo, **kwargs):
        received.append(kwargs['radii_model'])
        return topo

    # Only test admission/forwarding here; this is not CASTp execution evidence.
    monkeypatch.setattr(dispatcher, '_run_castp', receive)
    system, selection, _, _, _ = molecular_input('regular_tetrahedron')
    get_topography(system, selection=selection, radii_model=model, **selector)
    assert received == [model]


@pytest.mark.parametrize('model', ['castp_param', ['vdw']])
@pytest.mark.parametrize(
    'selector',
    [{'engine': 'dfnd'}, {'method': 'castp', 'engine': 'dfnd'}, {'method': 'DFND'}],
)
def test_dfnd_radius_validation_follows_dispatch_aliases(model, selector):
    system, selection, _, _, _ = molecular_input('regular_tetrahedron')
    with pytest.raises(ArgumentError, match='radii_model'):
        get_topography(system, selection=selection, radii_model=model, **selector)


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_explicit_dfnd_lengths_have_digesters_and_preserve_the_probe_model(policy):
    system, selection, _, _, query = molecular_input('regular_tetrahedron')
    with puw.context(standard_units=[*policy, 'radians']):
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter('always')
            topo = get_topography(
                system,
                method='dfnd',
                selection=selection,
                probe_radius=puw.quantity(0.14, 'nm'),
                **query,
            )
        assert not any('No digester is registered' in str(w.message) for w in captured)
        assert len(topo.get_features(by='type', value='void')) == 1
        raw = topo.dfnd.raw['parameters']
        assert raw['mesh_config']['epsilon'] == pytest.approx(1e-7)
        assert (
            raw['query']['residence_tolerance']
            == raw['query']['permeability_tolerance']
            == 0
        )


@pytest.mark.parametrize(
    'name', ['epsilon', 'residence_tolerance', 'permeability_tolerance']
)
@pytest.mark.parametrize('value', [-1.0, float('inf'), [0.1, 0.2]])
def test_invalid_dfnd_length_names_are_reported_at_the_public_boundary(name, value):
    system, selection, _, _, query = molecular_input('regular_tetrahedron')
    with pytest.raises(ArgumentError) as caught:
        get_topography(
            system,
            method='dfnd',
            selection=selection,
            probe_radius=puw.quantity(1.4, 'angstroms'),
            **{**query, name: value},
        )
    assert name in str(caught.value)


def test_dispatch_preserves_legacy_angstrom_conversion_and_its_warning():
    system, selection, _, _, query = molecular_input('regular_tetrahedron')
    with pytest.warns(FutureWarning):
        topo = get_topography(
            system,
            method='dfnd',
            selection=selection,
            probe_radius=puw.quantity(1.4, 'angstroms'),
            **{
                **query,
                'epsilon': 1e-6,
                'residence_tolerance': 0.01,
                'permeability_tolerance': 0.01,
            },
        )
    raw = topo.dfnd.raw['parameters']
    assert raw['mesh_config']['epsilon'] == pytest.approx(1e-7)
    assert raw['query']['residence_tolerance'] == pytest.approx(0.001)
    assert raw['query']['permeability_tolerance'] == pytest.approx(0.001)


@pytest.mark.parametrize(
    'name', ['epsilon', 'residence_tolerance', 'permeability_tolerance']
)
def test_wrong_dimensional_quantity_reports_the_native_argument(name):
    system, selection, _, _, query = molecular_input('regular_tetrahedron')
    with pytest.raises(ArgumentError) as caught:
        get_topography(
            system,
            method='dfnd',
            selection=selection,
            probe_radius=puw.quantity(1.4, 'angstroms'),
            **{**query, name: puw.quantity(1, 'ps')},
        )
    assert name in str(caught.value)
