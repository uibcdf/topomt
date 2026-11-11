"""Shared evidence guards for the specialist external adapters."""

import hashlib
from collections.abc import Iterator
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path

from topomt.provider_output import ProviderRun


@contextmanager
def failure_evidence(metadata: dict, additional: dict[str, Path]) -> Iterator[None]:
    """Retain the attempted original identity and controls when execution fails."""
    from topomt.third_party._execution import ProviderExecutionError

    try:
        yield
    except ProviderExecutionError as error:
        error.execution_metadata = deepcopy(metadata)
        error.additional_inputs = dict(additional)
        raise


def validate_inputs(run: ProviderRun, required: tuple[str, ...]) -> None:
    """Check the captured inputs rather than reopening producer-machine paths."""
    if run.metadata.get('adapter_protocol') != 'topomt.original-local@1':
        return
    identities = run.metadata.get('input_fingerprints')
    if not isinstance(identities, dict) or set(identities) != set(required):
        raise ValueError('Specialist original input fingerprints are absent')
    for name, digest in identities.items():
        try:
            original = run.get_artifact('input/' + name)
        except KeyError as cause:
            raise ValueError('Specialist original captured input is absent') from cause
        if hashlib.sha256(original).hexdigest() != digest:
            raise ValueError('Specialist original input fingerprint disagrees')
