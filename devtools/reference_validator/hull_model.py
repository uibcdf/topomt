"""Exact center-only source identity and bounded hull-checking contracts.

This is a numerical proof view, not another molecular representation. Radii,
probe and the receiving Model's domain do not define the center hull.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from .contracts import _digest_is
from .model import (
    Model,
    _is_binary64,
    _record,
    decode_point,
    encode_point,
    point,
    record_digest,
)


@dataclass(frozen=True)
class CenterSource:
    """Freeze exact nm centers with original row/frame/input identities."""

    centers: tuple[tuple[Fraction, Fraction, Fraction], ...]
    source_ids: tuple[int, ...]
    source_sha256: str
    frame_index: int = 0
    interpretation: str = 'exact_rational_nm'

    def __post_init__(self) -> None:
        object.__setattr__(self, 'centers', tuple(point(p) for p in self.centers))
        object.__setattr__(self, 'source_ids', tuple(self.source_ids))
        if (
            len(self.centers) != len(self.source_ids)
            or any(type(i) is not int or i < 0 for i in self.source_ids)
            or len(set(self.source_ids)) != len(self.source_ids)
        ):
            raise ValueError('Center row/source identity differs')
        if (
            not _digest_is(self.source_sha256)
            or type(self.frame_index) is not int
            or self.frame_index < 0
        ):
            raise ValueError('Invalid center input/frame identity')
        if not isinstance(self.interpretation, str) or self.interpretation not in {
            'exact_rational_nm',
            'received_binary64_nm',
        }:
            raise ValueError('Unknown center numerical interpretation')
        if self.interpretation == 'received_binary64_nm' and not all(
            _is_binary64(v) for p in self.centers for v in p
        ):
            raise ValueError('Received centers must round-trip as binary64')

    @classmethod
    def from_model(cls, model: Model) -> 'CenterSource':
        """Retain a model's centers/provenance without treating its domain as H."""
        return cls(
            tuple(a.center for a in model.atoms),
            tuple(a.source_id for a in model.atoms),
            model.source_sha256,
            model.frame_index,
            model.interpretation,
        )

    def to_record(self) -> dict[str, Any]:
        """Detach the center-only proof record with its explicit length unit."""
        return {
            'schema': 'topomt.reference-validator.center-source/1',
            'length_unit': 'nm',
            'source_sha256': self.source_sha256,
            'frame_index': self.frame_index,
            'interpretation': self.interpretation,
            'centers': [
                {'source_id': i, 'point': encode_point(p)}
                for i, p in zip(self.source_ids, self.centers)
            ],
        }

    @classmethod
    def from_record(cls, value: object) -> 'CenterSource':
        """Reject unknown units/fields and preserve all rows, including duplicates."""
        data = _record(
            value,
            {
                'schema',
                'length_unit',
                'source_sha256',
                'frame_index',
                'interpretation',
                'centers',
            },
        )
        if (
            data['schema'] != 'topomt.reference-validator.center-source/1'
            or data['length_unit'] != 'nm'
            or not isinstance(data['centers'], list)
        ):
            raise ValueError('Unsupported center source schema or unit')
        points, ids = [], []
        for row in data['centers']:
            _record(row, {'source_id', 'point'})
            points.append(decode_point(row['point']))
            ids.append(row['source_id'])
        return cls(
            tuple(points),
            tuple(ids),
            data['source_sha256'],
            data['frame_index'],
            data['interpretation'],
        )

    @property
    def digest(self) -> str:
        """Bind the complete center view and its provenance, independently of probe."""
        return record_digest(self.to_record())


@dataclass(frozen=True)
class HullLimits:
    """Finite pilot work ceilings, never geometric tolerances."""

    max_centers: int = 128
    max_facets: int = 192
    max_plane_triples: int = 1200000

    def __post_init__(self) -> None:
        for value, maximum in [
            (self.max_centers, 128),
            (self.max_facets, 192),
            (self.max_plane_triples, 1200000),
        ]:
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValueError(
                    'Hull work limit is outside the bounded pilot envelope'
                )

    def to_record(self) -> dict[str, int]:
        """Record resource ceilings separately from numerical geometry."""
        return {
            'max_centers': self.max_centers,
            'max_facets': self.max_facets,
            'max_plane_triples': self.max_plane_triples,
        }
