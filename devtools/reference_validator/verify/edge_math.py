"""Certified dyadic atan using integer interval Horner arithmetic.

The half-angle identity and alternating-series tail are the same mathematical
contract as the retained Fraction implementation. Every rounding is outward;
guard bits reduce arithmetic cost without changing a requested volume error.
"""

from fractions import Fraction
from functools import lru_cache

from ._interval import _exact, _Interval, _outward, _pi, _sqrt

BITS = (64, 128, 256, 512, 1024, 2048)


@lru_cache(maxsize=8)
def _pi_cached(terms: int) -> _Interval:
    return _pi(terms)


def _mul(a: tuple[int, int], b: tuple[int, int], scale: int) -> tuple[int, int]:
    products = [x * y for x in a for y in b]
    return min(products) // scale, -((-max(products)) // scale)


def _small(value: Fraction, bits: int) -> _Interval:
    work = bits + 32
    scale = 1 << work
    t = _exact(value) / (_exact(1) + _sqrt(1 + value * value, work + 4))
    interval = (
        (t.lower.numerator * scale) // t.lower.denominator,
        -((-t.upper.numerator * scale) // t.upper.denominator),
    )
    if not 0 <= interval[0] <= interval[1] < scale // 2:
        raise ArithmeticError('Half-angle reduction did not certify t<1/2')
    square = _mul(interval, interval, scale)
    terms = (work + 1) // 2 + 2

    def coefficient(k: int) -> tuple[int, int]:
        numerator = (-1 if k % 2 else 1) * scale
        denominator = 2 * k + 1
        return numerator // denominator, -((-numerator) // denominator)

    polynomial = coefficient(terms - 1)
    for k in range(terms - 2, -1, -1):
        lo, hi = _mul(polynomial, square, scale)
        c0, c1 = coefficient(k)
        polynomial = lo + c0, hi + c1
    lo, hi = _mul(polynomial, interval, scale)
    # The alternating remainder is at most (1/2)^(2N+1)/(2N+1).
    denominator = (2 * terms + 1) << (2 * terms + 1)
    tail = -((-scale) // denominator)
    return _outward(
        _Interval(Fraction(2 * (lo - tail), scale), Fraction(2 * (hi + tail), scale)),
        bits,
    )


def atan_dyadic(value: Fraction | int, bits: int) -> _Interval:
    """Bound atan of an exact rational with integer interval reduction.

    Parameters
    ----------
    value : Fraction or int
        Exact dimensionless rational argument.
    bits : int
        Admitted output precision, 64 through 2048 in powers of two.

    Returns
    -------
    _Interval
        Outward rational endpoints on the declared dyadic grid.

    Raises
    ------
    ValueError, ArithmeticError
        Invalid precision or unproved half-angle arithmetic admission.
    """
    if type(bits) is not int or bits not in BITS:
        raise ValueError('Unsupported dyadic atan precision')
    if isinstance(value, bool):
        raise ValueError('Boolean arguments are not rational angles')
    value = Fraction(value)
    if value < 0:
        positive = atan_dyadic(-value, bits)
        return _Interval(-positive.upper, -positive.lower)
    if value == 0:
        return _exact(0)
    if value > 1:
        return _outward(
            _pi_cached(bits + 36) / _exact(2) - _small(1 / value, bits), bits
        )
    return _small(value, bits)
