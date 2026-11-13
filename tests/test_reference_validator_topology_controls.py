"""Analytic controls freeze physical questions without a component solver."""

from fractions import Fraction
from itertools import product

from devtools.reference_validator.model import Atom, Box, Model, point, scalar
from devtools.reference_validator.verify.geometry import point_is_free, segment_is_free


def test_eight_corner_regions_are_not_lost_as_radius_approaches_corner():
    # Coordinate planes are blocked; each orthant is star-shaped at its corner.
    for radius in (Fraction(3, 2), Fraction(173205, 100000)):
        assert 2 < radius**2 < 3
        model = Model(
            (Atom(0, point((0, 0, 0)), radius),),
            scalar(0),
            Box(point((-1, -1, -1)), point((1, 1, 1))),
            'a' * 64,
        )
        for corner in product((-1, 1), repeat=3):
            assert point_is_free(model, point(corner))
        assert not point_is_free(model, point((0, 1, 1)))


def test_exact_throat_contact_is_excluded_without_perturbation():
    domain = Box(point((-10, -3, -4)), point((10, 3, 4)))
    for probe in (1 - Fraction(1, 2**20), Fraction(1), 1 + Fraction(1, 2**20)):
        model = Model((Atom(0, point((0, 0, 0)), scalar(4)),), probe, domain, 'a' * 64)
        assert segment_is_free(model, point((-10, 3, 4)), point((10, 3, 4))) == (
            probe < 1
        )
        assert point_is_free(model, point((0, 3, 4))) == (probe < 1)
