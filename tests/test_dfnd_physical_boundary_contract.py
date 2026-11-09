"""Executable acceptance proposal for #151, before scientific-kernel changes.

Only absence of the proposed view is an expected failure. Once supplied, wrong
counts, incomplete supports or unrelated exceptions must fail normally. These
tests do not reinterpret legacy external-link counts as physical patch counts.
"""

import json

import pytest

from devtools.verify_closed_shell_wall_cover import verify_certificate as verify_closed
from devtools.verify_opening_connectivity import verify_certificate as verify_opened
from devtools.verify_tetrahedron_boundary import (
    verify_certificate as verify_tetrahedron,
)
from tests.test_benchlab_public_topography import ROOT, public_result

CONTROLS = (
    ('regular_tetrahedron', 1.2, 4),
    ('regular_tetrahedron', 1.4, 0),
    ('regular_tetrahedron', 1.7, 0),
    ('closed_shell', 0.2, 0),
    ('shell_with_opening', 1.4, 1),
)


class PhysicalBoundaryViewAbsent(AssertionError):
    """The #151 candidate observation has not been implemented."""


def proposed_view(container, key):
    """Read the candidate view without inventing a zero or reusing face counts."""
    if key not in container:
        raise PhysicalBoundaryViewAbsent(f'#151: {key} is not available')
    return container[key]


@pytest.fixture(scope='module')
def reference_panel():
    results = {}
    for case, folder, verifier in (
        ('regular_tetrahedron', 'boundary_connectivity_v1', verify_tetrahedron),
        ('closed_shell', 'wall_certificate_v1', verify_closed),
        ('shell_with_opening', 'opening_connectivity_v1', verify_opened),
    ):
        directory = ROOT / case / 'artifacts'
        data = directory / folder
        certificate = json.loads((data / 'certificate.json').read_text())
        verified = verifier(
            directory / f'{case}_v1/input.json', data / 'protocol.json', certificate
        )
        assert verified == json.loads((data / 'verification.json').read_text())
        results[case] = verified
    return results


@pytest.fixture(scope='module')
def public_panel():
    return {(case, probe): public_result(case, probe)[0] for case, probe, _ in CONTROLS}


def test_independent_panel_qualifies_four_one_and_zero_boundary_patches(
    reference_panel,
):
    tetrahedron = reference_panel['regular_tetrahedron']
    assert tetrahedron['opening_component_count'] == 4
    assert tetrahedron['origin_connected_patch_count'] == 4
    assert tetrahedron['blocked_edge_count'] == 6
    assert tetrahedron['sealed_control']['opening_component_count'] == 0
    assert not tetrahedron['excluded_control']['has_free_finite_hull_point']
    opened = reference_panel['shell_with_opening']
    assert opened['opening_component_count'] == 1
    assert opened['origin_connected_to_opening']
    closed = reference_panel['closed_shell']
    assert closed['conclusion'] == 'origin_free_and_enclosed'
    assert closed['hull_face_count'] == 140
    # Complete coverage proves zero free hull patches, not zero interior volume.


def test_source_observables_keep_their_discrete_meaning(public_panel):
    tetrahedron = public_panel['regular_tetrahedron', 1.2]
    component = tetrahedron.dfnd.raw['wet_components'][0]
    assert component['n_external_links'] == 1
    assert component['n_wall_faces'] == 0
    assert len(tetrahedron.dfnd.raw['external_links'][0]['faces']) == 4
    assert len(tetrahedron.get_features(by='type', value='percolating')) == 1
    assert not tetrahedron.get_features(by='type', value='mouth')
    opened = public_panel['shell_with_opening', 1.4]
    assert len(opened.get_features(by='type', value='mouth')) == 1
    for case, probe in [('regular_tetrahedron', 1.4), ('closed_shell', 0.2)]:
        assert not public_panel[case, probe].get_features(by='type', value='mouth')
    assert not public_panel['regular_tetrahedron', 1.7].dfnd.raw['wet_components']


@pytest.mark.xfail(
    strict=True,
    raises=PhysicalBoundaryViewAbsent,
    reason='#151: proposed physical-boundary view is not implemented',
)
@pytest.mark.parametrize('case,probe,expected_count', CONTROLS)
def test_proposed_physical_patches_reach_the_actual_raw_result(
    case, probe, expected_count, reference_panel, public_panel
):
    """The proposed schema is specified in devguide/DFND/boundary_connectivity_contract.md."""
    record = proposed_view(public_panel[case, probe].dfnd.raw, 'boundary_connectivity')
    assert record['status'] == 'resolved'
    assert record['surface']['kind'] == 'atomic_center_convex_hull'
    assert record['n_patches'] == expected_count
    patches = record['patches']
    assert len(patches) == expected_count
    assert len({patch['patch_id'] for patch in patches}) == expected_count
    for patch in patches:
        assert patch['support']['kind'] == 'hull_free_patch'
        assert patch['support']['carrier_faces_source_atom_indices']
        assert patch['evidence']['connectivity'] == 'resolved'


@pytest.mark.xfail(
    strict=True,
    raises=PhysicalBoundaryViewAbsent,
    reason='#151: proposed public physical-contact view is not implemented',
)
@pytest.mark.parametrize(
    'case,probe,expected_count',
    [('regular_tetrahedron', 1.2, 4), ('shell_with_opening', 1.4, 1)],
)
def test_public_feature_exposes_physical_contacts_separately_from_mouth_promotion(
    case, probe, expected_count, reference_panel, public_panel
):
    topo = public_panel[case, probe]
    features = [feature for feature in topo.values() if feature.dimensionality == 2]
    assert len(features) == 1
    record = proposed_view(features[0].boundary, 'physical_openings')
    assert record['status'] == 'resolved'
    assert record['n_patches'] == expected_count
    assert len(set(record['patch_ids'])) == expected_count
    native = proposed_view(topo.dfnd.raw, 'boundary_connectivity')
    assert set(record['patch_ids']) <= {p['patch_id'] for p in native['patches']}
    assert record['association_evidence']['status'] == 'resolved'
