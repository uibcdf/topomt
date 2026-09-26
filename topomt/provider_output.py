"""Portable records of original third-party results and attributed measurements."""

import hashlib
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validate_artifact_name(name: str) -> None:
    path = PurePosixPath(name)
    if (
        not name
        or name.startswith('/')
        or '\\' in name
        or any(part in ('.', '..') for part in name.split('/'))
        or path.parts[0] not in ('input', 'output')
        or len(path.parts) < 2
    ):
        raise ValueError(f'Unsafe provider artifact name: {name!r}')


@dataclass(frozen=True)
class ProviderRun:
    """An immutable in-memory snapshot of a provider's input and output files."""

    provider: str
    backend: str
    run_id: str
    artifacts: tuple[tuple[str, bytes], ...]
    metadata_json: str

    @property
    def metadata(self) -> dict[str, Any]:
        """Return a separate copy of the JSON-compatible run metadata."""
        return json.loads(self.metadata_json)

    @classmethod
    def capture(
        cls,
        provider: str,
        backend: str,
        input_file: str | Path,
        output_dir: str | Path,
        metadata: dict[str, Any] | None = None,
    ) -> 'ProviderRun':
        """Read original files into memory before their directories disappear.

        Parameters
        ----------
        provider : str
            External program name.
        backend : str
            Execution route, such as ``cli`` or ``files``.
        input_file : str or Path
            Exact structure submitted to the provider.
        output_dir : str or Path
            Directory containing the provider's original output files.
        metadata : dict, optional
            JSON-compatible run settings and atom mapping.

        Returns
        -------
        ProviderRun
            Independent snapshot with a content-derived run ID.

        Raises
        ------
        ValueError
            If an output entry is a symbolic link or has an unsafe name.
        """
        input_path = Path(input_file)
        output_path = Path(output_dir)
        artifacts = [(f'input/{input_path.name}', input_path.read_bytes())]
        for path in sorted(output_path.rglob('*')):
            if path.is_symlink():
                raise ValueError(f'Symbolic links cannot be captured: {path}')
            if path.is_file():
                artifacts.append(
                    (
                        f'output/{path.relative_to(output_path).as_posix()}',
                        path.read_bytes(),
                    )
                )
        for name, _ in artifacts:
            _validate_artifact_name(name)
        artifact_tuple = tuple(sorted(artifacts))
        metadata_json = _canonical_json(metadata or {})
        manifest = cls._manifest_without_id(
            provider, backend, artifact_tuple, metadata_json
        )
        run_id = _digest(_canonical_json(manifest).encode('utf-8'))
        return cls(provider, backend, run_id, artifact_tuple, metadata_json)

    @staticmethod
    def _manifest_without_id(
        provider: str,
        backend: str,
        artifacts: tuple[tuple[str, bytes], ...],
        metadata_json: str,
    ) -> dict[str, Any]:
        return {
            'schema_version': 1,
            'provider': provider,
            'backend': backend,
            'metadata': json.loads(metadata_json),
            'artifacts': {name: _digest(data) for name, data in artifacts},
        }

    def get_artifact(self, name: str) -> bytes:
        """Return original bytes for a named input or output artifact."""
        _validate_artifact_name(name)
        for artifact_name, data in self.artifacts:
            if artifact_name == name:
                return data
        raise KeyError(name)

    def save(self, path: str | Path) -> None:
        """Write a portable ZIP bundle with a checksum manifest."""
        manifest = self._manifest_without_id(
            self.provider, self.backend, self.artifacts, self.metadata_json
        )
        manifest['run_id'] = self.run_id
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('manifest.json', _canonical_json(manifest))
            for name, data in self.artifacts:
                archive.writestr(name, data)

    @classmethod
    def load(cls, path: str | Path) -> 'ProviderRun':
        """Recover a bundle after verifying file names, content, and run ID.

        Raises
        ------
        ValueError
            If the bundle is incomplete, modified, or has unsafe paths.
        """
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or 'manifest.json' not in names:
                raise ValueError('Provider bundle has duplicate names or no manifest')
            manifest = json.loads(archive.read('manifest.json'))
            expected = manifest['artifacts']
            if set(names) != {'manifest.json', *expected}:
                raise ValueError('Provider bundle has missing or unexpected artifacts')
            artifacts = []
            for name, checksum in sorted(expected.items()):
                _validate_artifact_name(name)
                data = archive.read(name)
                if _digest(data) != checksum:
                    raise ValueError(f'Provider artifact checksum mismatch: {name}')
                artifacts.append((name, data))
        without_id = {key: value for key, value in manifest.items() if key != 'run_id'}
        run_id = _digest(_canonical_json(without_id).encode('utf-8'))
        if run_id != manifest['run_id'] or manifest['schema_version'] != 1:
            raise ValueError('Provider bundle manifest checksum or schema mismatch')
        return cls(
            manifest['provider'],
            manifest['backend'],
            run_id,
            tuple(artifacts),
            _canonical_json(manifest['metadata']),
        )


@dataclass(frozen=True)
class ExternalMeasurement:
    """A reported value linked to its exact provider field and calculation issue."""

    value: Any
    original_value: int | float
    original_unit: str
    source_field: str
    source_artifact: str
    run_id: str
    definition: str
    issue_url: str | None
    status: str = 'external_only'
