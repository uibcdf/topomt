"""Developer-only saved verification and bounded partition production.

Use ``python -m devtools.reference_validator verify MODEL CERTIFICATE`` or
``python -m devtools.reference_validator produce MODEL OUTPUT --max-depth 4``.
Run under external CPU/memory/time limits. No optional scientific provider or
DFND module is imported by the verification command.
"""

import argparse
import json
import sys
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
    freeze = commands.add_parser('freeze-tetrahedron')
    freeze.add_argument('input', type=Path)
    freeze.add_argument('output', type=Path)
    freeze.add_argument('--probe-angstroms', type=float, required=True)
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
        if args.command == 'freeze-tetrahedron':
            from .receiving import freeze_tetrahedron

            model = freeze_tetrahedron(args.input, probe_angstroms=args.probe_angstroms)
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
            from .producer import partition

            certificate = partition(
                model, max_depth=args.max_depth, max_leaves=args.max_leaves
            )
            result = verify(model, certificate)
            with args.output.open('x') as stream:
                json.dump(certificate, stream, indent=2, allow_nan=False)
                stream.write('\n')
        print(json.dumps(result, sort_keys=True, allow_nan=False))
    except (ValueError, TypeError, OverflowError, OSError) as exc:
        print(f'Reference validation failed: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
