"""Retain bounded hull/steric controls with independent saved-model checking."""

import argparse
import hashlib
import inspect
import json
import os
import resource
import subprocess
import sys
import time
from importlib.metadata import version
from pathlib import Path
from typing import Any

from .model import Model, decode_point, record_digest
from .producer import domain_certificate
from .receiving import freeze_hull_model
from .storage import read_record, read_record_with_digest
from .verify import verify


def _write(path: Path, value: object) -> None:
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def _name(value: object) -> str:
    if not isinstance(value, str) or not value or not value.replace('_', '').isalnum():
        raise ValueError('Invalid hull-steric profile/query name')
    return value


def _query(model: Model, row: dict[str, Any], directory: Path) -> dict[str, Any]:
    name = _name(row['name'])
    kind = row['kind']
    if kind == 'domain':
        cert = domain_certificate(model)
    else:
        cert = {
            'schema': 'topomt.reference-validator.certificate/1',
            'model_sha256': model.digest,
            'arithmetic': 'rational-exact/1',
            'kind': kind,
        }
        if kind == 'point':
            decode_point(row['point'])
            cert.update(point=row['point'], claim=row['claim'])
        elif kind == 'path':
            if (
                not isinstance(row['points'], list)
                or not 2 <= len(row['points']) <= 64
                or type(row['expected_acceptance']) is not bool
            ):
                raise ValueError('Invalid pilot path or point budget')
            for point in row['points']:
                decode_point(point)
            cert['points'] = row['points']
        else:
            raise ValueError('Unsupported hull-steric query kind')
    cert_file = directory / f'{name}.certificate.json'
    _write(cert_file, cert)
    saved = read_record(cert_file)
    expect_rejection = kind == 'path' and not row['expected_acceptance']
    try:
        checked = verify(model, saved)
    except ValueError as exc:
        if not expect_rejection or not str(exc).startswith('Path collides or leaves'):
            raise
        checked = {
            'verification_status': 'rejected_candidate',
            'model_sha256': model.digest,
            'certificate_sha256': record_digest(saved),
            'reason': str(exc),
            'scope': 'This candidate is invalid; no physical disconnection or empty free set is proved.',
        }
    else:
        if expect_rejection:
            raise ValueError('A negative path control unexpectedly passed')
        if kind == 'domain' and checked['domain_state'] != row['expected_state']:
            raise ValueError('Whole-domain control differs from the frozen expectation')
    _write(directory / f'{name}.verification.json', checked)
    return checked


def capture(protocol: Path, output: Path, *, originals: bool = False) -> None:
    """Save small controls and explicitly selected original-source probe profiles.

    Requires one CPU affinity and external finite CPU/address-space/wall limits.
    A rejected path candidate is retained separately from accepted positive
    proofs and never means physical disconnection. Existing output is preserved.

    Parameters
    ----------
    protocol, output : Path
        Frozen pilot protocol and a new receiving directory.
    originals : bool
        Explicitly include the selected original-source profiles; default false.

    Returns
    -------
    None
        Proofs, independent receipts and the final checksum manifest are saved.

    Raises
    ------
    ValueError
        Input, expected controls or the external resource envelope are invalid.
    FileExistsError
        Output already exists; earlier evidence is never overwritten.
    """
    if type(originals) is not bool:
        raise ValueError('Original-source selection must be explicit boolean')
    spec, digest = read_record_with_digest(protocol)
    if (
        spec['schema'] != 'topomt.reference-validator.hull-sterics-pilot/1'
        or spec['length_unit'] != 'nm'
        or spec['contact_policy'] != 'strict'
    ):
        raise ValueError('Unsupported hull-steric pilot protocol')
    if len(os.sched_getaffinity(0)) != 1:
        raise ValueError('Hull-steric pilot requires one CPU affinity')
    if (
        not 0 < resource.getrlimit(resource.RLIMIT_AS)[0] <= 2 * 1024**3
        or not 0 < resource.getrlimit(resource.RLIMIT_CPU)[0] <= 50
    ):
        raise ValueError(
            'Hull-steric pilot requires external 2 GiB/50 CPU-second ceilings'
        )
    selected = [(row, False) for row in spec['fixtures']] + (
        [(row, True) for row in spec['originals']] if originals else []
    )
    names = [_name(row['name']) for row, _ in selected]
    if not 1 <= len(names) <= 16 or len(set(names)) != len(names):
        raise ValueError('Invalid pilot profile count or duplicate names')
    root = Path(__file__).resolve().parents[2]
    if originals:
        reference = spec['path_reference']
        if read_record_with_digest(root / reference['path'])[1] != reference['sha256']:
            raise ValueError('Original path reference changed after protocol freeze')
    output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    profiles = []
    for row, original in selected:
        name = row['name']
        if original:
            certificate, hull_digest = read_record_with_digest(root / row['hull'])
            if hull_digest != row['hull_sha256']:
                raise ValueError('Original hull proof changed after protocol freeze')
            model = freeze_hull_model(
                root / row['input'],
                probe_angstroms=row['probe_angstroms'],
                certificate=certificate,
            )
            if (
                model.source_sha256 != row['input_sha256']
                or len(model.atoms) != row['n_atoms']
            ):
                raise ValueError('Original spheres differ from the frozen input')
        else:
            model = Model.from_record(row['seed']).with_center_hull()
        directory = output / name
        directory.mkdir(exist_ok=False)
        _write(directory / 'model.json', model.to_record())
        saved_model = Model.from_record(read_record(directory / 'model.json'))
        if saved_model != model:
            raise ValueError('Saved hull/steric model changed during receiving')
        queries = row['queries']
        query_names = [_name(query['name']) for query in queries]
        if not 1 <= len(queries) <= 32 or len(set(query_names)) != len(queries):
            raise ValueError('Invalid pilot query count or duplicate query names')
        query_dir = directory / 'queries'
        query_dir.mkdir()
        checked = {
            query['name']: _query(saved_model, query, query_dir) for query in queries
        }
        profiles.append(
            {
                'name': name,
                'original_source': original,
                'model_sha256': model.digest,
                'n_atoms': len(model.atoms),
                'queries': checked,
            }
        )
        print(f'Hull sterics {name}: {len(checked)} checked controls', flush=True)
    quantity = None
    if originals:
        from pyunitwizard import QuantityRecord

        quantity = {
            'dependency_versions': {
                name: version(name) for name in ['numpy', 'pyunitwizard']
            },
            'quantity_record_definition_sha256': hashlib.sha256(
                Path(inspect.getfile(QuantityRecord)).read_bytes()
            ).hexdigest(),
        }
    files = {
        str(path.relative_to(output)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(output.rglob('*.json'))
    }
    tool_root = Path(__file__).parent
    producer_names = [
        'capture_hull_sterics.py',
        'model.py',
        'producer.py',
        'receiving.py',
        'hull_model.py',
        'center_hull.py',
        'contracts.py',
        'storage.py',
        'verify/__init__.py',
        'verify/geometry.py',
        'verify/center_hull.py',
        'verify/polytope.py',
    ]
    _write(
        output / 'receipt.json',
        {
            'schema': 'topomt.reference-validator.hull-steric-receiving/1',
            'protocol_sha256': digest,
            'source_revision': subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], cwd=root, text=True
            ).strip(),
            'producer_files_sha256': {
                name: hashlib.sha256((tool_root / name).read_bytes()).hexdigest()
                for name in producer_names
            },
            'profiles': profiles,
            'originals_selected': originals,
            'quantity_receiving': quantity,
            'files': files,
            'elapsed_seconds': time.monotonic() - start,
            'peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'cpu_affinity': sorted(os.sched_getaffinity(0)),
            'address_space_limit_bytes': resource.getrlimit(resource.RLIMIT_AS)[0],
            'cpu_limit_seconds': resource.getrlimit(resource.RLIMIT_CPU)[0],
            'concurrency': 1,
            'python_version': sys.version,
            'scope': 'Selected hull/steric facts; general mixed free regions, boundary incidence and requested volume precision remain unqualified.',
        },
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--originals', action='store_true')
    args = parser.parse_args()
    capture(args.protocol, args.output, originals=args.originals)
