"""Developer-only saved verification and bounded partition production.

Use ``python -m devtools.reference_validator verify MODEL CERTIFICATE`` or
``python -m devtools.reference_validator produce MODEL OUTPUT --max-depth 4``.
Run under external CPU/memory/time limits. No optional scientific provider or
DFND module is imported by the verification command.
"""

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

from .model import Model
from .storage import load_bundle, save_bundle
from .storage import read_record as _read
from .verify import verify
from .verify.records import verify_run, verify_transition


def main() -> int:
    """Execute a bounded developer operation; report invalid evidence as failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    check = commands.add_parser('verify')
    check.add_argument('model', type=Path)
    check.add_argument('certificate', type=Path)
    produce = commands.add_parser('produce')
    produce.add_argument('model', type=Path)
    produce.add_argument('output', type=Path)
    produce.add_argument('--max-depth', type=int, default=4)
    produce.add_argument('--max-leaves', type=int, default=4096)
    topology = commands.add_parser('box-topology')
    topology.add_argument('model', type=Path)
    topology.add_argument('output', type=Path)
    domain_proof = commands.add_parser('domain-proof')
    domain_proof.add_argument('model', type=Path)
    domain_proof.add_argument('output', type=Path)
    integral = commands.add_parser('volume')
    integral.add_argument('model', type=Path)
    integral.add_argument('output', type=Path)
    integral.add_argument('--absolute-nm3')
    integral.add_argument('--relative')
    integral.add_argument('--max-atan-terms', type=int, default=64)
    integral.add_argument('--max-distance-bits', type=int, default=256)
    freeze = commands.add_parser('freeze-tetrahedron')
    freeze.add_argument('input', type=Path)
    freeze.add_argument('output', type=Path)
    freeze.add_argument('--probe-angstroms', type=float, required=True)
    hull_model = commands.add_parser('freeze-hull-model')
    hull_model.add_argument('input', type=Path)
    hull_model.add_argument('output', type=Path)
    hull_model.add_argument('--probe-angstroms', type=float, required=True)
    hull_model.add_argument('--hull-certificate', type=Path)
    hull_source = commands.add_parser('freeze-hull-source')
    hull_source.add_argument('input', type=Path)
    hull_source.add_argument('output', type=Path)
    hull = commands.add_parser('hull')
    hull.add_argument('source', type=Path)
    hull.add_argument('output', type=Path)
    clipped = commands.add_parser('clip-hull')
    clipped.add_argument('source', type=Path)
    clipped.add_argument('hull', type=Path)
    clipped.add_argument('output', type=Path)
    clipped.add_argument('--lower-nm', nargs=3, required=True)
    clipped.add_argument('--upper-nm', nargs=3, required=True)
    hull_check = commands.add_parser('verify-hull')
    hull_check.add_argument('source', type=Path)
    hull_check.add_argument('certificate', type=Path)
    for hull_command in (hull, clipped, hull_check):
        hull_command.add_argument('--max-centers', type=int, default=128)
        hull_command.add_argument('--max-facets', type=int, default=192)
        hull_command.add_argument('--max-plane-triples', type=int, default=1200000)
    start = commands.add_parser('start')
    start.add_argument('model', type=Path)
    start.add_argument('output', type=Path)
    start.add_argument('--max-depth', type=int, default=4)
    start.add_argument('--max-leaves', type=int, default=4096)
    start.add_argument('--split-budget', type=int, default=32)
    resume = commands.add_parser('resume')
    resume.add_argument('model', type=Path)
    resume.add_argument('previous', type=Path)
    resume.add_argument('output', type=Path)
    resume.add_argument('--split-budget', type=int, default=32)
    saved = commands.add_parser('verify-run')
    saved.add_argument('model', type=Path)
    saved.add_argument('directory', type=Path)
    saved.add_argument('--parent', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'freeze-hull-source':
            from .receiving import freeze_centers

            source = freeze_centers(args.input)
            with args.output.open('x') as stream:
                json.dump(source.to_record(), stream, indent=2, allow_nan=False)
                stream.write('\n')
            print(json.dumps({'source_sha256': source.digest}))
            return 0
        if args.command in {'hull', 'clip-hull', 'verify-hull'}:
            from .hull_model import CenterSource, HullLimits
            from .verify.center_hull import verify_hull

            source = CenterSource.from_record(_read(args.source))
            limits = HullLimits(
                args.max_centers, args.max_facets, args.max_plane_triples
            )
            if args.command == 'verify-hull':
                certificate = _read(args.certificate)
            else:
                from .center_hull import clip_certificate, hull_certificate
                from .model import Box, point

                if args.command == 'hull':
                    certificate = hull_certificate(source, limits=limits)
                else:
                    box = Box(
                        point([Fraction(v) for v in args.lower_nm]),
                        point([Fraction(v) for v in args.upper_nm]),
                    )
                    certificate = clip_certificate(
                        source, _read(args.hull), box, limits=limits
                    )
            result = verify_hull(source, certificate, limits=limits)
            if args.command != 'verify-hull':
                with args.output.open('x') as stream:
                    json.dump(certificate, stream, indent=2, allow_nan=False)
                    stream.write('\n')
            print(json.dumps(result, sort_keys=True, allow_nan=False))
            return 0
        if args.command in {'freeze-tetrahedron', 'freeze-hull-model'}:
            if args.command == 'freeze-tetrahedron':
                from .receiving import freeze_tetrahedron

                model = freeze_tetrahedron(
                    args.input, probe_angstroms=args.probe_angstroms
                )
            else:
                from .receiving import freeze_hull_model

                model = freeze_hull_model(
                    args.input,
                    probe_angstroms=args.probe_angstroms,
                    certificate=None
                    if args.hull_certificate is None
                    else _read(args.hull_certificate),
                )
            with args.output.open('x') as stream:
                json.dump(model.to_record(), stream, indent=2, allow_nan=False)
                stream.write('\n')
            print(json.dumps({'model_sha256': model.digest}))
            return 0
        model = Model.from_record(_read(args.model))
        if args.command == 'verify':
            result = verify(model, _read(args.certificate))
        elif args.command == 'verify-run':
            cp, run = load_bundle(args.directory, model)
            if args.parent is None:
                result = verify_run(model, run, cp)
            else:
                parent, _ = load_bundle(args.parent, model)
                result = verify_transition(model, parent, cp, run)
        elif args.command in {'start', 'resume'}:
            from .contracts import Configuration
            from .runs import resume_run, start_run

            if args.command == 'start':
                cp, run = start_run(
                    model,
                    configuration=Configuration(args.max_depth, args.max_leaves),
                    split_budget=args.split_budget,
                )
                result = verify_run(model, run, cp)
            else:
                parent, _ = load_bundle(args.previous, model)
                cp, run = resume_run(model, parent, split_budget=args.split_budget)
                result = verify_transition(model, parent, cp, run)
            save_bundle(args.output, model, cp, run)
        else:
            if args.command == 'volume':
                from .analytic_volume import volume_certificate
                from .volume_request import VolumeRequest

                request = VolumeRequest(
                    None if args.absolute_nm3 is None else Fraction(args.absolute_nm3),
                    None if args.relative is None else Fraction(args.relative),
                )
                certificate = volume_certificate(
                    model,
                    request,
                    max_atan_terms=args.max_atan_terms,
                    max_distance_bits=args.max_distance_bits,
                )
            elif args.command == 'domain-proof':
                from .producer import domain_certificate

                certificate = domain_certificate(model)
            elif args.command == 'box-topology':
                from .box_topology import single_ball_box

                certificate = single_ball_box(model)
            else:
                from .producer import partition

                certificate = partition(
                    model, max_depth=args.max_depth, max_leaves=args.max_leaves
                )
            result = verify(model, certificate)
            with args.output.open('x') as stream:
                json.dump(certificate, stream, indent=2, allow_nan=False)
                stream.write('\n')
        print(json.dumps(result, sort_keys=True, allow_nan=False))
    except (ValueError, TypeError, OverflowError, ZeroDivisionError, OSError) as exc:
        print(f'Reference validation failed: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
