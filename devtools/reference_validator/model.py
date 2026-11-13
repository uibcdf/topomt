"""Immutable exact models and strict portable records, without DFND imports."""

import hashlib
import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Any


def scalar(value: int | float | Fraction) -> Fraction:
    """Preserve an integer, rational or finite float's exact numerical value."""
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
        raise TypeError('Expected an integer, finite float or Fraction')
    try:
        return Fraction(value)
    except (ValueError, OverflowError) as exc:
        raise ValueError('Nonfinite scalar') from exc


def point(
    values: Sequence[int | float | Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    """Freeze three exact coordinates in the model's fixed nm convention."""
    if len(values) != 3:
        raise ValueError('A point needs three coordinates')
    return scalar(values[0]), scalar(values[1]), scalar(values[2])


_MAX_INTEGER_DIGITS = 20000


def _integer_text(value: int) -> str:
    """Encode bounded exact integers without changing Python's global guard."""
    negative = value < 0
    value = abs(value)
    # Reject grossly oversized operands before quadratic decimal conversion.
    if value.bit_length() > 4 * _MAX_INTEGER_DIGITS:
        raise ValueError('Exact integer codec budget exceeded')
    chunks = []
    while value:
        value, remainder = divmod(value, 10**9)
        chunks.append(remainder)
    digits = (
        str(chunks[-1]) + ''.join(f'{c:09d}' for c in reversed(chunks[:-1]))
        if chunks
        else '0'
    )
    if len(digits) > _MAX_INTEGER_DIGITS:
        raise ValueError('Exact integer codec budget exceeded')
    return '-' + digits if negative else digits


def _parse_integer(value: str) -> int:
    """Parse canonical integer chunks within an explicit per-scalar budget."""
    negative = value.startswith('-')
    digits = value[1:] if negative else value
    if len(digits) > _MAX_INTEGER_DIGITS:
        raise ValueError('Exact integer codec budget exceeded')
    result = 0
    for start in range(0, len(digits), 9):
        chunk = digits[start : start + 9]
        result = result * 10 ** len(chunk) + int(chunk)
    return -result if negative else result


def encode_scalar(value: Fraction) -> list[str]:
    """Encode an exact scalar without JSON floating-point conversion."""
    return [_integer_text(value.numerator), _integer_text(value.denominator)]


def decode_scalar(value: object) -> Fraction:
    """Read only canonical numerator/positive-denominator string pairs."""
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError('Expected a rational string pair')
    if not all(
        isinstance(v, str) and re.fullmatch(r'-?(0|[1-9][0-9]*)', v) for v in value
    ):
        raise ValueError('Invalid rational integer encoding')
    numerator, denominator = map(_parse_integer, value)
    if denominator <= 0:
        raise ValueError('Denominator must be positive')
    result = Fraction(numerator, denominator)
    if encode_scalar(result) != value:
        raise ValueError('Rational must be reduced and canonical')
    return result


def encode_point(value: tuple[Fraction, Fraction, Fraction]) -> list[list[str]]:
    """Encode coordinates using canonical rational scalars."""
    return [encode_scalar(v) for v in value]


def decode_point(value: object) -> tuple[Fraction, Fraction, Fraction]:
    """Reject malformed coordinate arrays before interpreting geometry."""
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError('Expected three encoded coordinates')
    return point([decode_scalar(v) for v in value])


def record_digest(record: dict[str, Any]) -> str:
    """Hash canonical JSON content, including all scientific context fields."""
    payload = json.dumps(
        record,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=True,
        allow_nan=False,
    ).encode('ascii')
    return hashlib.sha256(payload).hexdigest()


def _record(value: object, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f'Expected exactly these fields: {sorted(keys)}')
    return value


def _is_binary64(value: Fraction) -> bool:
    try:
        return scalar(float(value)) == value
    except (OverflowError, ValueError):
        return False


def _determinant(
    a: Sequence[Fraction], b: Sequence[Fraction], c: Sequence[Fraction]
) -> Fraction:
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


@dataclass(frozen=True)
class Atom:
    """One source-indexed excluded ball, with exact nm coordinates/radius."""

    source_id: int
    center: tuple[Fraction, Fraction, Fraction]
    radius: Fraction

    def __post_init__(self) -> None:
        if type(self.source_id) is not int or self.source_id < 0:
            raise ValueError('Invalid source atom ID')
        object.__setattr__(self, 'center', point(self.center))
        object.__setattr__(self, 'radius', scalar(self.radius))
        if self.radius < 0:
            raise ValueError('Negative atomic radius')


@dataclass(frozen=True)
class Box:
    """A closed, full-dimensional axis-aligned rational domain in nm."""

    lower: tuple[Fraction, Fraction, Fraction]
    upper: tuple[Fraction, Fraction, Fraction]

    def __post_init__(self) -> None:
        object.__setattr__(self, 'lower', point(self.lower))
        object.__setattr__(self, 'upper', point(self.upper))
        if any(a >= b for a, b in zip(self.lower, self.upper)):
            raise ValueError('A box must have strictly positive extents')

    @property
    def vertices(self) -> tuple[tuple[Fraction, Fraction, Fraction], ...]:
        """Return all eight corners exactly."""
        return tuple(point(v) for v in product(*zip(self.lower, self.upper)))


@dataclass(frozen=True)
class Tetrahedron:
    """A closed nondegenerate convex tetrahedral domain in nm."""

    vertices: tuple[tuple[Fraction, Fraction, Fraction], ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, 'vertices', tuple(point(v) for v in self.vertices))
        if len(self.vertices) != 4:
            raise ValueError('A tetrahedron needs four vertices')
        base = self.vertices[0]
        edges = [tuple(v[i] - base[i] for i in range(3)) for v in self.vertices[1:]]
        if _determinant(*edges) == 0:
            raise ValueError('Degenerate tetrahedral domain')


@dataclass(frozen=True)
class Model:
    """A frozen strict probe-center model, bound to source bytes and a frame.

    All numerical values are exact rationals in nm. Domain contact is allowed;
    obstacle contact is excluded. A captured floating value is interpreted
    exactly, rather than rounded to its apparent decimal. No atom is implicit.
    """

    atoms: tuple[Atom, ...]
    probe: Fraction
    domain: Box | Tetrahedron
    source_sha256: str
    frame_index: int = 0
    interpretation: str = 'exact_rational_nm'

    def __post_init__(self) -> None:
        object.__setattr__(self, 'atoms', tuple(self.atoms))
        object.__setattr__(self, 'probe', scalar(self.probe))
        if not all(isinstance(a, Atom) for a in self.atoms):
            raise ValueError('Invalid atom collection')
        if len({a.source_id for a in self.atoms}) != len(self.atoms):
            raise ValueError('Duplicate source atom IDs')
        if self.probe < 0 or not isinstance(self.domain, (Box, Tetrahedron)):
            raise ValueError('Invalid probe or unsupported domain')
        if not isinstance(self.source_sha256, str) or not re.fullmatch(
            r'[0-9a-f]{64}', self.source_sha256
        ):
            raise ValueError('A source SHA-256 is required')
        if type(self.frame_index) is not int or self.frame_index < 0:
            raise ValueError('Invalid frame index')
        if not isinstance(self.interpretation, str) or self.interpretation not in {
            'exact_rational_nm',
            'received_binary64_nm',
        }:
            raise ValueError('Unknown numerical model interpretation')
        if self.interpretation == 'received_binary64_nm':
            values = [self.probe]
            for atom in self.atoms:
                values.extend((*atom.center, atom.radius))
            if not all(_is_binary64(v) for v in values):
                raise ValueError('Received binary64 inputs must round-trip exactly')

    def to_record(self) -> dict[str, Any]:
        """Return a detached portable record with no numerical approximation."""
        domain = (
            {
                'kind': 'box',
                'lower': encode_point(self.domain.lower),
                'upper': encode_point(self.domain.upper),
            }
            if isinstance(self.domain, Box)
            else {
                'kind': 'tetrahedron',
                'vertices': [encode_point(v) for v in self.domain.vertices],
            }
        )
        return {
            'schema': 'topomt.reference-validator.model/1',
            'length_unit': 'nm',
            'contact_policy': 'strict',
            'interpretation': self.interpretation,
            'source_sha256': self.source_sha256,
            'frame_index': self.frame_index,
            'probe': encode_scalar(self.probe),
            'domain': domain,
            'atoms': [
                {
                    'source_id': a.source_id,
                    'center': encode_point(a.center),
                    'radius': encode_scalar(a.radius),
                }
                for a in self.atoms
            ],
        }

    @property
    def digest(self) -> str:
        """Bind all encoded geometry and context to a SHA-256 identity."""
        return record_digest(self.to_record())

    @classmethod
    def from_spheres(
        cls,
        centers_nm: Sequence[Sequence[int | float | Fraction]],
        radii_nm: Sequence[int | float | Fraction],
        probe_nm: int | float | Fraction,
        *,
        domain: Box | Tetrahedron,
    ) -> 'Model':
        """Freeze the three steric inputs and an explicit reporting domain.

        Parameters
        ----------
        centers_nm : sequence of three-coordinate sequences
            Atomic centers in nm. Input rows become stable source atom IDs.
        radii_nm : sequence
            One nonnegative radius in nm for every center.
        probe_nm : scalar
            Nonnegative probe radius in nm.
        domain : Box or Tetrahedron
            Declared finite observation domain; never inferred from DFND.

        Returns
        -------
        Model
            Detached exact model with a canonical numerical-source digest.
            That source digest identifies encoded spheres, not a PDB file.

        Raises
        ------
        ValueError, TypeError
            Shapes, values or domain violate the admitted model contract.
        """
        if len(centers_nm) != len(radii_nm):
            raise ValueError('Every center requires exactly one atomic radius')
        atoms = tuple(
            Atom(i, point(x), scalar(r))
            for i, (x, r) in enumerate(zip(centers_nm, radii_nm))
        )
        source = {
            'schema': 'topomt.reference-validator.sphere-input/1',
            'length_unit': 'nm',
            'atoms': [
                {
                    'source_id': a.source_id,
                    'center': encode_point(a.center),
                    'radius': encode_scalar(a.radius),
                }
                for a in atoms
            ],
        }
        return cls(atoms, scalar(probe_nm), domain, record_digest(source))

    @classmethod
    def from_record(cls, value: object) -> 'Model':
        """Read a strict model record; reject unknown fields and conventions."""
        data = _record(
            value,
            {
                'schema',
                'length_unit',
                'contact_policy',
                'interpretation',
                'source_sha256',
                'frame_index',
                'probe',
                'domain',
                'atoms',
            },
        )
        if (
            data['schema'] != 'topomt.reference-validator.model/1'
            or data['length_unit'] != 'nm'
            or data['contact_policy'] != 'strict'
        ):
            raise ValueError('Unsupported model schema, unit or contact convention')
        d = data['domain']
        if not isinstance(d, dict):
            raise ValueError('Invalid domain record')
        domain: Box | Tetrahedron
        if d.get('kind') == 'box':
            _record(d, {'kind', 'lower', 'upper'})
            domain = Box(decode_point(d['lower']), decode_point(d['upper']))
        elif d.get('kind') == 'tetrahedron':
            _record(d, {'kind', 'vertices'})
            if not isinstance(d['vertices'], list):
                raise ValueError('Invalid tetrahedron vertices')
            domain = Tetrahedron(tuple(decode_point(v) for v in d['vertices']))
        else:
            raise ValueError('Unsupported domain kind')
        if not isinstance(data['atoms'], list):
            raise ValueError('Atoms must be an array')
        atoms = []
        for raw in data['atoms']:
            a = _record(raw, {'source_id', 'center', 'radius'})
            atoms.append(
                Atom(
                    a['source_id'],
                    decode_point(a['center']),
                    decode_scalar(a['radius']),
                )
            )
        return cls(
            tuple(atoms),
            decode_scalar(data['probe']),
            domain,
            data['source_sha256'],
            data['frame_index'],
            data['interpretation'],
        )
