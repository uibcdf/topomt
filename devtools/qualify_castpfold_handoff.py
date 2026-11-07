"""Explicit prepare/submit/collect phases for a bounded original CASTpFold handoff.

The full reference source retains its chemistry. Only protein-heavy geometry
from frame 1 is submitted; the original server owns the pocket calculation.
"""

import argparse
import base64
import hashlib
import json
import math
import re
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any

import molsysmt as msm
import numpy as np

import topomt as tmt
from devtools.provider_handoff import (
    chemical_state_context,
    pocket_outputs_agree,
    prepare_reference_source,
)
from topomt.provider_output import ProviderRun
from topomt.third_party._common import prepare_wrapper_input_pdb
from topomt.third_party._saved_json import read_json
from topomt.third_party.castp._source import _validate_map
from topomt.third_party.castp.servers.castpfold import SUBMIT_URL, CastpFoldClient
from topomt.third_party.pdb_context import (
    reference_chemical_context,
    source_input_context,
)

PROFILE = 'original-castpfold-source-handoff-1'
REFERENCE_SEED_SHA256 = (
    'a42ef9868578ba16c62d52a1267d24160b973dca0d50dbc804ca46b6b2fe316a'
)
ARTIFACTS = ('source.h5msm', 'input.pdb', 'map.json', 'readiness.json')


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: Any) -> None:
    def plain(item):
        if isinstance(item, np.ndarray):
            return item.tolist()
        if isinstance(item, np.generic):
            return item.item()
        raise TypeError(type(item).__name__)

    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False, default=plain)
        stream.write('\n')


def _read(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f'Invalid handoff artifact: {path.name}')
    value = read_json(path.read_bytes(), provider='CASTpFold handoff')
    if not isinstance(value, dict):
        raise ValueError(f'Invalid handoff receipt: {path.name}')
    return value


def _rows(data: bytes) -> list[str]:
    return [
        line
        for line in data.decode().splitlines()
        if line.startswith(('ATOM  ', 'HETATM'))
    ]


def _prepared(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    receipt = _read(root / 'preflight.json')
    checks = receipt.get('checks')
    artifacts = receipt.get('artifacts')
    state = receipt.get('chemical_state')
    if (
        root.is_symlink()
        or type(receipt.get('schema_version')) is not int
        or receipt['schema_version'] != 1
        or receipt.get('profile') != PROFILE
        or receipt.get('server') != 'castpfold'
        or type(receipt.get('structure_index')) is not int
        or receipt['structure_index'] != 1
        or not isinstance(state, dict)
        or set(state) != {'count', 'reference_index'}
        or any(type(value) is not int for value in state.values())
        or state != {'count': 1, 'reference_index': 0}
        or not isinstance(checks, dict)
        or not checks
        or any(value is not True for value in checks.values())
        or not isinstance(artifacts, dict)
        or set(artifacts) != set(ARTIFACTS)
    ):
        raise ValueError('Invalid CASTpFold preflight profile or artifacts.')
    for name in ARTIFACTS:
        path = root / name
        if (
            path.is_symlink()
            or not path.is_file()
            or receipt['artifacts'][name] != _hash(path)
        ):
            raise ValueError(f'Changed or invalid handoff artifact hash: {name}')
    mapping = _read(root / 'map.json')
    rows = _rows((root / 'input.pdb').read_bytes())
    indices = mapping.get('row_to_source')
    limit = receipt.get('n_source_atoms')
    if (
        type(limit) is not int
        or limit <= 0
        or not isinstance(indices, list)
        or not indices
        or any(type(index) is not int or not 0 <= index < limit for index in indices)
        or len(set(indices)) != len(indices)
        or len(rows) != len(indices)
        or receipt.get('selection') != indices
        or mapping.get('serial_to_source')
        != {str(int(row[6:11])): index for row, index in zip(rows, indices)}
        or len({int(row[6:11]) for row in rows}) != len(rows)
    ):
        raise ValueError('Invalid submitted CASTpFold atom map.')
    return receipt, mapping


def prepare(input_file: Path, output_dir: Path) -> dict[str, Any]:
    """Persist a full source, explicitly selected heavy PDB/map and diagnostics.

    Parameters
    ----------
    input_file : Path
        Single-frame source accepted by prepare_reference_source.
    output_dir : Path
        New directory. No server is contacted or chemistry repaired.

    Returns
    -------
    dict
        Hashed preflight with frame 1 and existing reference state zero.

    Raises
    ------
    FileExistsError
        If output_dir exists.
    ValueError
        If source admission, heavy selection or exact PDB identity fails.
    """
    if output_dir.exists() or output_dir.is_symlink():
        raise FileExistsError(output_dir)
    source, protein = prepare_reference_source(input_file)
    heavy = set(msm.select(source, selection="atom_type != 'H'"))
    selection = [int(index) for index in protein if index in heavy]
    if not selection or chemical_state_context(source) != {
        'count': 1,
        'reference_index': 0,
    }:
        raise ValueError(
            'The profile requires protein-heavy atoms and reference state zero.'
        )
    output_dir.mkdir(parents=True, exist_ok=False)
    pdb, indices = prepare_wrapper_input_pdb(
        source,
        tmpdir=output_dir,
        selection=selection,
        structure_indices=1,
        syntax='MolSysMT',
    )
    indices = [int(index) for index in indices]
    _validate_map(source, pdb, indices, selection=selection, frame=1, syntax='MolSysMT')
    msm.convert(
        source, to_form='file:h5msm', output_filename=output_dir / 'source.h5msm'
    )
    readiness = msm.physchem.get_chemical_readiness(
        source, selection=selection, structure_indices=1, chemical_state=0
    )
    _write(output_dir / 'readiness.json', readiness)
    _write(
        output_dir / 'map.json',
        {
            'row_to_source': indices,
            'serial_to_source': {
                str(int(row[6:11])): index
                for row, index in zip(_rows(pdb.read_bytes()), indices)
            },
        },
    )
    receipt = {
        'schema_version': 1,
        'profile': PROFILE,
        'server': 'castpfold',
        'selection_profile': 'protein intersection atom_type != H; full source unchanged',
        'selection': indices,
        'n_source_atoms': int(msm.get(source, n_atoms=True)),
        'structure_index': 1,
        'chemical_state': chemical_state_context(source),
        'input_sha256': _hash(input_file),
        'reference_seed_sha256': REFERENCE_SEED_SHA256,
        'checks': {
            'declared_heavy_selection': True,
            'pdb_identity_and_coordinates': True,
            'existing_reference_state': True,
        },
        'artifacts': {name: _hash(output_dir / name) for name in ARTIFACTS},
        'diagnostic_limits': 'Missing stored bond orders and duplicate native IDs remain visible in readiness.json. MolSysMT supplies effective aromatic multiplicity for declared aromatic bonds. Neither this report nor earlier bounded PharmacophoreMT receiving is a universal chemical certificate.',
    }
    _write(output_dir / 'preflight.json', receipt)
    _prepared(output_dir)
    return receipt


def submit(output_dir: Path) -> str:
    """Explicitly POST once, retaining the client's acknowledgement or failure.

    Parameters
    ----------
    output_dir : Path
        Prepare output. Any submission.json prevents another POST.

    Returns
    -------
    str
        Accepted job ID; completion is not implied.

    Raises
    ------
    FileExistsError
        If a marker exists, including after failure or uncertain delivery.
    ValueError
        If preflight artifacts changed.
    OSError
        If transport fails; the client's no-repeat marker remains authoritative.
    """
    marker = output_dir / 'submission.json'
    if marker.exists() or marker.is_symlink():
        raise FileExistsError(marker)
    _prepared(output_dir)
    return CastpFoldClient().submit(
        output_dir / 'input.pdb', probe_radius=1.4, email='N/A', submission_file=marker
    )


def collect(output_dir: Path) -> dict[str, Any]:
    """GET a known job and verify its source-bound, persisted original output.

    Parameters
    ----------
    output_dir : Path
        Prepare output with the original schema-1 submission receipt.

    Returns
    -------
    dict
        Standard source-handoff receipt with literal-True checks.

    Raises
    ------
    ValueError
        If receipts, hashes, atom coverage or public recovery disagree.
    FileExistsError
        If the final receipt already exists. An identical saved bundle resumes.
    RuntimeError
        If the original result is not ready. Collection never submits.
    """
    if (output_dir / 'receipt.json').exists() or (
        output_dir / 'receipt.json'
    ).is_symlink():
        raise FileExistsError('CASTpFold handoff is already recorded.')
    if (output_dir / 'original.zip').is_symlink():
        raise ValueError('Invalid original bundle artifact.')
    preflight, mapping = _prepared(output_dir)
    submission = _read(output_dir / 'submission.json')
    jobid = submission.get('jobid')
    pdb = output_dir / 'input.pdb'
    acknowledgement = submission.get('acknowledgement')
    parameters = submission.get('parameters')
    if not isinstance(parameters, dict):
        raise ValueError('Invalid CASTpFold submission parameters.')
    probe = parameters.get('probe_radius')
    if not isinstance(probe, dict):
        raise ValueError('Invalid CASTpFold submission parameters.')
    if (
        type(submission.get('schema_version')) is not int
        or submission['schema_version'] != 1
        or submission.get('provider') != 'castp'
        or submission.get('server') != 'castpfold'
        or submission.get('endpoint') != SUBMIT_URL
        or submission.get('state') != 'submitted_pending'
        or not isinstance(jobid, str)
        or re.fullmatch(r'j_[A-Za-z0-9_]+', jobid) is None
        or not isinstance(acknowledgement, dict)
        or acknowledgement.get('success') is not True
        or acknowledgement.get('jobid') != jobid
        or submission.get('input_pdb')
        != {'filename': 'input.pdb', 'bytes': pdb.stat().st_size, 'sha256': _hash(pdb)}
        or type(probe.get('value')) not in (int, float)
        or not math.isfinite(probe['value'])
        or not 0 <= probe['value'] <= 5
        or probe['value'] != 1.4
        or probe.get('unit') != 'angstroms'
        or parameters.get('email') != 'N/A'
    ):
        raise ValueError('Invalid or incompatible CASTpFold submission receipt.')
    http = submission.get('http')
    if (
        not isinstance(http, dict)
        or type(http.get('status')) is not int
        or not 200 <= http['status'] < 300
    ):
        raise ValueError('Invalid CASTpFold submission HTTP acknowledgement.')
    try:
        raw_ack = base64.b64decode(http['response_base64'], validate=True)
        decoded = read_json(raw_ack, provider='CASTpFold submission acknowledgement')
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(
            'Invalid CASTpFold submission acknowledgement bytes.'
        ) from error
    if hashlib.sha256(raw_ack).hexdigest() != http.get('response_sha256') or json.dumps(
        decoded, sort_keys=True
    ) != json.dumps(acknowledgement, sort_keys=True):
        raise ValueError('CASTpFold submission acknowledgement integrity disagrees.')
    result = output_dir / 'result.zip'
    download_file = output_dir / 'download.json'
    if result.exists() or result.is_symlink():
        download = _read(download_file)
        if result.is_symlink() or download != {'jobid': jobid, 'sha256': _hash(result)}:
            raise ValueError('Changed CASTpFold result artifact hash.')
    else:
        if download_file.exists() or download_file.is_symlink():
            raise ValueError('Missing CASTpFold result artifact.')
        raw = CastpFoldClient().download_result_zip_bytes(
            jobid, wait=0, extra_wait=0, retries=0
        )
        with result.open('xb') as stream:
            stream.write(raw)
        _write(download_file, {'jobid': jobid, 'sha256': _hash(result)})
    with zipfile.ZipFile(BytesIO(result.read_bytes())) as archive:
        candidates = [name for name in archive.namelist() if name.endswith('.pdb')]
        if len(candidates) != 1:
            raise ValueError('The result requires exactly one original PDB.')
        serials = [str(int(row[6:11])) for row in _rows(archive.read(candidates[0]))]
    known = mapping['serial_to_source']
    if len(serials) != len(known) or set(serials) != set(known):
        raise ValueError('The result must preserve every submitted atom exactly once.')
    returned = [known[serial] for serial in serials]
    source_file = output_dir / 'source.h5msm'
    source = msm.convert(source_file, to_form='molsysmt.MolSys')
    before = (
        source_input_context(source, 1),
        reference_chemical_context(source, 0, provider='CASTpFold'),
    )
    original = tmt.get_provider_output(
        source,
        method='castpfold',
        backend='files',
        zip_file=result,
        source_atom_indices=returned,
        selection=returned,
        structure_indices=1,
        chemical_state=0,
        provider_jobid=jobid,
        probe_radius=probe['value'],
    )
    bundle = output_dir / 'original.zip'
    if bundle.exists():
        if ProviderRun.load(bundle) != original.run:
            raise ValueError(
                'Existing original bundle disagrees with reconstructed run.'
            )
    else:
        original.run.save(bundle)
    after = (
        source_input_context(source, 1),
        reference_chemical_context(source, 0, provider='CASTpFold'),
    )
    restored = msm.convert(source_file, to_form='molsysmt.MolSys')
    recovered = tmt.get_provider_output(
        restored, method='castpfold', backend='files', bundle_file=bundle
    )
    run = ProviderRun.load(bundle)
    checks = {
        'nonempty_pockets': bool(original.pockets),
        'all_submitted_atoms_preserved': True,
        'public_source_bound_import': True,
        'bundle_identity': run == original.run == recovered.run,
        'persisted_recovery': bool(pocket_outputs_agree(original, recovered)),
        'source_unchanged': _hash(source_file) == preflight['artifacts']['source.h5msm']
        and before == after,
        'independent_source_readback': before
        == (
            source_input_context(restored, 1),
            reference_chemical_context(restored, 0, provider='CASTpFold'),
        ),
        'existing_reference_state': chemical_state_context(restored)
        == {'count': 1, 'reference_index': 0},
        'original_server_identity': run.provider == 'castp'
        and run.backend == 'files'
        and run.metadata.get('server') == 'castpfold',
    }
    if any(value is not True for value in checks.values()):
        raise ValueError(f'CASTpFold handoff checks failed: {checks}')
    receipt = {
        'profile': PROFILE,
        'provider': run.provider,
        'backend': run.backend,
        'server': 'castpfold',
        'jobid': jobid,
        'probe_radius': probe,
        'run_id': run.run_id,
        'source_sha256': _hash(source_file),
        'original_bundle_sha256': _hash(bundle),
        'result_zip_sha256': _hash(result),
        'input_sha256': preflight['input_sha256'],
        'selection': returned,
        'structure_index': 1,
        'chemical_state': chemical_state_context(source),
        'pocket_count': len(original.pockets),
        'checks': checks,
        'limitations': [
            'Source control, not installed-package qualification.',
            'Explicit protein-heavy geometry; full prepared chemistry is retained without repair.',
            'Original evidence and bounded recovery, not universal chemical certification.',
        ],
    }
    _write(output_dir / 'receipt.json', receipt)
    return receipt


def main() -> None:
    """Run one explicit phase; collection never performs submission."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('prepare', 'submit', 'collect'))
    parser.add_argument('output_dir', type=Path)
    parser.add_argument('--input-file', type=Path)
    args = parser.parse_args()
    if args.phase == 'prepare':
        if args.input_file is None:
            parser.error('prepare requires --input-file')
        result = prepare(args.input_file, args.output_dir)
    else:
        result = (
            {'jobid': submit(args.output_dir)}
            if args.phase == 'submit'
            else collect(args.output_dir)
        )
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
