"""Retain bounded analytic precision controls and optional MPFR cross-checks."""

import argparse
import hashlib
import json
import os
import resource
import subprocess
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

from .analytic_volume import volume_certificate
from .model import Model, encode_scalar, record_digest
from .storage import read_record, read_record_with_digest
from .verify import verify
from .volume_request import VolumeRequest


def _mpfr_audit() -> dict[str, Any]:
    """Compare constants to explicitly requested directed MPFR, not a runtime need."""
    import gmpy2 as g

    from .verify._interval import _pi, _sqrt

    def rational(value: Any) -> Fraction:
        a, b = value.as_integer_ratio()
        return Fraction(int(a), int(b))

    with g.context(precision=1024, round=g.RoundDown):
        pi_lo, root_lo = rational(g.const_pi()), rational(g.sqrt(g.mpfr(2)))
    with g.context(precision=1024, round=g.RoundUp):
        pi_hi, root_hi = rational(g.const_pi()), rational(g.sqrt(g.mpfr(2)))
    data = {}
    for name, bounds, lo, hi in [
        ('pi', _pi(64), pi_lo, pi_hi),
        ('sqrt_two', _sqrt(Fraction(2), 128), root_lo, root_hi),
    ]:
        if not bounds.lower <= lo <= hi <= bounds.upper:
            raise ValueError(
                'Directed MPFR cross-check does not fit the analytic enclosure'
            )
        data[name] = {
            'rational_lower': encode_scalar(bounds.lower),
            'rational_upper': encode_scalar(bounds.upper),
            'mpfr_lower': encode_scalar(lo),
            'mpfr_upper': encode_scalar(hi),
        }
    return {
        'schema': 'topomt.reference-validator.constant-crosscheck/1',
        'gmpy2_version': g.version(),
        'mpfr_version': g.mpfr_version(),
        'mpfr_precision_bits': 1024,
        'pi_atan_terms': 64,
        'sqrt_distance_bits': 128,
        'constants': data,
        'scope': 'Secondary constant cross-check; geometric coverage and independent proof do not depend on MPFR',
    }


def capture(
    protocol_path: Path, output: Path, *, crosscheck_mpfr: bool = False
) -> None:
    """Save/read/check the finite precision ladder under external resource limits.

    MPFR is optional, explicitly selected diagnostic evidence. The analytic
    producer and saved certificate checker use only standard-library arithmetic.
    Expected precision dispositions only compare checked results after execution.
    """
    spec, protocol_digest = read_record_with_digest(protocol_path)
    if spec['schema'] != 'topomt.reference-validator.analytic-volume-pilot/1':
        raise ValueError('Unsupported analytic volume pilot protocol')
    if len(os.sched_getaffinity(0)) != 1:
        raise ValueError('Volume pilot requires one CPU affinity')
    output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    root = Path(__file__).resolve().parents[2]
    audit = _mpfr_audit() if crosscheck_mpfr else None
    if audit is not None:
        with (output / 'constant_crosscheck.json').open('x') as stream:
            json.dump(audit, stream, indent=2, allow_nan=False)
            stream.write('\n')
    profiles = {}
    for row in spec['profiles']:
        name = row['name']
        if (
            not isinstance(name, str)
            or not name.replace('_', '').isalnum()
            or name in profiles
        ):
            raise ValueError('Invalid or duplicate precision profile name')
        model = Model.from_record(row['model'])
        request = VolumeRequest.from_record(row['request'])
        certificate = volume_certificate(
            model,
            request,
            max_atan_terms=row['max_atan_terms'],
            max_distance_bits=row['max_distance_bits'],
        )
        for suffix, data in [
            ('model', model.to_record()),
            ('certificate', certificate),
        ]:
            with (output / f'{name}.{suffix}.json').open('x') as stream:
                json.dump(data, stream, indent=2, allow_nan=False)
                stream.write('\n')
        saved = Model.from_record(read_record(output / f'{name}.model.json'))
        checked = verify(saved, read_record(output / f'{name}.certificate.json'))
        if (
            checked['precision_status'] != row['expected_precision']
            or checked['precision_request'] != row['request']
        ):
            raise ValueError(
                'Precision profile did not establish its frozen disposition'
            )
        with (output / f'{name}.verification.json').open('x') as stream:
            json.dump(checked, stream, indent=2, allow_nan=False)
            stream.write('\n')
        profiles[name] = {
            key: checked[key]
            for key in [
                'model_sha256',
                'certificate_sha256',
                'volume_lower',
                'volume_upper',
                'precision_status',
                'stop_reason',
            ]
        }
        profiles[name]['verification_sha256'] = record_digest(checked)
        profiles[name]['actual_refinement'] = certificate['refinement']
    files = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.glob('*.json'))
    }
    receipt = {
        'schema': 'topomt.reference-validator.analytic-volume-receiving/1',
        'protocol_sha256': protocol_digest,
        'source_revision': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=root, text=True
        ).strip(),
        'producer_files_sha256': {
            name: hashlib.sha256(
                (Path(__file__).parent / name).read_bytes()
            ).hexdigest()
            for name in [
                'analytic_volume.py',
                'capture_volume.py',
                'model.py',
                'storage.py',
                'volume_request.py',
            ]
        },
        'profiles': profiles,
        'files': files,
        'mpfr_crosscheck': None
        if audit is None
        else {
            'file': 'constant_crosscheck.json',
            'gmpy2_version': audit['gmpy2_version'],
            'mpfr_version': audit['mpfr_version'],
        },
        'general_topology_status': 'not_qualified',
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
    parser.add_argument('--crosscheck-mpfr', action='store_true')
    args = parser.parse_args()
    capture(args.protocol, args.output, crosscheck_mpfr=args.crosscheck_mpfr)
