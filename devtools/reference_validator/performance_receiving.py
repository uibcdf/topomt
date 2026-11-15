"""Run matched bounded measurements from an explicitly selected source tree.

Invoke this file directly to compare an archived baseline with the candidate.
The instrumentation comes from this driver; scientific imports come solely
from the selected source root. Limits/host sampling are supplied by the caller.
"""

import argparse
import hashlib
import json
import runpy
import sys
from fractions import Fraction
from pathlib import Path


def main() -> None:
    """Retain an exclusive phase/proof receipt for a frozen original protocol."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reuse', action='store_true')
    parser.add_argument('--profile', action='store_true')
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--max-leaves', type=int, default=64)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 3:
        raise ValueError('Measurement repeats must be in 1..3')
    measurements_type = runpy.run_path(str(Path(__file__).with_name('performance.py')))[
        'Measurements'
    ]
    sys.path.insert(0, str(args.source_root.resolve()))
    from devtools.reference_validator.model import Model, point
    from devtools.reference_validator.power_cells import topology_certificate
    from devtools.reference_validator.region_volume import region_volume_certificate
    from devtools.reference_validator.verify import verify
    from devtools.reference_validator.verify.power_cells import query_anchors
    from devtools.reference_validator.volume_request import VolumeRequest

    payload = args.protocol.read_bytes()
    spec = json.loads(payload)
    old_proof = json.loads((args.repository / spec['topology_path']).read_text())
    args.output.mkdir(parents=True, exist_ok=False)
    rows = []
    for repeat in range(args.repeats):
        measurements = measurements_type(profile=args.profile)
        model = measurements.run('model', lambda: Model.from_record(spec['model']))
        # Absolute original requests use the exact domain volume.
        from devtools.reference_validator.verify.geometry import volume

        request = VolumeRequest(
            volume(model.domain) / 2 ** spec['k'], Fraction(1, 2 ** spec['k'])
        )
        proof = measurements.run('construction', lambda: topology_certificate(model))
        if proof != old_proof:
            raise ValueError(
                'Reconstructed mathematical proof differs from frozen input'
            )
        if args.reuse:
            from devtools.reference_validator.verify.context import CheckedTopology

            context = measurements.run(
                'verification', lambda: CheckedTopology(model, proof)
            )
            checked = context.result
        else:
            checked = measurements.run('verification', lambda: verify(model, proof))
        center = point(
            [
                sum((p[i] for p in model.domain.vertices), Fraction())
                / len(model.domain.vertices)
                for i in range(3)
            ]
        )
        anchors = {'center': center}
        answer = measurements.run(
            'queries',
            lambda: (
                context.query_anchors(anchors=anchors, pairs=[])
                if args.reuse
                else query_anchors(model, proof, anchors=anchors, pairs=[])
            ),
        )
        cert = measurements.run(
            'integration',
            lambda: region_volume_certificate(
                model, proof, request, max_leaves=args.max_leaves
            ),
        )
        bounds = measurements.run('volume_checking', lambda: verify(model, cert))
        row = {
            'measurements': measurements.to_record(),
            'model_sha256': model.digest,
            'topology_complete': checked['topology_complete'],
            'queries': answer,
            'leaves': cert['leaves'],
            'request': request.to_record(),
            'bounds': {
                key: bounds[key]
                for key in (
                    'volume_lower',
                    'volume_upper',
                    'regions',
                    'precision_status',
                )
            },
        }
        rows.append(row)
        (args.output / f'repeat_{repeat}.json').write_text(
            json.dumps(row, indent=2) + '\n'
        )
    sources = {
        str(p.relative_to(args.source_root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (args.source_root / 'devtools/reference_validator').rglob('*.py')
    }
    (args.output / 'receipt.json').write_text(
        json.dumps(
            {
                'protocol_sha256': hashlib.sha256(payload).hexdigest(),
                'source_files': sources,
                'reuse': args.reuse,
                'profiled': args.profile,
                'completed_repeats': len(rows),
                'driver_sha256': hashlib.sha256(
                    Path(__file__).read_bytes()
                ).hexdigest(),
            },
            indent=2,
        )
        + '\n'
    )


if __name__ == '__main__':
    main()
