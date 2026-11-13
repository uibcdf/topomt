"""Immutable execution contracts shared as data, never as search conclusions."""

import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .model import Box, Model, _record, record_digest


@dataclass(frozen=True)
class Configuration:
    """Fixed partition request, separate from the work allowed in one step."""

    max_depth: int = 4
    max_leaves: int = 4096

    def __post_init__(self) -> None:
        if (
            type(self.max_depth) is not int
            or not 0 <= self.max_depth <= 24
            or type(self.max_leaves) is not int
            or not 1 <= self.max_leaves <= 4096
        ):
            raise ValueError('Configuration requires depth 0..24 and 1..4096 leaves')

    def to_record(self) -> dict[str, int]:
        """Encode the complete fixed request, without a per-step work budget."""
        return {'max_depth': self.max_depth, 'max_leaves': self.max_leaves}

    @classmethod
    def from_record(cls, value: object) -> 'Configuration':
        """Reject unknown request fields rather than silently override them."""
        data = _record(value, {'max_depth', 'max_leaves'})
        return cls(data['max_depth'], data['max_leaves'])


def kernel_identity() -> dict[str, Any]:
    """Pin executable subdivision/checking semantics and the Python runtime.

    Saved mathematical certificates can be checked with later code. Resuming
    executable work under changed code/runtime instead requires a new run.
    """
    root = Path(__file__).parent
    names = (
        'model.py',
        'producer.py',
        'contracts.py',
        'runs.py',
        'storage.py',
        'verify/__init__.py',
        'verify/geometry.py',
        'verify/records.py',
    )
    return {
        'schema': 'topomt.reference-validator.kernel/1',
        'algorithm': 'rational-convex-partition/1',
        'python_version': sys.version,
        'files': {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in names
        },
    }


def run_identity(
    model: Model, configuration: Configuration, kernel: dict[str, Any]
) -> str:
    """Bind one model, fixed request and kernel to a reproducible run identity."""
    return record_digest(
        {
            'model_sha256': model.digest,
            'configuration': configuration.to_record(),
            'kernel': kernel,
        }
    )


def _digest_is(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def _split_budget(value: int) -> None:
    if type(value) is not int or not 0 <= value <= 4095:
        raise ValueError('Step split budget must be an integer in 0..4095')


def _stop_reason(
    model: Model, certificate: dict[str, Any], configuration: Configuration
) -> str:
    unknown = [leaf for leaf in certificate['leaves'] if leaf['state'] == 'unknown']
    if not unknown:
        return 'no_unknown_cells'
    if all(len(leaf['path']) >= configuration.max_depth for leaf in unknown):
        return 'depth_limit'
    arity = 8 if isinstance(model.domain, Box) else 2
    if len(certificate['leaves']) + arity - 1 > configuration.max_leaves:
        return 'leaf_limit'
    return 'step_budget'
