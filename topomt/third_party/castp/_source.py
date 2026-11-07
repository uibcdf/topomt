"""Explicit source correspondence for retained original CASTp file evidence."""

import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import molsysmt as msm
import numpy as np

from topomt.io.load_CASTp import (
    _discover_castp_files_in_dir,
    _extract_castp_archive,
    load_CASTp,
)
from topomt.provider_output import ProviderRun
from topomt.third_party._common import validate_single_frame_pdb
from topomt.third_party._saved_json import read_json
from topomt.third_party.output import _from_topography
from topomt.third_party.pdb_context import (
    reference_chemical_context,
    source_input_context,
    validate_reference_chemical_context,
    validate_source_input_context,
    validate_submitted_pdb,
)

from .output import CASTpOutput

CONTEXT_ARTIFACT = 'output/topomt_source_context.json'
FILE_ARGUMENTS = {
    'poc': 'poc_file',
    'poc_info': 'pocInfo_file',
    'mouth': 'mouth_file',
    'mouth_info': 'mouthInfo_file',
    'pdb': 'pdb_file',
}


def _restore(run: ProviderRun, root: Path) -> Path:
    # Reuse archive admission without recapturing or changing the retained run.
    bundle = root / 'retained.zip'
    run.save(bundle)
    destination = root / 'materialized'
    destination.mkdir()
    _extract_castp_archive(bundle, str(destination))
    _verify_original_archive(run, destination, root)
    return destination


def _verify_original_archive(run: ProviderRun, destination: Path, root: Path) -> None:
    candidates = [
        name
        for name, _ in run.artifacts
        if name.startswith('input/') and zipfile.is_zipfile(destination / name)
    ]
    if not candidates:
        candidates = [
            name
            for name, _ in run.artifacts
            if name.startswith('output/raw_server_zip/') and name.endswith('.zip')
        ]
    if not candidates:
        return
    if len(candidates) != 1:
        raise ValueError('CASTp original ZIP witness is ambiguous.')
    original = root / 'original_archive'
    original.mkdir()
    _extract_castp_archive(destination / candidates[0], str(original))
    expected = {
        'output/' + path.relative_to(original).as_posix(): path.read_bytes()
        for path in original.rglob('*')
        if path.is_file()
    }
    actual = {
        name: data
        for name, data in run.artifacts
        if name.startswith('output/')
        and name != CONTEXT_ARTIFACT
        and name not in candidates
    }
    if expected != actual:
        raise ValueError('CASTp original ZIP and retained output artifacts disagree.')


def _result_files(output: Path) -> dict[str, str]:
    return {
        key: 'output/' + path.relative_to(output).as_posix()
        for key, path in _discover_castp_files_in_dir(output).items()
    }


def _file_selection(run: ProviderRun, files: Any) -> dict[str, str]:
    if (
        not isinstance(files, dict)
        or not set(files).issubset(FILE_ARGUMENTS)
        or 'pdb' not in files
        or not set(files) - {'pdb'}
    ):
        raise ValueError('Invalid CASTp result artifact selection.')
    for name in files.values():
        if not isinstance(name, str) or not name.startswith('output/'):
            raise ValueError('Invalid CASTp result artifact path.')
        try:
            run.get_artifact(name)
        except KeyError as error:
            raise ValueError('CASTp selected result artifact is absent.') from error
    if len(set(files.values())) != len(files):
        raise ValueError('CASTp result roles require distinct artifacts.')
    return files


def _indices(value: Any, limit: int) -> list[int]:
    if (
        not isinstance(value, (list, tuple, range, np.ndarray))
        or np.asarray(value).ndim != 1
        or not len(value)
        or any(
            not isinstance(i, (int, np.integer))
            or isinstance(i, (bool, np.bool_))
            or not 0 <= int(i) < limit
            for i in value
        )
        or len(set(value)) != len(value)
    ):
        raise ValueError(
            'Invalid CASTp source atom map; unique integer indices are required.'
        )
    return [int(i) for i in value]


def _frame(source: Any, value: Any) -> int:
    from topomt._private.arg_digestion.external_arguments import (
        digest_structure_indices,
    )

    value = digest_structure_indices(value)
    if value is None or isinstance(value, str):
        if msm.get(source, n_structures=True) != 1:
            raise ValueError(
                'CASTp source binding requires one explicit coordinate frame.'
            )
        return 0
    return int(value) if isinstance(value, (int, np.integer)) else int(value[0])


def _pdb_rows(path: Path) -> list[str]:
    return [
        r for r in path.read_text().splitlines() if r.startswith(('ATOM  ', 'HETATM'))
    ]


def _identity(row: str) -> tuple[str, str, str]:
    return row[:6], row[6:11], row[12:27]


def _coordinates(row: str) -> np.ndarray:
    values = np.asarray([float(row[i : i + 8]) for i in (30, 38, 46)])
    if not np.isfinite(values).all():
        raise ValueError('CASTp PDB and membership coordinates must be finite.')
    return values


def _validate_rows(root: Path, files: dict[str, str]) -> Any:
    if 'pdb' not in files:
        raise ValueError('CASTp source binding requires the original result PDB.')
    pdb = root / files['pdb']
    validate_single_frame_pdb(pdb, provider='CASTp')
    rows = _pdb_rows(pdb)
    if any(row[16:17].strip() or row[26:27].strip() for row in rows):
        raise ValueError(
            'CASTp bound profile does not admit alternate-location or insertion-code rows.'
        )
    by_serial = {int(row[6:11]): row for row in rows}
    if len(by_serial) != len(rows):
        raise ValueError('CASTp result PDB serials must be unique.')
    for key in ('poc', 'mouth'):
        if key not in files:
            continue
        seen = set()
        for row in (root / files[key]).read_text().splitlines():
            if not row.strip():
                continue
            serial = int(row[6:11])
            original = by_serial.get(serial)
            if (
                original is None
                or _identity(row) != _identity(original)
                or not np.allclose(
                    _coordinates(row), _coordinates(original), rtol=0, atol=0.00051
                )
            ):
                raise ValueError(
                    'CASTp membership row disagrees with its original PDB identity or coordinates.'
                )
            record = (int(row[66:70]), serial)
            if record in seen:
                raise ValueError('Duplicate CASTp membership row.')
            seen.add(record)
    for key in ('poc_info', 'mouth_info'):
        if key in files:
            lines = [
                row.split()
                for row in (root / files[key]).read_text().splitlines()
                if row.strip()
            ]
            identifiers = [int(row[2]) for row in lines[1:]]
            if len(set(identifiers)) != len(identifiers):
                raise ValueError('Duplicate CASTp measurement row ID.')
    archive_source = msm.convert(
        pdb, to_form='molsysmt.MolSys', get_missing_bonds=False
    )
    validate_submitted_pdb(
        archive_source,
        pdb,
        list(range(len(rows))),
        selection='all',
        structure_indices=0,
        syntax='MolSysMT',
    )
    return archive_source


def _validate_map(
    source: Any,
    pdb: Path,
    indices: list[int],
    *,
    selection: Any,
    frame: int,
    syntax: str,
) -> None:
    validate_submitted_pdb(
        source,
        pdb,
        indices,
        selection=selection,
        structure_indices=frame,
        syntax=syntax,
    )
    attributes = msm.get(
        source,
        element='atom',
        selection=indices,
        output_type='dictionary',
        get_missing_bonds=False,
        atom_name=True,
        atom_type=True,
        group_id=True,
        group_name=True,
        chain_id=True,
    )
    for i, row in enumerate(_pdb_rows(pdb)):
        expected = {
            'atom_name': row[12:16].strip(),
            'group_id': row[22:26].strip(),
            'group_name': row[17:20].strip(),
            'chain_id': row[21:22].strip(),
        }
        if any(
            attributes[name] is None or str(attributes[name][i]) != value
            for name, value in expected.items()
        ):
            raise ValueError(
                'CASTp source atom map disagrees with PDB atom/residue/chain identity.'
            )
        element = row[76:78].strip()
        if element and (
            attributes['atom_type'] is None
            or str(attributes['atom_type'][i]).upper() != element.upper()
        ):
            raise ValueError(
                'CASTp source atom map disagrees with the declared PDB element.'
            )


def _output(
    run: ProviderRun,
    root: Path,
    source: Any,
    archive_source: Any,
    indices: list[int],
    frame: int,
) -> CASTpOutput:
    topography = load_CASTp(
        molecular_system=archive_source,
        _provider_run=run,
        _artifact_root=root / 'output',
        **{
            FILE_ARGUMENTS[key]: root / name
            for key, name in run.metadata['result_artifacts'].items()
        },
    )
    return _from_topography(
        topography,
        CASTpOutput,
        source_molecular_system=source,
        source_structure_indices=frame,
        atom_index_map=tuple(indices),
    )


def _bind(
    run: ProviderRun,
    source: Any,
    source_atom_indices: Any,
    *,
    selection: Any,
    structure_indices: Any,
    syntax: str,
    chemical_state: str | int,
    result_artifacts: dict[str, str] | None = None,
) -> CASTpOutput:
    if run.provider != 'castp' or run.backend != 'files':
        raise ValueError('CASTp binding requires an original files import.')
    frame = _frame(source, structure_indices)
    context = source_input_context(source, frame)
    chemistry = reference_chemical_context(source, chemical_state, provider='CASTp')
    indices = _indices(source_atom_indices, context['n_atoms'])
    with tempfile.TemporaryDirectory(prefix='topomt_castp_binding_') as folder:
        root = _restore(run, Path(folder))
        mode = 'discovered' if result_artifacts is None else 'explicit'
        files = (
            _result_files(root / 'output')
            if result_artifacts is None
            else _file_selection(run, result_artifacts)
        )
        archive_source = _validate_rows(root, files)
        _validate_map(
            source,
            root / files['pdb'],
            indices,
            selection=selection,
            frame=frame,
            syntax=syntax,
        )
        supplement = root / CONTEXT_ARTIFACT
        if supplement.exists():
            raise ValueError(
                'CASTp output already contains the reserved source context artifact.'
            )
        supplement.write_text(json.dumps(context, sort_keys=True, allow_nan=False))
        metadata = run.metadata
        metadata.update(
            {
                'source_binding_protocol': 1,
                'source_context_artifact': CONTEXT_ARTIFACT,
                'reference_pdb_artifact': files['pdb'],
                'result_artifacts': files,
                'result_artifact_selection': mode,
                'source_atom_indices': indices,
                'selection': selection
                if isinstance(selection, str)
                else [int(i) for i in selection],
                'structure_indices': [frame],
                'syntax': syntax,
                'chemical_state_context': chemistry,
            }
        )
        inputs = [name for name, _ in run.artifacts if name.startswith('input/')]
        if len(inputs) != 1:
            raise ValueError(
                'CASTp files binding requires exactly one original input artifact.'
            )
        bound = ProviderRun.capture(
            'castp', 'files', root / inputs[0], root / 'output', metadata=metadata
        )
        return _output(bound, root, source, archive_source, indices, frame)


def _recover(
    run: ProviderRun, source: Any, provider_server: str | None = None
) -> CASTpOutput:
    from topomt._private.arg_digestion.external_arguments import (
        digest_selection,
        digest_syntax,
    )

    metadata = run.metadata
    required = {
        'source_binding_protocol',
        'source_context_artifact',
        'reference_pdb_artifact',
        'result_artifacts',
        'result_artifact_selection',
        'source_atom_indices',
        'selection',
        'structure_indices',
        'syntax',
        'chemical_state_context',
    }
    if (
        run.provider != 'castp'
        or run.backend != 'files'
        or not required.issubset(metadata)
    ):
        raise ValueError('CASTp recovery requires a source-bound original files run.')
    if (
        type(metadata['source_binding_protocol']) is not int
        or metadata['source_binding_protocol'] != 1
        or metadata['source_context_artifact'] != CONTEXT_ARTIFACT
    ):
        raise ValueError('Invalid CASTp source-binding protocol or context artifact.')
    if provider_server is not None and provider_server != metadata.get('server'):
        raise ValueError('Requested CASTp server disagrees with the retained run.')
    saved_frame = metadata['structure_indices']
    if (
        not isinstance(saved_frame, list)
        or len(saved_frame) != 1
        or type(saved_frame[0]) is not int
        or saved_frame[0] < 0
    ):
        raise ValueError('Invalid CASTp saved source frame.')
    frame = saved_frame[0]
    selection = digest_selection(metadata['selection'])
    syntax = digest_syntax(metadata['syntax'])
    validate_reference_chemical_context(
        source, metadata['chemical_state_context'], provider='CASTp'
    )
    try:
        context = read_json(run.get_artifact(CONTEXT_ARTIFACT), provider='CASTp')
    except KeyError as error:
        raise ValueError('CASTp saved source context artifact is absent.') from error
    if not isinstance(context, dict):
        raise ValueError('Invalid CASTp full-source context.')
    validate_source_input_context(source, context, frame)
    if not isinstance(metadata['source_atom_indices'], list):
        raise ValueError('Invalid CASTp saved atom map schema.')
    indices = _indices(metadata['source_atom_indices'], context['n_atoms'])
    with tempfile.TemporaryDirectory(prefix='topomt_castp_recovery_') as folder:
        root = _restore(run, Path(folder))
        files = _file_selection(run, metadata['result_artifacts'])
        mode = metadata['result_artifact_selection']
        if (
            mode not in ('discovered', 'explicit')
            or mode == 'discovered'
            and files != _result_files(root / 'output')
        ):
            raise ValueError('CASTp saved result selection mode or family disagrees.')
        if metadata['result_artifacts'] != files or metadata[
            'reference_pdb_artifact'
        ] != files.get('pdb'):
            raise ValueError('CASTp saved result artifact selection disagrees.')
        archive_source = _validate_rows(root, files)
        _validate_map(
            source,
            root / files['pdb'],
            indices,
            selection=selection,
            frame=frame,
            syntax=syntax,
        )
        return _output(run, root, source, archive_source, indices, frame)
