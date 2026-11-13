"""Exact developer volume tolerances with explicit units and no unit policy."""

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Optional

from .model import _record, decode_scalar, encode_scalar, scalar


@dataclass(frozen=True)
class VolumeRequest:
    """Request every enabled absolute/relative volume bound, including zero.

    Parameters
    ----------
    absolute_nm3 : scalar or None
        Nonnegative absolute error tolerance in nm**3; None disables it.
    relative : scalar or None
        Nonnegative dimensionless relative tolerance; None disables it.

    Raises
    ------
    ValueError, TypeError
        No constraint is enabled or a value is negative, nonfinite or invalid.
    """

    absolute_nm3: Optional[Fraction] = None
    relative: Optional[Fraction] = None

    def __post_init__(self) -> None:
        if self.absolute_nm3 is None and self.relative is None:
            raise ValueError('At least one volume precision constraint is required')
        for name in ('absolute_nm3', 'relative'):
            value = getattr(self, name)
            if value is not None:
                value = scalar(value)
                if value < 0:
                    raise ValueError('Volume tolerances must be nonnegative')
                object.__setattr__(self, name, value)

    def to_record(self) -> dict[str, Any]:
        """Detach both tolerances and their declared dimensions."""
        return {
            'schema': 'topomt.reference-validator.volume-request/1',
            'volume_unit': 'nm**3',
            'absolute_tolerance': None
            if self.absolute_nm3 is None
            else encode_scalar(self.absolute_nm3),
            'relative_unit': 'dimensionless',
            'relative_tolerance': None
            if self.relative is None
            else encode_scalar(self.relative),
        }

    @classmethod
    def from_record(cls, value: object) -> 'VolumeRequest':
        """Reject incompatible units, unknown fields and malformed rationals."""
        data = _record(
            value,
            {
                'schema',
                'volume_unit',
                'absolute_tolerance',
                'relative_unit',
                'relative_tolerance',
            },
        )
        if (
            data['schema'] != 'topomt.reference-validator.volume-request/1'
            or data['volume_unit'] != 'nm**3'
            or data['relative_unit'] != 'dimensionless'
        ):
            raise ValueError('Invalid volume request schema or units')
        return cls(
            None
            if data['absolute_tolerance'] is None
            else decode_scalar(data['absolute_tolerance']),
            None
            if data['relative_tolerance'] is None
            else decode_scalar(data['relative_tolerance']),
        )

    def satisfied(self, lower: Fraction, upper: Fraction) -> bool:
        """Check all enabled constraints, withholding relative error at L=0<U."""
        if not 0 <= lower <= upper:
            raise ValueError('Volume bounds must be nonnegative and ordered')
        width = upper - lower
        absolute_ok = self.absolute_nm3 is None or width <= self.absolute_nm3
        relative_ok = (
            self.relative is None
            or (lower == upper == 0)
            or (lower > 0 and width <= self.relative * lower)
        )
        return absolute_ok and relative_ok
