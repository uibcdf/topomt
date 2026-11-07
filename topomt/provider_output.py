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
    if not isinstance(name, str) or not name or '\0' in name:
        raise ValueError(f'Unsafe provider artifact name: {name!r}')
    path = PurePosixPath(name)
    if (
        name.startswith('/')
        or '\\' in name
        or any(part in ('.', '..') for part in name.split('/'))
        or path.parts[0] not in ('input', 'output')
        or len(path.parts) < 2
        or path.as_posix() != name
    ):
        raise ValueError(f'Unsafe provider artifact name: {name!r}')


def _validate_run_context(provider: Any, backend: Any, metadata: Any) -> None:
    for name, value in (('provider', provider), ('backend', backend)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'Provider bundle {name} must be a nonempty string.')
    if not isinstance(metadata, dict):
        raise ValueError('Provider bundle metadata must be a JSON object.')


def _validate_sha256(value: Any) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in '0123456789abcdef' for character in value)
    ):
        raise ValueError('Provider bundle checksum must be a lowercase SHA-256 string.')


def _validate_manifest(manifest: Any) -> dict[str, Any]:
    required = {
        'schema_version',
        'provider',
        'backend',
        'metadata',
        'artifacts',
        'run_id',
    }
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise ValueError('Provider bundle manifest has missing or unexpected fields.')
    if type(manifest['schema_version']) is not int or manifest['schema_version'] != 1:
        raise ValueError('Provider bundle requires literal integer schema version 1.')
    _validate_run_context(
        manifest['provider'], manifest['backend'], manifest['metadata']
    )
    if not isinstance(manifest['artifacts'], dict):
        raise ValueError('Provider bundle artifacts must be a checksum object.')
    for name, checksum in manifest['artifacts'].items():
        _validate_artifact_name(name)
        _validate_sha256(checksum)
    _validate_sha256(manifest['run_id'])
    return manifest


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
        *,
        additional_inputs: dict[str, str | Path] | None = None,
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
        additional_inputs : dict, optional
            Additional submitted files keyed by their relative names under
            ``input/``, for example ``{'binder/ligand.pdb': ligand_path}``.

        Returns
        -------
        ProviderRun
            Independent snapshot with a content-derived run ID.

        Raises
        ------
        ValueError
            If an output entry is a symbolic link, or an artifact name is unsafe
            or duplicates the primary input.
        """
        metadata = {} if metadata is None else metadata
        _validate_run_context(provider, backend, metadata)
        input_path = Path(input_file)
        output_path = Path(output_dir)
        artifacts = [(f'input/{input_path.name}', input_path.read_bytes())]
        for relative_name, additional_path in (additional_inputs or {}).items():
            name = f'input/{relative_name}'
            if not relative_name or any(not part for part in relative_name.split('/')):
                raise ValueError(f'Unsafe provider artifact name: {name!r}')
            _validate_artifact_name(name)
            if name == artifacts[0][0]:
                raise ValueError(f'Duplicate provider input artifact: {name}')
            artifacts.append((name, Path(additional_path).read_bytes()))
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
        metadata_json = _canonical_json(metadata)
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
        _validate_manifest(manifest)
        body = {key: value for key, value in manifest.items() if key != 'run_id'}
        if _digest(_canonical_json(body).encode('utf-8')) != self.run_id:
            raise ValueError('Provider bundle manifest checksum mismatch.')
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
        # A top-level import would cycle through third_party's API imports while
        # Topography is importing ProviderRun. Reuse the strict reader at load time.
        from .third_party._saved_json import read_json

        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            if any(member.orig_filename != member.filename for member in members):
                raise ValueError('Unsafe provider archive member name.')
            names = [member.filename for member in members]
            if len(names) != len(set(names)) or 'manifest.json' not in names:
                raise ValueError('Provider bundle has duplicate names or no manifest')
            manifest = _validate_manifest(
                read_json(archive.read('manifest.json'), provider='ProviderRun')
            )
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
    original_value: int | float | list[float]
    original_unit: str
    source_field: str
    source_artifact: str
    run_id: str
    definition: str
    issue_url: str | None
    status: str = 'external_only'
