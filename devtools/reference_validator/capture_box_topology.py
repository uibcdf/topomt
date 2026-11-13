"""Retain exact P1 one-ball box controls without changing original studies."""

import argparse
import hashlib
import json
import os
import resource
import subprocess
import time
from pathlib import Path
from typing import Any

from .box_topology import single_ball_box
from .model import Model, record_digest
from .producer import partition
from .storage import read_record, read_record_with_digest
from .verify import verify


def capture(protocol_path: Path, output: Path) -> None:
    """Save/read/check the frozen analytic fixtures inside external limits.

    This developer helper requires one Linux CPU affinity and an externally
    bounded process. Expected fixture counts only check the independent result;
    they are not passed to the producer or mathematical checker.
    """
    spec, protocol_digest = read_record_with_digest(protocol_path)
    if spec['schema'] != 'topomt.reference-validator.box-topology-pilot/1':
        raise ValueError('Unsupported topology pilot protocol')
    if len(os.sched_getaffinity(0)) != 1:
        raise ValueError('Topology pilot requires one CPU affinity')
    output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    root = Path(__file__).resolve().parents[2]
    cases: dict[str, Any] = {}
    for case in spec['cases']:
        name = case['name']
        if (
            not isinstance(name, str)
            or not name.replace('_', '').isalnum()
            or name in cases
        ):
            raise ValueError('Invalid or duplicate topology fixture name')
        model = Model.from_record(case['model'])
        if case['method'] == 'single_ball_box':
            certificate = single_ball_box(model)
        elif case['method'] == 'partition' and not model.atoms:
            certificate = partition(model, max_depth=0)
        else:
            raise ValueError('Unsupported topology pilot method')
        for suffix, data in [
            ('model', model.to_record()),
            ('certificate', certificate),
        ]:
            with (output / f'{name}.{suffix}.json').open('x') as stream:
                json.dump(data, stream, indent=2, allow_nan=False)
                stream.write('\n')
        saved_model = Model.from_record(read_record(output / f'{name}.model.json'))
        checked = verify(saved_model, read_record(output / f'{name}.certificate.json'))
        if (
            not checked['topology_complete']
            or checked['n_components'] != case['expected_components']
        ):
            raise ValueError('Topology pilot did not establish its analytic control')
        with (output / f'{name}.verification.json').open('x') as stream:
            json.dump(checked, stream, indent=2, allow_nan=False)
            stream.write('\n')
        cases[name] = {
            'model_sha256': saved_model.digest,
            'certificate_sha256': checked['certificate_sha256'],
            'verification_sha256': record_digest(checked),
            'n_components': checked['n_components'],
        }
    files = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.glob('*.json'))
    }
    receipt = {
        'schema': 'topomt.reference-validator.box-topology-receiving/1',
        'protocol_sha256': protocol_digest,
        'source_revision': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=root, text=True
        ).strip(),
        'producer_files_sha256': {
            name: hashlib.sha256(
                (Path(__file__).parent / name).read_bytes()
            ).hexdigest()
            for name in [
                'box_topology.py',
                'capture_box_topology.py',
                'model.py',
                'producer.py',
                'storage.py',
            ]
        },
        'cases': cases,
        'files': files,
        'general_multi_ball_status': 'unresolved',
        'requested_precision_status': 'not_computed',
        'elapsed_seconds': time.monotonic() - start,
        'peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'cpu_affinity': sorted(os.sched_getaffinity(0)),
        'address_space_limit_bytes': resource.getrlimit(resource.RLIMIT_AS)[0],
    }
    with (output / 'receipt.json').open('x') as stream:
        json.dump(receipt, stream, indent=2, allow_nan=False)
        stream.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    capture(args.protocol, args.output)
