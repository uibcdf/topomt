"""Trusted private rational intervals, Machin remainder and dyadic square roots.

These elementary bounded operations are shared with the producer; geometric
coverage/admission is checked separately. No floating rounding is involved.
"""

from dataclasses import dataclass
from fractions import Fraction
from math import isqrt


@dataclass(frozen=True)
class _Interval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise ValueError('Invalid rational interval')

    def __add__(self, other: '_Interval') -> '_Interval':
        return _Interval(self.lower + other.lower, self.upper + other.upper)

    def __sub__(self, other: '_Interval') -> '_Interval':
        return _Interval(self.lower - other.upper, self.upper - other.lower)

    def __mul__(self, other: '_Interval') -> '_Interval':
        values = [
            a * b for a in (self.lower, self.upper) for b in (other.lower, other.upper)
        ]
        return _Interval(min(values), max(values))

    def __truediv__(self, other: '_Interval') -> '_Interval':
        if other.lower <= 0 <= other.upper:
            raise ValueError('Interval denominator contains zero')
        return self * _Interval(1 / other.upper, 1 / other.lower)

    def square(self) -> '_Interval':
        values = [self.lower**2, self.upper**2]
        return _Interval(
            Fraction() if self.lower <= 0 <= self.upper else min(values), max(values)
        )

    def clip(self, lower: Fraction, upper: Fraction) -> '_Interval':
        return _Interval(max(lower, self.lower), min(upper, self.upper))


def _exact(value: Fraction | int) -> _Interval:
    value = Fraction(value)
    return _Interval(value, value)


def _sqrt(value: Fraction, bits: int) -> _Interval:
    numerator = isqrt((value.numerator << (2 * bits)) // value.denominator)
    lower = Fraction(numerator, 1 << bits)
    upper = lower if lower**2 == value else lower + Fraction(1, 1 << bits)
    return _Interval(lower, upper)


def _atan_reciprocal(denominator: int, terms: int) -> _Interval:
    total = sum(
        (
            Fraction((-1) ** k, (2 * k + 1) * denominator ** (2 * k + 1))
            for k in range(terms)
        ),
        Fraction(),
    )
    remainder = Fraction(1, (2 * terms + 1) * denominator ** (2 * terms + 1))
    return (
        _Interval(total - remainder, total)
        if terms % 2
        else _Interval(total, total + remainder)
    )


def _pi(terms: int) -> _Interval:
    value = _exact(16) * _atan_reciprocal(5, terms) - _exact(4) * _atan_reciprocal(
        239, terms
    )
    return _Interval(max(Fraction(), value.lower), value.upper)
