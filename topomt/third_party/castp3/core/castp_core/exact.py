"""Exact arithmetic helpers for canonical CASTp weighted events."""

from dataclasses import dataclass
import math
from math import gcd

import numpy as np


@dataclass(frozen=True, slots=True)
class ExactRatio:
    """Normalized exact ratio used to order historical CASTp rho events."""

    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        numerator = int(self.numerator)
        denominator = int(self.denominator)

        if denominator < 0:
            numerator = -numerator
            denominator = -denominator

        if denominator != 0:
            common_divisor = gcd(abs(numerator), denominator)
            if common_divisor > 1:
                numerator //= common_divisor
                denominator //= common_divisor
        elif numerator != 0:
            numerator = 1 if numerator > 0 else -1

        object.__setattr__(self, 'numerator', numerator)
        object.__setattr__(self, 'denominator', denominator)

    def compare(self, other: 'ExactRatio') -> int:
        """Return ``-1``, ``0`` or ``1`` from an exact ratio comparison."""

        if self.numerator == other.numerator and self.denominator == other.denominator:
            return 0

        if self.denominator == 0:
            if other.denominator == 0:
                return (self.numerator > other.numerator) - (self.numerator < other.numerator)
            return (self.numerator > 0) - (self.numerator < 0)

        if other.denominator == 0:
            return -other.compare(self)

        left = self.numerator * other.denominator
        right = self.denominator * other.numerator
        return (left > right) - (left < right)

    def to_float(self) -> float:
        """Return the floating-point value of the exact ratio."""

        if self.denominator == 0:
            if self.numerator > 0:
                return float('inf')
            if self.numerator < 0:
                return float('-inf')
            return 0.0
        return float(self.numerator) / float(self.denominator)


def fixed_point_int(value: float, decimals: int) -> int:
    """Return the nearest fixed-point integer at the given decimal scale."""

    scale = 10 ** int(decimals)
    return int(round(float(value) * scale))


def fixed_point_array(values: np.ndarray, decimals: int) -> np.ndarray:
    """Return an integer array on a fixed-point decimal grid."""

    values_array = np.asarray(values, dtype=float)
    scale = 10 ** int(decimals)
    return np.rint(values_array * scale).astype(object)


def castp1_fixed_point_int(value: float, decimals: int = 5, source_decimals: int = 3) -> int:
    """Return CASTp 1.0 fixed-point integer materialization.

    Historical CASTp inputs written with ``# fix: 7.5`` are read through
    ``lia_ffpload``. That path parses decimal text as a C double and stores
    ``floor(value * 10**decimals)`` rather than rounding to the nearest grid
    point. PDB2ALF writes coordinates and radii at fixed decimal precision, so
    values are first rematerialized through that text precision.
    """

    if source_decimals >= 0:
        value = float(f'{float(value):.{int(source_decimals)}f}')
    scale = 10 ** int(decimals)
    return int(math.floor(float(value) * scale))


def castp1_fixed_point_array(
    values: np.ndarray,
    decimals: int = 5,
    source_decimals: int = 3,
) -> np.ndarray:
    """Return an array materialized with CASTp 1.0 fixed-point semantics."""

    values_array = np.asarray(values, dtype=float)
    fixed_values = [
        castp1_fixed_point_int(float(value), decimals, source_decimals)
        for value in values_array.reshape(-1)
    ]
    return np.asarray(fixed_values, dtype=object).reshape(values_array.shape)


def exact_determinant(matrix: np.ndarray) -> int:
    """Return the exact determinant of an integer matrix via Bareiss elimination."""

    array = np.asarray(matrix, dtype=object)
    if array.ndim != 2 or array.shape[0] != array.shape[1]:
        raise ValueError('matrix must be square')

    size = int(array.shape[0])
    if size == 0:
        return 1

    work = array.copy()
    sign = 1
    previous_pivot = 1

    for pivot_index in range(size - 1):
        pivot = work[pivot_index, pivot_index]
        if pivot == 0:
            swap_index = None
            for candidate in range(pivot_index + 1, size):
                if work[candidate, pivot_index] != 0:
                    swap_index = candidate
                    break
            if swap_index is None:
                return 0
            work[[pivot_index, swap_index]] = work[[swap_index, pivot_index]]
            sign *= -1
            pivot = work[pivot_index, pivot_index]

        for row_index in range(pivot_index + 1, size):
            for column_index in range(pivot_index + 1, size):
                numerator = (
                    work[row_index, column_index] * pivot
                    - work[row_index, pivot_index] * work[pivot_index, column_index]
                )
                if previous_pivot != 1:
                    numerator //= previous_pivot
                work[row_index, column_index] = numerator

        previous_pivot = pivot
        for row_index in range(pivot_index + 1, size):
            work[row_index, pivot_index] = 0
        for column_index in range(pivot_index + 1, size):
            work[pivot_index, column_index] = 0

    return int(sign * work[size - 1, size - 1])
