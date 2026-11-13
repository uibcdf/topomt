"""Capture the fixed P0 tetrahedron pilot under an external one-CPU envelope."""

import argparse
import hashlib
import inspect
import json
import os
import resource
import subprocess
import time
from importlib.metadata import version
from pathlib import Path

from .model import encode_point, point
from .producer import partition
from .receiving import freeze_tetrahedron
from .verify import verify


def capture(protocol_path: Path, output: Path) -> None:
    """Write fresh models/proofs/checks and a receipt without changing inputs.

    Parameters
    ----------
    protocol_path : Path
        Frozen P0 protocol, relative input paths resolved from this checkout.
    output : Path
        New destination directory. Existing paths are never overwritten.

    Raises
    ------
    ValueError
        The protocol/model differs, CPU affinity is not one or a control fails.
    FileExistsError
        Output already exists; retain it rather than overwrite evidence.
    """
    root = Path(__file__).resolve().parents[2]
    spec = json.loads(protocol_path.read_text())
    if spec['schema'] != 'topomt.reference-validator.tetrahedron-pilot/1':
        raise ValueError('Unsupported pilot protocol')
    source = root / spec['input']
    if hashlib.sha256(source.read_bytes()).hexdigest() != spec['input_sha256']:
        raise ValueError('Input differs from the frozen protocol')
    if len(os.sched_getaffinity(0)) != 1:
        raise ValueError('Pilot requires one CPU affinity and external resource limits')
    output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    rows = []

    def save(name: str, value: dict) -> None:
        with (output / name).open('x') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')

    requests = [(r['id'], r) for r in spec['partition_requests']]
    requests += [
        (f'point_{i}', {'probe_angstroms': p, 'kind': 'point'})
        for i, p in enumerate(spec['point_probes_angstroms'])
    ]
    requests += [
        (
            f'face_path_{i}',
            {
                'probe_angstroms': spec['path_probe_angstroms'],
                'kind': 'path',
                'face_index': i,
            },
        )
        for i in range(4)
    ]
    for name, request in requests:
        model = freeze_tetrahedron(source, probe_angstroms=request['probe_angstroms'])
        if model.source_sha256 != spec['input_sha256']:
            raise ValueError('Decoded model differs from the frozen input')
        if model.interpretation != spec['interpretation']:
            raise ValueError('Different numerical model interpretation')
        if request.get('kind') in {'point', 'path'}:
            vertices = model.domain.vertices
            center = point([sum(v[i] for v in vertices) / 4 for i in range(3)])
            cert = {
                'schema': 'topomt.reference-validator.certificate/1',
                'model_sha256': model.digest,
                'arithmetic': 'rational-exact/1',
                'kind': request['kind'],
            }
            if request['kind'] == 'point':
                cert.update(point=encode_point(center), claim='free')
            else:
                face = [v for i, v in enumerate(vertices) if i != request['face_index']]
                target = point([sum(v[i] for v in face) / 3 for i in range(3)])
                cert['points'] = [encode_point(center), encode_point(target)]
        else:
            cert = partition(
                model, max_depth=request['max_depth'], max_leaves=request['max_leaves']
            )
        result = verify(model, cert)
        if 'expected_components' in request:
            if result['n_components'] != request['expected_components']:
                raise ValueError(f'Unexpected pilot disposition: {name}')
        save(f'{name}.model.json', model.to_record())
        save(f'{name}.certificate.json', cert)
        save(f'{name}.verification.json', result)
        rows.append(
            {
                'id': name,
                'probe_angstroms': request['probe_angstroms'],
                'model_sha256': model.digest,
                'kind': cert['kind'],
                'n_components': result['n_components'],
                'topology_complete': result['topology_complete'],
            }
        )
    files = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.iterdir())
    }
    import pyunitwizard as puw
    from pyunitwizard import QuantityRecord

    quantity_root = Path(puw.__file__).resolve().parents[1]
    quantity_revision = None
    if (quantity_root / '.git').exists():
        revision = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=quantity_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if revision.returncode == 0:
            quantity_revision = revision.stdout.strip()
    save(
        'receipt.json',
        {
            'schema': 'topomt.reference-validator.p0-receiving/1',
            'protocol_sha256': hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
            'source_revision': subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], cwd=root, text=True
            ).strip(),
            'producer_files_sha256': {
                str(p.relative_to(Path(__file__).parent)): hashlib.sha256(
                    p.read_bytes()
                ).hexdigest()
                for p in sorted(Path(__file__).parent.rglob('*.py'))
            },
            'quantity_codec_source_revision': quantity_revision,
            'quantity_codec_file_sha256': hashlib.sha256(
                Path(inspect.getfile(QuantityRecord)).read_bytes()
            ).hexdigest(),
            'dependency_versions': {
                name: version(name) for name in ('pyunitwizard', 'numpy')
            },
            'models': rows,
            'files': files,
            'elapsed_seconds': time.monotonic() - start,
            'peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'cpu_affinity': sorted(os.sched_getaffinity(0)),
            'address_space_limit_bytes': resource.getrlimit(resource.RLIMIT_AS)[0],
            'scope': 'P0 developer proofs; no general topology, requested volume precision, native receiving, original provider or installed-package qualification',
        },
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path)
    parser.add_argument('output', type=Path)
    arguments = parser.parse_args()
    capture(arguments.protocol, arguments.output)
