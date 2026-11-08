"""Receive the frozen three-case geometry through the actual public dispatcher."""

import hashlib
import json
from pathlib import Path

import molsysmt as msm
import numpy as np
import pytest
from pyunitwizard import QuantityRecord

from topomt import Topography, get_topography
from topomt import pyunitwizard as puw

ROOT = Path(__file__).resolve().parents[1] / 'docs/content/benchlab/synthetic'
CASES = ('regular_tetrahedron', 'closed_shell', 'shell_with_opening')


def values(record, field, unit):
    quantity = QuantityRecord.from_dict(record).to_quantity(field=field, unit=unit)
    return np.asarray(puw.get_value(quantity, to_unit=unit))


def load_case(case):
    directory = ROOT / case
    input_directory = directory / 'artifacts' / f'{case}_v1'
    fixture = json.loads((input_directory / 'input.json').read_text())
    native_directory = (
        input_directory
        if case == 'shell_with_opening'
        else directory / 'artifacts/native_study_v1'
    )
    observations = json.loads((native_directory / 'dfnd_observations.json').read_text())
    return directory, fixture, observations


def molecular_input(case):
    directory, fixture, observations = load_case(case)
    if case == 'shell_with_opening':
        source_directory, source_fixture, _ = load_case('closed_shell')
        selection = fixture['derivation']['parent_atom_indices']
    else:
        source_directory, source_fixture = directory, fixture
        selection = list(range(len(fixture['atom_radii']['values'])))
    source_case = 'closed_shell' if case == 'shell_with_opening' else case
    pdb = source_directory / 'artifacts' / f'{source_case}_v1' / 'input.pdb'
    system = msm.convert(str(pdb), to_form='molsysmt.MolSys')
    # PDB supplies dummy topology only; do not qualify its rounded coordinates.
    coords = values(source_fixture['coordinates'], 'coordinates', 'angstroms')
    msm.set(system, coordinates=puw.quantity(coords[None], 'angstroms'))
    received = msm.physchem.get_atomic_radius(
        system, element='atom', selection=selection, definition='vdw'
    )
    np.testing.assert_allclose(
        puw.get_value(received, to_unit='angstroms'),
        values(fixture['atom_radii'], 'atom_radii', 'angstroms'),
        rtol=0,
        atol=1e-14,
    )
    query = {
        key: QuantityRecord.from_dict(value).to_quantity(field=key, unit='angstroms')
        if isinstance(value, dict)
        else value
        for key, value in observations['query'].items()
    }
    query['epsilon'] = QuantityRecord.from_dict(fixture['epsilon']).to_quantity(
        field='epsilon', unit='angstroms'
    )
    return system, selection, fixture, observations, query


def public_result(case, probe, min_size=0):
    system, selection, fixture, observations, query = molecular_input(case)
    topo = get_topography(
        system,
        method='dfnd',
        selection=selection,
        probe_radius=puw.quantity(float(probe), 'angstroms'),
        **{**query, 'min_size': min_size},
    )
    return topo, fixture, observations


@pytest.mark.parametrize('case', CASES)
@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_public_three_case_projection_retains_native_catalog_and_relations(
    case, policy
):
    _, _, observations = load_case(case)
    with puw.context(standard_units=[*policy, 'radians']):
        for anchor in observations['anchors']:
            probe = float(values(anchor['probe_radius'], 'probe_radius', 'angstroms'))
            topo, fixture, _ = public_result(case, probe)
            assert isinstance(topo, Topography)
            np.testing.assert_allclose(
                puw.get_value(topo.input_context.coordinates, to_unit='angstroms'),
                values(fixture['coordinates'], 'coordinates', 'angstroms'),
                rtol=0,
                atol=1e-13,
            )
            np.testing.assert_allclose(
                puw.get_value(topo.input_context.radii, to_unit='angstroms'),
                values(fixture['atom_radii'], 'atom_radii', 'angstroms'),
                rtol=0,
                atol=1e-14,
            )
            mapping = fixture.get('derivation', {}).get(
                'parent_atom_indices', list(range(len(fixture['atom_radii']['values'])))
            )
            assert topo.input_context.atom_indices.tolist() == mapping
            raw = topo.dfnd.raw
            assert len(raw['wet_components']) == anchor['raw_component_count']
            features = [
                feature for feature in topo.values() if feature.dimensionality == 2
            ]
            mouths = topo.get_features(by='type', value='mouth')
            assert len(features) == sum(anchor['reported_counts'].values())
            for feature in topo.values():
                assert feature.topography is topo
                assert feature in topo.get_features(
                    by='type', value=feature.feature_type
                )
                assert feature in topo.get_features(
                    by='shape', value=feature.shape_type
                )
                assert feature in topo.get_features(
                    by='dimensionality', value=feature.dimensionality
                )
            for feature in features:
                assert (
                    type(feature).__name__
                    == {
                        'void': 'Void',
                        'pocket': 'Pocket',
                        'channel': 'Channel',
                        'percolating': 'Percolating',
                        'open_concavity': 'OpenConcavity',
                        'groove': 'Groove',
                        'cleft': 'Cleft',
                    }[feature.feature_type]
                )
                component = topo.dfnd.dfn.components[feature.component_id]
                assert feature.family == component.family
                assert (
                    feature.feature_type
                    == feature.classification['name']
                    == component.classification['name']
                )
                assert feature.signature == component.signature
                assert (
                    feature.source_id
                    == feature.component_key
                    == component.component_key
                )
                assert feature.support_key == component.support_key
                assert feature.atom_indices == component.atom_indices
                expected_mouths = (
                    component.n_mouths if feature.family in ('pocket', 'channel') else 0
                )
                children = topo.children_of(feature.feature_id)
                assert len(children) == expected_mouths
                assert children == {
                    m for m in mouths if m.parent_component_key == feature.component_key
                }
                if feature.feature_type == 'percolating':
                    assert feature.shape_type == 'neutral' and not children
                else:
                    assert feature.shape_type == 'concavity'
                assert (
                    puw.get_value(
                        feature.volume_solvent_estimate, to_unit='angstroms**3'
                    )
                    >= 0
                )
                for mouth in children:
                    assert mouth.dimensionality == 1 and mouth.shape_type == 'boundary'
                    assert topo.parents_of(mouth.feature_id) == {feature}
                    assert feature.feature_id in mouth.surfaces
                    assert mouth.feature_id in feature.boundaries
                    assert mouth.component_key == feature.component_key
                    assert set(mouth.atom_indices) <= set(mapping)
                    assert puw.get_value(mouth.area, to_unit='angstroms**2') > 0
                    assert (
                        puw.get_value(mouth.R_gate_min, to_unit='angstroms')
                        >= probe - 1e-6
                    )
            if not raw['wet_components']:
                assert not topo and not mouths
                assert (
                    topo.dfnd.mesh.tetrahedra
                )  # Empty public result retains the substrate.


@pytest.mark.parametrize(
    'case,probe',
    [('regular_tetrahedron', 1.4), ('closed_shell', 1.4), ('shell_with_opening', 1.4)],
)
def test_public_reporting_hides_features_and_mouths_without_changing_support(
    case, probe
):
    before, _, _ = public_result(case, probe)
    cutoff = max(c['n_nodes'] for c in before.dfnd.raw['wet_components']) + 1
    filtered, _, _ = public_result(case, probe, min_size=cutoff)
    assert not filtered
    assert (
        filtered.dfnd.raw['parameters']['result_key']
        == before.dfnd.raw['parameters']['result_key']
    )
    for old, new in zip(
        before.dfnd.raw['wet_components'],
        filtered.dfnd.raw['wet_components'],
        strict=True,
    ):
        assert old['tetrahedron_ids'] == new['tetrahedron_ids']
        assert old['support_key'] == new['support_key']
        assert old['component_key'] == new['component_key']


@pytest.mark.parametrize('case', CASES)
def test_public_receiving_record_is_versioned_and_preserves_earlier_evidence(case):
    directory, _, native = load_case(case)
    data = directory / 'artifacts/public_topography_v1'
    protocol = json.loads((data / 'protocol.json').read_text())
    report = json.loads((data / 'report.json').read_text())
    for relative, digest in protocol['preserved_files'].items():
        assert (
            hashlib.sha256((ROOT.parent / relative).read_bytes()).hexdigest() == digest
        )
    assert (
        report['protocol_sha256']
        == hashlib.sha256((data / 'protocol.json').read_bytes()).hexdigest()
    )
    assert report['receiving_checks'] == 'passed'
    assert len(report['anchors']) == 3
    for row, anchor in zip(report['anchors'], native['anchors'], strict=True):
        assert row['probe_radius'] == anchor['probe_radius']
        assert row['raw_wet_component_count'] == anchor['raw_component_count']
        regions = [f for f in row['features'] if f['legacy_dimensionality'] == 2]
        assert len(regions) == sum(anchor['reported_counts'].values())
        by_id = {f['feature_id']: f for f in row['features']}
        for feature in row['features']:
            assert feature['feature_id'] in by_id
            for parent in feature['parent_feature_ids']:
                assert feature['feature_id'] in by_id[parent]['child_feature_ids']
            for child in feature['child_feature_ids']:
                assert feature['feature_id'] in by_id[child]['parent_feature_ids']
            if feature['feature_type'] == 'mouth':
                assert feature['python_class'] == 'Mouth'
                assert len(feature['parent_feature_ids']) == 1
                assert (
                    float(
                        values(
                            feature['area_geometric'], 'area_geometric', 'angstroms**2'
                        )
                    )
                    > 0
                )
            else:
                assert feature['feature_type'] == feature['classification']['name']
                assert (
                    float(
                        values(
                            feature['volume_solvent_estimate'],
                            'volume_solvent_estimate',
                            'angstroms**3',
                        )
                    )
                    >= 0
                )
