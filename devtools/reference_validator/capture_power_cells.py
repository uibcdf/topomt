"""Retain bounded exact multi-ball regions, boundary patches and anchor proofs."""

import argparse
import hashlib
import json
import os
import re
import resource
import subprocess
import time
from pathlib import Path
from typing import Any

from .model import Model, _record, decode_point
from .power_cells import topology_certificate
from .storage import read_record, read_record_with_digest
from .verify import verify
from .verify.power_cells import query_anchors


def _write(path: Path, value: object) -> None:
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def _name(value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or not value.isascii()
        or not value.replace('_', '').isalnum()
    ):
        raise ValueError('Invalid power-cell fixture/anchor name')
    return value


def capture(protocol: Path, output: Path) -> None:
    """Save, independently read/check and measure a frozen small-control panel.

    Parameters
    ----------
    protocol, output : Path
        Frozen models/expectations and an exclusive new receiving directory.
        An expected count is checked only after independent verification.

    Returns
    -------
    None
        Exact models, proofs, query results and a final checksum receipt are
        written. The caller supplies an external finite wall deadline.

    Raises
    ------
    ValueError
        Input/expected controls are invalid or external one-CPU/finite CPU and
        address-space limits are absent. No physical answer replaces a failure.
    FileExistsError
        Earlier receiving evidence already occupies the output path.
    """
    spec, digest = read_record_with_digest(protocol)
    if (
        spec['schema'] != 'topomt.reference-validator.power-cell-pilot/1'
        or spec['length_unit'] != 'nm'
        or spec['contact_policy'] != 'strict'
        or not isinstance(spec['cases'], list)
        or not 1 <= len(spec['cases']) <= 64
    ):
        raise ValueError('Unsupported power-cell pilot protocol')
    if len(os.sched_getaffinity(0)) != 1:
        raise ValueError('Power-cell pilot requires one CPU affinity')
    cpu_limit = resource.getrlimit(resource.RLIMIT_CPU)[0]
    address_limit = resource.getrlimit(resource.RLIMIT_AS)[0]
    if cpu_limit == resource.RLIM_INFINITY or not 0 < address_limit <= 2 * 1024**3:
        raise ValueError(
            'Power-cell pilot requires finite CPU and <=2 GiB address limits'
        )
    names = [_name(row['name']) for row in spec['cases']]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate power-cell fixture name')
    output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    cpu_start = time.process_time()
    cases: dict[str, Any] = {}
    root = Path(__file__).resolve().parents[2]
    for row in spec['cases']:
        name = row['name']
        folder = output / name
        folder.mkdir()
        before, cpu_before = time.monotonic(), time.process_time()
        phase_wall, phase_cpu = before, cpu_before
        phases: dict[str, dict[str, float]] = {}

        def mark_phase(name: str) -> None:
            nonlocal phase_wall, phase_cpu
            wall, cpu = time.monotonic(), time.process_time()
            phases[name] = {
                'wall_seconds': wall - phase_wall,
                'cpu_seconds': cpu - phase_cpu,
            }
            phase_wall, phase_cpu = wall, cpu

        model = Model.from_record(row['model'])
        # Preserve the received input even if construction exhausts a budget.
        # Only the final receipt marks a complete receiving; this input alone
        # must never acquire an empty/disconnected geometric interpretation.
        _write(folder / 'model.json', model.to_record())
        mark_phase('model_receiving')
        reference = row.get('saved_certificate')
        if reference is None:
            proof = topology_certificate(model)
            origin = {'route': 'constructed_here'}
        else:
            _record(reference, {'path', 'sha256', 'producer_revision'})
            if (
                not isinstance(reference['path'], str)
                or not isinstance(reference['producer_revision'], str)
                or re.fullmatch('[0-9a-f]{40}', reference['producer_revision']) is None
            ):
                raise ValueError('Invalid saved-certificate provenance')
            proof, proof_digest = read_record_with_digest(
                root / Path(reference['path'])
            )
            if proof_digest != reference['sha256']:
                raise ValueError('Saved-certificate digest differs')
            origin = {'route': 'saved_certificate', **reference}
        _write(folder / 'certificate.json', proof)
        mark_phase('construction' if reference is None else 'saved_certificate_reading')
        saved_model = Model.from_record(read_record(folder / 'model.json'))
        saved_proof = read_record(folder / 'certificate.json')
        mark_phase('saved_reading')
        checked = verify(saved_model, saved_proof)
        for field, expectation in [
            ('n_components', 'expected_components'),
            ('n_boundary_patches', 'expected_boundary_patches'),
        ]:
            expected = row[expectation]
            if expected is not None and (
                type(expected) is not int or expected < 0 or checked[field] != expected
            ):
                raise ValueError(
                    'Checked power-cell result differs from frozen expectation'
                )
        _write(folder / 'verification.json', checked)
        mark_phase('verification')
        anchors = row['anchors']
        if not isinstance(anchors, dict) or len(anchors) > 32:
            raise ValueError('Invalid anchor inventory or work budget')
        points = {_name(key): decode_point(value) for key, value in anchors.items()}
        pairs = row['pairs']
        if not isinstance(pairs, list) or len(pairs) > 32:
            raise ValueError('Invalid anchor-pair inventory or work budget')
        connections: list[tuple[str, str]] = []
        for pair in pairs:
            if (
                not isinstance(pair, list)
                or len(pair) != 2
                or any(k not in anchors for k in pair)
            ):
                raise ValueError('Invalid named anchor pair')
            connections.append((pair[0], pair[1]))
        queries = (
            query_anchors(saved_model, saved_proof, anchors=points, pairs=connections)
            if points or connections
            else {
                'length_unit': 'nm',
                'model_sha256': saved_model.digest,
                'topology_certificate_sha256': checked['certificate_sha256'],
                'points': {},
                'locations': {},
                'pairs': [],
            }
        )
        _write(
            folder / 'anchors.json',
            queries,
        )
        mark_phase('anchor_queries')
        _write(folder / 'phases.json', phases)
        cases[name] = {
            'model_sha256': saved_model.digest,
            'certificate_sha256': checked['certificate_sha256'],
            'certificate_origin': origin,
            'n_components': checked['n_components'],
            'n_boundary_patches': checked['n_boundary_patches'],
            'per_region_volume_status': checked['per_region_volume_status'],
            'elapsed_seconds': time.monotonic() - before,
            'cpu_seconds': time.process_time() - cpu_before,
        }
    receipt = {
        'schema': 'topomt.reference-validator.power-cell-receiving/1',
        'protocol_sha256': digest,
        'source_revision': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=root, text=True
        ).strip(),
        'source_tree_modified': bool(
            subprocess.check_output(
                [
                    'git',
                    'status',
                    '--porcelain',
                    '--untracked-files=all',
                    '--',
                    'devtools/reference_validator',
                ],
                cwd=root,
                text=True,
            ).strip()
        ),
        'source_files_sha256': {
            str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(__file__).parent.rglob('*.py'))
        },
        'files': {
            str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob('*.json'))
        },
        'cases': cases,
        'elapsed_seconds': time.monotonic() - start,
        'cpu_seconds': time.process_time() - cpu_start,
        'peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'cpu_affinity': sorted(os.sched_getaffinity(0)),
        'address_space_limit_bytes': address_limit,
        'cpu_limit_seconds': cpu_limit,
        'requested_precision_status': 'not_computed',
        'native_dfnd_qualification': 'not_changed',
    }
    _write(output / 'receipt.json', receipt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    capture(args.protocol, args.output)
