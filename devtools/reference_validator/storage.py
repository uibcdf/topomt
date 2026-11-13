"""Append-only proof bundles with a checksum manifest published last.

An interrupted/partial directory is rejected. Previous step directories are
never replaced. This is a verified commit-marker protocol, not a guarantee of
filesystem durability against every operating-system or storage failure.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .model import Model, _record
from .verify.records import verify_run


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON field: {key}')
        result[key] = value
    return result


def _payload(path: Path) -> bytes:
    with path.open('rb') as stream:
        data = stream.read(16 * 1024**2 + 1)
    if len(data) > 16 * 1024**2:
        raise ValueError('Pilot input exceeds 16 MiB limit')
    return data


def read_record(path: Path) -> Any:
    """Read bounded JSON, rejecting duplicate fields before interpreting it."""
    return read_record_with_digest(path)[0]


def read_record_with_digest(path: Path) -> tuple[Any, str]:
    """Bind the parsed record to the exact bytes that were read once."""
    data = _payload(path)
    return json.loads(data, object_pairs_hook=_unique), hashlib.sha256(data).hexdigest()


def save_bundle(directory: Path, model: Model, checkpoint: object, run: object) -> None:
    """Verify and exclusively create a new checkpoint/run bundle.

    The manifest is written after all data files are flushed. Interrupted
    directories stay visible but cannot be loaded as successful checkpoints.
    Existing directories, even empty ones, are not overwritten.
    """
    verify_run(model, run, checkpoint)
    directory.mkdir(parents=True, exist_ok=False)
    files = {}
    for name, value in (('checkpoint.json', checkpoint), ('run.json', run)):
        payload = (
            json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n'
        ).encode()
        with (directory / name).open('xb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        files[name] = hashlib.sha256(payload).hexdigest()
    manifest = {'schema': 'topomt.reference-validator.bundle/1', 'files': files}
    with (directory / 'MANIFEST.json').open('x') as stream:
        json.dump(manifest, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def load_bundle(directory: Path, model: Model) -> tuple[dict[str, Any], dict[str, Any]]:
    """Require complete storage integrity and independent proof verification."""
    try:
        manifest = _record(
            read_record(directory / 'MANIFEST.json'), {'schema', 'files'}
        )
        if manifest['schema'] != 'topomt.reference-validator.bundle/1':
            raise ValueError('Unsupported bundle schema')
        files = _record(manifest['files'], {'checkpoint.json', 'run.json'})
        records = {}
        for name, expected in files.items():
            payload = _payload(directory / name)
            if hashlib.sha256(payload).hexdigest() != expected:
                raise ValueError('Incomplete or changed checkpoint bundle')
            # Interpret precisely the bytes whose digest was checked, even if
            # another process later replaces the file in this directory.
            records[name] = json.loads(payload, object_pairs_hook=_unique)
        checkpoint, run = records['checkpoint.json'], records['run.json']
        verify_run(model, run, checkpoint)
        return checkpoint, run
    except OSError as exc:
        raise ValueError('Incomplete checkpoint bundle') from exc
