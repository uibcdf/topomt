"""Certified cap/wedge integration for a ball cutting a centered cube.

This deliberately small admission is a boundary-integration feasibility control,
not an integrator for arbitrary original power cells. All interval rounding is
outward to dyadics; series tails are bounded before any precision claim.
"""

from fractions import Fraction

from ..model import Box, Model, _record
from ._interval import _exact, _Interval, _pi, _sqrt


def _out(value: _Interval, bits: int) -> _Interval:
    scale = 1 << bits
    low = (value.lower.numerator * scale) // value.lower.denominator
    high = -((-value.upper.numerator * scale) // value.upper.denominator)
    return _Interval(Fraction(low, scale), Fraction(high, scale))


def _atan_positive(x: Fraction, bits: int) -> _Interval:
    if x == 0:
        return _exact(0)
    if x > 1:
        return _out(_pi(bits) / _exact(2) - _atan_positive(1 / x, bits), bits)
    # Half-angle reduction: t <= sqrt(2)-1. The alternating tail is
    # bounded at its largest admitted argument; interval Horner evaluation
    # encloses every polynomial value without exploding rational operands.
    t = _out(_exact(x) / (_exact(1) + _sqrt(1 + x * x, bits)), bits)
    terms = bits
    square = _out(t * t, bits)
    polynomial = _exact(Fraction((-1) ** (terms - 1), 2 * terms - 1))
    for k in range(terms - 2, -1, -1):
        polynomial = _out(
            polynomial * square + _exact(Fraction((-1) ** k, 2 * k + 1)), bits
        )
    polynomial = _out(polynomial * t, bits)
    if not 0 <= t.lower <= t.upper < Fraction(1, 2):
        raise ValueError('Half-angle reduction did not admit its series bound')
    tail = Fraction(1, (2 * terms + 1) * 2 ** (2 * terms + 1))
    return _out(
        _exact(2) * _Interval(polynomial.lower - tail, polynomial.upper + tail), bits
    )


def _atan(value: _Interval, bits: int) -> _Interval:
    def endpoint(x: Fraction) -> _Interval:
        return (
            _atan_positive(x, bits) if x >= 0 else _exact(0) - _atan_positive(-x, bits)
        )

    return _Interval(endpoint(value.lower).lower, endpoint(value.upper).upper)


def corner_bounds(model: Model, certificate: object) -> _Interval:
    """Reconstruct certified total volume for the exact eight-corner admission.

    Parameters
    ----------
    model : Model
        One expanded ball centered in an axis-aligned cube, with
        2*a**2 < R**2 < 3*a**2.
    certificate : object
        Strict cap/wedge scheme and bounded dyadic precision record.

    Returns
    -------
    _Interval
        Total free volume in nm**3, enclosed by exact rational endpoints.

    Raises
    ------
    ValueError
        Geometry, record or arithmetic precision violates this admission.
    """
    record = _record(certificate, {'scheme', 'bits'})
    if record['scheme'] != 'cube-cap-wedge/1':
        raise ValueError('Unsupported boundary integration scheme')
    bits = record['bits']
    if type(bits) is not int or bits not in [64, 128, 256, 512, 1024, 2048]:
        raise ValueError('Unsupported bounded precision')
    if not isinstance(model.domain, Box) or len(model.atoms) != 1:
        raise ValueError('One ball and an exact centered cube are required')
    atom = model.atoms[0]
    halves = [(hi - lo) / 2 for lo, hi in zip(model.domain.lower, model.domain.upper)]
    center = tuple(
        (hi + lo) / 2 for lo, hi in zip(model.domain.lower, model.domain.upper)
    )
    if atom.center != center or len(set(halves)) != 1:
        raise ValueError('One ball and an exact centered cube are required')
    a = halves[0]
    radius = atom.radius + model.probe
    if not 2 * a * a < radius * radius < 3 * a * a:
        raise ValueError('Expected eight positive separated corner regions')
    t = _sqrt(radius * radius - 2 * a * a, bits)
    phi = _atan(_out(t / _exact(a), bits), bits)
    gamma = _atan(_out(_exact(radius) * t / _exact(a * a), bits), bits)
    wedge = _out(
        (
            _exact(2 * radius**3) * gamma
            - _exact(2 * a * (3 * radius**2 - a * a)) * phi
            + _exact(2 * a * a) * t
        )
        / _exact(3),
        bits,
    )
    pi = _pi(bits)
    cap = _out(pi * _exact((radius - a) ** 2 * (2 * radius + a) / 3), bits)
    total = _out(
        _exact(8 * a**3)
        - _exact(Fraction(4, 3) * radius**3) * pi
        + _exact(6) * cap
        - _exact(12) * wedge,
        bits,
    )
    return _Interval(max(Fraction(), total.lower), min(8 * a**3, total.upper))
