"""Whole cells and whole segments, rather than sampled centers/endpoints."""

from fractions import Fraction

from devtools.reference_validator.model import (
    Atom,
    Box,
    Model,
    Tetrahedron,
    point,
    scalar,
)
from devtools.reference_validator.verify.geometry import (
    cell_is_covered,
    cell_is_free,
    contains,
    point_is_free,
    segment_is_free,
    split,
    volume,
)


def test_hidden_obstacle_and_tangent_segment_are_not_free():
    box = Box(point((-2, -2, -2)), point((2, 2, 2)))
    model = Model((Atom(0, point((0, 0, 0)), scalar(1)),), scalar(0), box, 'a' * 64)
    assert point_is_free(model, box.lower) and point_is_free(model, box.upper)
    assert not cell_is_free(model, box)
    assert not segment_is_free(model, point((-2, 0, 0)), point((2, 0, 0)))
    assert not segment_is_free(model, point((-2, 1, 0)), point((2, 1, 0)))
    assert segment_is_free(
        model, point((-2, Fraction(1001, 1000), 0)), point((2, Fraction(1001, 1000), 0))
    )
    assert not point_is_free(model, point((1, 0, 0)))


def test_nonlocal_large_ball_is_not_omitted_for_nearest_center():
    model = Model(
        (
            Atom(4, point((0, 0, 0)), scalar(Fraction(1, 10))),
            Atom(20, point((10, 0, 0)), scalar(10)),
        ),
        scalar(0),
        Box(point((-2, -2, -2)), point((12, 2, 2))),
        'a' * 64,
    )
    assert not point_is_free(model, point((1, 0, 0)))


def test_sub_float_gap_and_large_translation_keep_exact_sign():
    gap = Fraction(1, 2**70)
    for offset in (0, 10**20):
        box = Box(point((offset - 2, -2, -2)), point((offset + 2, 2, 2)))
        model = Model(
            (Atom(0, point((offset, 0, 0)), scalar(1)),), scalar(0), box, 'a' * 64
        )
        assert point_is_free(model, point((offset, 1 + gap, 0)))
        assert not point_is_free(model, point((offset, 1 - gap, 0)))
        assert not point_is_free(model, point((offset, 1, 0)))


def test_complete_cover_uses_maximum_over_whole_cell():
    box = Box(point((-1, -1, -1)), point((1, 1, 1)))
    model = Model((Atom(9, point((0, 0, 0)), scalar(2)),), scalar(0), box, 'a' * 64)
    assert cell_is_covered(model, box, 9)
    smaller = Model((Atom(9, point((0, 0, 0)), scalar(1)),), scalar(0), box, 'a' * 64)
    assert not cell_is_covered(smaller, box, 9)
    assert not cell_is_covered(model, box, 8)


def test_exact_convex_domains_and_subdivision():
    tet = Tetrahedron(
        tuple(point(x) for x in ((0, 0, 0), (2, 0, 0), (0, 2, 0), (0, 0, 2)))
    )
    assert contains(tet, point((Fraction(1, 3),) * 3))
    assert contains(tet, point((0, 0, 0)))
    assert not contains(tet, point((1, 1, 1)))
    assert volume(tet) == Fraction(4, 3)
    domains = (tet, Box(point((-1, -1, -1)), point((1, 1, 1))))
    for domain in domains:
        children = split(domain)
        assert sum(volume(c) for c in children) == volume(domain)
        assert all(volume(c) == volume(domain) / len(children) for c in children)
        model = Model((), scalar(0), domain, 'a' * 64)
        assert cell_is_free(model, domain)
    assert not segment_is_free(
        Model((), scalar(0), tet, 'a' * 64), point((0, 0, 0)), point((2, 2, 2))
    )
