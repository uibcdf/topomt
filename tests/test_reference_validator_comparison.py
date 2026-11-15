"""Reference comparisons match numerical models and qualify explicit supports."""

import pytest

from devtools.reference_validator.compare import compare_reference_claims
from devtools.reference_validator.model import Box, Model, point
from devtools.reference_validator.power_cells import topology_certificate


def test_point_path_and_unknown_carrier_claims_keep_different_guarantees():
    model = Model.from_spheres(
        [(-8, 0, 0), (8, 0, 0)],
        [4, 4],
        1,
        domain=Box(point((-20, -3, -4)), point((20, 3, 4))),
    )
    result = compare_reference_claims(
        model,
        topology_certificate(model),
        native_model=model,
        points={'blocked': point((-8, 0, 0)), 'clear': point((0, 0, 0))},
        paths={'colliding': [point((-20, 0, 0)), point((20, 0, 0))]},
    )
    assert result['points']['blocked']['point_state'] == 'blocked'
    assert result['points']['clear']['point_state'] == 'free'
    assert result['paths']['colliding']['all_atom_free'] is False
    assert result['morphology_status'] == 'not_inferred'


def test_different_native_numerical_model_is_rejected():
    model = Model.from_spheres(
        [], [], 0, domain=Box(point((-1, -1, -1)), point((1, 1, 1)))
    )
    other = Model.from_spheres([], [], 1, domain=model.domain)
    with pytest.raises(ValueError):
        compare_reference_claims(
            model, topology_certificate(model), native_model=other, points={}, paths={}
        )


def test_whole_hull_exclusion_qualifies_a_source_tetrahedron_carrier():
    from fractions import Fraction

    model = Model.from_spheres(
        [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)],
        [Fraction(7, 4)] * 4,
        0,
        domain=Box(point((-1, -1, -1)), point((1, 1, 1))),
    ).with_center_hull()
    carriers = {'candidate': [[0, 1, 2, 3]]}
    result = compare_reference_claims(
        model,
        topology_certificate(model),
        native_model=model,
        points={},
        paths={},
        carrier_tetrahedra=carriers,
    )
    assert result['carriers']['candidate']['physical_state'] == 'empty'
    assert result['carriers']['candidate']['proof_route'] == 'whole_domain_exclusion'
    carriers['candidate'][0][0] = 999
    assert result['carriers']['candidate']['source_tetrahedra'] == [[0, 1, 2, 3]]


def test_mixed_carrier_is_unresolved_instead_of_being_qualified_from_a_point():
    model = Model.from_spheres(
        [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)],
        [0] * 4,
        0,
        domain=Box(point((0, 0, 0)), point((1, 1, 1))),
    ).with_center_hull()
    result = compare_reference_claims(
        model,
        topology_certificate(model),
        native_model=model,
        points={'clear': point((0.1, 0.1, 0.1))},
        paths={},
        carrier_tetrahedra={'candidate': [[0, 1, 2, 3]]},
    )
    assert result['points']['clear']['point_state'] == 'free'
    assert result['carriers']['candidate']['physical_state'] == 'unresolved'


def test_complete_exclusion_also_covers_lower_dimensional_source_carriers():
    model = Model.from_spheres(
        [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)],
        [5] * 4,
        0,
        domain=Box(point((-2, -2, -2)), point((2, 2, 2))),
    )
    result = compare_reference_claims(
        model,
        topology_certificate(model),
        native_model=model,
        points={},
        paths={},
        carrier_tetrahedra={'flat': [[0, 1, 2, 3]]},
    )
    assert result['carriers']['flat']['physical_state'] == 'empty'
