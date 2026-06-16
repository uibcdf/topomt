"""Typed immutable configuration objects for DFND."""

from dataclasses import asdict, dataclass, replace
from typing import Any

import numpy as np


def _freeze_sequence(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        value = value.tolist()
    if isinstance(value, list | tuple):
        return tuple(_freeze_sequence(item) for item in value)
    return value


def _non_negative_finite(name: str, value: float) -> float:
    value = float(value)
    if not np.isfinite(value) or value < 0.0:
        raise ValueError(f'{name} must be a finite non-negative number')
    return value


@dataclass(frozen=True)
class DFNDMeshConfig:
    """Configuration that determines the cached Delaunay substrate."""

    selection: Any = 'all'
    structure_indices: Any = 0
    hydrogen_policy: str = 'exclude'
    radii_model: str = 'vdw'
    epsilon: float = 1e-7

    def __post_init__(self) -> None:
        object.__setattr__(self, 'selection', _freeze_sequence(self.selection))
        object.__setattr__(
            self, 'structure_indices', _freeze_sequence(self.structure_indices)
        )
        object.__setattr__(
            self, 'epsilon', _non_negative_finite('epsilon', self.epsilon)
        )
        if self.hydrogen_policy not in {'exclude', 'include', 'provided_atoms'}:
            raise ValueError(
                "hydrogen_policy must be 'exclude', 'include', or 'provided_atoms'"
            )
        if self.radii_model not in {'vdw', 'protor', 'provided'}:
            raise ValueError(
                "radii_model must be 'vdw', 'protor', or 'provided'"
            )

    def to_dict(self) -> dict[str, Any]:
        """Return the canonicalizable configuration mapping."""
        return asdict(self)


@dataclass(frozen=True)
class DFNDQuery:
    """Probe-dependent DFND query that can reuse an existing substrate."""

    probe_radius: float = 0.14  # nanometers (the 1.4 angstrom water probe)
    residence_tolerance: float = 0.0
    permeability_tolerance: float = 0.0
    transit_policy: str = 'with_connectors'
    gate_intrusion_policy: str = 'flag_only'
    dry_adjacency: str = 'face'

    def __post_init__(self) -> None:
        for name in (
            'probe_radius',
            'residence_tolerance',
            'permeability_tolerance',
        ):
            object.__setattr__(
                self, name, _non_negative_finite(name, getattr(self, name))
            )
        if self.transit_policy not in {'resident_only', 'with_connectors'}:
            raise ValueError(
                "transit_policy must be 'resident_only' or 'with_connectors'"
            )
        if self.gate_intrusion_policy not in {'flag_only', 'block_suspect'}:
            raise ValueError(
                "gate_intrusion_policy must be 'flag_only' or 'block_suspect'"
            )
        if self.dry_adjacency not in {'face', 'edge', 'vertex'}:
            raise ValueError("dry_adjacency must be 'face', 'edge', or 'vertex'")

    def replace(self, **overrides: Any) -> 'DFNDQuery':
        """Return a validated query with selected fields replaced."""
        return replace(self, **overrides)

    def to_dict(self) -> dict[str, Any]:
        """Return the canonicalizable query mapping used by result identity."""
        return asdict(self)
