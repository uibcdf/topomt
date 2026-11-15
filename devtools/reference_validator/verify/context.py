"""In-process immutable topology reuse, constructed only by real checking."""

import json
import os
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, SupportsIndex

from ..model import Model
from .power_progress import kernel_identity


@dataclass(frozen=True, init=False)
class CheckedTopology:
    """Detach and check a topology once; reuse it only within this process.

    Parameters
    ----------
    model : Model
        Immutable exact numerical model.
    certificate : object
        Untrusted complete topology proof. No accepted flag is consumed.

    Raises
    ------
    ValueError
        Independent checking rejects the proof or its type.
    """

    model: Model
    _pid: int
    _proof_json: str
    _result_json: str
    _kernel_json: str

    def __init__(self, model: Model, certificate: object) -> None:
        from . import verify

        payload = json.dumps(certificate, sort_keys=True, allow_nan=False)
        result = verify(model, json.loads(payload))
        if result['kind'] != 'power_cell_topology':
            raise ValueError('A checked context requires complete power-cell topology')
        object.__setattr__(self, 'model', model)
        object.__setattr__(self, '_pid', os.getpid())
        object.__setattr__(self, '_proof_json', payload)
        object.__setattr__(self, '_result_json', json.dumps(result, sort_keys=True))
        object.__setattr__(
            self, '_kernel_json', json.dumps(kernel_identity(), sort_keys=True)
        )

    def __reduce_ex__(self, protocol: SupportsIndex) -> Any:
        raise TypeError('Save proof data; checked contexts cannot be serialized')

    def _check_kernel(self) -> None:
        if os.getpid() != self._pid:
            raise ValueError('Checked topology belongs to another process')
        if json.dumps(kernel_identity(), sort_keys=True) != self._kernel_json:
            raise ValueError('Checked topology executable kernel changed')

    @property
    def result(self) -> dict[str, Any]:
        """Return a detached receipt; changing it cannot change checked state."""
        self._check_kernel()
        return json.loads(self._result_json)

    def query_anchors(
        self,
        *,
        anchors: dict[str, tuple[Fraction, Fraction, Fraction]],
        pairs: list[tuple[str, str]],
    ) -> dict[str, Any]:
        """Query the bound model; every returned path retains all-atom checking.

        Parameters
        ----------
        anchors, pairs : dict, list
            At most 32 named exact positions and 32 named connection pairs.

        Returns
        -------
        dict
            Detached memberships and independently checked path certificates.

        Raises
        ------
        ValueError
            Invalid query or executable identity changed.
        """
        from .power_cells import _query_checked

        return _query_checked(
            self.model,
            json.loads(self._proof_json),
            self.result,
            anchors=anchors,
            pairs=pairs,
        )
